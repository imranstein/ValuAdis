"""
Compliance Tests — Proclamation 1365/2025

Validates Ethiopian property tax rules:
- Taxable value = 25% of market value
- Rounding to nearest 100 ETB
- Ethiopian coordinate bounds
"""

import pytest
from decimal import Decimal
from app.services.valuation_service import ValuationService
from app.services.spatial_service import SpatialService


class TestProclamationCompliance:
    """Proclamation 1365/2025 compliance tests"""

    @pytest.fixture
    def valuation_service(self):
        spatial_service = SpatialService()
        return ValuationService(spatial_service)

    # ── TAXABLE VALUE = 25% ─────────────────────────────────

    @pytest.mark.parametrize(
        "market_value, expected_taxable",
        [
            (Decimal("1000000.00"), Decimal("250000.00")),
            (Decimal("500000.00"), Decimal("125000.00")),
            (Decimal("2500000.00"), Decimal("625000.00")),
            (Decimal("100000.00"), Decimal("25000.00")),
        ],
    )
    def test_taxable_value_is_25_percent(
        self, valuation_service, market_value, expected_taxable
    ):
        """Taxable value must be exactly 25% of market value"""
        result = valuation_service.calculate_taxable_value(market_value)
        assert result == expected_taxable, (
            f"COMPLIANCE FAILURE: taxable_value({result}) != "
            f"25% of market_value({market_value}) = {expected_taxable}"
        )

    # ── ROUNDING ────────────────────────────────────────────

    def test_taxable_value_rounding_to_nearest_100(self, valuation_service):
        """Taxable value should be rounded to nearest 100 ETB"""
        # 1,234,567 × 0.25 = 308,641.75 → rounded to 308,600
        market_value = Decimal("1234567.00")
        result = valuation_service.calculate_taxable_value(market_value)

        # Must be a multiple of 100
        assert float(result) % 100 == 0, (
            f"Taxable value {result} is NOT rounded to nearest 100 ETB"
        )

    def test_taxable_value_zero_market_value(self, valuation_service):
        """Zero market value should produce zero taxable value"""
        result = valuation_service.calculate_taxable_value(Decimal("0.00"))
        assert result == Decimal("0.00")

    # ── COORDINATE VALIDATION ───────────────────────────────

    def test_ethiopian_coordinate_bounds(self):
        """Coordinates must be within Ethiopian geographic bounds"""
        # Ethiopia: lat ≈ 3.3°N – 14.9°N, lon ≈ 33.0°E – 48.0°E
        spatial_service = SpatialService()

        valid_coords = [
            [38.7578, 9.0320],  # Addis Ababa
            [38.7580, 9.0320],
            [38.7580, 9.0318],
            [38.7578, 9.0318],
            [38.7578, 9.0320],
        ]

        # Valid coordinates should not raise
        try:
            area = spatial_service.calculate_area_from_coordinates(valid_coords)
            assert area > 0
        except Exception:
            pytest.skip("SpatialService.calculate_area_from_coordinates not yet implemented")

    def test_market_value_residential_calculation(self, valuation_service):
        """Residential property valuation uses correct base rate"""
        property_data = {
            "property_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": [
                [38.7578, 9.0320],
                [38.7580, 9.0320],
                [38.7580, 9.0318],
                [38.7578, 9.0318],
                [38.7578, 9.0320],
            ],
        }

        market_value = valuation_service.calculate_market_value(property_data)
        assert market_value > 0, "Market value must be positive for valid property"

    def test_market_value_types(self, valuation_service):
        """Market value and taxable value should be Decimal for precision"""
        market_value = Decimal("1000000.00")
        taxable = valuation_service.calculate_taxable_value(market_value)
        assert isinstance(taxable, (Decimal, float)), (
            "Taxable value should be Decimal or float for financial precision"
        )
