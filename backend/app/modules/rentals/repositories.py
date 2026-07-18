"""
Rental Listing Repository

Data access layer for rental listing operations.
"""

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.data.repositories.base import BaseRepository
from .models import RentalListing, RentalListingStatus


class RentalListingRepository(BaseRepository[RentalListing]):
    def __init__(self, db: Session):
        super().__init__(RentalListing, db)

    def get_by_public_id(self, public_id: str) -> Optional[RentalListing]:
        return (
            self.db.query(RentalListing)
            .options(joinedload(RentalListing.property))
            .filter(RentalListing.public_id == public_id)
            .first()
        )

    def public_id_exists(self, public_id: str) -> bool:
        return (
            self.db.query(RentalListing.id)
            .filter(RentalListing.public_id == public_id)
            .first()
            is not None
        )

    def get_owner_listings(
        self, owner_user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[RentalListing], int]:
        query = (
            self.db.query(RentalListing)
            .options(joinedload(RentalListing.property))
            .filter(RentalListing.owner_user_id == owner_user_id)
            .order_by(RentalListing.created_at.desc())
        )
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    def get_review_queue(
        self, status: str = RentalListingStatus.PENDING_REVIEW.value, skip: int = 0, limit: int = 20
    ) -> Tuple[List[RentalListing], int]:
        query = (
            self.db.query(RentalListing)
            .options(joinedload(RentalListing.property), joinedload(RentalListing.owner))
            .filter(RentalListing.status == status)
            .order_by(RentalListing.created_at.asc())
        )
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    def search_published(
        self,
        district: Optional[str] = None,
        property_subtype: Optional[str] = None,
        bedrooms: Optional[int] = None,
        band_min: Optional[float] = None,
        band_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[RentalListing], int]:
        """Public search across published listings only."""
        from app.data.models.property import Property

        query = (
            self.db.query(RentalListing)
            .join(Property, RentalListing.property_id == Property.id)
            .options(joinedload(RentalListing.property))
            .filter(RentalListing.status == RentalListingStatus.PUBLISHED.value)
        )

        if district:
            query = query.filter(Property.subcity.ilike(f"%{district}%"))
        if property_subtype:
            query = query.filter(Property.property_subtype == property_subtype)
        if bedrooms is not None:
            query = query.filter(Property.number_of_bedrooms == bedrooms)
        if band_min is not None:
            query = query.filter(RentalListing.band_max >= band_min)
        if band_max is not None:
            query = query.filter(RentalListing.band_min <= band_max)

        query = query.order_by(RentalListing.published_at.desc())
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    def get_active_listing_for_property(self, property_id: int) -> Optional[RentalListing]:
        """A property may only have one non-terminal listing at a time."""
        active_statuses = [
            RentalListingStatus.DRAFT.value,
            RentalListingStatus.PENDING_REVIEW.value,
            RentalListingStatus.PUBLISHED.value,
            RentalListingStatus.RENTED.value,
        ]
        return (
            self.db.query(RentalListing)
            .filter(
                RentalListing.property_id == property_id,
                RentalListing.status.in_(active_statuses),
            )
            .first()
        )
