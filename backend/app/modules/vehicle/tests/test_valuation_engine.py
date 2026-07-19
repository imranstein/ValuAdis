"""
Vehicle Valuation Engine Tests

Unit tests for the Ethiopian-market valuation engine owned by the vehicle
module (consolidated from the legacy app/services/vehicle_valuation_service).
"""

from datetime import datetime

from app.data.models.vehicle import Vehicle
from app.modules.vehicle.services import (
    VehicleValuationService,
    vehicle_valuation_service,
)

CURRENT_YEAR = datetime.now().year


def make_vehicle(**overrides):
    defaults = {
        "id": 1,
        "user_id": 1,
        "make": "Toyota",
        "model": "Corolla",
        "year": CURRENT_YEAR - 3,
        "vin": "JH4KA8260MC000000",
        "plate_number": "AA-12345",
        "mileage": 30000,
        "previous_owners": 1,
        "custom_duty_paid": True,
        "region": "Addis Ababa",
        "is_active": True,
    }
    defaults.update(overrides)
    return Vehicle(**defaults)


def test_singleton_engine_is_exported():
    assert isinstance(vehicle_valuation_service, VehicleValuationService)


def test_taxable_value_is_quarter_of_market_value():
    result = vehicle_valuation_service.calculate_vehicle_valuation(make_vehicle())

    assert result["taxable_value"] == round(result["market_value"] * 0.25, 2)


def test_valuation_result_contains_fields_persisted_by_the_route():
    result = vehicle_valuation_service.calculate_vehicle_valuation(make_vehicle())

    for key in (
        "base_value",
        "market_value",
        "taxable_value",
        "condition_factor",
        "market_position",
        "confidence_score",
        "ethiopian_factors",
        "condition_analysis",
        "recommendations",
    ):
        assert key in result, f"missing valuation key: {key}"
    for factor in (
        "regional_multiplier",
        "import_year_adjustment",
        "customs_duty_factor",
        "make_reliability",
        "fuel_type_adjustment",
        "body_type_demand",
        "total_multiplier",
    ):
        assert factor in result["ethiopian_factors"], f"missing factor: {factor}"
    assert "condition_rating" in result["condition_analysis"]
    assert "age_depreciation" in result["condition_analysis"]


def test_unpaid_customs_duty_applies_penalty_and_recommendation():
    result = vehicle_valuation_service.calculate_vehicle_valuation(
        make_vehicle(custom_duty_paid=False)
    )

    assert result["ethiopian_factors"]["customs_duty_factor"] == 0.8
    assert any("customs" in r.lower() for r in result["recommendations"])


def test_paid_customs_duty_earns_small_premium():
    result = vehicle_valuation_service.calculate_vehicle_valuation(make_vehicle())

    assert result["ethiopian_factors"]["customs_duty_factor"] == 1.05


def test_addis_ababa_region_has_highest_demand_multiplier():
    result = vehicle_valuation_service.calculate_vehicle_valuation(make_vehicle())

    assert result["ethiopian_factors"]["regional_multiplier"] == 1.15


def test_unknown_make_falls_back_to_default_reliability():
    result = vehicle_valuation_service.calculate_vehicle_valuation(
        make_vehicle(make="Zaz")
    )

    assert result["ethiopian_factors"]["make_reliability"] == 0.7


def test_condition_factor_never_drops_below_floor():
    beaten_up = make_vehicle(
        year=CURRENT_YEAR - 20, mileage=900000, previous_owners=9
    )

    result = vehicle_valuation_service.calculate_vehicle_valuation(beaten_up)

    assert result["condition_factor"] >= 0.3


def test_new_low_mileage_single_owner_vehicle_rates_excellent():
    fresh = make_vehicle(year=CURRENT_YEAR - 1, mileage=5000, previous_owners=1)

    result = vehicle_valuation_service.calculate_vehicle_valuation(fresh)

    assert result["condition_analysis"]["condition_rating"] == "excellent"
