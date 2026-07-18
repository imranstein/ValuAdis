"""
Rental Listing Model

Government-mediated rental registry listing (plans/valuadis-rentals/plan.mdx,
Phase B). A listing wraps an existing Property and a rent Valuation
(purpose='rent') with a frozen suggested-rent band and an officer review
workflow. The public_id is a registry-style string exposed everywhere in
place of the integer PK.
"""

import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    false,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RentalListingStatus(str, enum.Enum):
    """Rental listing status enumeration."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    RENTED = "rented"
    WITHDRAWN = "withdrawn"


class RentalListing(Base):
    __tablename__ = "rental_listings"

    id = Column(Integer, primary_key=True, index=True)

    # Registry-style public identifier (e.g. AA-LST-2026-000123); server
    # generated, unique, never reused. Contract numbers and listing ids
    # appear on paper and in disputes, so they must be stable and
    # human-quotable from day one (plan decision).
    public_id = Column(String(20), unique=True, nullable=False, index=True)

    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    valuation_id = Column(Integer, ForeignKey("valuations.id", ondelete="CASCADE"), nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Band frozen at publish time — a listing's legal price promise must not
    # drift when the model updates (plan decision). Values are set from the
    # auto rent valuation at creation and may only be adjusted by an officer
    # with a mandatory reason before publish.
    suggested_rent = Column(Float, nullable=False)
    band_min = Column(Float, nullable=False)
    band_max = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    requires_officer_review = Column(Boolean, default=False, server_default=false(), nullable=False)

    status = Column(String(20), default=RentalListingStatus.PENDING_REVIEW.value, nullable=False, index=True)
    listing_agreement_pdf = Column(String(500), nullable=True)
    review_reason = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    property = relationship("Property")
    valuation = relationship("Valuation")
    owner = relationship("User")

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','pending_review','published','rented','withdrawn')",
            name="ck_rental_listings_status",
        ),
    )

    def __repr__(self):
        return f"<RentalListing(id={self.id}, public_id={self.public_id}, status={self.status})>"
