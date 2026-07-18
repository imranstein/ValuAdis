"""
Rent Index Aggregation Service (Phase D)

Computes the public district rent index: median monthly rent by
district x property_subtype x bedrooms, per period. ACTIVE tenancy
contracts are the primary (ground-truth) source; where a group's contract
sample is below MIN_SAMPLE_SIZE, published listing bands for the same group
are blended in to raise the sample. Rows below MIN_SAMPLE_SIZE even after
blending are still stored (officer/audit visibility) but the public
/rentals/index endpoint filters them out — a single household's rent must
never be inferable from the public index.

The pure grouping math (median_rent, sample_size, source) lives in
compute_group_stats() with no DB access, so it is unit-testable with plain
lists of floats. run_aggregation() is the only DB-touching entry point; it
is idempotent per period (reruns replace that period's rows, never append).
"""

from datetime import datetime, timezone
from statistics import median
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
import structlog

from app.data.models.property import Property
from app.data.models.rent_index_snapshot import RentIndexSnapshot
from .models import RentalListing, RentalListingStatus, TenancyContract, TenancyContractStatus

logger = structlog.get_logger()

# Below this combined sample size, a group's median is not statistically
# meaningful enough to publish and must be suppressed from public output
# (plan decision: "rows below a minimum sample threshold are suppressed").
MIN_SAMPLE_SIZE = 3

GroupKey = Tuple[str, str, Optional[int]]


def current_period(as_of: Optional[datetime] = None) -> str:
    """Year-month bucket, e.g. '2026-07'."""
    moment = as_of or datetime.now(timezone.utc)
    return moment.strftime("%Y-%m")


def compute_group_stats(contract_rents: List[float], listing_rents: List[float]) -> Dict[str, Any]:
    """Pure math for one (district, subtype, bedrooms) group.

    Prefers active-contract rents; blends in listing rents only when the
    contract sample alone is below MIN_SAMPLE_SIZE, so a district with
    plenty of registered contracts is never diluted by asking-price bands.
    """
    if len(contract_rents) >= MIN_SAMPLE_SIZE:
        return {
            "median_rent": float(median(contract_rents)),
            "sample_size": len(contract_rents),
            "source": "contracts",
        }

    combined = [*contract_rents, *listing_rents]
    if not combined:
        return {"median_rent": None, "sample_size": 0, "source": "contracts"}

    if contract_rents and listing_rents:
        source = "blended"
    elif listing_rents:
        source = "listings"
    else:
        source = "contracts"
    return {"median_rent": float(median(combined)), "sample_size": len(combined), "source": source}


def is_suppressed(sample_size: int) -> bool:
    return sample_size < MIN_SAMPLE_SIZE


class RentIndexService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Aggregation job
    # ------------------------------------------------------------------

    def run_aggregation(self, period: Optional[str] = None) -> List[RentIndexSnapshot]:
        """Recompute the index for `period` (default: current year-month).

        Idempotent: existing rows for the period are replaced, not appended,
        so rerunning the job (e.g. a daily/weekly schedule) never duplicates
        or accumulates stale groups.
        """
        period = period or current_period()

        contract_groups = self._active_contract_rents_by_group()
        listing_groups = self._published_listing_rents_by_group()
        all_keys = set(contract_groups.keys()) | set(listing_groups.keys())

        rows: List[RentIndexSnapshot] = []
        for key in all_keys:
            district, subtype, bedrooms = key
            stats = compute_group_stats(contract_groups.get(key, []), listing_groups.get(key, []))
            if stats["median_rent"] is None:
                continue
            rows.append(
                RentIndexSnapshot(
                    district=district,
                    property_subtype=subtype,
                    bedrooms=bedrooms,
                    median_rent=stats["median_rent"],
                    sample_size=stats["sample_size"],
                    source=stats["source"],
                    period=period,
                )
            )

        # Replace-in-place for idempotency: delete this period's prior rows
        # first, in the same transaction as the insert. expire_all() clears
        # the session's identity map so a reused primary key (e.g. a second
        # run in the same long-lived session, as in tests) does not collide
        # with the stale in-memory reference to the row just deleted.
        self.db.query(RentIndexSnapshot).filter(RentIndexSnapshot.period == period).delete()
        self.db.expire_all()
        for row in rows:
            self.db.add(row)
        self.db.commit()

        logger.info("Rent index aggregation complete", period=period, groups=len(rows))
        return rows

    def _active_contract_rents_by_group(self) -> Dict[GroupKey, List[float]]:
        results = (
            self.db.query(
                Property.subcity, Property.property_subtype, Property.number_of_bedrooms,
                TenancyContract.monthly_rent,
            )
            .join(RentalListing, TenancyContract.listing_id == RentalListing.id)
            .join(Property, RentalListing.property_id == Property.id)
            .filter(TenancyContract.status == TenancyContractStatus.ACTIVE.value)
            .all()
        )
        return self._group_rents(results)

    def _published_listing_rents_by_group(self) -> Dict[GroupKey, List[float]]:
        results = (
            self.db.query(
                Property.subcity, Property.property_subtype, Property.number_of_bedrooms,
                RentalListing.suggested_rent,
            )
            .join(Property, RentalListing.property_id == Property.id)
            .filter(RentalListing.status == RentalListingStatus.PUBLISHED.value)
            .all()
        )
        return self._group_rents(results)

    @staticmethod
    def _group_rents(rows) -> Dict[GroupKey, List[float]]:
        grouped: Dict[GroupKey, List[float]] = {}
        for district, subtype, bedrooms, rent in rows:
            if not district or not subtype or rent is None:
                continue
            key = (district, subtype, bedrooms)
            grouped.setdefault(key, []).append(float(rent))
        return grouped

    # ------------------------------------------------------------------
    # Public read
    # ------------------------------------------------------------------

    def get_public_index(
        self,
        district: Optional[str] = None,
        property_subtype: Optional[str] = None,
        period: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Published index rows only: sample_size >= MIN_SAMPLE_SIZE. A
        below-threshold group is absent, not zeroed — the honest empty state
        is the caller's job, not a fabricated number here."""
        query = self.db.query(RentIndexSnapshot).filter(RentIndexSnapshot.sample_size >= MIN_SAMPLE_SIZE)
        if district:
            query = query.filter(RentIndexSnapshot.district.ilike(f"%{district}%"))
        if property_subtype:
            query = query.filter(RentIndexSnapshot.property_subtype == property_subtype)
        if period:
            query = query.filter(RentIndexSnapshot.period == period)
        query = query.order_by(
            RentIndexSnapshot.district.asc(),
            RentIndexSnapshot.period.desc(),
            RentIndexSnapshot.property_subtype.asc(),
        )
        return [self.to_public_dict(row) for row in query.all()]

    @staticmethod
    def to_public_dict(row: RentIndexSnapshot) -> Dict[str, Any]:
        return {
            "district": row.district,
            "property_subtype": row.property_subtype,
            "bedrooms": row.bedrooms,
            "median_rent": row.median_rent,
            "sample_size": row.sample_size,
            "source": row.source,
            "period": row.period,
        }


def run_rent_index_aggregation():
    """Standalone entry point for a scheduled run (same pattern as
    app.data.seeders.rent_ratio_seeder — manually invoked or wired to a
    cron/scheduler at deploy time; no in-process scheduler exists yet)."""
    from app.core.database import get_db

    db = next(get_db())
    try:
        rows = RentIndexService(db).run_aggregation()
        print(f"🌱 Rent index aggregation: {len(rows)} groups computed for {current_period()}")
        return rows
    finally:
        db.close()


if __name__ == "__main__":
    run_rent_index_aggregation()
