"""
Vehicle Schemas

Pydantic schemas for vehicle data validation and serialization
with Ethiopian market-specific fields.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VehicleType(str, Enum):
    """Vehicle type enumeration"""
    SEDAN = "sedan"
    SUV = "suv"
    HATCHBACK = "hatchback"
    PICKUP = "pickup"
    TRUCK = "truck"
    VAN = "van"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    STATION_WAGON = "station_wagon"


class FuelType(str, Enum):
    """Fuel type enumeration"""
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    LPG = "lpg"
    CNG = "cng"


class TransmissionType(str, Enum):
    """Transmission type enumeration"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"


# Base vehicle schema
class VehicleBase(BaseModel):
    """Base vehicle schema with common fields"""
    make: str = Field(..., min_length=1, max_length=100, description="Vehicle make (e.g., Toyota, Honda)")
    model: str = Field(..., min_length=1, max_length=100, description="Vehicle model (e.g., Corolla, Civic)")
    year: int = Field(..., ge=1900, le=datetime.now().year + 1, description="Vehicle manufacturing year")
    vin: str = Field(..., min_length=17, max_length=17, description="17-character Vehicle Identification Number")
    plate_number: str = Field(..., min_length=1, max_length=20, description="Vehicle license plate number")
    body_type: Optional[VehicleType] = Field(None, description="Vehicle body type")
    fuel_type: Optional[FuelType] = Field(None, description="Vehicle fuel type")
    transmission: Optional[TransmissionType] = Field(None, description="Vehicle transmission type")
    engine_capacity: Optional[int] = Field(None, ge=0, le=10000, description="Engine capacity in cubic centimeters")
    mileage: Optional[int] = Field(None, ge=0, le=10000000, description="Current mileage in kilometers")
    color: Optional[str] = Field(None, max_length=50, description="Vehicle color")
    previous_owners: int = Field(1, ge=1, le=50, description="Number of previous owners")
    purchase_date: Optional[datetime] = Field(None, description="Date of vehicle purchase")
    purchase_price: Optional[float] = Field(None, ge=0, description="Purchase price in ETB")
    region: Optional[str] = Field(None, max_length=100, description="Ethiopian region where vehicle is located")
    city: Optional[str] = Field(None, max_length=100, description="City where vehicle is located")
    import_year: Optional[int] = Field(None, ge=1900, le=datetime.now().year, description="Year vehicle was imported to Ethiopia")
    custom_duty_paid: bool = Field(False, description="Whether customs duty has been paid")
    customs_declaration_number: Optional[str] = Field(None, max_length=50, description="Customs declaration number")
    description: Optional[str] = Field(None, max_length=1000, description="Vehicle description")
    features: Optional[str] = Field(None, description="Additional features (JSON string)")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    is_active: bool = Field(True, description="Whether vehicle is active")
    is_listed_for_sale: bool = Field(False, description="Whether vehicle is listed for sale")
    
    @validator('vin')
    def validate_vin(cls, v):
        """Validate VIN format"""
        if len(v) != 17:
            raise ValueError('VIN must be exactly 17 characters')
        
        # Check for invalid characters
        invalid_chars = ['I', 'O', 'Q']
        if any(char in v.upper() for char in invalid_chars):
            raise ValueError('VIN cannot contain characters I, O, or Q')
        
        return v.upper()
    
    @validator('plate_number')
    def validate_plate_number(cls, v):
        """Validate plate number format"""
        if not v.strip():
            raise ValueError('Plate number cannot be empty')
        return v.strip()
    
    @validator('make', 'model')
    def normalize_strings(cls, v):
        """Normalize string values"""
        return v.strip().title()
    
    @validator('color')
    def normalize_color(cls, v):
        """Normalize color value"""
        if v:
            return v.strip().title()
        return v
    
    @validator('region', 'city')
    def normalize_location(cls, v):
        """Normalize location values"""
        if v:
            return v.strip().title()
        return v


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating an existing vehicle"""
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    plate_number: Optional[str] = Field(None, min_length=1, max_length=20)
    body_type: Optional[VehicleType] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    engine_capacity: Optional[int] = Field(None, ge=0, le=10000)
    mileage: Optional[int] = Field(None, ge=0, le=10000000)
    color: Optional[str] = Field(None, max_length=50)
    previous_owners: Optional[int] = Field(None, ge=1, le=50)
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    region: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    import_year: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    custom_duty_paid: Optional[bool] = None
    customs_declaration_number: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    features: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    is_listed_for_sale: Optional[bool] = None
    
    @validator('vin')
    def validate_vin(cls, v):
        """Validate VIN format if provided"""
        if v and len(v) != 17:
            raise ValueError('VIN must be exactly 17 characters')
        
        if v:
            # Check for invalid characters
            invalid_chars = ['I', 'O', 'Q']
            if any(char in v.upper() for char in invalid_chars):
                raise ValueError('VIN cannot contain characters I, O, or Q')
            return v.upper()
        return v


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VehicleSearchResult(BaseModel):
    """Schema for vehicle search results"""
    make: str
    model: str
    display_name: str
    year_range: Optional[str] = None
    body_types: Optional[List[str]] = None


class VehicleStatistics(BaseModel):
    """Schema for vehicle statistics"""
    total_vehicles: int
    total_valuations: int
    total_market_value: float
    total_taxable_value: float
    average_vehicle_value: float
    recent_valuations: int
    make_breakdown: Dict[str, int]
    year_breakdown: Dict[str, int]
    region_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]


class VehicleMarketData(BaseModel):
    """Schema for vehicle market data"""
    make: str
    model: str
    year: int
    average_market_value: float
    median_market_value: float
    price_range: Dict[str, float]
    comparable_count: int
    market_position: str
    demand_factor: float


class VehicleImportData(BaseModel):
    """Schema for vehicle import data"""
    vin: str
    make: str
    model: str
    year: int
    trim: Optional[str] = None
    body_type: Optional[str] = None
    engine: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    drive_type: Optional[str] = None
    manufacturer: Optional[str] = None
    plant_country: Optional[str] = None
    vehicle_type: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class VehicleRecommendation(BaseModel):
    """Schema for vehicle recommendations"""
    type: str  # improvement, maintenance, market, regulatory
    title: str
    description: str
    priority: str  # high, medium, low
    potential_value_impact: Optional[float] = None  # in ETB
    action_required: bool = False


class VehicleConditionReport(BaseModel):
    """Schema for vehicle condition report"""
    overall_condition: str  # excellent, good, fair, poor
    condition_score: float  # 0-100
    age_years: int
    mileage: Optional[int] = None
    mileage_status: str  # below_average, average, above_average
    expected_mileage: int
    mileage_difference: int
    ownership_history: str
    maintenance_recommendations: List[str]
    market_readiness_score: int  # 0-100


class VehicleEthiopianFactors(BaseModel):
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


class VehicleCompliance(BaseModel):
    """Schema for vehicle compliance status"""
    is_ethiopian_compliant: bool
    compliance_issues: List[str]
    required_actions: List[str]
    restrictions: List[str]
    recommendations: List[str]


class VehicleExport(BaseModel):
    """Schema for vehicle data export"""
    id: int
    make: str
    model: str
    year: int
    vin: str
    plate_number: str
    body_type: Optional[str]
    fuel_type: Optional[str]
    transmission: Optional[str]
    engine_capacity: Optional[int]
    mileage: Optional[int]
    color: Optional[str]
    region: Optional[str]
    city: Optional[str]
    import_year: Optional[int]
    custom_duty_paid: bool
    latest_valuation: Optional[float] = None
    valuation_date: Optional[datetime] = None
    condition_rating: Optional[str] = None
    market_position: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VehicleBulkImport(BaseModel):
    """Schema for bulk vehicle import"""
    vehicles: List[VehicleCreate]
    skip_duplicates: bool = True
    update_existing: bool = False
    create_valuations: bool = True


class VehicleBulkImportResult(BaseModel):
    """Schema for bulk import results"""
    total_processed: int
    successful_imports: int
    failed_imports: int
    skipped_duplicates: int
    updated_existing: int
    valuations_created: int
    errors: List[Dict[str, str]]
    processing_time: float  # in seconds


class VehicleFilter(BaseModel):
    """Schema for vehicle filtering"""
    makes: Optional[List[str]] = None
    models: Optional[List[str]] = None
    years: Optional[List[int]] = None
    body_types: Optional[List[VehicleType]] = None
    fuel_types: Optional[List[FuelType]] = None
    regions: Optional[List[str]] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    min_mileage: Optional[int] = None
    max_mileage: Optional[int] = None
    custom_duty_paid: Optional[bool] = None
    is_active: Optional[bool] = None
    is_listed_for_sale: Optional[bool] = None
    has_valuation: Optional[bool] = None
    valuation_status: Optional[str] = None
    min_market_value: Optional[float] = None
    max_market_value: Optional[float] = None
