"""
Property Model

ValuAdis property model with PostGIS spatial data for Ethiopian properties
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address = Column(String(500), nullable=False)
    municipality = Column(String(100), nullable=False)
    property_type = Column(String(50), nullable=False)  # residential, commercial, agricultural
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)  # WGS 84
    area_sqm = Column(Float, nullable=False)
    market_value = Column(Float)
    taxable_value = Column(Float)
    status = Column(String(50), default="draft")  # draft, valued, certified
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="properties")
    valuations = relationship("Valuation", back_populates="property")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address": self.address,
            "municipality": self.municipality,
            "property_type": self.property_type,
            "area_sqm": self.area_sqm,
            "market_value": self.market_value,
            "taxable_value": self.taxable_value,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
