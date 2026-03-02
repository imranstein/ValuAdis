"""
Valuations API Tests

Test valuation CRUD endpoints and calculation logic
Following God Mode QA checklist Phase 4
"""

import pytest
from fastapi.testclient import TestClient


class TestValuationsAPI:
    """Test valuation API endpoints"""

    def _register_and_get_token(self, client: TestClient, user_data: dict) -> str:
        """Helper: register user and return access token"""
        response = client.post("/api/v1/auth/register", json=user_data)
        return response.json()["data"]["access_token"]

    def _create_property(self, client: TestClient, headers: dict, property_data: dict) -> int:
        """Helper: create a property and return its ID"""
        response = client.post("/api/v1/properties", json=property_data, headers=headers)
        return response.json()["data"]["id"]

    # ── CREATE ──────────────────────────────────────────────

    def test_create_valuation_success(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Test successful valuation creation via POST /api/v1/valuations"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}
        property_id = self._create_property(client, headers, test_property_data)

        valuation_payload = {
            "property_id": property_id,
            "property_type": test_property_data["property_type"],
            "municipality": test_property_data["municipality"],
            "area_sqm": 150.0,
            "coordinates": test_property_data["coordinates"],
        }

        response = client.post(
            "/api/v1/valuations", json=valuation_payload, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert "market_value" in data["data"]
        assert "taxable_value" in data["data"]

    def test_create_valuation_unauthorized(self, client: TestClient):
        """Test valuation creation without auth returns 401"""
        payload = {
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
        response = client.post("/api/v1/valuations", json=payload)
        assert response.status_code == 401

    # ── READ ────────────────────────────────────────────────

    def test_get_user_valuations(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Test listing valuations via GET /api/v1/valuations"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}
        property_id = self._create_property(client, headers, test_property_data)

        # Create a valuation first
        valuation_payload = {
            "property_id": property_id,
            "property_type": test_property_data["property_type"],
            "municipality": test_property_data["municipality"],
            "area_sqm": 100.0,
            "coordinates": test_property_data["coordinates"],
        }
        client.post("/api/v1/valuations", json=valuation_payload, headers=headers)

        # List valuations
        response = client.get("/api/v1/valuations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    def test_get_valuation_by_id(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Test getting a specific valuation via GET /api/v1/valuations/{id}"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}
        property_id = self._create_property(client, headers, test_property_data)

        valuation_payload = {
            "property_id": property_id,
            "property_type": test_property_data["property_type"],
            "municipality": test_property_data["municipality"],
            "area_sqm": 100.0,
            "coordinates": test_property_data["coordinates"],
        }
        create_resp = client.post(
            "/api/v1/valuations", json=valuation_payload, headers=headers
        )
        valuation_id = create_resp.json()["data"]["id"]

        # GET by ID
        response = client.get(
            f"/api/v1/valuations/{valuation_id}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == valuation_id

    # ── CALCULATE (PREVIEW) ────────────────────────────────

    def test_calculate_valuation_preview(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Test preview calculation via POST /api/v1/valuations/calculate"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        calc_payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 200.0,
            "coordinates": test_property_data["coordinates"],
        }

        response = client.post(
            "/api/v1/valuations/calculate", json=calc_payload, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "market_value" in data["data"]
        assert "taxable_value" in data["data"]

    def test_taxable_value_is_25_percent(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """
        Compliance: taxable_value MUST be exactly 25% of market_value
        Per Proclamation 1365/2025
        """
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        calc_payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": test_property_data["coordinates"],
        }

        response = client.post(
            "/api/v1/valuations/calculate", json=calc_payload, headers=headers
        )

        data = response.json()["data"]
        market_value = float(data["market_value"])
        taxable_value = float(data["taxable_value"])

        # Core compliance assertion
        assert taxable_value == pytest.approx(market_value * 0.25, rel=1e-2), (
            f"Proclamation 1365/2025 VIOLATION: taxable_value ({taxable_value}) "
            f"is not 25% of market_value ({market_value})"
        )

    # ── DELETE ──────────────────────────────────────────────

    def test_delete_valuation(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Test deleting a valuation via DELETE /api/v1/valuations/{id}"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}
        property_id = self._create_property(client, headers, test_property_data)

        valuation_payload = {
            "property_id": property_id,
            "property_type": test_property_data["property_type"],
            "municipality": test_property_data["municipality"],
            "area_sqm": 100.0,
            "coordinates": test_property_data["coordinates"],
        }
        create_resp = client.post(
            "/api/v1/valuations", json=valuation_payload, headers=headers
        )
        valuation_id = create_resp.json()["data"]["id"]

        # Delete
        response = client.delete(
            f"/api/v1/valuations/{valuation_id}", headers=headers
        )
        assert response.status_code == 200

        # Verify deleted
        get_resp = client.get(
            f"/api/v1/valuations/{valuation_id}", headers=headers
        )
        assert get_resp.status_code == 404
