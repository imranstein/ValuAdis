"""
ValuAdis Security Module

JWT authentication, password hashing, and security utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import uuid4
from jose import JWTError, jwt
import bcrypt
import base64
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.

    Fails closed: anything that is not a bcrypt hash (plaintext, SHA-256,
    corrupt values) never verifies.
    """
    if not hashed_password or not hashed_password.startswith('$2'):
        return False

    # Truncate password to 72 characters max for bcrypt compatibility
    if len(plain_password) > 72:
        plain_password = plain_password[:72]

    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash with direct bcrypt"""
    # Truncate password to 72 characters max for bcrypt compatibility
    if len(password) > 72:
        password = password[:72]

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    to_encode.update({"type": "access"})
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # jti makes every refresh token unique so rotation always changes the value
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extract user ID from JWT token"""
    payload = verify_token(token)
    raw_sub = payload.get("sub")
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if raw_sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    try:
        return int(raw_sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def validate_ethiopian_phone_number(phone: str) -> bool:
    """Validate Ethiopian phone number format"""
    # Ethiopian phone numbers: +2519xxxxxxxx or 09xxxxxxxx
    import re
    
    # Remove any non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Ethiopian number
    if phone_digits.startswith('2519') and len(phone_digits) == 12:
        return True
    elif phone_digits.startswith('09') and len(phone_digits) == 10:
        return True
    
    return False


def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    import html
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove any potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """Get current user ID from JWT token - alias for get_current_user_id"""
    return get_current_user_id(token)


def validate_ethiopian_license(license: str) -> dict:
    """
    Validate Ethiopian business license number format

    Expected format: XXX-NNNNNNNNNN (e.g., AA-1234567890)
    - 2-4 uppercase letters (prefix indicating region/authority)
    - Hyphen separator
    - 6-10 digits

    Returns:
        dict: {"valid": bool, "error": str|None}
    """
    import re

    # Check if license is provided
    if not license or not isinstance(license, str):
        return {"valid": False, "error": "License number is required"}

    # Trim whitespace
    trimmed = license.strip()

    # Check length
    if len(trimmed) < 9:
        return {"valid": False, "error": "License number must be at least 9 characters"}

    if len(trimmed) > 20:
        return {"valid": False, "error": "License number must not exceed 20 characters"}

    # Ethiopian license format: XXX-NNNNNNNNNN
    # - 2-4 uppercase letters (prefix)
    # - hyphen separator
    # - 10 digits
    ethiopian_license_regex = re.compile(r'^[A-Z]{2,4}-\d{10}$')

    if not ethiopian_license_regex.match(trimmed):
        return {
            "valid": False,
            "error": "Invalid Ethiopian license format. Expected format: XXX-NNNNNNNNNN (e.g., AA-1234567890)"
        }

    return {"valid": True, "error": None}
