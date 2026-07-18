"""
In-memory rate limiter — pure unit tests (Phase D hardening).

No DB, no HTTP: exercises the sliding-window counter directly so the
threshold math itself is exhaustively covered without spinning up 60+ real
requests per test.
"""

import pytest

from app.modules.rentals.exceptions import RateLimitError
from app.modules.rentals.rate_limit import InMemoryRateLimiter


class TestInMemoryRateLimiter:
    def test_allows_requests_under_the_limit(self):
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.check("1.2.3.4", window_seconds=60, max_hits=5)  # does not raise

    def test_blocks_the_request_that_exceeds_the_limit(self):
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.check("1.2.3.4", window_seconds=60, max_hits=5)
        with pytest.raises(RateLimitError):
            limiter.check("1.2.3.4", window_seconds=60, max_hits=5)

    def test_keys_are_independent(self):
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.check("1.2.3.4", window_seconds=60, max_hits=5)
        limiter.check("5.6.7.8", window_seconds=60, max_hits=5)  # different key, does not raise

    def test_old_hits_outside_the_window_do_not_count(self):
        limiter = InMemoryRateLimiter()
        for _ in range(5):
            limiter.check("1.2.3.4", window_seconds=0, max_hits=5)
        # window_seconds=0 means every prior hit is immediately "outside the
        # window", so the counter never actually fills.
        limiter.check("1.2.3.4", window_seconds=0, max_hits=5)
