"""
Valuation Schemas

Pydantic models for valuation request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Tuple, Optional
from datetime import datetime


class ValuationCreate(BaseModel):
    """Valuation creation request"""
    property_id: int = Field(..., description="ID of the property being valued")
    property_type: str = Field(..., description="Type of property (residential, commercial, agricultural)")
    municipality: str = Field(..., description="Ethiopian municipality")
    area_sqm: float = Field(..., gt=0, lt=100_000, description="Property area in square meters")
    coordinates: List[Tuple[float, float]] = Field(..., description="GPS boundary coordinates")
    
    @validator('property_type')
    def validate_property_type(cls, v):
        allowed_types = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use']
        if v not in allowed_types:
            raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('municipality')
    def validate_municipality(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Municipality name must be at least 2 characters')
        return v.strip()
    
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


class ValuationUpdate(BaseModel):
    """Valuation update request"""
    property_type: Optional[str] = None
    municipality: Optional[str] = None
    area_sqm: Optional[float] = None
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
    
    @validator('area_sqm')
    def validate_area_sqm(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Area must be greater than 0')
        return v


class ValuationResponse(BaseModel):
    """Valuation response"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class ValuationListResponse(BaseModel):
    """Valuation list response"""
    success: bool
    data: Optional[List[dict]] = None
    total: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None
    message: Optional[str] = None


class ValuationDetail(BaseModel):
    """Valuation detail model"""
    id: int
    property_id: int
    property_type: str
    municipality: str
    area_sqm: float
    market_value: Optional[float]
    taxable_value: Optional[float]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ValuationCalculation(BaseModel):
    """Valuation calculation result"""
    market_value: float = Field(..., description="Calculated market value in ETB")
    taxable_value: float = Field(..., description="25% of market value per Proclamation 1365/2025")
    base_rate: float = Field(..., description="Base rate per sqm used")
    multiplier: float = Field(..., description="Property type multiplier applied")
    calculation_date: datetime = Field(default_factory=datetime.now)
