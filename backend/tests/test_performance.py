"""
Performance Tests

Verify API response times meet SLA requirements:
- Property list: < 2 seconds
- Valuation calculate: < 2 seconds
- Health check: < 500ms
"""

import pytest
import time
from fastapi.testclient import TestClient


class TestPerformance:
    """API response time tests"""

    def _register_and_get_token(self, client: TestClient, user_data: dict) -> str:
        response = client.post("/api/v1/auth/register", json=user_data)
        return response.json()["data"]["access_token"]

    def test_health_check_response_time(self, client: TestClient):
        """Health endpoint must respond within 500ms"""
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.5, f"Health check took {duration:.3f}s (> 500ms SLA)"

    def test_property_list_response_time(
        self, client: TestClient, test_user_data
    ):
        """Property list API must respond within 2 seconds"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        start = time.time()
        response = client.get("/api/v1/properties", headers=headers)
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0, (
            f"Property list took {duration:.3f}s (> 2.0s SLA)"
        )

    def test_valuation_calculate_response_time(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Valuation calculation must complete within 2 seconds"""
        token = self._register_and_get_token(client, test_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        calc_payload = {
            "property_id": 0,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 200.0,
            "coordinates": test_property_data["coordinates"],
        }

        start = time.time()
        response = client.post(
            "/api/v1/valuations/calculate",
            json=calc_payload,
            headers=headers,
        )
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0, (
            f"Valuation calculation took {duration:.3f}s (> 2.0s SLA)"
        )

    def test_login_response_time(self, client: TestClient, test_user_data):
        """Login API must respond within 2 seconds"""
        # Register first
        client.post("/api/v1/auth/register", json=test_user_data)

        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        start = time.time()
        response = client.post("/api/v1/auth/login", json=login_data)
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0, (
            f"Login took {duration:.3f}s (> 2.0s SLA)"
        )
