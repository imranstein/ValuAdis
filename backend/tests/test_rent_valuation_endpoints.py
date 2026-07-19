"""
Rent Valuation Endpoint Tests

Covers purpose='rent' on POST /api/v1/valuations/quick and
POST /api/v1/valuations/calculate: optional field, default 'sale' unchanged
for existing callers, and rent responses carry suggested_rent/band/
confidence/requires_officer_review.
"""

import pytest
from fastapi.testclient import TestClient


def _register_and_get_token(client: TestClient, user_data: dict) -> str:
    response = client.post("/api/v1/auth/register", json=user_data)
    return response.json()["data"]["access_token"]


class TestQuickValuationPurpose:
    def test_default_purpose_is_sale_and_unaffected(
        self, client: TestClient, test_user_data
    ):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/valuations/quick",
            json={
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "market_value" in data
        # Additive fields must not appear for the default 'sale' purpose
        assert "suggested_rent" not in data
        assert "confidence" not in data

    def test_purpose_rent_returns_suggested_rent_and_band(
        self, client: TestClient, test_user_data
    ):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/valuations/quick",
            json={
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
                "purpose": "rent",
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == "rent"
        assert data["suggested_rent"] > 0
        assert data["band_min"] < data["suggested_rent"] < data["band_max"]
        assert 0 <= data["confidence"] <= 1
        assert data["requires_officer_review"] is True  # no comps in a fresh test DB

    def test_invalid_purpose_rejected(self, client: TestClient, test_user_data):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/valuations/quick",
            json={
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
                "purpose": "lease",
            },
            headers=headers,
        )

        assert response.status_code == 400

    def test_unauthenticated_rent_request_returns_401(self, client: TestClient):
        response = client.post(
            "/api/v1/valuations/quick",
            json={
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
                "purpose": "rent",
            },
        )
        assert response.status_code == 401


class TestCalculateValuationPurpose:
    def test_default_purpose_is_sale_and_unaffected(
        self, client: TestClient, test_user_data, test_property_data
    ):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 150.0,
            "coordinates": test_property_data["coordinates"],
        }

        response = client.post("/api/v1/valuations/calculate", json=payload, headers=headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert "market_value" in data
        assert "suggested_rent" not in data

    def test_purpose_rent_returns_suggested_rent_and_band(
        self, client: TestClient, test_user_data, test_property_data
    ):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 150.0,
            "coordinates": test_property_data["coordinates"],
            "purpose": "rent",
        }

        response = client.post("/api/v1/valuations/calculate", json=payload, headers=headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["purpose"] == "rent"
        assert data["suggested_rent"] > 0
        assert data["band_min"] < data["suggested_rent"] < data["band_max"]

    def test_invalid_purpose_rejected_by_schema_validation(
        self, client: TestClient, test_user_data, test_property_data
    ):
        token = _register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 150.0,
            "coordinates": test_property_data["coordinates"],
            "purpose": "auction",
        }

        response = client.post("/api/v1/valuations/calculate", json=payload, headers=headers)

        assert response.status_code == 422
