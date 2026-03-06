"""
Vehicle Model

SQLAlchemy model for vehicle data with Ethiopian market-specific fields
Following ValuAdis clean architecture and Ethiopian compliance requirements
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class VehicleType(str, enum.Enum):
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


class FuelType(str, enum.Enum):
    """Fuel type enumeration"""
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    LPG = "lpg"
    CNG = "cng"


class TransmissionType(str, enum.Enum):
    """Transmission type enumeration"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"


class Vehicle(Base):
    """
    Vehicle model for Ethiopian market
    
    Stores vehicle specifications, ownership details, and Ethiopian-specific
    market information for valuation purposes.
    """
    
    __tablename__ = "vehicles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic vehicle information
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    vin = Column(String(17), nullable=False, unique=True, index=True)
    plate_number = Column(String(20), nullable=False, unique=True, index=True)
    
    # Vehicle specifications
    body_type = Column(SQLEnum(VehicleType), nullable=True, index=True)
    fuel_type = Column(SQLEnum(FuelType), nullable=True, index=True)
    transmission = Column(SQLEnum(TransmissionType), nullable=True)
    engine_capacity = Column(Integer, nullable=True)  # in cc
    mileage = Column(Integer, nullable=True)  # in km
    color = Column(String(50), nullable=True)
    
    # Ownership and condition
    previous_owners = Column(Integer, default=1, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_price = Column(Float, nullable=True)
    
    # Ethiopian market specific
    region = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    import_year = Column(Integer, nullable=True, index=True)
    custom_duty_paid = Column(Boolean, default=False, nullable=False, index=True)
    customs_declaration_number = Column(String(50), nullable=True)
    
    # Additional information
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)  # JSON string of additional features
    notes = Column(Text, nullable=True)
    
    # Status and workflow
    is_active = Column(Boolean, default=True, nullable=False)
    is_listed_for_sale = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="vehicles")
    valuations = relationship("VehicleValuation", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of vehicle"""
        return (
            f"<Vehicle(id={self.id}, make={self.make}, model={self.model}, "
            f"year={self.year}, vin={self.vin})>"
        )
    
    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "vin": self.vin,
            "plate_number": self.plate_number,
            "body_type": self.body_type.value if self.body_type else None,
            "fuel_type": self.fuel_type.value if self.fuel_type else None,
            "transmission": self.transmission.value if self.transmission else None,
            "engine_capacity": self.engine_capacity,
            "mileage": self.mileage,
            "color": self.color,
            "previous_owners": self.previous_owners,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "purchase_price": self.purchase_price,
            "region": self.region,
            "city": self.city,
            "import_year": self.import_year,
            "custom_duty_paid": self.custom_duty_paid,
            "customs_declaration_number": self.customs_declaration_number,
            "description": self.description,
            "features": self.features,
            "notes": self.notes,
            "is_active": self.is_active,
            "is_listed_for_sale": self.is_listed_for_sale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_full_name(self):
        """Get full vehicle name (Make Model Year)"""
        return f"{self.make} {self.model} {self.year}"
    
    def get_age_years(self):
        """Get vehicle age in years"""
        current_year = datetime.now().year
        return current_year - self.year
    
    def get_import_age_years(self):
        """Get import age in years"""
        if not self.import_year:
            return None
        current_year = datetime.now().year
        return current_year - self.import_year
    
    def is_vin_valid(self):
        """Validate VIN format"""
        if not self.vin or len(self.vin) != 17:
            return False
        
        # Basic VIN validation (alphanumeric except I, O, Q)
        invalid_chars = ['I', 'O', 'Q']
        return not any(char in self.vin.upper() for char in invalid_chars)
    
    def calculate_expected_mileage(self):
        """Calculate expected mileage based on age (Ethiopian average: 15,000 km/year)"""
        age = self.get_age_years()
        return age * 15000
    
    def get_mileage_status(self):
        """Get mileage status compared to expected"""
        if not self.mileage:
            return "unknown"
        
        expected = self.calculate_expected_mileage()
        actual = self.mileage
        
        if actual < expected * 0.8:
            return "below_average"
        elif actual < expected * 1.2:
            return "average"
        else:
            return "above_average"
    
    def is_ethiopian_compliant(self):
        """Check if vehicle meets Ethiopian regulatory requirements"""
        if not self.custom_duty_paid:
            return False
        
        if not self.plate_number:
            return False
        
        if self.get_import_age_years() and self.get_import_age_years() > 15:
            return False  # Vehicles older than 15 years may have restrictions
        
        return True
    
    def get_market_readiness_score(self):
        """Calculate market readiness score (0-100)"""
        score = 50  # Base score
        
        # Customs duty compliance
        if self.custom_duty_paid:
            score += 20
        
        # Documentation
        if self.plate_number and self.customs_declaration_number:
            score += 10
        
        # Condition factors
        mileage_status = self.get_mileage_status()
        if mileage_status == "average":
            score += 10
        elif mileage_status == "below_average":
            score += 15
        
        # Age factor
        age = self.get_age_years()
        if age <= 5:
            score += 10
        elif age <= 10:
            score += 5
        
        # Ownership history
        if self.previous_owners <= 2:
            score += 5
        
        return min(100, score)
    
    def can_be_valued(self):
        """Check if vehicle can be valued"""
        return (
            self.make and 
            self.model and 
            self.year and 
            self.is_active and
            self.is_vin_valid()
        )
    
    def needs_maintenance_records(self):
        """Check if vehicle needs maintenance records for better valuation"""
        age = self.get_age_years()
        return age > 5 or self.get_mileage_status() == "above_average"
