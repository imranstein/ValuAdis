"""
Rent Index Snapshot Model

Public district rent index (plans/valuadis-rentals/plan.mdx, Phase D). One
row per (district, property_subtype, bedrooms, period) computed by the
aggregation job in app.modules.rentals.index_service. median_rent is
computed primarily from ACTIVE tenancy_contracts (ground truth); when the
contract sample for a group is below the minimum-sample threshold, published
listing bands are blended in to raise the sample (source records which).
sample_size is always stored (including below-threshold rows, for officer
observability); the public /rentals/index endpoint filters rows below the
threshold out of its response — suppression is a query-time concern, not a
storage concern, so the job can report its own coverage honestly.
"""

from sqlalchemy import CheckConstraint, Column, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class RentIndexSnapshot(Base):
    __tablename__ = "rent_index_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    # District bucket — the same value as Property.subcity / the rental
    # listing search "district" filter, so index rows line up with what
    # renters filter by on /rent and /rent/index.
    district = Column(String(100), nullable=False, index=True)
    property_subtype = Column(String(50), nullable=False)
    # Nullable: a null bedrooms bucket aggregates across all bedroom counts
    # for districts too thin to slice further.
    bedrooms = Column(Integer, nullable=True)

    median_rent = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    # 'contracts' (active tenancy contracts only), 'listings' (published
    # listing bands only — contract sample was zero), or 'blended' (both,
    # because the contract sample alone was below the minimum threshold).
    source = Column(String(20), nullable=False)

    # Aggregation period, e.g. "2026-07" (year-month). Snapshots are
    # recomputed idempotently per period by index_service.run_aggregation.
    period = Column(String(20), nullable=False, index=True)

    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "district", "property_subtype", "bedrooms", "period",
            name="uq_rent_index_snapshots_group_period",
        ),
        CheckConstraint("sample_size >= 0", name="ck_rent_index_snapshots_sample_size"),
        CheckConstraint(
            "source IN ('contracts','listings','blended')",
            name="ck_rent_index_snapshots_source",
        ),
    )

    def __repr__(self):
        return (
            f"<RentIndexSnapshot(district={self.district}, subtype={self.property_subtype}, "
            f"bedrooms={self.bedrooms}, period={self.period}, sample_size={self.sample_size})>"
        )
