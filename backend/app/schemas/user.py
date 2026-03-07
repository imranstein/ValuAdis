"""
User Schemas for API Request/Response Models
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    municipality: str
    license_number: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    is_valuer: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []
    permissions: List[dict] = []
    
    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Permission response model"""
    id: int
    name: str
    display_name: str
    resource: str
    action: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    municipality: str
    license_number: str
    is_active: bool
    is_verified: bool
    is_approved: Optional[bool] = True
    is_admin: bool
    is_valuer: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []
    permissions: List[PermissionResponse] = []


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    municipality: str
    license_number: str
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    is_valuer: bool = True
    role_ids: List[int] = []
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Basic phone validation for Ethiopian numbers
        if not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +251)')
        return v
    
    @field_validator('license_number')
    @classmethod
    def validate_license_number(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('License number must be at least 3 characters long')
        return v.strip()


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    municipality: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_valuer: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip() if v else v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None and not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +251)')
        return v
    
    @field_validator('license_number')
    @classmethod
    def validate_license_number(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('License number must be at least 3 characters long')
        return v.strip() if v else v


class UserListResponse(BaseModel):
    success: bool
    data: List[UserResponse]
    total: int
    skip: int
    limit: int
    message: str
