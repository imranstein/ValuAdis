"""
User Schemas for API Request/Response Models
"""

from pydantic import BaseModel, EmailStr, validator
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


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    password: str
    municipality: str
    license_number: str
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    is_valuer: bool = True
    role_ids: Optional[List[int]] = []
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation for Ethiopian numbers
        if not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +251)')
        return v
    
    @validator('license_number')
    def validate_license_number(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('License number must be at least 3 characters long')
        return v.strip()


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    municipality: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_valuer: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip() if v else v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +251)')
        return v
    
    @validator('license_number')
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
