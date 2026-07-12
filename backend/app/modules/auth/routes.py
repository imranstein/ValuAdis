"""
Authentication Endpoints

JWT authentication for ValuAdis users
"""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user_id,
    validate_ethiopian_phone_number
)
from app.core.exceptions import AuthenticationException, ValidationException
from .schemas import UserLogin, UserRegister, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer(auto_error=False)

# httpOnly refresh cookie for browser session persistence.
# Path-limited so the browser only sends it to the refresh endpoint.
REFRESH_COOKIE_NAME = "valuadis_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"
SECONDS_PER_DAY = 24 * 60 * 60


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * SECONDS_PER_DAY,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )


def token_envelope(tokens: TokenResponse, message: str):
    return {
        "success": True,
        "message": message,
        "data": tokens.model_dump(),
    }


def error_envelope(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message},
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register new user"""
    auth_service = AuthService(db)
    
    # Validate Ethiopian phone number
    if not validate_ethiopian_phone_number(user_data.phone):
        return error_envelope(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Invalid Ethiopian phone number format",
        )
    
    # Create user
    try:
        user = await auth_service.create_user(user_data.model_dump())
    except ValidationException as exc:
        return error_envelope(status.HTTP_400_BAD_REQUEST, str(exc))
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return token_envelope(
        TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        "Registration successful",
    )


@router.post("/login", tags=["Authentication"])
async def login(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login user and return JWT tokens"""
    auth_service = AuthService(db)

    # Authenticate user
    try:
        user = await auth_service.authenticate_user(
            user_credentials.email,
            user_credentials.password,
        )
    except AuthenticationException as exc:
        return error_envelope(status.HTTP_401_UNAUTHORIZED, str(exc))

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Browser session persistence; JSON body stays unchanged for mobile clients
    set_refresh_cookie(response, refresh_token)

    return token_envelope(
        TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        "Login successful",
    )


@router.post("/refresh", tags=["Authentication"])
async def refresh_token(
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    refresh_cookie: Optional[str] = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
):
    """Refresh access token — rotates the refresh token on every call.

    Accepts the refresh token as a bearer header (mobile) or as the
    httpOnly valuadis_refresh cookie (browser). The header wins when both
    are present.
    """
    raw_token = credentials.credentials if credentials else refresh_cookie
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token"
        )

    try:
        payload = verify_token(raw_token)

        # Reject access tokens used as refresh tokens
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Issue fresh access + refresh tokens (rotation)
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})

        set_refresh_cookie(response, new_refresh_token)

        return token_envelope(
            TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            "Token refreshed",
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", tags=["Authentication"])
async def logout(response: Response):
    """Logout the browser session by clearing the refresh cookie.

    Access tokens are short-lived and stateless; clients drop them locally.
    """
    clear_refresh_cookie(response)
    return {"success": True, "message": "Logged out"}


@router.get("/me", tags=["Authentication"])
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = get_current_user_id(credentials.credentials)
    auth_service = AuthService(db)
    
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        role_names = [r.name for r in user.roles] if user.roles else []
    except SQLAlchemyError:
        role_names = []
    primary_role = role_names[0] if role_names else ("system_admin" if user.is_admin else "valuer")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "municipality": user.municipality,
        "license_number": user.license_number,
        "is_admin": user.is_admin,
        "role": primary_role,
        "roles": role_names,
        "created_at": user.created_at
    }
