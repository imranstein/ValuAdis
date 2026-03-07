"""
VA-109: External API Integration Tests

Tests that call API endpoints as an external client would.
Uses TestClient with in-memory SQLite for isolation.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test public health endpoints"""

    def test_health_ping(self, client: TestClient):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data or "pong" in str(data).lower()

    def test_api_health_ping(self, client: TestClient):
        r = client.get("/api/v1/health/ping")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "pong" or "pong" in str(data).lower()


class TestAuthAPI:
    """Test auth endpoints"""

    def test_register_success(self, client: TestClient, test_user_data):
        r = client.post("/api/v1/auth/register", json=test_user_data)
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data.get("token_type") == "bearer"

    def test_login_success(self, client: TestClient, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        r = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_invalid_credentials(self, client: TestClient):
        r = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrong"
        })
        assert r.status_code in (401, 422)


class TestPropertiesAPI:
    """Test properties API with auth"""

    def test_get_properties_requires_auth(self, client: TestClient):
        r = client.get("/api/v1/properties")
        assert r.status_code == 401

    def test_create_property_with_auth(self, client: TestClient, test_user_data, test_property_data):
        reg = client.post("/api/v1/auth/register", json=test_user_data)
        token = reg.json().get("access_token")
        r = client.post(
            "/api/v1/properties",
            json=test_property_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 201
        assert r.json().get("success") is True


class TestValuationsAPI:
    """Test valuations API"""

    def test_get_valuations_requires_auth(self, client: TestClient):
        r = client.get("/api/v1/valuations")
        assert r.status_code == 401

    def test_export_valuations_requires_auth(self, client: TestClient):
        r = client.get("/api/v1/valuations/export?format=csv")
        assert r.status_code == 401


class TestAuditAPI:
    """Test audit/report endpoints"""

    def test_audit_logs_requires_auth(self, client: TestClient):
        r = client.get("/api/v1/audit/logs")
        assert r.status_code == 401

    def test_audit_report_requires_auth(self, client: TestClient):
        r = client.get("/api/v1/audit/report/summary")
        assert r.status_code == 401
