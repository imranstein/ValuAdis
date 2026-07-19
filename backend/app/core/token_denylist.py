"""
Refresh Token Denylist

Revoked refresh-token jti values, stored in Redis with a TTL equal to the
token's remaining lifetime. When Redis is unavailable (dev/tests) an
in-process dict with per-entry expiry is used so revocation still holds
within the running process.
"""

import time
from typing import Dict, Optional

import redis as redis_lib

from app.core.redis import redis_client

DENYLIST_KEY_PREFIX = "token_denylist:"

# jti -> unix expiry timestamp; fallback when Redis is unreachable
_local_denylist: Dict[str, float] = {}


def _purge_expired_local(now: float) -> None:
    expired = [jti for jti, expires_at in _local_denylist.items() if expires_at <= now]
    for jti in expired:
        del _local_denylist[jti]


def denylist_jti(jti: str, expires_at: Optional[float]) -> None:
    """Denylist a refresh token's jti until the token itself expires.

    expires_at is the token's exp claim (unix timestamp); an already
    expired token needs no denylist entry because verification rejects it.
    """
    if not jti:
        return
    now = time.time()
    ttl_seconds = int(expires_at - now) if expires_at else 0
    if ttl_seconds <= 0:
        return
    try:
        redis_client.setex(f"{DENYLIST_KEY_PREFIX}{jti}", ttl_seconds, "revoked")
    except redis_lib.RedisError:
        _purge_expired_local(now)
        _local_denylist[jti] = now + ttl_seconds


def is_jti_denylisted(jti: str) -> bool:
    """Check whether a refresh token's jti has been revoked."""
    if not jti:
        return False
    now = time.time()
    _purge_expired_local(now)
    if jti in _local_denylist:
        return True
    try:
        return bool(redis_client.exists(f"{DENYLIST_KEY_PREFIX}{jti}"))
    except redis_lib.RedisError:
        return False
