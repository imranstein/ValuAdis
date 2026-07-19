"""
Renewal Cap Config Seeder

Seeds the current renewal-cap directive: 11.5% for Addis Ababa, effective
from the start of the 2026/27 directive period (Rent Control and
Administration Proclamation No. 1320/2024 — plans/valuadis-rentals/plan.mdx,
Phase D). Idempotent — re-running does not duplicate an already-seeded
directive for the same region/effective_from.
"""

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.data.models.renewal_cap_config import RenewalCapConfig

# Addis Ababa's 2026/27 directive under Proclamation 1320/2024. The
# proclamation's Ethiopian fiscal year runs July-to-July; 2026-07-01 is the
# directive's effective start.
ADDIS_ABABA_REGION = "Addis Ababa"
ADDIS_ABABA_2026_27_CAP_PCT = 0.115
ADDIS_ABABA_2026_27_EFFECTIVE_FROM = date(2026, 7, 1)
ADDIS_ABABA_2026_27_DIRECTIVE_REFERENCE = "Proclamation 1320/2024 — Addis Ababa 2026/27 directive"


def seed_renewal_cap(db: Session) -> RenewalCapConfig:
    """Create the current directive row if it is not already seeded."""
    existing = (
        db.query(RenewalCapConfig)
        .filter(
            RenewalCapConfig.region == ADDIS_ABABA_REGION,
            RenewalCapConfig.effective_from == ADDIS_ABABA_2026_27_EFFECTIVE_FROM,
        )
        .first()
    )
    if existing is not None:
        return existing

    row = RenewalCapConfig(
        region=ADDIS_ABABA_REGION,
        cap_pct=ADDIS_ABABA_2026_27_CAP_PCT,
        effective_from=ADDIS_ABABA_2026_27_EFFECTIVE_FROM,
        effective_until=None,
        directive_reference=ADDIS_ABABA_2026_27_DIRECTIVE_REFERENCE,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def run_renewal_cap_seeder():
    from app.core.database import get_db

    db = next(get_db())
    try:
        row = seed_renewal_cap(db)
        print(f"🌱 Seeded renewal cap directive: {row.region} {row.cap_pct:.1%} from {row.effective_from}")
        return row
    finally:
        db.close()


if __name__ == "__main__":
    run_renewal_cap_seeder()
