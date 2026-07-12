"""
Settings API Routes

Owner-scoped user preferences and API-key lifecycle. Preferences upsert onto a
single per-user row. API keys are generated with secrets.token_urlsafe; only a
SHA-256 hash and a short display prefix are stored, so the plaintext is
returned exactly once at creation and can never be retrieved again.
"""

import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.data.models.settings import ApiKey, UserSetting

from .schemas import (
    DEFAULT_PREFERENCES,
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    PreferencesResponse,
    PreferencesUpdate,
)

router = APIRouter()

KEY_PREFIX_LENGTH = 8


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


@router.get("", response_model=PreferencesResponse)
def get_preferences(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PreferencesResponse:
    """Return the caller's saved preferences, or sensible defaults if unset."""
    setting = (
        db.query(UserSetting)
        .filter(UserSetting.user_id == current_user_id)
        .first()
    )
    if setting is None:
        return PreferencesResponse(preferences=dict(DEFAULT_PREFERENCES))
    return PreferencesResponse(preferences=setting.preferences or {})


@router.put("", response_model=PreferencesResponse)
def update_preferences(
    payload: PreferencesUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PreferencesResponse:
    """Upsert the caller's preferences over the current defaults."""
    setting = (
        db.query(UserSetting)
        .filter(UserSetting.user_id == current_user_id)
        .first()
    )
    merged = {**DEFAULT_PREFERENCES, **payload.preferences}
    if setting is None:
        setting = UserSetting(user_id=current_user_id, preferences=merged)
        db.add(setting)
    else:
        setting.preferences = merged
    db.commit()
    db.refresh(setting)
    return PreferencesResponse(preferences=setting.preferences)


@router.post(
    "/api-keys",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_api_key(
    payload: ApiKeyCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ApiKeyCreatedResponse:
    """Generate a key, store only its hash + prefix, return the plaintext once."""
    raw_key = secrets.token_urlsafe(32)
    api_key = ApiKey(
        user_id=current_user_id,
        name=payload.name,
        key_prefix=raw_key[:KEY_PREFIX_LENGTH],
        key_hash=_hash_key(raw_key),
        revoked=False,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        revoked=api_key.revoked,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        key=raw_key,
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[ApiKey]:
    """List the caller's keys without the secret or its hash."""
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user_id)
        .order_by(ApiKey.id)
        .all()
    )


@router.delete("/api-keys/{key_id}", response_model=ApiKeyResponse)
def revoke_api_key(
    key_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ApiKey:
    """Soft-delete (revoke) one of the caller's own keys."""
    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.user_id == current_user_id)
        .first()
    )
    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked = True
    db.commit()
    db.refresh(api_key)
    return api_key
