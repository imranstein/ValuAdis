"""Scalability configuration tests."""

from app.core.config import Settings


def test_database_pool_settings_are_configurable():
    settings = Settings(
        DB_POOL_SIZE=16,
        DB_MAX_OVERFLOW=24,
        DB_POOL_TIMEOUT=15,
        DB_POOL_RECYCLE_SECONDS=120,
    )

    assert settings.DB_POOL_SIZE == 16
    assert settings.DB_MAX_OVERFLOW == 24
    assert settings.DB_POOL_TIMEOUT == 15
    assert settings.DB_POOL_RECYCLE_SECONDS == 120


def test_database_pool_settings_have_safe_defaults():
    settings = Settings()

    assert settings.DB_POOL_SIZE >= 1
    assert settings.DB_MAX_OVERFLOW >= 0
    assert settings.DB_POOL_TIMEOUT >= 1
    assert settings.DB_POOL_RECYCLE_SECONDS >= 60
