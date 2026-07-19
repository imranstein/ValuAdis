"""
Valuation Schemas

Pydantic models for valuation request/response validation
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Tuple, Optional
from datetime import date, datetime


class ValuationCreate(BaseModel):
    """Valuation creation request"""
    property_id: int = Field(..., description="ID of the property being valued")
    property_type: str = Field(..., description="Type of property (residential, commercial, agricultural)")
    municipality: str = Field(..., description="Ethiopian municipality")
    area_sqm: float = Field(..., gt=0, lt=100_000, description="Property area in square meters")
    coordinates: List[Tuple[float, float]] = Field(..., description="GPS boundary coordinates")
    # Proclamation 1365/2025 Annex B inputs — optional, with sensible defaults
    condition: str = Field("good", description="Property condition grade (excellent/good/fair/poor)")
    neighborhood_quality: str = Field("average", description="Neighborhood quality tier")
    construction_year: Optional[int] = Field(None, description="Year of construction for depreciation")
    purpose: str = Field(
        "sale",
        description="Valuation purpose: 'sale' (market value, default) or 'rent' (suggested monthly rent + band)",
    )

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v):
        allowed = ["sale", "rent"]
        if v not in allowed:
            raise ValueError(f'purpose must be one of: {", ".join(allowed)}')
        return v

    @field_validator("property_type")
    @classmethod
    def validate_property_type(cls, v):
        allowed_types = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use']
        if v not in allowed_types:
            raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v):
        allowed = ['excellent', 'good', 'fair', 'poor']
        if v not in allowed:
            raise ValueError(f'Condition must be one of: {", ".join(allowed)}')
        return v

    @field_validator("neighborhood_quality")
    @classmethod
    def validate_neighborhood_quality(cls, v):
        allowed = ['prime', 'above_average', 'average', 'below_average', 'developing']
        if v not in allowed:
            raise ValueError(f'neighborhood_quality must be one of: {", ".join(allowed)}')
        return v

    @field_validator("construction_year")
    @classmethod
    def validate_construction_year(cls, v):
        if v is not None:
            current_year = date.today().year
            if not (1800 <= v <= current_year):
                raise ValueError(f'construction_year must be between 1800 and {current_year}')
        return v

    @field_validator("municipality")
    @classmethod
    def validate_municipality(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Municipality name must be at least 2 characters')
        return v.strip()

    @field_validator("coordinates")
    @classmethod
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
    
    @field_validator("property_type")
    @classmethod
    def validate_property_type(cls, v):
        if v is not None:
            allowed_types = ['residential', 'commercial', 'industrial', 'agricultural', 'mixed_use']
            if v not in allowed_types:
                raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v
    
    @field_validator("area_sqm")
    @classmethod
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
    model_config = ConfigDict(from_attributes=True)


class ValuationCalculation(BaseModel):
    """Valuation calculation result"""
    market_value: float = Field(..., description="Calculated market value in ETB")
    taxable_value: float = Field(..., description="25% of market value per Proclamation 1365/2025")
    base_rate: float = Field(..., description="Base rate per sqm used")
    multiplier: float = Field(..., description="Property type multiplier applied")
    calculation_date: datetime = Field(default_factory=datetime.now)
    purpose: str = Field("sale", description="'sale' or 'rent'")
    # Populated only when purpose='rent'; omitted from sale responses via
    # response_model_exclude_none so existing 'sale' callers see an
    # unchanged payload shape.
    suggested_rent: Optional[float] = Field(None, description="Suggested monthly rent in ETB (purpose='rent')")
    band_min: Optional[float] = Field(None, description="Lower bound of the suggested rent band (purpose='rent')")
    band_max: Optional[float] = Field(None, description="Upper bound of the suggested rent band (purpose='rent')")
    confidence: Optional[float] = Field(None, description="Blended confidence score 0..1 (purpose='rent')")
    requires_officer_review: Optional[bool] = Field(
        None, description="True when confidence is below the review floor (purpose='rent')"
    )


class ValuationOverrideRequest(BaseModel):
    """Request schema for senior valuer/admin valuation override"""
    market_value: float = Field(..., gt=0, description="Override market value in ETB")
    taxable_value: Optional[float] = Field(None, gt=0, description="Override taxable value (default: 25% of market_value)")
    override_reason: Optional[str] = Field(None, max_length=500, description="Reason for override (audit trail)")


class ValuationStatusTransitionRequest(BaseModel):
    """Request schema for valuation status transitions"""
    status: str = Field(..., description="Target status (pending, approved, archived, rejected)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change (audit trail)")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["pending", "approved", "archived", "rejected", "draft"]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v
