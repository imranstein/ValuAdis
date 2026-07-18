"""
Rent Valuation Service Tests

Unit tests for the Phase A rent valuation engine (ratio method, direct
comps, blend, band math, low-confidence flagging). These exercise only the
pure functions on ValuationService — no DB session, no network, no
scraper — per plans/valuadis-rentals/tasks/phase-a.md's acceptance
criteria.
"""

from decimal import Decimal

import pytest

from app.core.exceptions import PropertyValidationError
from app.modules.valuation import ValuationService
from app.services.spatial_service import SpatialService


@pytest.fixture
def svc() -> ValuationService:
    return ValuationService(SpatialService())


# ---------------------------------------------------------------------------
# Ratio method
# ---------------------------------------------------------------------------

class TestRentFromRatio:
    def test_market_value_times_ratio(self, svc):
        result = svc.calculate_rent_from_ratio(Decimal("1000000"), Decimal("0.006"))
        assert result == Decimal("6000.00")

    def test_zero_ratio_yields_zero_rent(self, svc):
        assert svc.calculate_rent_from_ratio(Decimal("1000000"), Decimal("0")) == Decimal("0.00")


# ---------------------------------------------------------------------------
# Direct comps method
# ---------------------------------------------------------------------------

class TestRentFromComps:
    def test_empty_comps_returns_none(self, svc):
        assert svc.calculate_rent_from_comps([]) is None

    def test_odd_count_returns_middle_value(self, svc):
        result = svc.calculate_rent_from_comps([Decimal("5000"), Decimal("6000"), Decimal("7000")])
        assert result == Decimal("6000.00")

    def test_even_count_returns_average_of_middle_two(self, svc):
        result = svc.calculate_rent_from_comps(
            [Decimal("5000"), Decimal("6000"), Decimal("7000"), Decimal("8000")]
        )
        assert result == Decimal("6500.00")


# ---------------------------------------------------------------------------
# Trend adjustment
# ---------------------------------------------------------------------------

class TestRentTrendAdjustment:
    def test_positive_trend_increases_rent(self, svc):
        result = svc.apply_rent_trend_adjustment(Decimal("6000"), Decimal("0.02"))
        assert result == Decimal("6120.00")

    def test_negative_trend_decreases_rent(self, svc):
        result = svc.apply_rent_trend_adjustment(Decimal("6000"), Decimal("-0.02"))
        assert result == Decimal("5880.00")

    def test_zero_trend_is_a_no_op(self, svc):
        assert svc.apply_rent_trend_adjustment(Decimal("6000"), Decimal("0")) == Decimal("6000.00")

    def test_trend_is_capped_at_max_adjustment(self, svc):
        # 50% trend input should be capped to RENT_MAX_TREND_ADJUSTMENT (5%)
        result = svc.apply_rent_trend_adjustment(Decimal("6000"), Decimal("0.50"))
        assert result == Decimal("6300.00")

    def test_negative_trend_is_floored_at_max_adjustment(self, svc):
        result = svc.apply_rent_trend_adjustment(Decimal("6000"), Decimal("-0.50"))
        assert result == Decimal("5700.00")


# ---------------------------------------------------------------------------
# Blend + confidence
# ---------------------------------------------------------------------------

class TestBlendRentEstimates:
    def test_both_methods_present_averages_them(self, svc):
        blended, _ = svc.blend_rent_estimates(Decimal("6000"), Decimal("6400"), comp_count=3)
        assert blended == Decimal("6200.00")

    def test_ratio_only_uses_ratio_estimate(self, svc):
        blended, _ = svc.blend_rent_estimates(Decimal("6000"), None, comp_count=0)
        assert blended == Decimal("6000.00")

    def test_comps_only_uses_comps_estimate(self, svc):
        blended, _ = svc.blend_rent_estimates(None, Decimal("6400"), comp_count=4)
        assert blended == Decimal("6400.00")

    def test_neither_estimate_raises(self, svc):
        with pytest.raises(PropertyValidationError):
            svc.blend_rent_estimates(None, None, comp_count=0)

    def test_both_methods_with_full_comps_yields_max_confidence(self, svc):
        _, confidence = svc.blend_rent_estimates(
            Decimal("6000"), Decimal("6400"), comp_count=svc.RENT_COMPS_FOR_FULL_CONFIDENCE
        )
        assert confidence == Decimal("1.00")

    def test_ratio_only_zero_comps_yields_low_confidence(self, svc):
        _, confidence = svc.blend_rent_estimates(Decimal("6000"), None, comp_count=0)
        assert confidence == svc.RENT_CONFIDENCE_BASE_RATIO_ONLY

    def test_confidence_increases_with_comp_count(self, svc):
        _, low = svc.blend_rent_estimates(Decimal("6000"), Decimal("6400"), comp_count=0)
        _, high = svc.blend_rent_estimates(Decimal("6000"), Decimal("6400"), comp_count=3)
        assert high > low


# ---------------------------------------------------------------------------
# Band math
# ---------------------------------------------------------------------------

class TestRentBand:
    def test_band_is_plus_minus_ten_percent(self, svc):
        band_min, band_max = svc.calculate_rent_band(Decimal("6000"))
        assert band_min == Decimal("5400.00")
        assert band_max == Decimal("6600.00")

    def test_band_width_uses_named_constant(self, svc):
        band_min, band_max = svc.calculate_rent_band(Decimal("1000"))
        expected_min = Decimal("1000") * (Decimal("1") - svc.RENT_BAND_PCT)
        assert band_min == expected_min.quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# Full pure orchestrator: calculate_rent_valuation
# ---------------------------------------------------------------------------

class TestCalculateRentValuation:
    def test_no_comps_requires_officer_review(self, svc):
        result = svc.calculate_rent_valuation(Decimal("1000000"), Decimal("0.006"), [])
        assert result["requires_officer_review"] is True
        assert result["confidence"] < float(svc.RENT_CONFIDENCE_FLOOR)

    def test_enough_comps_does_not_require_review(self, svc):
        comps = [Decimal("5800"), Decimal("6000"), Decimal("6100"), Decimal("6200"), Decimal("5900")]
        result = svc.calculate_rent_valuation(Decimal("1000000"), Decimal("0.006"), comps)
        assert result["requires_officer_review"] is False

    def test_result_contains_all_required_fields(self, svc):
        result = svc.calculate_rent_valuation(Decimal("1000000"), Decimal("0.006"), [])
        for key in (
            "suggested_rent", "band_min", "band_max", "confidence",
            "requires_officer_review", "comp_count", "ratio_estimate", "comps_estimate",
        ):
            assert key in result, f"Missing key: {key}"

    def test_band_bracket_suggested_rent(self, svc):
        result = svc.calculate_rent_valuation(Decimal("1000000"), Decimal("0.006"), [])
        assert result["band_min"] < result["suggested_rent"] < result["band_max"]

    def test_no_network_or_db_calls_required(self, svc):
        """Pure function: no db session was ever passed to this fixture."""
        assert svc.db is None
        # Should not raise despite db being None
        svc.calculate_rent_valuation(Decimal("500000"), Decimal("0.005"), [Decimal("3000")])
