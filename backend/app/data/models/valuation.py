"""
Valuation Model

SQLAlchemy model for property valuation data with PostGIS spatial support
Following ValuAdis clean architecture and Ethiopian compliance requirements
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
import uuid
import enum

from app.core.database import Base


class ValuationStatus(str, enum.Enum):
    """Valuation status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PropertyType(str, enum.Enum):
    """Property type enumeration"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    AGRICULTURAL = "agricultural"


class Valuation(Base):
    """
    Property valuation model
    
    Stores valuation calculations and metadata for Ethiopian properties
    with PostGIS spatial data support
    """
    
    __tablename__ = "valuations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Property information
    property_type = Column(SQLEnum(PropertyType), nullable=False, index=True)
    municipality = Column(String(100), nullable=False, index=True)
    area_sqm = Column(Float, nullable=False)
    
    # Valuation calculations (stored in Birr)
    market_value = Column(Float, nullable=False)
    taxable_value = Column(Float, nullable=False)  # 25% of market value per Proclamation 1365/2025
    
    # Status and workflow
    status = Column(SQLEnum(ValuationStatus), default=ValuationStatus.DRAFT, nullable=False, index=True)
    
    # Spatial data - PostGIS Geometry for property boundaries
    coordinates = Column(
        Geometry(
            geometry_type='POLYGON',
            srid=4326,  # WGS84 coordinate system
            spatial_index=True,
            dimension=2
        ),
        nullable=True,
        index=True
    )
    
    # Additional metadata
    valuation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="valuations")
    property = relationship("Property", back_populates="valuations")
    
    def __repr__(self):
        """String representation of valuation"""
        return (
            f"<Valuation(id={self.id}, property_id={self.property_id}, "
            f"municipality={self.municipality}, market_value={self.market_value})>"
        )
    
    def to_dict(self):
        """Convert valuation to dictionary"""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "user_id": self.user_id,
            "property_type": self.property_type.value if self.property_type else None,
            "municipality": self.municipality,
            "area_sqm": self.area_sqm,
            "market_value": self.market_value,
            "taxable_value": self.taxable_value,
            "status": self.status.value if self.status else None,
            "valuation_date": self.valuation_date.isoformat() if self.valuation_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_coordinates_wkt(self):
        """Get coordinates as WKT string"""
        if self.coordinates:
            # This would need to be called with a session in practice
            return "WKT representation available with session"
        return None
    
    def get_coordinates_geojson(self):
        """Get coordinates as GeoJSON"""
        if self.coordinates:
            # This would need to be called with a session in practice
            return "GeoJSON representation available with session"
        return None
    
    def calculate_taxable_value(self):
        """
        Calculate taxable value per Proclamation 1365/2025
        
        Returns 25% of market value
        """
        return self.market_value * 0.25
    
    def is_editable(self):
        """
        Check if valuation can be edited
        
        Only draft and pending valuations can be edited
        """
        return self.status in [ValuationStatus.DRAFT, ValuationStatus.PENDING]
    
    def can_be_approved(self):
        """
        Check if valuation can be approved
        
        Only pending valuations can be approved
        """
        return self.status == ValuationStatus.PENDING
    
    def is_expired(self, days_valid=365):
        """
        Check if valuation is expired
        
        Args:
            days_valid: Number of days valuation is valid (default: 1 year)
        
        Returns:
            True if valuation is expired, False otherwise
        """
        if not self.valuation_date:
            return True
        
        expiry_date = self.valuation_date + timedelta(days=days_valid)
        return datetime.utcnow() > expiry_date
