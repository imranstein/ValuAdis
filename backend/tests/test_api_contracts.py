"""API contract tests for deterministic QA checks.

These tests lock in behavior required by downstream checks before larger test suites run.
"""

from fastapi.testclient import TestClient


def _is_valid_error_payload(payload: dict) -> bool:
    """Return True when an error response follows expected error contract."""
    if "detail" in payload:
        return isinstance(payload["detail"], (str, list, dict))
    return "message" in payload and isinstance(payload["message"], str)


def test_health_full_contract(client: TestClient):
    response = client.get("/api/v1/health/full")

    assert response.status_code == 200

    payload = response.json()
    assert payload["service"] == "valuadis-api"
    assert payload["status"] in {"healthy", "unhealthy"}
    assert isinstance(payload["checks"], dict)
    assert set(payload["checks"].keys()) >= {"database", "redis"}
    assert payload["checks"]["database"]["status"] in {"healthy", "unhealthy"}
    assert payload["checks"]["redis"]["status"] in {"healthy", "unhealthy"}


def test_auth_me_error_contract_is_machine_readable(client: TestClient):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert _is_valid_error_payload(response.json())


def test_unknown_route_error_contract_is_machine_readable(client: TestClient):
    response = client.get("/api/v1/nonexistent")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert _is_valid_error_payload(response.json())
