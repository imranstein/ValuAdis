"""
Authentication Schemas

Pydantic models for authentication request/response
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    full_name: str
    phone: str
    password: str
    municipality: str
    license_number: str
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Full name must be at least 3 characters')
        return v.strip()
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        # Ethiopian phone validation
        if not v.startswith('+2519') and not v.startswith('09'):
            raise ValueError('Invalid Ethiopian phone number format')
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    full_name: str
    phone: str
    municipality: str
    license_number: str
    is_active: bool
    is_verified: bool
    created_at: str
    model_config = ConfigDict(from_attributes=True)
