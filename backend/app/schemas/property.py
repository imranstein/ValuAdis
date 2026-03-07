"""
Property Schemas

Pydantic models for property request/response - extended for wizard
"""

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


class SpatialRequest(BaseModel):
    coordinates: List[List[float]]


class OverlapRequest(BaseModel):
    coordinates_a: List[List[float]]
    coordinates_b: List[List[float]]


class PropertyCreate(BaseModel):
    # Identity
    parcel_number: Optional[str] = None
    title_deed_number: Optional[str] = None
    registration_date: Optional[datetime] = None

    # Location (required)
    address: str
    municipality: str
    region: Optional[str] = None
    subcity: Optional[str] = None
    woreda: Optional[str] = None
    kebele: Optional[str] = None
    zone: Optional[str] = None
    neighborhood: Optional[str] = None

    # Classification
    property_type: str
    property_subtype: Optional[str] = None

    # Spatial
    coordinates: Optional[List[List[float]]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_sqm: float
    building_area_sqm: Optional[float] = None

    # Physical
    number_of_floors: Optional[int] = None
    number_of_rooms: Optional[int] = None
    number_of_bedrooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    construction_material: Optional[str] = None
    roof_material: Optional[str] = None
    floor_material: Optional[str] = None
    construction_quality: Optional[str] = None
    condition: Optional[str] = None
    parking_spaces: Optional[int] = 0

    # Amenities & Utilities
    amenities: Optional[Dict[str, bool]] = Field(default_factory=dict)
    utilities: Optional[Dict[str, bool]] = Field(default_factory=dict)
    additional_features: Optional[str] = None

    # Ownership
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_id_type: Optional[str] = None
    owner_id_number: Optional[str] = None
    ownership_type: Optional[str] = None
    legal_description: Optional[str] = None

    # Valuation
    valuation_method: Optional[str] = None
    land_value: Optional[float] = None
    building_value: Optional[float] = None
    market_value: Optional[float] = None
    valuation_date: Optional[datetime] = None
    valuer_name: Optional[str] = None
    valuer_license_number: Optional[str] = None
    valuer_phone: Optional[str] = None
    comparable_properties: Optional[List[Dict]] = Field(default_factory=list)
    valuation_notes: Optional[str] = None

    # AI valuation metadata — stored on the property so reviewer panel can activate
    ai_estimated_value: Optional[float] = None
    ai_confidence_score: Optional[float] = None
    ai_trust_score_at_time: Optional[float] = None

    @validator('address')
    def validate_address(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Address must be at least 5 characters')
        return v.strip()

    @validator('property_type')
    def validate_property_type(cls, v):
        allowed = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use', 'institutional', 'recreational']
        if v not in allowed:
            raise ValueError(f'Property type must be one of: {", ".join(allowed)}')
        return v

    @validator('area_sqm')
    def validate_area(cls, v):
        if v <= 0:
            raise ValueError('Area must be greater than 0')
        return v


class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    municipality: Optional[str] = None
    region: Optional[str] = None
    subcity: Optional[str] = None
    woreda: Optional[str] = None
    kebele: Optional[str] = None
    zone: Optional[str] = None
    neighborhood: Optional[str] = None
    property_type: Optional[str] = None
    property_subtype: Optional[str] = None
    coordinates: Optional[List[List[float]]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_sqm: Optional[float] = None
    building_area_sqm: Optional[float] = None
    number_of_floors: Optional[int] = None
    number_of_rooms: Optional[int] = None
    number_of_bedrooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    construction_material: Optional[str] = None
    roof_material: Optional[str] = None
    floor_material: Optional[str] = None
    construction_quality: Optional[str] = None
    condition: Optional[str] = None
    parking_spaces: Optional[int] = None
    amenities: Optional[Dict[str, bool]] = None
    utilities: Optional[Dict[str, bool]] = None
    additional_features: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_id_type: Optional[str] = None
    owner_id_number: Optional[str] = None
    ownership_type: Optional[str] = None
    legal_description: Optional[str] = None
    valuation_method: Optional[str] = None
    land_value: Optional[float] = None
    building_value: Optional[float] = None
    market_value: Optional[float] = None
    taxable_value: Optional[float] = None
    valuation_date: Optional[datetime] = None
    valuer_name: Optional[str] = None
    valuer_license_number: Optional[str] = None
    valuer_phone: Optional[str] = None
    comparable_properties: Optional[List[Dict]] = None
    valuation_notes: Optional[str] = None
    status: Optional[str] = None

    # AI valuation metadata
    ai_estimated_value: Optional[float] = None
    ai_confidence_score: Optional[float] = None
    ai_trust_score_at_time: Optional[float] = None

    @validator('property_type')
    def validate_property_type(cls, v):
        if v is not None:
            allowed = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use', 'institutional', 'recreational']
            if v not in allowed:
                raise ValueError(f'Property type must be one of: {", ".join(allowed)}')
        return v


class PropertyResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class PropertyListResponse(BaseModel):
    success: bool
    data: Optional[List[dict]] = None
    total: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None
    message: Optional[str] = None


class PropertyDetail(BaseModel):
    id: int
    property_ref: Optional[str] = None
    address: str
    municipality: str
    region: Optional[str] = None
    property_type: str
    property_subtype: Optional[str] = None
    area_sqm: float
    building_area_sqm: Optional[float] = None
    condition: Optional[str] = None
    market_value: Optional[float] = None
    taxable_value: Optional[float] = None
    ai_estimated_value: Optional[float] = None
    ai_confidence_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
