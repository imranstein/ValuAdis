"""
Public endpoint rate limits — integration (Phase D hardening).

Confirms the search and signup endpoints actually return 429 once their
budget is exhausted, using monkeypatched (small) limits so the test does
not need 60+ real requests to prove the wiring.
"""

import app.modules.rentals.routes as rentals_routes


def test_search_endpoint_returns_429_once_exhausted(client, monkeypatch):
    monkeypatch.setattr(rentals_routes, "SEARCH_RATE_LIMIT_MAX_REQUESTS", 2)
    for _ in range(2):
        response = client.get("/api/v1/rentals/listings")
        assert response.status_code == 200
    blocked = client.get("/api/v1/rentals/listings")
    assert blocked.status_code == 429


def test_signup_endpoint_returns_429_once_exhausted(client, monkeypatch):
    monkeypatch.setattr(rentals_routes, "SIGNUP_RATE_LIMIT_MAX_REQUESTS", 2)
    base_payload = {
        "full_name": "Test Citizen",
        "password": "Citizenpass1!",
        "municipality": "Addis Ababa",
        "account_type": "renter",
    }
    for i in range(2):
        response = client.post(
            "/api/v1/rentals/signup",
            json={
                **base_payload,
                "email": f"citizen{i}@example.com",
                "phone": f"+25191100000{i}",
                "fayda_id_number": f"90000000000{i}",
            },
        )
        assert response.status_code == 201, response.text
    blocked = client.post(
        "/api/v1/rentals/signup",
        json={
            **base_payload,
            "email": "citizen-blocked@example.com",
            "phone": "+251911000099",
            "fayda_id_number": "900000000099",
        },
    )
    assert blocked.status_code == 429
