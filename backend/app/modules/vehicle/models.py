"""
Vehicle Valuation Models

SQLAlchemy models for vehicles and their valuations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Vehicle(Base):
    """Vehicle information model"""
    
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Basic vehicle information
    make = Column(String(100), nullable=False)  # Toyota, Honda, etc.
    model = Column(String(100), nullable=False)  # Corolla, Civic, etc.
    year = Column(Integer, nullable=False)
    vin = Column(String(17), unique=True, nullable=False)  # Vehicle Identification Number
    plate_number = Column(String(20), unique=True, nullable=False)
    
    # Vehicle specifications
    body_type = Column(String(50))  # Sedan, SUV, Truck, etc.
    fuel_type = Column(String(20))  # Gasoline, Diesel, Electric, Hybrid
    transmission = Column(String(20))  # Manual, Automatic
    engine_capacity = Column(Float)  # in cc
    mileage = Column(Float)  # current mileage in km
    color = Column(String(50))
    
    # Ethiopian-specific fields
    custom_duty_paid = Column(Boolean, default=False)
    import_year = Column(Integer)
    previous_owners = Column(Integer, default=1)
    
    # Location
    region = Column(String(100))  # Addis Ababa, Oromia, etc.
    city = Column(String(100))
    
    # Owner information
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="vehicles")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Vehicle {self.year} {self.make} {self.model}>"


class VehicleValuation(Base):
    """Vehicle valuation results"""
    
    __tablename__ = "vehicle_valuations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vehicle reference
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="valuations")
    
    # Valuation details
    valuation_date = Column(DateTime, default=datetime.utcnow)
    market_value = Column(Float, nullable=False)  # ETB
    taxable_value = Column(Float, nullable=False)  # 25% of market value per regulations
    
    # Valuation methodology
    valuation_method = Column(String(50), nullable=False)  # Market Comparison, Cost Approach, etc.
    depreciation_rate = Column(Float, default=0.0)  # Annual depreciation percentage
    condition_factor = Column(Float, default=1.0)  # 1.0 = Excellent, 0.6 = Poor
    
    # Comparable vehicles used
    comparable_vehicles = Column(Text)  # JSON string of comparable vehicle data
    
    # AI analysis results
    ai_confidence_score = Column(Float)  # 0.0 to 1.0
    ai_market_trends = Column(Text)  # JSON string of market trend analysis
    
    # Ethiopian market factors
    local_demand_factor = Column(Float, default=1.0)
    import_tax_adjustment = Column(Float, default=0.0)
    regional_price_adjustment = Column(Float, default=0.0)
    
    # Valuer information
    valuer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    valuer = relationship("User", foreign_keys=[valuer_id])
    
    # Status
    status = Column(String(20), default="draft")  # draft, submitted, approved, rejected
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Certificate information
    certificate_number = Column(String(50), unique=True)
    certificate_issued_at = Column(DateTime)
    
    def __repr__(self):
        return f"<VehicleValuation {self.vehicle_id}: ETB {self.market_value:,.2f}>"
