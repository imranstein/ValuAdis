"""
Valuation Service Tests

Comprehensive unit tests for the Proclamation 1365/2025 valuation algorithm.
Covers every condition grade, neighborhood tier, depreciation branch, property
type multiplier, municipality rate, and the get_valuation_breakdown helper.
"""

import pytest
from datetime import date
from decimal import Decimal

from app.core.exceptions import PropertyValidationError
from app.services.spatial_service import SpatialService
from app.services.valuation_service import ValuationService


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

# A minimal closed polygon within Ethiopia (Addis Ababa area)
_CLOSED_POLY_ADDIS = [
    [38.7578, 9.0320],
    [38.7580, 9.0320],
    [38.7580, 9.0318],
    [38.7578, 9.0318],
    [38.7578, 9.0320],   # closes the ring
]


@pytest.fixture
def svc() -> ValuationService:
    return ValuationService(SpatialService())


def _base_data(**overrides) -> dict:
    """Return a minimal valid property-data dict for Addis Ababa, residential."""
    data = {
        "municipality":         "Addis Ababa",
        "area_sqm":             100.0,
        "property_type":        "residential",
        "condition":            "good",
        "neighborhood_quality": "average",
        "coordinates":          _CLOSED_POLY_ADDIS,
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Taxable value
# ---------------------------------------------------------------------------

class TestTaxableValue:
    def test_25_percent_of_market_value(self, svc):
        assert svc.calculate_taxable_value(Decimal("1000000.00")) == Decimal("250000.00")

    def test_small_value(self, svc):
        assert svc.calculate_taxable_value(Decimal("4.00")) == Decimal("1.00")

    def test_zero_raises_validation_error(self, svc):
        with pytest.raises(PropertyValidationError):
            svc.calculate_taxable_value(Decimal("0"))

    def test_negative_raises_validation_error(self, svc):
        with pytest.raises(PropertyValidationError):
            svc.calculate_taxable_value(Decimal("-100"))


# ---------------------------------------------------------------------------
# Condition grade branches
# ---------------------------------------------------------------------------
#
# Baseline: Addis Ababa, residential, 100 sqm, average neighborhood,
#           no construction year, good condition.
#
#   base_value         = 1 000 × 100 × 1.0  = 100 000
#   land_value         = 100 000 × 0.60     =  60 000
#   structure_value    = 100 000 × 0.40     =  40 000
#   depreciation       = 0  (no construction_year)
#   subtotal           =  60 000 + 40 000   = 100 000
#   after_neighborhood = 100 000 × 1.0      = 100 000
#   market_value       = 100 000 × <condition_factor>
# ---------------------------------------------------------------------------

class TestConditionGrades:
    def test_good_condition_baseline(self, svc):
        assert svc.calculate_market_value(_base_data()) == Decimal("100000.00")

    def test_excellent_condition_1_20x(self, svc):
        # 100 000 × 1.20 = 120 000
        assert svc.calculate_market_value(_base_data(condition="excellent")) == Decimal("120000.00")

    def test_fair_condition_0_80x(self, svc):
        # 100 000 × 0.80 = 80 000
        assert svc.calculate_market_value(_base_data(condition="fair")) == Decimal("80000.00")

    def test_poor_condition_0_60x(self, svc):
        # 100 000 × 0.60 = 60 000
        assert svc.calculate_market_value(_base_data(condition="poor")) == Decimal("60000.00")

    def test_invalid_condition_raises(self, svc):
        with pytest.raises(PropertyValidationError, match="Invalid condition"):
            svc.calculate_market_value(_base_data(condition="demolished"))


# ---------------------------------------------------------------------------
# Neighborhood quality branches
# ---------------------------------------------------------------------------

class TestNeighborhoodQuality:
    def test_average_no_adjustment(self, svc):
        assert svc.calculate_market_value(_base_data(neighborhood_quality="average")) == Decimal("100000.00")

    def test_prime_1_30x(self, svc):
        # 100 000 × 1.30 = 130 000
        assert svc.calculate_market_value(_base_data(neighborhood_quality="prime")) == Decimal("130000.00")

    def test_above_average_1_10x(self, svc):
        assert svc.calculate_market_value(_base_data(neighborhood_quality="above_average")) == Decimal("110000.00")

    def test_below_average_0_85x(self, svc):
        assert svc.calculate_market_value(_base_data(neighborhood_quality="below_average")) == Decimal("85000.00")

    def test_developing_0_70x(self, svc):
        assert svc.calculate_market_value(_base_data(neighborhood_quality="developing")) == Decimal("70000.00")

    def test_invalid_neighborhood_quality_raises(self, svc):
        with pytest.raises(PropertyValidationError, match="Invalid neighborhood_quality"):
            svc.calculate_market_value(_base_data(neighborhood_quality="slum"))


# ---------------------------------------------------------------------------
# Depreciation
# ---------------------------------------------------------------------------
#
# Structure = 40% of base_value = 40 000.
# Land      = 60% of base_value = 60 000  (never depreciated).
#
# depreciation = min(0.01 × age, 0.50)
# ---------------------------------------------------------------------------

class TestDepreciation:
    def test_no_construction_year_zero_depreciation(self, svc):
        # market_value = 100 000 (full structure)
        assert svc.calculate_market_value(_base_data()) == Decimal("100000.00")

    def test_brand_new_building_zero_depreciation(self, svc):
        result = svc.calculate_market_value(_base_data(construction_year=date.today().year))
        assert result == Decimal("100000.00")

    def test_10_year_old_building(self, svc):
        # age = 10 → depreciation = 10%
        # structure_depreciated = 40 000 × 0.90 = 36 000
        # market_value = 60 000 + 36 000 = 96 000
        year = date.today().year - 10
        assert svc.calculate_market_value(_base_data(construction_year=year)) == Decimal("96000.00")

    def test_25_year_old_building(self, svc):
        # age = 25 → depreciation = 25%
        # structure_depreciated = 40 000 × 0.75 = 30 000
        # market_value = 60 000 + 30 000 = 90 000
        year = date.today().year - 25
        assert svc.calculate_market_value(_base_data(construction_year=year)) == Decimal("90000.00")

    def test_depreciation_capped_at_50_percent(self, svc):
        # age = 60 → raw 60% capped to 50%
        # structure_depreciated = 40 000 × 0.50 = 20 000
        # market_value = 60 000 + 20 000 = 80 000
        year = date.today().year - 60
        assert svc.calculate_market_value(_base_data(construction_year=year)) == Decimal("80000.00")

    def test_calculate_depreciation_helper_returns_zero_for_none(self, svc):
        assert svc._calculate_depreciation(None) == Decimal("0")

    def test_calculate_depreciation_helper_is_capped_at_50_pct(self, svc):
        assert svc._calculate_depreciation(1900) == Decimal("0.50")


# ---------------------------------------------------------------------------
# Property type multipliers
# ---------------------------------------------------------------------------

class TestPropertyTypeMultipliers:
    def test_residential_1x(self, svc):
        assert svc.calculate_market_value(_base_data(property_type="residential")) == Decimal("100000.00")

    def test_commercial_1_5x(self, svc):
        # base_value = 1 000 × 100 × 1.5 = 150 000
        assert svc.calculate_market_value(_base_data(property_type="commercial")) == Decimal("150000.00")

    def test_industrial_1_3x(self, svc):
        # base_value = 1 000 × 100 × 1.3 = 130 000
        assert svc.calculate_market_value(_base_data(property_type="industrial")) == Decimal("130000.00")

    def test_agricultural_0_3x(self, svc):
        # base_value = 1 000 × 100 × 0.3 = 30 000
        assert svc.calculate_market_value(_base_data(property_type="agricultural")) == Decimal("30000.00")

    def test_mixed_use_1_2x(self, svc):
        # base_value = 1 000 × 100 × 1.2 = 120 000
        assert svc.calculate_market_value(_base_data(property_type="mixed_use")) == Decimal("120000.00")


# ---------------------------------------------------------------------------
# Municipality base rates and fallback
# ---------------------------------------------------------------------------

class TestMunicipalityRates:
    def test_addis_ababa_tier1_1000_per_sqm(self, svc):
        assert svc.calculate_market_value(_base_data(municipality="Addis Ababa")) == Decimal("100000.00")

    def test_dire_dawa_tier1_800_per_sqm(self, svc):
        # base_value = 800 × 100 × 1.0 = 80 000
        assert svc.calculate_market_value(_base_data(municipality="Dire Dawa")) == Decimal("80000.00")

    def test_hawassa_tier2_450_per_sqm(self, svc):
        # base_value = 450 × 100 × 1.0 = 45 000
        assert svc.calculate_market_value(_base_data(municipality="Hawassa")) == Decimal("45000.00")

    def test_debre_birhan_tier3_250_per_sqm(self, svc):
        # base_value = 250 × 100 × 1.0 = 25 000
        assert svc.calculate_market_value(_base_data(municipality="Debre Birhan")) == Decimal("25000.00")

    def test_unknown_city_uses_fallback_220_per_sqm(self, svc):
        # Fallback rate = 220 → base_value = 22 000
        assert svc.calculate_market_value(_base_data(municipality="Unknown City")) == Decimal("22000.00")


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class TestValidationErrors:
    def test_missing_municipality_raises(self, svc):
        data = _base_data()
        del data["municipality"]
        with pytest.raises(PropertyValidationError, match="municipality"):
            svc.calculate_market_value(data)

    def test_missing_area_sqm_raises(self, svc):
        data = _base_data()
        del data["area_sqm"]
        with pytest.raises(PropertyValidationError, match="area_sqm"):
            svc.calculate_market_value(data)

    def test_zero_area_raises(self, svc):
        with pytest.raises(PropertyValidationError, match="greater than 0"):
            svc.calculate_market_value(_base_data(area_sqm=0))

    def test_excessive_area_raises(self, svc):
        with pytest.raises(PropertyValidationError, match="maximum"):
            svc.calculate_market_value(_base_data(area_sqm=200_001))

    def test_non_numeric_area_raises(self, svc):
        with pytest.raises(PropertyValidationError, match="Invalid area"):
            svc.calculate_market_value(_base_data(area_sqm="huge"))

    def test_open_coordinates_raises(self, svc):
        # First != last  →  validate_polygon returns False
        open_poly = [
            [38.7578, 9.0320], [38.7580, 9.0320],
            [38.7580, 9.0318], [38.7578, 9.0318],
        ]
        with pytest.raises(PropertyValidationError):
            svc.calculate_market_value(_base_data(coordinates=open_poly))

    def test_non_ethiopian_coordinates_raises(self, svc):
        outside = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]
        with pytest.raises(PropertyValidationError, match="Ethiopia"):
            svc.calculate_market_value(_base_data(coordinates=outside))


# ---------------------------------------------------------------------------
# get_valuation_breakdown
# ---------------------------------------------------------------------------

class TestValuationBreakdown:
    _REQUIRED_KEYS = (
        "municipality", "area_sqm", "property_type", "condition",
        "neighborhood_quality", "construction_year",
        "base_rate_per_sqm", "is_fallback_rate",
        "type_multiplier", "condition_factor", "neighborhood_multiplier",
        "depreciation_rate",
        "land_value", "structure_value_before_depreciation",
        "structure_value_after_depreciation",
        "subtotal", "market_value", "taxable_value",
        "proclamation_reference",
    )

    def test_contains_all_required_fields(self, svc):
        bd = svc.get_valuation_breakdown(_base_data())
        for key in self._REQUIRED_KEYS:
            assert key in bd, f"Missing key in breakdown: {key}"

    def test_is_fallback_rate_false_for_known_city(self, svc):
        bd = svc.get_valuation_breakdown(_base_data(municipality="Addis Ababa"))
        assert bd["is_fallback_rate"] is False

    def test_is_fallback_rate_true_for_unknown_city(self, svc):
        bd = svc.get_valuation_breakdown(_base_data(municipality="Unknown City"))
        assert bd["is_fallback_rate"] is True
        assert bd["base_rate_per_sqm"] == 220.0

    def test_market_value_matches_calculate(self, svc):
        data = _base_data()
        bd = svc.get_valuation_breakdown(data)
        direct = svc.calculate_market_value(data)
        assert Decimal(str(bd["market_value"])) == direct

    def test_taxable_value_is_25_percent_of_market_value(self, svc):
        bd = svc.get_valuation_breakdown(_base_data())
        assert pytest.approx(bd["taxable_value"], rel=1e-6) == bd["market_value"] * 0.25

    def test_land_plus_structure_equals_subtotal(self, svc):
        bd = svc.get_valuation_breakdown(_base_data())
        assert pytest.approx(
            bd["land_value"] + bd["structure_value_after_depreciation"], rel=1e-6
        ) == bd["subtotal"]

    def test_proclamation_reference_mentions_1365(self, svc):
        bd = svc.get_valuation_breakdown(_base_data())
        assert "1365/2025" in bd["proclamation_reference"]
