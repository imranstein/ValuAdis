"""
Health & Root Endpoint Tests

Test infrastructure health checks (Phase 0 of QA checklist)
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check and root endpoints"""

    def test_root_endpoint(self, client: TestClient):
        """Test GET / returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ValuAdis" in data["message"]

    def test_health_endpoint(self, client: TestClient):
        """Test GET /health returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "valuadis-backend"
        assert "version" in data

    def test_api_health_endpoint(self, client: TestClient):
        """Test GET /api/v1/health returns detailed health info"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_endpoint(self, client: TestClient):
        """Test GET /api/v1/health/ready returns deployment readiness contract"""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "valuadis-api"
        assert data["status"] in {"ready", "not ready"}
        assert data["checks"]["database"]["status"] in {"healthy", "unhealthy"}
        assert data["checks"]["redis"]["status"] in {"healthy", "unhealthy"}

    def test_liveness_endpoint(self, client: TestClient):
        """Test GET /api/v1/health/live returns liveness state"""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "alive", "service": "valuadis-api"}

    def test_docs_endpoint(self, client: TestClient):
        """Test GET /docs returns Swagger UI"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, client: TestClient):
        """Test GET /redoc returns ReDoc UI"""
        response = client.get("/redoc")
        assert response.status_code == 200
