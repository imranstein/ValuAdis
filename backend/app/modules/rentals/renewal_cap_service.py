"""
Renewal Cap Service (Phase D)

Validates a proposed renewal rent against the legal cap over the active
contract's current rent (Proclamation 1320/2024; Addis Ababa's 11.5% for
2026/27). The cap is read from RenewalCapConfig (a configured value with an
effective period — plans/valuadis-rentals/plan.mdx), never hard-coded
inline in the check. The math is a pure, DB-free function so the boundary
case (exactly at the cap) and configured-value changes are cheap to test.

This is a contract-shape stub: the check and endpoint land now so the API is
settled, but the full renewal workflow (a new contract record, officer
approval, PDF) is post-pilot (plan decision, Phase D scope note).
"""

from datetime import date, timezone, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.data.models.renewal_cap_config import RenewalCapConfig
from .exceptions import RenewalCapExceededError

# In-code fallback used only when no RenewalCapConfig row is seeded for the
# region yet (mirrors ValuationService.RENT_RATIO_CITYWIDE_FALLBACK — the
# seeder is the source of truth; this is a documented safety net, not a
# literal buried in the validation logic).
FALLBACK_CAP_PCT = Decimal("0.115")
FALLBACK_REGION = "Addis Ababa"


def compute_max_allowed_rent(current_rent: Decimal, cap_pct: Decimal) -> Decimal:
    """Pure math: the highest renewal rent the cap permits over current_rent."""
    return (current_rent * (Decimal("1") + cap_pct)).quantize(Decimal("0.01"))


def is_within_cap(proposed_rent: Decimal, max_allowed_rent: Decimal) -> bool:
    """Boundary is inclusive: a renewal at exactly the cap is allowed."""
    return proposed_rent <= max_allowed_rent


class RenewalCapService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_cap(self, region: str = FALLBACK_REGION, as_of: Optional[date] = None) -> Dict[str, Any]:
        """The directive covering `as_of` (default: today), or the documented
        fallback when no config row is seeded yet for the region."""
        as_of = as_of or datetime.now(timezone.utc).date()
        row = (
            self.db.query(RenewalCapConfig)
            .filter(
                RenewalCapConfig.region == region,
                RenewalCapConfig.effective_from <= as_of,
            )
            .filter(
                (RenewalCapConfig.effective_until.is_(None)) | (RenewalCapConfig.effective_until > as_of)
            )
            .order_by(RenewalCapConfig.effective_from.desc())
            .first()
        )
        if row is not None:
            return {
                "cap_pct": Decimal(str(row.cap_pct)),
                "region": row.region,
                "effective_from": row.effective_from,
                "effective_until": row.effective_until,
                "directive_reference": row.directive_reference,
                "source": "configured",
            }
        return {
            "cap_pct": FALLBACK_CAP_PCT,
            "region": region,
            "effective_from": None,
            "effective_until": None,
            "directive_reference": None,
            "source": "fallback",
        }

    def validate_renewal(
        self,
        current_rent: float,
        proposed_rent: float,
        region: str = FALLBACK_REGION,
        as_of: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Check a proposed renewal rent against the active cap.

        Raises ValidationException when the proposal exceeds the cap; callers
        map that to a 422 (the contract's out-of-band-offer convention).
        """
        if current_rent <= 0:
            raise ValidationException("current_rent must be positive")
        if proposed_rent <= 0:
            raise ValidationException("proposed_rent must be positive")

        cap = self.get_active_cap(region, as_of)
        max_allowed = compute_max_allowed_rent(Decimal(str(current_rent)), cap["cap_pct"])
        allowed = is_within_cap(Decimal(str(proposed_rent)), max_allowed)

        result = {
            "current_rent": current_rent,
            "proposed_rent": proposed_rent,
            "cap_pct": float(cap["cap_pct"]),
            "max_allowed_rent": float(max_allowed),
            "allowed": allowed,
            "region": cap["region"],
            "directive_reference": cap["directive_reference"],
        }
        if not allowed:
            raise RenewalCapExceededError(
                f"Proposed renewal rent {proposed_rent:,.2f} exceeds the "
                f"{float(cap['cap_pct']):.1%} legal cap over the current rent "
                f"{current_rent:,.2f} (maximum allowed {float(max_allowed):,.2f})."
            )
        return result
