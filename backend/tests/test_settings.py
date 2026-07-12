"""
Settings + API Key Endpoint Tests

Covers the /api/v1/settings module: user preference read/upsert with sensible
defaults, and API-key lifecycle where the plaintext key is returned exactly
once and never exposed again. Every query is owner-scoped by the caller.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient, test_user_data) -> dict:
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(client: TestClient) -> dict:
    other_user = {
        "email": "other@example.com",
        "full_name": "Other User",
        "phone": "+251922334455",
        "password": "Otherpassword123!",
        "municipality": "Addis Ababa",
        "license_number": "VAL-2023-002",
    }
    response = client.post("/api/v1/auth/register", json=other_user)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestPreferences:
    def test_get_requires_auth(self, client):
        response = client.get("/api/v1/settings")
        assert response.status_code == 401

    def test_get_returns_defaults_when_none_saved(self, client, auth_headers):
        response = client.get("/api/v1/settings", headers=auth_headers)
        assert response.status_code == 200
        prefs = response.json()["preferences"]
        assert prefs["email_notifications"] is True

    def test_put_requires_auth(self, client):
        response = client.put("/api/v1/settings", json={"preferences": {}})
        assert response.status_code == 401

    def test_put_persists_and_round_trips(self, client, auth_headers):
        new_prefs = {"email_notifications": False, "language": "am"}
        put_response = client.put(
            "/api/v1/settings",
            json={"preferences": new_prefs},
            headers=auth_headers,
        )
        assert put_response.status_code == 200

        get_response = client.get("/api/v1/settings", headers=auth_headers)
        stored = get_response.json()["preferences"]
        assert stored["email_notifications"] is False
        assert stored["language"] == "am"

    def test_preferences_are_owner_scoped(
        self, client, auth_headers, other_auth_headers
    ):
        client.put(
            "/api/v1/settings",
            json={"preferences": {"language": "am"}},
            headers=auth_headers,
        )
        other_response = client.get("/api/v1/settings", headers=other_auth_headers)
        assert other_response.json()["preferences"]["language"] == "en"


class TestApiKeys:
    def test_create_requires_auth(self, client):
        response = client.post("/api/v1/settings/api-keys", json={"name": "ci"})
        assert response.status_code == 401

    def test_create_returns_plaintext_key_once(self, client, auth_headers):
        response = client.post(
            "/api/v1/settings/api-keys",
            json={"name": "ci-key"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["key"]
        assert len(body["key"]) > 20
        assert body["name"] == "ci-key"
        assert body["revoked"] is False

    def test_list_never_exposes_secret(self, client, auth_headers):
        create = client.post(
            "/api/v1/settings/api-keys",
            json={"name": "ci-key"},
            headers=auth_headers,
        )
        plaintext = create.json()["key"]

        list_response = client.get("/api/v1/settings/api-keys", headers=auth_headers)
        assert list_response.status_code == 200
        items = list_response.json()
        assert len(items) == 1
        item = items[0]
        assert "key" not in item
        assert "key_hash" not in item
        assert plaintext not in str(item)
        assert item["key_prefix"]

    def test_list_is_owner_scoped(self, client, auth_headers, other_auth_headers):
        client.post(
            "/api/v1/settings/api-keys",
            json={"name": "mine"},
            headers=auth_headers,
        )
        other_list = client.get("/api/v1/settings/api-keys", headers=other_auth_headers)
        assert other_list.json() == []

    def test_revoke_sets_revoked_true(self, client, auth_headers):
        create = client.post(
            "/api/v1/settings/api-keys",
            json={"name": "ci-key"},
            headers=auth_headers,
        )
        key_id = create.json()["id"]

        delete_response = client.delete(
            f"/api/v1/settings/api-keys/{key_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

        listed = client.get("/api/v1/settings/api-keys", headers=auth_headers).json()
        assert listed[0]["revoked"] is True

    def test_revoke_other_users_key_returns_404(
        self, client, auth_headers, other_auth_headers
    ):
        create = client.post(
            "/api/v1/settings/api-keys",
            json={"name": "ci-key"},
            headers=auth_headers,
        )
        key_id = create.json()["id"]

        response = client.delete(
            f"/api/v1/settings/api-keys/{key_id}", headers=other_auth_headers
        )
        assert response.status_code == 404
