"""
Vehicle Valuation Model

SQLAlchemy model for vehicle valuation data with Ethiopian market factors
Following ValuAdis clean architecture and Ethiopian compliance requirements
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, func, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from typing import ClassVar, Optional

from app.core.database import Base


class VehicleValuationStatus(str, enum.Enum):
    """Vehicle valuation status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class VehicleValuation(Base):
    """
    Vehicle valuation model
    
    Stores valuation calculations, market analysis, and Ethiopian market-specific
    factors for vehicle valuation purposes.
    """
    
    __tablename__ = "vehicle_valuations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Vehicle information snapshot (stored for historical accuracy)
    vehicle_make = Column(String(100), nullable=False, index=True)
    vehicle_model = Column(String(100), nullable=False, index=True)
    vehicle_year = Column(Integer, nullable=False)
    vehicle_vin = Column(String(17), nullable=False, index=True)
    vehicle_plate = Column(String(20), nullable=False)
    vehicle_mileage = Column(Integer, nullable=True)
    vehicle_region = Column(String(100), nullable=True, index=True)
    
    # Valuation calculations (stored in ETB)
    base_value = Column(Float, nullable=False)  # Base market value before adjustments
    market_value = Column(Float, nullable=False)  # Final market value
    taxable_value = Column(Float, nullable=False)  # 25% of market value per Ethiopian regulations
    
    # Valuation factors (stored for transparency and audit)
    condition_factor = Column(Float, nullable=False)  # Condition-based multiplier
    regional_multiplier = Column(Float, nullable=False)  # Regional demand adjustment
    import_year_adjustment = Column(Float, nullable=False)  # Import year impact
    customs_duty_factor = Column(Float, nullable=False)  # Customs duty status impact
    make_reliability = Column(Float, nullable=False)  # Make reliability score
    fuel_type_adjustment = Column(Float, nullable=False)  # Fuel type market demand
    body_type_demand = Column(Float, nullable=False)  # Body type market demand
    
    # Ethiopian market factors (detailed JSON storage)
    ethiopian_factors = Column(JSON, nullable=True)  # Detailed breakdown of all factors
    
    # Market analysis
    market_position = Column(String(50), nullable=False, index=True)  # premium, average, budget
    confidence_score = Column(Float, nullable=False)  # 0-1 confidence in valuation
    comparable_vehicles_count = Column(Integer, default=0)  # Number of comparable vehicles in market
    
    # Condition analysis
    condition_rating = Column(String(20), nullable=False, index=True)  # excellent, good, fair, poor
    age_depreciation = Column(Float, nullable=False)  # Age-based depreciation rate
    mileage_depreciation = Column(Float, nullable=False)  # Mileage-based depreciation
    
    # Status and workflow
    status = Column(SQLEnum(VehicleValuationStatus), default=VehicleValuationStatus.DRAFT, nullable=False, index=True)
    
    # Review and approval
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Additional metadata
    valuation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    valuation_method = Column(String(50), default="automated", nullable=False)  # automated, manual, hybrid
    data_sources = Column(JSON, nullable=True)  # List of data sources used
    
    # Recommendations and notes
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    notes = Column(Text, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="valuations")
    user = relationship("User", foreign_keys=[user_id], back_populates="vehicle_valuations")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        """String representation of vehicle valuation"""
        return (
            f"<VehicleValuation(id={self.id}, vehicle_id={self.vehicle_id}, "
            f"market_value={self.market_value}, status={self.status})>"
        )

    # Backward-compatible legacy fields
    _legacy_certificate_number: ClassVar[Optional[str]] = None

    @property
    def approved_by(self) -> Optional[int]:
        return self.reviewed_by

    @approved_by.setter
    def approved_by(self, value: Optional[int]) -> None:
        self.reviewed_by = value

    @property
    def approved_at(self) -> Optional[datetime]:
        return self.reviewed_at

    @approved_at.setter
    def approved_at(self, value: Optional[datetime]) -> None:
        self.reviewed_at = value

    @property
    def certificate_number(self) -> Optional[str]:
        return self._legacy_certificate_number

    @certificate_number.setter
    def certificate_number(self, value: Optional[str]) -> None:
        self._legacy_certificate_number = value

    @property
    def certificate_issued_at(self) -> Optional[datetime]:
        return self.reviewed_at

    @certificate_issued_at.setter
    def certificate_issued_at(self, value: Optional[datetime]) -> None:
        if value is not None:
            self.reviewed_at = value
    
    def to_dict(self):
        """Convert vehicle valuation to dictionary"""
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "user_id": self.user_id,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_year": self.vehicle_year,
            "vehicle_vin": self.vehicle_vin,
            "vehicle_plate": self.vehicle_plate,
            "vehicle_mileage": self.vehicle_mileage,
            "vehicle_region": self.vehicle_region,
            "base_value": self.base_value,
            "market_value": self.market_value,
            "taxable_value": self.taxable_value,
            "condition_factor": self.condition_factor,
            "regional_multiplier": self.regional_multiplier,
            "import_year_adjustment": self.import_year_adjustment,
            "customs_duty_factor": self.customs_duty_factor,
            "make_reliability": self.make_reliability,
            "fuel_type_adjustment": self.fuel_type_adjustment,
            "body_type_demand": self.body_type_demand,
            "ethiopian_factors": self.ethiopian_factors,
            "market_position": self.market_position,
            "confidence_score": self.confidence_score,
            "comparable_vehicles_count": self.comparable_vehicles_count,
            "condition_rating": self.condition_rating,
            "age_depreciation": self.age_depreciation,
            "mileage_depreciation": self.mileage_depreciation,
            "status": self.status.value if self.status else None,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_notes": self.review_notes,
            "valuation_date": self.valuation_date.isoformat() if self.valuation_date else None,
            "valuation_method": self.valuation_method,
            "data_sources": self.data_sources,
            "recommendations": self.recommendations,
            "notes": self.notes,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_total_multiplier(self):
        """Calculate total multiplier applied to base value"""
        return (
            self.condition_factor *
            self.regional_multiplier *
            self.import_year_adjustment *
            self.customs_duty_factor *
            self.make_reliability *
            self.fuel_type_adjustment *
            self.body_type_demand
        )
    
    def get_valuation_summary(self):
        """Get valuation summary for display"""
        return {
            "vehicle_name": f"{self.vehicle_make} {self.vehicle_model} {self.vehicle_year}",
            "market_value": self.market_value,
            "taxable_value": self.taxable_value,
            "condition_rating": self.condition_rating,
            "market_position": self.market_position,
            "confidence_score": self.confidence_score,
            "status": self.status.value if self.status else None
        }
    
    def is_editable(self):
        """Check if valuation can be edited"""
        return self.status in [VehicleValuationStatus.DRAFT, VehicleValuationStatus.PENDING]
    
    def can_be_approved(self):
        """Check if valuation can be approved"""
        return self.status == VehicleValuationStatus.PENDING
    
    def is_expired(self):
        """Check if valuation is expired"""
        if not self.expires_at:
            return False
        
        return datetime.utcnow() > self.expires_at
    
    def set_expiration_date(self, days_valid=365):
        """Set expiration date for valuation"""
        # valuation_date is filled by the database server_default, so it is
        # still None before the first flush; fall back to now in that case.
        base_date = self.valuation_date or datetime.utcnow()
        self.expires_at = base_date + timedelta(days=days_valid)
    
    def get_factor_breakdown(self):
        """Get detailed breakdown of all valuation factors"""
        return {
            "base_value": self.base_value,
            "condition_factor": self.condition_factor,
            "regional_multiplier": self.regional_multiplier,
            "import_year_adjustment": self.import_year_adjustment,
            "customs_duty_factor": self.customs_duty_factor,
            "make_reliability": self.make_reliability,
            "fuel_type_adjustment": self.fuel_type_adjustment,
            "body_type_demand": self.body_type_demand,
            "total_multiplier": self.get_total_multiplier(),
            "final_market_value": self.market_value,
            "taxable_value": self.taxable_value
        }
    
    def get_ethiopian_market_insights(self):
        """Get Ethiopian market-specific insights"""
        insights = []
        
        if self.regional_multiplier > 1.0:
            insights.append(f"Regional demand premium: +{(self.regional_multiplier - 1) * 100:.1f}%")
        
        if self.customs_duty_factor > 1.0:
            insights.append("Customs duty compliance bonus: +5%")
        elif self.customs_duty_factor < 1.0:
            insights.append("Customs duty penalty: -20%")
        
        if self.import_year_adjustment > 1.0:
            insights.append("Recent import premium: +10%")
        elif self.import_year_adjustment < 1.0:
            insights.append("Older import discount")
        
        if self.make_reliability > 0.9:
            insights.append("High reliability make premium")
        elif self.make_reliability < 0.8:
            insights.append("Lower reliability make adjustment")
        
        return insights
    
    def calculate_tax_savings(self):
        """Calculate potential tax savings if customs duty is paid"""
        if self.customs_duty_factor >= 1.0:
            return 0  # Already paid
        
        # Calculate what the value would be with customs duty paid
        current_multiplier = self.get_total_multiplier()
        adjusted_multiplier = current_multiplier / self.customs_duty_factor * 1.05  # Replace with 1.05
        potential_market_value = self.base_value * adjusted_multiplier
        
        return potential_market_value - self.market_value
    
    def get_market_comparison(self):
        """Get market comparison data"""
        return {
            "market_position": self.market_position,
            "confidence_score": self.confidence_score,
            "comparable_vehicles": self.comparable_vehicles_count,
            "data_sources": self.data_sources or [],
            "valuation_method": self.valuation_method
        }
    
    def validate_valuation(self):
        """Validate valuation data for consistency"""
        errors = []
        
        # Check if factors multiply to give correct market value
        expected_market_value = self.base_value * self.get_total_multiplier()
        if abs(expected_market_value - self.market_value) > 100:  # Allow 100 ETB difference
            errors.append("Market value calculation mismatch")
        
        # Check if taxable value is 25% of market value
        expected_taxable = self.market_value * 0.25
        if abs(expected_taxable - self.taxable_value) > 50:  # Allow 50 ETB difference
            errors.append("Taxable value calculation error")
        
        # Check confidence score range
        if not 0 <= self.confidence_score <= 1:
            errors.append("Confidence score out of range")
        
        # Check factor ranges
        factors = [
            ("condition_factor", self.condition_factor),
            ("regional_multiplier", self.regional_multiplier),
            ("import_year_adjustment", self.import_year_adjustment),
            ("customs_duty_factor", self.customs_duty_factor),
            ("make_reliability", self.make_reliability),
            ("fuel_type_adjustment", self.fuel_type_adjustment),
            ("body_type_demand", self.body_type_demand)
        ]
        
        for name, factor in factors:
            if factor < 0.5 or factor > 1.5:
                errors.append(f"{name} out of reasonable range: {factor}")
        
        return errors

# Add to VehicleValuation model:
# status = Column(String(50), default="draft")  # draft, pending, approved, archived
