"""
Public-endpoint rate limiting (Phase D hardening)

Applications already have a per-account rate limit built on a plain DB row
count (application_service.py). Search and signup are anonymous — there is
no authenticated account to count rows against — so this uses the same
"simple, no Redis" mechanism family via an in-process sliding-window counter
keyed by client IP instead of a DB query. Single-process pilot deployment;
if this scales to multiple workers, swap the in-memory dict for a shared
store (Redis) without changing the call sites.
"""

import threading
import time
from collections import defaultdict
from typing import Dict, List

from .exceptions import RateLimitError

# Public listing search: generous enough for real browsing, tight enough to
# blunt scraping bursts.
SEARCH_RATE_LIMIT_WINDOW_SECONDS = 60
SEARCH_RATE_LIMIT_MAX_REQUESTS = 60

# Citizen signup: an account-creation endpoint, so the budget is tighter
# than search (abuse risk is fake accounts, not scraping). Same window and
# ceiling as the Phase C per-account application limit — one deliberately
# consistent number across the module's rate limits, and enough headroom
# for a shared household/office IP signing up several real accounts.
SIGNUP_RATE_LIMIT_WINDOW_SECONDS = 3600
SIGNUP_RATE_LIMIT_MAX_REQUESTS = 10


class InMemoryRateLimiter:
    """Fixed-window-ish limiter: keeps only hit timestamps within the
    trailing `window_seconds` per key, thread-safe for FastAPI's threadpool."""

    def __init__(self):
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, key: str, window_seconds: int, max_hits: int) -> None:
        now = time.time()
        with self._lock:
            recent = [t for t in self._hits[key] if now - t < window_seconds]
            if len(recent) >= max_hits:
                self._hits[key] = recent
                raise RateLimitError("Rate limit reached. Please try again later.")
            recent.append(now)
            self._hits[key] = recent


# One bucket per protected surface so a burst against one endpoint cannot
# exhaust another's budget.
search_rate_limiter = InMemoryRateLimiter()
signup_rate_limiter = InMemoryRateLimiter()


def client_ip(request) -> str:
    """Best-effort client identity for anonymous rate limiting."""
    if request is None or request.client is None:
        return "unknown"
    return request.client.host or "unknown"
