"""
Rental Application Service (Phase C)

Renters apply to published listings at an offered rent; the offer is
validated server-side against the listing's frozen band (never trusted from
the client). One active application per renter per listing, a per-account
rate limit, and state guards keep the registry honest. Accepting one
application auto-rejects its pending siblings and moves the listing to
`rented`.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
import structlog

from app.core.exceptions import AuthorizationException, ValidationException, ValuAdisException
from app.data.models.audit_log import AuditLog
from app.data.models.user import User
from .exceptions import BandViolationError, RateLimitError
from .models import (
    RentalApplication,
    RentalApplicationStatus,
    RentalListing,
    RentalListingStatus,
)
from .repositories import RentalApplicationRepository, RentalListingRepository

logger = structlog.get_logger()

# Per-account application rate limit (abuse control, plan risk: fake renters).
RATE_LIMIT_WINDOW_SECONDS = 3600
RATE_LIMIT_MAX_APPLICATIONS = 10

# Retry budget for the accept row-lock, mirroring
# contract_service._next_sequence_value's SQLite "database is locked" hedge.
ACCEPT_LOCK_MAX_ATTEMPTS = 3


class RentalApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RentalApplicationRepository(db)
        self.listing_repo = RentalListingRepository(db)

    # ------------------------------------------------------------------
    # Renter flow
    # ------------------------------------------------------------------

    def apply(
        self, public_id: str, renter: User, offered_rent: float, message: Optional[str] = None
    ) -> Dict[str, Any]:
        listing = self.listing_repo.get_by_public_id(public_id)
        if not listing:
            raise ValuAdisException("Listing not found")

        # State guard: only a published listing accepts applications.
        if listing.status != RentalListingStatus.PUBLISHED.value:
            raise ValidationException(
                f"This listing is not open for applications (status '{listing.status}')."
            )

        if listing.owner_user_id == renter.id:
            raise ValidationException("You cannot apply to your own listing.")

        # Rate limit before any band math, so abuse is cheap to reject.
        recent = self.repo.count_recent_for_renter(renter.id, RATE_LIMIT_WINDOW_SECONDS)
        if recent >= RATE_LIMIT_MAX_APPLICATIONS:
            raise RateLimitError(
                "Application rate limit reached. Please try again later."
            )

        # Server-side band enforcement — the band is the legal price promise.
        # Inclusive at both edges; anything outside is a 422 (plan contract).
        if offered_rent < listing.band_min or offered_rent > listing.band_max:
            raise BandViolationError(
                f"Offered rent {offered_rent:,.0f} is outside the published band "
                f"{listing.band_min:,.0f}–{listing.band_max:,.0f} ETB/month."
            )

        existing = self.repo.get_active_for_renter_on_listing(listing.id, renter.id)
        if existing:
            raise ValidationException(
                "You already have an active application on this listing."
            )

        application = self.repo.create(
            {
                "listing_id": listing.id,
                "renter_user_id": renter.id,
                "offered_rent": offered_rent,
                "message": message,
                "status": RentalApplicationStatus.PENDING.value,
            }
        )
        self._audit("apply", application, renter.id, {"offered_rent": offered_rent})
        logger.info(
            "Rental application created",
            application_id=application.id,
            listing_public_id=listing.public_id,
        )
        return self.to_renter_dict(application, listing)

    def get_renter_applications(
        self, renter_user_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        applications, total = self.repo.get_renter_applications(renter_user_id, skip, limit)
        return [self.to_renter_dict(app, app.listing) for app in applications], total

    # ------------------------------------------------------------------
    # Owner flow
    # ------------------------------------------------------------------

    def get_owner_listing_applications(self, public_id: str, actor: User) -> List[Dict[str, Any]]:
        from .services import _is_rental_officer

        listing = self.listing_repo.get_by_public_id(public_id)
        if not listing:
            raise ValuAdisException("Listing not found")
        # The owner manages their applicants; officers need the accepted
        # application to register the contract.
        if listing.owner_user_id != actor.id and not _is_rental_officer(actor):
            raise AuthorizationException(
                "Only the listing owner or a rental officer can view its applications."
            )
        applications = self.repo.get_listing_applications(listing.id)
        return [self.to_owner_dict(app) for app in applications]

    def decide(
        self, application_id: int, owner: User, action: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        application = self.repo.get_by_id(application_id)
        if not application:
            raise ValuAdisException("Application not found")

        listing = application.listing
        if listing.owner_user_id != owner.id and not owner.is_admin:
            raise AuthorizationException("Only the listing owner can decide on this application.")

        if application.status != RentalApplicationStatus.PENDING.value:
            raise ValidationException(
                f"Only a pending application can be decided (this one is '{application.status}')."
            )

        if action == "reject":
            if listing.status != RentalListingStatus.PUBLISHED.value:
                raise ValidationException(
                    f"The listing is no longer published (status '{listing.status}')."
                )
            return self._reject(application, owner, reason)
        if action == "accept":
            # The published check happens inside _accept_with_lock, under a
            # row lock on the listing, so two concurrent accepts on sibling
            # applications cannot both observe "published" before either
            # commits its status change.
            return self._accept_with_lock(application, listing.id, owner)
        raise ValidationException(f"Unknown decision action '{action}'")

    def _accept_with_lock(
        self, application: RentalApplication, listing_id: int, owner: User
    ) -> Dict[str, Any]:
        last_error: Optional[Exception] = None
        for _ in range(ACCEPT_LOCK_MAX_ATTEMPTS):
            try:
                listing = self.listing_repo.get_locked(listing_id)
                if listing is None:
                    raise ValuAdisException("Listing not found")
                if listing.status != RentalListingStatus.PUBLISHED.value:
                    raise ValidationException(
                        f"The listing is no longer published (status '{listing.status}')."
                    )
                # Re-check under the lock: a concurrent accept on a sibling
                # application may have rejected this one between the initial
                # read in decide() and acquiring the listing lock here.
                self.db.refresh(application)
                if application.status != RentalApplicationStatus.PENDING.value:
                    raise ValidationException(
                        f"Only a pending application can be decided (this one is '{application.status}')."
                    )
                return self._accept(application, listing, owner)
            except OperationalError as exc:
                # e.g. SQLite "database is locked" under contention — retry.
                self.db.rollback()
                last_error = exc
        raise ValuAdisException(f"Could not accept application after retries: {last_error}")

    def _reject(self, application: RentalApplication, owner: User, reason: Optional[str]) -> Dict[str, Any]:
        updated = self.repo.update(
            application,
            {
                "status": RentalApplicationStatus.REJECTED.value,
                "decided_at": datetime.now(timezone.utc),
            },
        )
        self._audit("reject", updated, owner.id, {"reason": reason})
        return self.to_owner_dict(updated)

    def _accept(
        self, application: RentalApplication, listing: RentalListing, owner: User
    ) -> Dict[str, Any]:
        # Accept the chosen application, auto-reject pending siblings, and move
        # the listing to `rented` pending the officer's contract registration.
        siblings = self.repo.get_pending_siblings(listing.id, application.id)
        for sibling in siblings:
            self.repo.update(
                sibling,
                {
                    "status": RentalApplicationStatus.REJECTED.value,
                    "decided_at": datetime.now(timezone.utc),
                },
            )
            self._audit("auto_reject", sibling, owner.id, {"reason": "sibling accepted"})

        updated = self.repo.update(
            application,
            {
                "status": RentalApplicationStatus.ACCEPTED.value,
                "decided_at": datetime.now(timezone.utc),
            },
        )
        self.listing_repo.update(listing, {"status": RentalListingStatus.RENTED.value})
        self._audit(
            "accept",
            updated,
            owner.id,
            {"offered_rent": updated.offered_rent, "auto_rejected": len(siblings)},
        )
        logger.info(
            "Rental application accepted",
            application_id=updated.id,
            listing_public_id=listing.public_id,
            auto_rejected=len(siblings),
        )
        return self.to_owner_dict(updated)

    # ------------------------------------------------------------------
    # Serializers
    # ------------------------------------------------------------------

    @staticmethod
    def to_owner_dict(application: RentalApplication) -> Dict[str, Any]:
        renter = application.renter
        return {
            "id": application.id,
            "listing_public_id": application.listing.public_id if application.listing else None,
            "offered_rent": application.offered_rent,
            "status": application.status,
            "message": application.message,
            "renter_name": renter.full_name if renter else None,
            "renter_phone": renter.phone if renter else None,
            "decided_at": application.decided_at.isoformat() if application.decided_at else None,
            "created_at": application.created_at.isoformat() if application.created_at else None,
        }

    @staticmethod
    def to_renter_dict(application: RentalApplication, listing: Optional[RentalListing]) -> Dict[str, Any]:
        return {
            "id": application.id,
            "listing_public_id": listing.public_id if listing else None,
            "listing_status": listing.status if listing else None,
            "property_address": listing.property.address if listing and listing.property else None,
            "offered_rent": application.offered_rent,
            "band_min": listing.band_min if listing else None,
            "band_max": listing.band_max if listing else None,
            "status": application.status,
            "message": application.message,
            "created_at": application.created_at.isoformat() if application.created_at else None,
        }

    def _audit(
        self,
        action: str,
        application: RentalApplication,
        actor_user_id: int,
        new_values: Dict[str, Any],
    ) -> None:
        self.db.add(
            AuditLog(
                table_name="rental_applications",
                record_id=application.id,
                action=action,
                new_values={"listing_id": application.listing_id, "status": application.status, **new_values},
                user_id=actor_user_id,
            )
        )
        self.db.commit()
