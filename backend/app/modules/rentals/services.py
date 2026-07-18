"""
Rental Listing Service

Business logic for the government-mediated rental registry (Phase B):
owner listing registration with auto rent valuation, the officer review
queue (verify / adjust band with mandatory reason / publish / reject),
and the PII-redacted public browse surface.
"""

import secrets
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
import structlog

from app.core.exceptions import AuthorizationException, ValidationException, ValuAdisException
from app.data.models.audit_log import AuditLog
from app.data.models.property import Property
from app.data.models.user import User
from app.data.models.valuation import Valuation, ValuationPurpose, ValuationStatus
from app.modules.valuation.services import ValuationService
from app.services.spatial_service import SpatialService
from .models import RentalListing, RentalListingStatus
from .repositories import RentalListingRepository
from .schemas import PublicListing, PublicListingProperty

logger = structlog.get_logger()

# Registry prefix for listing public ids: <region>-LST-<year>-<serial>.
# AA = Addis Ababa pilot (Bole + Yeka sub-cities activate by data, not code).
PUBLIC_ID_REGION = "AA"
PUBLIC_ID_KIND = "LST"
PUBLIC_ID_MAX_ATTEMPTS = 20

# Proclamation 1320/2024 covers residential rentals only; commercial and
# other premises must be impossible to list. mixed_use is excluded until a
# legal reading says its residential portion qualifies.
RENTABLE_PROPERTY_TYPES = ("residential",)


class RentalListingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RentalListingRepository(db)
        self.valuation_service = ValuationService(SpatialService(), db)

    # ------------------------------------------------------------------
    # Owner flow
    # ------------------------------------------------------------------

    def create_listing(self, property_id: int, owner: User, notes: Optional[str] = None) -> Dict[str, Any]:
        """Register an existing property for rent.

        Auto-creates a rent valuation (Phase A engine) and a listing in
        pending_review carrying the suggested band. Low-confidence
        valuations mark the listing for mandatory officer band review.
        """
        prop = (
            self.db.query(Property)
            .filter(Property.id == property_id, Property.user_id == owner.id)
            .first()
        )
        if not prop:
            raise ValidationException("Property not found or not owned by you")

        if prop.property_type not in RENTABLE_PROPERTY_TYPES:
            raise ValidationException(
                "Only residential properties can be listed for rent "
                "(Rent Control and Administration Proclamation No. 1320/2024)"
            )

        existing = self.repo.get_active_listing_for_property(property_id)
        if existing:
            raise ValidationException(
                f"Property already has an active rental listing ({existing.public_id})"
            )

        rent_result, valuation = self._create_rent_valuation(prop, owner.id)

        listing = self.repo.create(
            {
                "public_id": self._generate_public_id(),
                "property_id": prop.id,
                "valuation_id": valuation.id,
                "owner_user_id": owner.id,
                "suggested_rent": rent_result["suggested_rent"],
                "band_min": rent_result["band_min"],
                "band_max": rent_result["band_max"],
                "confidence": rent_result["confidence"],
                "requires_officer_review": rent_result["requires_officer_review"],
                "status": RentalListingStatus.PENDING_REVIEW.value,
                "review_reason": notes,
            }
        )

        self._audit("create", listing, owner.id, {"status": listing.status})
        logger.info(
            "Rental listing created",
            listing_id=listing.id,
            public_id=listing.public_id,
            property_id=prop.id,
            requires_officer_review=listing.requires_officer_review,
        )
        return self.to_owner_dict(listing)

    def get_owner_listings(self, owner_user_id: int, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        listings, total = self.repo.get_owner_listings(owner_user_id, skip, limit)
        return [self.to_owner_dict(listing) for listing in listings], total

    def withdraw_listing(self, public_id: str, actor: User, reason: Optional[str] = None) -> Dict[str, Any]:
        listing = self.repo.get_by_public_id(public_id)
        if not listing:
            raise ValuAdisException("Listing not found")

        is_owner = listing.owner_user_id == actor.id
        if not is_owner and not _is_rental_officer(actor):
            raise AuthorizationException("Only the owner or a rental officer can withdraw a listing")

        if listing.status in (RentalListingStatus.WITHDRAWN.value, RentalListingStatus.RENTED.value):
            raise ValidationException(f"Cannot withdraw a listing in status '{listing.status}'")

        updated = self.repo.update(
            listing,
            {"status": RentalListingStatus.WITHDRAWN.value, "review_reason": reason},
        )
        self._audit("withdraw", updated, actor.id, {"status": updated.status, "reason": reason})
        return self.to_owner_dict(updated)

    # ------------------------------------------------------------------
    # Officer flow
    # ------------------------------------------------------------------

    def get_review_queue(self, status: str, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        listings, total = self.repo.get_review_queue(status, skip, limit)
        return [self.to_officer_dict(listing) for listing in listings], total

    def review_listing(
        self,
        public_id: str,
        officer: User,
        action: str,
        band_min: Optional[float] = None,
        band_max: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Officer review action: publish, adjust_band, or reject.

        Band values freeze on publish; adjusting after publish requires
        withdraw -> re-review. Band adjustment and rejection require a
        mandatory reason (audited).
        """
        listing = self.repo.get_by_public_id(public_id)
        if not listing:
            raise ValuAdisException("Listing not found")

        if listing.status != RentalListingStatus.PENDING_REVIEW.value:
            raise ValidationException(
                f"Only pending_review listings can be reviewed; this listing is '{listing.status}'. "
                "A published listing must be withdrawn and re-submitted for re-review."
            )

        if action == "publish":
            return self._publish(listing, officer)
        if action == "adjust_band":
            return self._adjust_band(listing, officer, band_min, band_max, reason)
        if action == "reject":
            return self._reject(listing, officer, reason)
        raise ValidationException(f"Unknown review action '{action}'")

    def verify_owner(self, user_id: int, officer: User) -> Dict[str, Any]:
        """Officer verifies a citizen account as a property owner (audited)."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValuAdisException("User not found")
        if user.owner_verified:
            raise ValidationException("User is already verified as a property owner")

        user.owner_verified = True
        user.owner_verified_at = datetime.now(timezone.utc)
        self.db.add(user)
        self.db.commit()

        self.db.add(
            AuditLog(
                table_name="users",
                record_id=user.id,
                action="owner_verify",
                new_values={"owner_verified": True, "verified_by": officer.id},
                user_id=officer.id,
            )
        )
        self.db.commit()
        logger.info("Owner verified", verified_user_id=user.id, officer_id=officer.id)
        return {"user_id": user.id, "owner_verified": True}

    def _publish(self, listing: RentalListing, officer: User) -> Dict[str, Any]:
        owner = self.db.query(User).filter(User.id == listing.owner_user_id).first()
        if not owner or not owner.owner_verified:
            raise ValidationException(
                "Owner account is not verified. Verify the owner before publishing their listing."
            )

        # Approve the backing rent valuation through the existing state
        # machine so the published band is backed by an approved valuation
        # (certificate gate reuses this).
        valuation = self.db.query(Valuation).filter(Valuation.id == listing.valuation_id).first()
        if valuation is not None:
            current = valuation.status.value if hasattr(valuation.status, "value") else str(valuation.status)
            if current == ValuationStatus.DRAFT.value:
                self.valuation_service.transition_status(valuation.id, "pending", officer.id)
                self.valuation_service.transition_status(valuation.id, "approved", officer.id)
            elif current == ValuationStatus.PENDING.value:
                self.valuation_service.transition_status(valuation.id, "approved", officer.id)

        updated = self.repo.update(
            listing,
            {
                "status": RentalListingStatus.PUBLISHED.value,
                "published_at": datetime.now(timezone.utc),
                "requires_officer_review": False,
            },
        )
        self._audit(
            "publish",
            updated,
            officer.id,
            {
                "status": updated.status,
                "band_min": updated.band_min,
                "band_max": updated.band_max,
                "suggested_rent": updated.suggested_rent,
            },
        )
        logger.info("Rental listing published", public_id=updated.public_id, officer_id=officer.id)
        return self.to_officer_dict(updated)

    def _adjust_band(
        self,
        listing: RentalListing,
        officer: User,
        band_min: Optional[float],
        band_max: Optional[float],
        reason: Optional[str],
    ) -> Dict[str, Any]:
        if not reason or not reason.strip():
            raise ValidationException("A reason is mandatory when adjusting the band")
        if band_min is None or band_max is None:
            raise ValidationException("band_min and band_max are required to adjust the band")
        if band_min >= band_max:
            raise ValidationException("band_min must be less than band_max")

        old_values = {"band_min": listing.band_min, "band_max": listing.band_max}
        suggested = round((band_min + band_max) / 2, 2)
        updated = self.repo.update(
            listing,
            {
                "band_min": band_min,
                "band_max": band_max,
                "suggested_rent": suggested,
                "review_reason": reason,
                "requires_officer_review": False,
            },
        )
        self._audit(
            "adjust_band",
            updated,
            officer.id,
            {"band_min": band_min, "band_max": band_max, "reason": reason},
            old_values=old_values,
        )
        return self.to_officer_dict(updated)

    def _reject(self, listing: RentalListing, officer: User, reason: Optional[str]) -> Dict[str, Any]:
        if not reason or not reason.strip():
            raise ValidationException("A reason is mandatory when rejecting a listing")
        updated = self.repo.update(
            listing,
            {"status": RentalListingStatus.WITHDRAWN.value, "review_reason": reason},
        )
        self._audit("reject", updated, officer.id, {"status": updated.status, "reason": reason})
        return self.to_officer_dict(updated)

    # ------------------------------------------------------------------
    # Public browse
    # ------------------------------------------------------------------

    def search_published(
        self,
        district: Optional[str] = None,
        property_subtype: Optional[str] = None,
        bedrooms: Optional[int] = None,
        band_min: Optional[float] = None,
        band_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[PublicListing], int]:
        listings, total = self.repo.search_published(
            district=district,
            property_subtype=property_subtype,
            bedrooms=bedrooms,
            band_min=band_min,
            band_max=band_max,
            skip=skip,
            limit=limit,
        )
        return [self.to_public_listing(listing) for listing in listings], total

    def get_public_listing(self, public_id: str) -> Optional[PublicListing]:
        """Published listings only; anything else is a public 404."""
        listing = self.repo.get_by_public_id(public_id)
        if not listing or listing.status != RentalListingStatus.PUBLISHED.value:
            return None
        return self.to_public_listing(listing)

    # ------------------------------------------------------------------
    # Serializers
    # ------------------------------------------------------------------

    @staticmethod
    def to_public_listing(listing: RentalListing) -> PublicListing:
        prop = listing.property
        return PublicListing(
            public_id=listing.public_id,
            suggested_rent=listing.suggested_rent,
            band_min=listing.band_min,
            band_max=listing.band_max,
            published_at=listing.published_at,
            property=PublicListingProperty(
                address=prop.address,
                municipality=prop.municipality,
                subcity=prop.subcity,
                property_type=prop.property_type,
                property_subtype=prop.property_subtype,
                area_sqm=prop.area_sqm,
                building_area_sqm=prop.building_area_sqm,
                number_of_bedrooms=prop.number_of_bedrooms,
                number_of_bathrooms=prop.number_of_bathrooms,
                number_of_floors=prop.number_of_floors,
                year_built=prop.year_built,
                condition=prop.condition,
                latitude=prop.latitude,
                longitude=prop.longitude,
            ),
        )

    @staticmethod
    def to_owner_dict(listing: RentalListing) -> Dict[str, Any]:
        prop = listing.property
        return {
            "public_id": listing.public_id,
            "property_id": listing.property_id,
            "property_address": prop.address if prop else None,
            "suggested_rent": listing.suggested_rent,
            "band_min": listing.band_min,
            "band_max": listing.band_max,
            "confidence": listing.confidence,
            "requires_officer_review": listing.requires_officer_review,
            "status": listing.status,
            "review_reason": listing.review_reason,
            "published_at": listing.published_at.isoformat() if listing.published_at else None,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
        }

    @staticmethod
    def to_officer_dict(listing: RentalListing) -> Dict[str, Any]:
        data = RentalListingService.to_owner_dict(listing)
        owner = listing.owner
        prop = listing.property
        data.update(
            {
                "valuation_id": listing.valuation_id,
                "owner_user_id": listing.owner_user_id,
                "owner_name": owner.full_name if owner else None,
                "owner_verified": bool(owner.owner_verified) if owner else False,
                "property_municipality": prop.municipality if prop else None,
                "property_subcity": prop.subcity if prop else None,
                "property_type": prop.property_type if prop else None,
                "property_area_sqm": prop.area_sqm if prop else None,
            }
        )
        return data

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _create_rent_valuation(self, prop: Property, owner_user_id: int) -> Tuple[Dict[str, Any], Valuation]:
        # create_listing guarantees residential-only before this point.
        valuation_type = "residential"
        property_data = {
            "municipality": prop.municipality,
            "area_sqm": prop.area_sqm,
            "property_type": valuation_type,
            "condition": prop.condition if prop.condition in ("excellent", "good", "fair", "poor") else "good",
            "construction_year": prop.year_built,
        }
        market_value = (
            Decimal(str(prop.market_value))
            if prop.market_value
            else self.valuation_service.calculate_market_value(property_data)
        )
        rent_result = self.valuation_service.get_rent_valuation(property_data, market_value=market_value)

        valuation = Valuation(
            property_id=prop.id,
            user_id=owner_user_id,
            property_type=valuation_type,
            municipality=prop.municipality,
            area_sqm=prop.area_sqm,
            market_value=float(market_value),
            taxable_value=float(self.valuation_service.calculate_taxable_value(market_value)),
            status=ValuationStatus.DRAFT,
            purpose=ValuationPurpose.RENT.value,
            notes=f"Auto rent valuation for rental listing (property {prop.id})",
        )
        self.db.add(valuation)
        self.db.commit()
        self.db.refresh(valuation)
        return rent_result, valuation

    def _generate_public_id(self) -> str:
        year = datetime.now(timezone.utc).year
        for _ in range(PUBLIC_ID_MAX_ATTEMPTS):
            serial = secrets.randbelow(1_000_000)
            candidate = f"{PUBLIC_ID_REGION}-{PUBLIC_ID_KIND}-{year}-{serial:06d}"
            if not self.repo.public_id_exists(candidate):
                return candidate
        raise ValuAdisException("Could not allocate a unique listing public id")

    def _audit(
        self,
        action: str,
        listing: RentalListing,
        actor_user_id: int,
        new_values: Dict[str, Any],
        old_values: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.db.add(
            AuditLog(
                table_name="rental_listings",
                record_id=listing.id,
                action=action,
                old_values=old_values,
                new_values={"public_id": listing.public_id, **new_values},
                user_id=actor_user_id,
            )
        )
        self.db.commit()


def _is_rental_officer(user: User) -> bool:
    """Officer gate: the rental_officer role, honoring the is_admin flag
    (seeded admin accounts may have no role rows — session learning)."""
    if user.is_admin:
        return True
    try:
        return any(role.name == "rental_officer" for role in user.roles)
    except Exception:
        return False
