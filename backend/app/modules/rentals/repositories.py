"""
Rental Listing Repository

Data access layer for rental listing operations.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.data.repositories.base import BaseRepository
from .models import (
    ACTIVE_APPLICATION_STATUSES,
    RentalApplication,
    RentalApplicationStatus,
    RentalListing,
    RentalListingStatus,
    TenancyContract,
)


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

    def get_locked(self, listing_id: int) -> Optional[RentalListing]:
        """Fetch a listing under a row lock (mirrors
        contract_service._next_sequence_value's pattern) so a concurrent
        accept on a sibling application cannot also pass the published
        check before this transaction commits its status change."""
        return (
            self.db.query(RentalListing)
            .filter(RentalListing.id == listing_id)
            .with_for_update()
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


class RentalApplicationRepository(BaseRepository[RentalApplication]):
    def __init__(self, db: Session):
        super().__init__(RentalApplication, db)

    def get_by_id(self, application_id: int) -> Optional[RentalApplication]:
        return (
            self.db.query(RentalApplication)
            .options(joinedload(RentalApplication.listing), joinedload(RentalApplication.renter))
            .filter(RentalApplication.id == application_id)
            .first()
        )

    def get_active_for_renter_on_listing(
        self, listing_id: int, renter_user_id: int
    ) -> Optional[RentalApplication]:
        return (
            self.db.query(RentalApplication)
            .filter(
                RentalApplication.listing_id == listing_id,
                RentalApplication.renter_user_id == renter_user_id,
                RentalApplication.status.in_(ACTIVE_APPLICATION_STATUSES),
            )
            .first()
        )

    def get_listing_applications(self, listing_id: int) -> List[RentalApplication]:
        return (
            self.db.query(RentalApplication)
            .options(joinedload(RentalApplication.renter))
            .filter(RentalApplication.listing_id == listing_id)
            .order_by(RentalApplication.created_at.desc())
            .all()
        )

    def get_pending_siblings(self, listing_id: int, exclude_id: int) -> List[RentalApplication]:
        return (
            self.db.query(RentalApplication)
            .filter(
                RentalApplication.listing_id == listing_id,
                RentalApplication.id != exclude_id,
                RentalApplication.status == RentalApplicationStatus.PENDING.value,
            )
            .all()
        )

    def get_renter_applications(
        self, renter_user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[RentalApplication], int]:
        query = (
            self.db.query(RentalApplication)
            .options(joinedload(RentalApplication.listing))
            .filter(RentalApplication.renter_user_id == renter_user_id)
            .order_by(RentalApplication.created_at.desc())
        )
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    def count_recent_for_renter(self, renter_user_id: int, window_seconds: int) -> int:
        since = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        return (
            self.db.query(func.count(RentalApplication.id))
            .filter(
                RentalApplication.renter_user_id == renter_user_id,
                RentalApplication.created_at >= since,
            )
            .scalar()
            or 0
        )


class TenancyContractRepository(BaseRepository[TenancyContract]):
    def __init__(self, db: Session):
        super().__init__(TenancyContract, db)

    def get_by_contract_no(self, contract_no: str) -> Optional[TenancyContract]:
        return (
            self.db.query(TenancyContract)
            .options(
                joinedload(TenancyContract.listing),
                joinedload(TenancyContract.application),
            )
            .filter(TenancyContract.contract_no == contract_no)
            .first()
        )

    def get_for_application(self, application_id: int) -> Optional[TenancyContract]:
        return (
            self.db.query(TenancyContract)
            .filter(TenancyContract.application_id == application_id)
            .first()
        )

    def list_all(self, skip: int = 0, limit: int = 20) -> Tuple[List[TenancyContract], int]:
        query = (
            self.db.query(TenancyContract)
            .options(joinedload(TenancyContract.listing))
            .order_by(TenancyContract.created_at.desc())
        )
        total = query.count()
        return query.offset(skip).limit(limit).all(), total
