"""
Property Model

ValuAdis property model with PostGIS spatial data for Ethiopian properties
Extended with comprehensive fields for wizard-based registration
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Identity ---
    property_ref = Column(String(50), unique=True, index=True)  # e.g. ADD-2025-001234
    parcel_number = Column(String(100))
    title_deed_number = Column(String(100))
    registration_date = Column(DateTime(timezone=True))

    # --- Location ---
    address = Column(String(500), nullable=False)
    municipality = Column(String(100), nullable=False)
    region = Column(String(100))
    subcity = Column(String(100))
    woreda = Column(String(100))
    kebele = Column(String(100))
    zone = Column(String(100))
    neighborhood = Column(String(200))

    # --- Classification ---
    property_type = Column(String(50), nullable=False)
    property_subtype = Column(String(50))

    # --- Spatial ---
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    area_sqm = Column(Float, nullable=False)
    building_area_sqm = Column(Float)

    # --- Physical ---
    number_of_floors = Column(Integer)
    number_of_rooms = Column(Integer)
    number_of_bedrooms = Column(Integer)
    number_of_bathrooms = Column(Integer)
    year_built = Column(Integer)
    construction_material = Column(String(50))
    roof_material = Column(String(50))
    floor_material = Column(String(50))
    construction_quality = Column(String(20))
    condition = Column(String(20))
    parking_spaces = Column(Integer, default=0)

    # --- Amenities & Utilities ---
    amenities = Column(JSON, default=dict)
    utilities = Column(JSON, default=dict)
    additional_features = Column(Text)

    # --- Ownership ---
    owner_name = Column(String(200))
    owner_phone = Column(String(30))
    owner_email = Column(String(200))
    owner_id_type = Column(String(50))
    owner_id_number = Column(String(100))
    ownership_type = Column(String(50))
    legal_description = Column(Text)

    # --- Valuation ---
    valuation_method = Column(String(30))
    land_value = Column(Float)
    building_value = Column(Float)
    market_value = Column(Float)
    taxable_value = Column(Float)
    valuation_date = Column(DateTime(timezone=True))
    valuer_name = Column(String(200))
    valuer_license_number = Column(String(100))
    valuer_phone = Column(String(30))
    comparable_properties = Column(JSON, default=list)
    valuation_notes = Column(Text)

    # --- AI Valuation ---
    ai_estimated_value = Column(Float)
    ai_confidence_score = Column(Float)
    ai_trust_score_at_time = Column(Float)

    # --- Status ---
    status = Column(String(50), default="draft")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="properties")
    valuations = relationship("Valuation", back_populates="property")
    feedback = relationship("ValuationFeedback", back_populates="property", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "property_ref": self.property_ref,
            "address": self.address,
            "municipality": self.municipality,
            "region": self.region,
            "property_type": self.property_type,
            "property_subtype": self.property_subtype,
            "area_sqm": self.area_sqm,
            "building_area_sqm": self.building_area_sqm,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "condition": self.condition,
            "market_value": self.market_value,
            "taxable_value": self.taxable_value,
            "ai_estimated_value": self.ai_estimated_value,
            "ai_confidence_score": self.ai_confidence_score,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
