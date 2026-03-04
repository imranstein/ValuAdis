"""
Vehicle Valuation Pydantic Schemas

Request and response schemas for vehicle valuation API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Base schemas
class VehicleBase(BaseModel):
    make: str = Field(..., min_length=1, max_length=100, description="Vehicle manufacturer")
    model: str = Field(..., min_length=1, max_length=100, description="Vehicle model")
    year: int = Field(..., ge=1900, le=datetime.now().year + 1, description="Vehicle year")
    vin: str = Field(..., min_length=17, max_length=17, description="Vehicle Identification Number")
    plate_number: str = Field(..., min_length=1, max_length=20, description="License plate number")
    
    body_type: Optional[str] = Field(None, max_length=50, description="Vehicle body type")
    fuel_type: Optional[str] = Field(None, max_length=20, description="Fuel type")
    transmission: Optional[str] = Field(None, max_length=20, description="Transmission type")
    engine_capacity: Optional[float] = Field(None, ge=0, description="Engine capacity in cc")
    mileage: Optional[float] = Field(None, ge=0, description="Current mileage in km")
    color: Optional[str] = Field(None, max_length=50, description="Vehicle color")
    
    custom_duty_paid: Optional[bool] = Field(False, description="Custom duty paid status")
    import_year: Optional[int] = Field(None, ge=1900, le=datetime.now().year, description="Import year")
    previous_owners: Optional[int] = Field(1, ge=1, description="Number of previous owners")
    
    region: Optional[str] = Field(None, max_length=100, description="Region in Ethiopia")
    city: Optional[str] = Field(None, max_length=100, description="City")
    
    @field_validator('vin')
    @classmethod
    def validate_vin(cls, v):
        # Basic VIN validation - can be enhanced with proper VIN algorithm
        if not v.isalnum():
            raise ValueError('VIN must contain only alphanumeric characters')
        return v.upper()
    
    @field_validator('plate_number')
    @classmethod
    def validate_plate_number(cls, v):
        # Ethiopian plate number format validation
        if not v.replace('-', '').replace(' ', '').isalnum():
            raise ValueError('Plate number must contain only alphanumeric characters')
        return v


class VehicleCreate(VehicleBase):
    owner_id: int = Field(..., description="Vehicle owner ID")


class VehicleUpdate(BaseModel):
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    mileage: Optional[float] = Field(None, ge=0)
    color: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class VehicleResponse(VehicleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: int
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


# Vehicle Valuation schemas
class VehicleValuationBase(BaseModel):
    market_value: float = Field(..., gt=0, description="Market value in ETB")
    taxable_value: float = Field(0, description="Taxable value (25% of market value)")
    valuation_method: str = Field(..., description="Valuation method used")
    depreciation_rate: float = Field(0.0, ge=0, le=1, description="Depreciation rate")
    condition_factor: float = Field(1.0, ge=0.6, le=1.0, description="Vehicle condition factor")
    
    comparable_vehicles: Optional[str] = Field(None, description="Comparable vehicles data (JSON)")
    ai_confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    ai_market_trends: Optional[str] = Field(None, description="AI market trends analysis (JSON)")
    
    local_demand_factor: float = Field(1.0, ge=0.5, le=2.0, description="Local demand factor")
    import_tax_adjustment: float = Field(0.0, description="Import tax adjustment")
    regional_price_adjustment: float = Field(0.0, description="Regional price adjustment")
    
    @field_validator('taxable_value', mode='before')
    @classmethod
    def calculate_taxable_value(cls, v, values):
        """Calculate taxable value as 25% of market value"""
        market_value = values.get('market_value', 0)
        return market_value * 0.25


class VehicleValuationCreate(VehicleValuationBase):
    vehicle_id: UUID = Field(..., description="Vehicle ID")
    valuer_id: int = Field(..., description="Valuer ID")


class VehicleValuationUpdate(BaseModel):
    market_value: Optional[float] = Field(None, gt=0)
    valuation_method: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|submitted|approved|rejected)$")


class VehicleValuationResponse(VehicleValuationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    vehicle_id: UUID
    valuation_date: datetime
    taxable_value: float
    valuer_id: int
    status: str
    approved_at: Optional[datetime]
    approved_by: Optional[int]
    certificate_number: Optional[str]
    certificate_issued_at: Optional[datetime]
    
    # Include vehicle information
    vehicle: Optional[VehicleResponse] = None
    
    class Config:
        from_attributes = True


# List responses
class VehicleListResponse(BaseModel):
    vehicles: List[VehicleResponse]
    total: int
    page: int
    per_page: int
    pages: int


class VehicleValuationListResponse(BaseModel):
    valuations: List[VehicleValuationResponse]
    total: int
    page: int
    per_page: int
    pages: int


# AI Analysis schemas
class VehicleAnalysisRequest(BaseModel):
    vehicle_id: UUID
    include_market_trends: bool = True
    include_comparable_vehicles: bool = True
    region: Optional[str] = None


class VehicleAnalysisResponse(BaseModel):
    confidence_score: float
    estimated_market_value: float
    market_trends: dict
    comparable_vehicles: List[dict]
    local_demand_factor: float
    recommended_adjustments: dict


# Certificate schemas
class VehicleCertificateRequest(BaseModel):
    valuation_id: UUID
    include_qr_code: bool = True
    include_watermark: bool = True


class VehicleCertificateResponse(BaseModel):
    certificate_url: str
    certificate_number: str
    issued_at: datetime
    expires_at: Optional[datetime]
    qr_code_url: Optional[str]
