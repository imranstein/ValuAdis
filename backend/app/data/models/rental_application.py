"""
Rental Application Model

A renter's application to a published rental listing (plans/valuadis-rentals/
plan.mdx, Phase C). The offered rent is validated server-side against the
listing's frozen band before the row is ever created — the band is a legal
price promise, never a client-trusted value. Accepting one application
auto-rejects its siblings and moves the listing to `rented`.
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RentalApplicationStatus(str, enum.Enum):
    """Rental application status enumeration."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Statuses that occupy a renter's single active slot on a listing. A renter
# may re-apply only after a prior application is rejected or withdrawn.
ACTIVE_APPLICATION_STATUSES = (
    RentalApplicationStatus.PENDING.value,
    RentalApplicationStatus.ACCEPTED.value,
)


class RentalApplication(Base):
    __tablename__ = "rental_applications"

    id = Column(Integer, primary_key=True, index=True)

    listing_id = Column(
        Integer, ForeignKey("rental_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    renter_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Frozen at creation from the renter's offer; guaranteed in-band by the
    # service before insert (band_min <= offered_rent <= band_max).
    offered_rent = Column(Float, nullable=False)
    message = Column(Text, nullable=True)

    status = Column(
        Text, default=RentalApplicationStatus.PENDING.value, nullable=False, index=True
    )
    decided_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    listing = relationship("RentalListing")
    renter = relationship("User")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','accepted','rejected','withdrawn')",
            name="ck_rental_applications_status",
        ),
        CheckConstraint("offered_rent > 0", name="ck_rental_applications_offered_rent_positive"),
    )

    def __repr__(self):
        return (
            f"<RentalApplication(id={self.id}, listing_id={self.listing_id}, "
            f"status={self.status})>"
        )
