"""
Vehicle Valuation Schemas

Pydantic schemas for vehicle valuation data validation and serialization
with Ethiopian market-specific factors.
"""

from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VehicleValuationStatus(str, Enum):
    """Vehicle valuation status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class MarketPosition(str, Enum):
    """Market position enumeration"""
    PREMIUM = "premium"
    ABOVE_AVERAGE = "above_average"
    AVERAGE = "average"
    BUDGET = "budget"


class ConditionRating(str, Enum):
    """Condition rating enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


# Base vehicle valuation schema
class VehicleValuationBase(BaseModel):
    """Base vehicle valuation schema with common fields"""
    vehicle_id: int = Field(..., description="Vehicle ID")
    base_value: float = Field(..., ge=0, description="Base market value before adjustments")
    market_value: float = Field(..., ge=0, description="Final market value after adjustments")
    taxable_value: float = Field(..., ge=0, description="Taxable value (25% of market value)")
    condition_factor: float = Field(..., ge=0.5, le=1.5, description="Condition-based multiplier")
    regional_multiplier: float = Field(..., ge=0.5, le=2.0, description="Regional demand adjustment")
    import_year_adjustment: float = Field(..., ge=0.5, le=1.5, description="Import year impact")
    customs_duty_factor: float = Field(..., ge=0.5, le=1.5, description="Customs duty status impact")
    make_reliability: float = Field(..., ge=0.5, le=1.0, description="Make reliability score")
    fuel_type_adjustment: float = Field(..., ge=0.5, le=1.5, description="Fuel type market demand")
    body_type_demand: float = Field(..., ge=0.5, le=1.5, description="Body type market demand")
    market_position: MarketPosition = Field(..., description="Market position category")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in valuation (0-1)")
    comparable_vehicles_count: int = Field(0, ge=0, description="Number of comparable vehicles")
    condition_rating: ConditionRating = Field(..., description="Overall condition rating")
    age_depreciation: float = Field(..., ge=0, le=1, description="Age-based depreciation rate")
    mileage_depreciation: float = Field(0, ge=0, le=1, description="Mileage-based depreciation")
    valuation_method: str = Field("automated", description="Valuation method used")
    data_sources: Optional[List[str]] = Field(None, description="Data sources used")
    recommendations: Optional[List[str]] = Field(None, description="Valuation recommendations")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator("taxable_value")
    @classmethod
    def validate_taxable_value(cls, v, info: ValidationInfo):
        """Validate taxable value is 25% of market value"""
        values = info.data
        if "market_value" in values:
            expected_taxable = values["market_value"] * 0.25
            # Allow small rounding differences
            if abs(v - expected_taxable) > 100:  # Allow 100 ETB difference
                raise ValueError('Taxable value must be 25% of market value')
        return v
    
    @field_validator("market_value")
    @classmethod
    def validate_market_value(cls, v, info: ValidationInfo):
        """Validate market value calculation"""
        values = info.data
        if all(k in values for k in ["base_value", "condition_factor", "regional_multiplier", 
                                   "import_year_adjustment", "customs_duty_factor", "make_reliability",
                                   "fuel_type_adjustment", "body_type_demand"]):
            base = values["base_value"]
            total_multiplier = (
                values["condition_factor"] *
                values["regional_multiplier"] *
                values["import_year_adjustment"] *
                values["customs_duty_factor"] *
                values["make_reliability"] *
                values["fuel_type_adjustment"] *
                values["body_type_demand"]
            )
            expected_market = base * total_multiplier
            # Allow small rounding differences
            if abs(v - expected_market) > 200:  # Allow 200 ETB difference
                raise ValueError('Market value calculation mismatch')
        return v


class VehicleValuationCreate(VehicleValuationBase):
    """Schema for creating a new vehicle valuation"""
    pass


class VehicleValuationUpdate(BaseModel):
    """Schema for updating an existing vehicle valuation"""
    status: Optional[VehicleValuationStatus] = None
    review_notes: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    recommendations: Optional[List[str]] = None


class VehicleValuationResponse(VehicleValuationBase):
    """Schema for vehicle valuation response"""
    id: int
    user_id: int
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    vehicle_vin: str
    vehicle_plate: str
    vehicle_mileage: Optional[int]
    vehicle_region: Optional[str]
    ethiopian_factors: Optional[Dict[str, Any]]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    valuation_date: datetime
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VehicleValuationSummary(BaseModel):
    """Schema for vehicle valuation summary"""
    id: int
    vehicle_name: str
    market_value: float
    taxable_value: float
    condition_rating: str
    market_position: str
    confidence_score: float
    status: str
    valuation_date: datetime
    expires_at: Optional[datetime]


class VehicleValuationFactors(BaseModel):
    """Schema for valuation factor breakdown"""
    base_value: float
    condition_factor: float
    regional_multiplier: float
    import_year_adjustment: float
    customs_duty_factor: float
    make_reliability: float
    fuel_type_adjustment: float
    body_type_demand: float
    total_multiplier: float
    final_market_value: float
    taxable_value: float


class EthiopianMarketFactors(BaseModel):
    """Schema for Ethiopian market factors"""
    regional_multiplier: float
    regional_demand: str
    import_year_adjustment: float
    import_status: str
    customs_duty_factor: float
    customs_status: str
    make_reliability: float
    make_reputation: str
    fuel_type_adjustment: float
    fuel_demand: str
    body_type_demand: float
    body_popularity: str
    total_multiplier: float
    market_insights: List[str]


class VehicleConditionAnalysis(BaseModel):
    """Schema for vehicle condition analysis"""
    age_years: int
    mileage: Optional[int]
    previous_owners: int
    age_depreciation: float
    condition_rating: str
    mileage_status: Optional[str]
    expected_mileage: int
    maintenance_recommendations: List[str]


class MarketComparison(BaseModel):
    """Schema for market comparison data"""
    market_position: str
    confidence_score: float
    comparable_vehicles: int
    data_sources: List[str]
    valuation_method: str
    market_saturation: str
    price_percentile: float


class VehicleValuationRequest(BaseModel):
    """Schema for vehicle valuation request"""
    vehicle_id: int
    force_recalculate: bool = False
    include_market_analysis: bool = True
    include_recommendations: bool = True


class VehicleValuationReport(BaseModel):
    """Schema for comprehensive vehicle valuation report"""
    valuation: VehicleValuationResponse
    factors_breakdown: VehicleValuationFactors
    ethiopian_factors: EthiopianMarketFactors
    condition_analysis: VehicleConditionAnalysis
    market_comparison: MarketComparison
    tax_savings_potential: float
    market_readiness_score: int
    compliance_status: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


class VehicleValuationBulk(BaseModel):
    """Schema for bulk vehicle valuation"""
    vehicle_ids: List[int]
    force_recalculate: bool = False
    create_if_missing: bool = True


class VehicleValuationBulkResult(BaseModel):
    """Schema for bulk valuation results"""
    total_processed: int
    successful_valuations: int
    failed_valuations: int
    skipped_vehicles: int
    processing_time: float
    errors: List[Dict[str, str]]
    results: List[VehicleValuationResponse]


class VehicleValuationFilter(BaseModel):
    """Schema for vehicle valuation filtering"""
    vehicle_makes: Optional[List[str]] = None
    vehicle_models: Optional[List[str]] = None
    years: Optional[List[int]] = None
    regions: Optional[List[str]] = None
    statuses: Optional[List[VehicleValuationStatus]] = None
    market_positions: Optional[List[MarketPosition]] = None
    condition_ratings: Optional[List[ConditionRating]] = None
    min_market_value: Optional[float] = None
    max_market_value: Optional[float] = None
    min_confidence_score: Optional[float] = None
    max_confidence_score: Optional[float] = None
    valuation_method: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    expires_before: Optional[datetime] = None
    expires_after: Optional[datetime] = None
    reviewed_by: Optional[int] = None


class VehicleValuationStatistics(BaseModel):
    """Schema for vehicle valuation statistics"""
    total_valuations: int
    total_market_value: float
    total_taxable_value: float
    average_market_value: float
    average_confidence_score: float
    valuations_by_status: Dict[str, int]
    valuations_by_market_position: Dict[str, int]
    valuations_by_condition_rating: Dict[str, int]
    valuations_by_region: Dict[str, int]
    valuations_by_make: Dict[str, int]
    recent_valuations: int
    expiring_soon: int
    expired_valuations: int
    high_confidence_valuations: int
    low_confidence_valuations: int


class VehicleValuationExport(BaseModel):
    """Schema for vehicle valuation export"""
    id: int
    vehicle_id: int
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    vehicle_vin: str
    vehicle_plate: str
    base_value: float
    market_value: float
    taxable_value: float
    condition_factor: float
    regional_multiplier: float
    import_year_adjustment: float
    customs_duty_factor: float
    make_reliability: float
    fuel_type_adjustment: float
    body_type_demand: float
    market_position: str
    confidence_score: float
    condition_rating: str
    status: str
    valuation_date: datetime
    expires_at: Optional[datetime]
    created_at: datetime


class VehicleValuationReview(BaseModel):
    """Schema for vehicle valuation review"""
    valuation_id: int
    action: str  # approve, reject, request_changes
    review_notes: Optional[str] = None
    new_market_value: Optional[float] = None
    new_factors: Optional[Dict[str, float]] = None


class VehicleValuationValidation(BaseModel):
    """Schema for valuation validation results"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_score: float
    recommendations: List[str]


class VehicleValuationComparison(BaseModel):
    """Schema for comparing multiple vehicle valuations"""
    valuations: List[VehicleValuationResponse]
    market_analysis: Dict[str, Any]
    price_trends: Dict[str, Any]
    recommendations: List[str]


class VehicleValuationTrend(BaseModel):
    """Schema for vehicle valuation trends"""
    vehicle_id: int
    valuations: List[VehicleValuationResponse]
    trend_direction: str  # increasing, decreasing, stable
    trend_percentage: float
    average_change_per_month: float
    market_factors: List[str]
    predictions: Optional[Dict[str, Any]]


class VehicleValuationAlert(BaseModel):
    """Schema for valuation alerts"""
    type: str  # expiring, expired, low_confidence, high_value_change
    message: str
    vehicle_id: int
    valuation_id: int
    severity: str  # low, medium, high, critical
    action_required: bool
    action_suggestions: List[str]
    created_at: datetime
