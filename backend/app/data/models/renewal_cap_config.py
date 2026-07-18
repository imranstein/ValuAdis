"""
Renewal Cap Config Model

The legal rent-increase cap for tenancy renewals (Rent Control and
Administration Proclamation No. 1320/2024; Addis Ababa set 11.5% for the
2026/27 directive — plans/valuadis-rentals/plan.mdx, Phase D). The cap is a
configured value with an effective period, not a literal in the renewal
service: the directive is expected to be reissued (a new percentage, a new
period) without a code change, mirroring the DistrictRentRatio seeded-config
pattern from Phase A.

RenewalCapService picks the row whose [effective_from, effective_until) span
covers the date being checked. effective_until is nullable — an open-ended
row is the current directive until a new one supersedes it.
"""

from sqlalchemy import CheckConstraint, Column, Date, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class RenewalCapConfig(Base):
    __tablename__ = "rental_renewal_cap_configs"

    id = Column(Integer, primary_key=True, index=True)

    # Pilot scope is Addis Ababa (plan decision); the column exists so a
    # second region's directive can be added without a schema change.
    region = Column(String(100), nullable=False, default="Addis Ababa", server_default="Addis Ababa")

    # e.g. 0.115 for the 11.5% Addis Ababa 2026/27 directive.
    cap_pct = Column(Float, nullable=False)

    effective_from = Column(Date, nullable=False, index=True)
    effective_until = Column(Date, nullable=True)

    directive_reference = Column(String(200), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("cap_pct >= 0", name="ck_renewal_cap_configs_cap_pct_non_negative"),
        CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="ck_renewal_cap_configs_period",
        ),
    )

    def __repr__(self):
        return (
            f"<RenewalCapConfig(region={self.region}, cap_pct={self.cap_pct}, "
            f"effective_from={self.effective_from}, effective_until={self.effective_until})>"
        )
