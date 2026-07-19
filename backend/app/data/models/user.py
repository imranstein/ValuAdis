"""
User Model

ValuAdis user account model for Ethiopian property valuers
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, false
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    municipality = Column(String(100), nullable=False)
    license_number = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_valuer = Column(Boolean, default=False)

    # Rentals module (plans/valuadis-rentals/plan.mdx, Phase B): citizen
    # self-registration captures a Fayda ID; a property_owner account must
    # be verified by a rental_officer before their first listing can
    # publish (app/modules/rentals/services.py).
    fayda_id_number = Column(String(50), nullable=True, unique=True, index=True)
    owner_verified = Column(Boolean, default=False, server_default=false(), nullable=False)
    owner_verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    properties = relationship("Property", back_populates="user")
    valuations = relationship("Valuation", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    vehicles = relationship("Vehicle", back_populates="user")
    vehicle_valuations = relationship("VehicleValuation", foreign_keys="VehicleValuation.user_id", back_populates="user")
