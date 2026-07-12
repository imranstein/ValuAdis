"""
Settings Module Schemas

Request/response contracts for user preferences and API-key management. The
plaintext API key appears only in ApiKeyCreatedResponse (the create response);
list responses never carry the secret or its hash.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

DEFAULT_PREFERENCES: Dict[str, Any] = {
    "email_notifications": True,
    "sms_notifications": False,
    "valuation_updates": True,
    "marketing_emails": False,
    "language": "en",
    "theme": "light",
}


class PreferencesResponse(BaseModel):
    preferences: Dict[str, Any]


class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Any] = Field(default_factory=dict)


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    revoked: bool
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned once on creation; carries the plaintext key, never persisted."""

    key: str
