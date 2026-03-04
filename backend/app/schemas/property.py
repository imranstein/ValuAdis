"""
Property Schemas

Pydantic models for property request/response
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Tuple
from datetime import datetime


class PropertyCreate(BaseModel):
    """Property creation request"""
    address: str
    municipality: str
    property_type: str  # residential, commercial, agricultural
    coordinates: List[Tuple[float, float]]  # GPS boundary coordinates
    
    @validator('address')
    def validate_address(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Address must be at least 5 characters')
        return v.strip()
    
    @validator('property_type')
    def validate_property_type(cls, v):
        allowed_types = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use']
        if v not in allowed_types:
            raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if len(v) < 4:
            raise ValueError('At least 3 coordinate points required to form a polygon')
        
        # Check if polygon is closed
        if v[0] != v[-1]:
            raise ValueError('Coordinates must form a closed polygon (first == last)')
        
        # Validate coordinate ranges
        for lon, lat in v:
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                raise ValueError('Invalid coordinate range')
        
        return v


class PropertyUpdate(BaseModel):
    """Property update request"""
    address: Optional[str] = None
    municipality: Optional[str] = None
    property_type: Optional[str] = None
    coordinates: Optional[List[Tuple[float, float]]] = None
    market_value: Optional[float] = None
    taxable_value: Optional[float] = None
    status: Optional[str] = None
    
    @validator('property_type')
    def validate_property_type(cls, v):
        if v is not None:
            allowed_types = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use']
            if v not in allowed_types:
                raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v is not None:
            if len(v) < 4:
                raise ValueError('At least 3 coordinate points required to form a polygon')
            
            # Check if polygon is closed
            if v[0] != v[-1]:
                raise ValueError('Coordinates must form a closed polygon (first == last)')
            
            # Validate coordinate ranges
            for lon, lat in v:
                if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                    raise ValueError('Invalid coordinate range')
        
        return v


class PropertyResponse(BaseModel):
    """Property response"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class PropertyListResponse(BaseModel):
    """Property list response"""
    success: bool
    data: Optional[List[dict]] = None
    total: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None
    message: Optional[str] = None


class PropertyDetail(BaseModel):
    """Property detail model"""
    id: int
    address: str
    municipality: str
    property_type: str
    area_sqm: float
    market_value: Optional[float]
    taxable_value: Optional[float]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
