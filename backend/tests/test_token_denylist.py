"""
Token Denylist Tests

The in-process fallback must hold refresh-token revocations when Redis is
unreachable (dev/tests); expired entries must not linger.
"""

import time

import pytest
import redis as redis_lib

from app.core import token_denylist


class _DownRedis:
    """Redis stand-in that is always unreachable"""

    def setex(self, *args, **kwargs):
        raise redis_lib.ConnectionError("redis unavailable")

    def exists(self, *args, **kwargs):
        raise redis_lib.ConnectionError("redis unavailable")


@pytest.fixture
def down_redis(monkeypatch):
    monkeypatch.setattr(token_denylist, "redis_client", _DownRedis())
    token_denylist._local_denylist.clear()
    yield
    token_denylist._local_denylist.clear()


class TestLocalFallbackDenylist:
    def test_denylisted_jti_is_reported_revoked(self, down_redis):
        token_denylist.denylist_jti("jti-revoked", time.time() + 60)

        assert token_denylist.is_jti_denylisted("jti-revoked") is True

    def test_unknown_jti_is_not_revoked(self, down_redis):
        assert token_denylist.is_jti_denylisted("jti-unknown") is False

    def test_already_expired_token_is_not_stored(self, down_redis):
        token_denylist.denylist_jti("jti-expired", time.time() - 10)

        assert token_denylist.is_jti_denylisted("jti-expired") is False

    def test_missing_jti_is_a_noop(self, down_redis):
        token_denylist.denylist_jti("", time.time() + 60)

        assert token_denylist.is_jti_denylisted("") is False

    def test_expired_entries_are_purged_on_check(self, down_redis, monkeypatch):
        real_time = time.time
        token_denylist.denylist_jti("jti-short", real_time() + 5)
        monkeypatch.setattr(token_denylist.time, "time", lambda: real_time() + 10)

        assert token_denylist.is_jti_denylisted("jti-short") is False
        assert "jti-short" not in token_denylist._local_denylist
