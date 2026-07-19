"""
Renewal cap — pure math (Phase D).

compute_max_allowed_rent() and is_within_cap() take no DB session. The
boundary case (a renewal at exactly the cap) must be allowed, and a change
to the configured cap_pct must change the computed ceiling — both are unit
tests here, not integration tests, because the math has nothing to do with
persistence.
"""

from decimal import Decimal

from app.modules.rentals.renewal_cap_service import compute_max_allowed_rent, is_within_cap


class TestCapMath:
    def test_max_allowed_rent_at_eleven_point_five_percent(self):
        max_allowed = compute_max_allowed_rent(Decimal("20000"), Decimal("0.115"))
        assert max_allowed == Decimal("22300.00")

    def test_configured_value_change_shifts_the_ceiling(self):
        lower_cap = compute_max_allowed_rent(Decimal("20000"), Decimal("0.05"))
        higher_cap = compute_max_allowed_rent(Decimal("20000"), Decimal("0.20"))
        assert lower_cap == Decimal("21000.00")
        assert higher_cap == Decimal("24000.00")
        assert lower_cap < higher_cap


class TestBoundary:
    def test_proposal_exactly_at_cap_is_allowed(self):
        max_allowed = compute_max_allowed_rent(Decimal("20000"), Decimal("0.115"))
        assert is_within_cap(max_allowed, max_allowed) is True

    def test_proposal_one_cent_over_cap_is_rejected(self):
        max_allowed = compute_max_allowed_rent(Decimal("20000"), Decimal("0.115"))
        assert is_within_cap(max_allowed + Decimal("0.01"), max_allowed) is False

    def test_proposal_below_cap_is_allowed(self):
        max_allowed = compute_max_allowed_rent(Decimal("20000"), Decimal("0.115"))
        assert is_within_cap(Decimal("20500"), max_allowed) is True
