"""
Vehicle Endpoint Contract Tests

Behavioral regression tests for the /api/v1/vehicles surface. Written before
the vehicle stack consolidation into app/modules/vehicle so the module-owned
routes must keep the exact flat-endpoint contract.
"""

from app.core.security import get_current_user_id

VEHICLE_PAYLOAD = {
    "make": "Toyota",
    "model": "Corolla",
    "year": 2020,
    "vin": "JH4KA8260MC000000",
    "plate_number": "AA-12345",
    "fuel_type": "gasoline",
    "body_type": "sedan",
    "engine_capacity": 1800,
    "mileage": 40000,
    "previous_owners": 1,
    "custom_duty_paid": True,
    "region": "Addis Ababa",
}


def _auth(client, user_id=1):
    client.app.dependency_overrides[get_current_user_id] = lambda: user_id


def _create_vehicle(client, **overrides):
    payload = {**VEHICLE_PAYLOAD, **overrides}
    return client.post("/api/v1/vehicles/", json=payload)


def test_create_vehicle_returns_contract_shape(client):
    _auth(client)

    response = _create_vehicle(client)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] > 0
    assert body["user_id"] == 1
    assert body["make"] == "Toyota"
    assert body["vin"] == "JH4KA8260MC000000"


def test_create_vehicle_rejects_duplicate_vin(client):
    _auth(client)
    _create_vehicle(client)

    response = _create_vehicle(client, plate_number="AA-99999")

    assert response.status_code == 400
    assert "VIN" in response.json()["detail"]


def test_create_vehicle_rejects_duplicate_plate(client):
    _auth(client)
    _create_vehicle(client)

    response = _create_vehicle(client, vin="JH4KA8260MC000001")

    assert response.status_code == 400
    assert "plate" in response.json()["detail"].lower()


def test_list_vehicles_returns_user_vehicles(client):
    _auth(client)
    _create_vehicle(client)

    response = client.get("/api/v1/vehicles/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_vehicles_filters_by_make(client):
    _auth(client)
    _create_vehicle(client)

    response = client.get("/api/v1/vehicles/?make=Nissan")

    assert response.status_code == 200
    assert response.json() == []


def test_get_vehicle_by_id(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]

    response = client.get(f"/api/v1/vehicles/{vehicle_id}")

    assert response.status_code == 200
    assert response.json()["id"] == vehicle_id


def test_get_unknown_vehicle_returns_404(client):
    _auth(client)

    response = client.get("/api/v1/vehicles/9999")

    assert response.status_code == 404


def test_update_vehicle_changes_fields(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]

    response = client.put(
        f"/api/v1/vehicles/{vehicle_id}", json={"color": "Silver"}
    )

    assert response.status_code == 200
    assert response.json()["color"] == "Silver"


def test_delete_vehicle_returns_message_then_404(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]

    delete_response = client.delete(f"/api/v1/vehicles/{vehicle_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Vehicle deleted successfully"}
    assert client.get(f"/api/v1/vehicles/{vehicle_id}").status_code == 404


def test_create_valuation_calculates_ethiopian_taxable_value(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]

    response = client.post(f"/api/v1/vehicles/{vehicle_id}/valuation")

    assert response.status_code == 200
    body = response.json()
    assert body["vehicle_id"] == vehicle_id
    assert body["taxable_value"] == round(body["market_value"] * 0.25, 2)


def test_list_vehicle_valuations(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]
    client.post(f"/api/v1/vehicles/{vehicle_id}/valuation")

    response = client.get(f"/api/v1/vehicles/{vehicle_id}/valuations")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_latest_valuation_returns_most_recent(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]
    client.post(f"/api/v1/vehicles/{vehicle_id}/valuation")

    response = client.get(f"/api/v1/vehicles/{vehicle_id}/latest-valuation")

    assert response.status_code == 200
    assert response.json()["vehicle_id"] == vehicle_id


def test_latest_valuation_without_valuations_returns_404(client):
    _auth(client)
    vehicle_id = _create_vehicle(client).json()["id"]

    response = client.get(f"/api/v1/vehicles/{vehicle_id}/latest-valuation")

    assert response.status_code == 404


def test_statistics_summary_counts_created_vehicles(client):
    _auth(client)
    _create_vehicle(client)

    response = client.get("/api/v1/vehicles/statistics/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_vehicles"] == 1
    assert body["make_breakdown"] == {"Toyota": 1}
