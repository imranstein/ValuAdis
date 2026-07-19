"""
Settings Module

Owner of the /api/v1/settings contract: user preferences and API-key
management, backed by UserSetting and ApiKey models.
"""

from .routes import router as settings_router
from app.data.models.settings import ApiKey, UserSetting

__all__ = ["settings_router", "ApiKey", "UserSetting"]
