"""
Authentication Tests

Test authentication endpoints and JWT token management
"""

import pytest
from jose import jwt
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_register_user_success(self, client: TestClient, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user_data):
        """Test registration with duplicate email fails"""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "already registered" in data["message"].lower()
    
    def test_register_user_invalid_phone(self, client: TestClient, test_user_data):
        """Test registration with invalid phone number fails"""
        test_user_data["phone"] = "1234567890"  # Invalid Ethiopian phone
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client: TestClient, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
    
    def test_login_invalid_credentials(self, client: TestClient, test_user_data):
        """Test login with invalid credentials fails"""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "invalid" in data["message"].lower()
    
    def test_refresh_token_success(self, client: TestClient, test_user_data):
        """Test token refresh works"""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Refresh token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = client.post("/api/v1/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
    
    def test_get_current_user(self, client: TestClient, test_user_data):
        """Test getting current user info"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = register_response.json()["data"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
    
    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token fails"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401

    def test_refresh_token_rejected_on_protected_endpoint(self, client: TestClient, test_user_data):
        """Test refresh token cannot access access-token-only endpoints"""
        client.post("/api/v1/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["data"]["refresh_token"]

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})

        assert response.status_code == 401

    def test_access_token_can_only_be_expired_token(self, client: TestClient, test_user_data):
        """Expired access tokens are rejected by protected routes"""
        client.post("/api/v1/auth/register", json=test_user_data)

        expired_token = jwt.encode(
            {
                "sub": "1",
                "type": "access",
                "exp": 0,
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

        assert response.status_code == 401

    def test_admin_routes_block_regular_users(self, client: TestClient, db_session, test_user_data):
        """Admin-only routes reject non-admin tokens"""
        client.post("/api/v1/auth/register", json=test_user_data)

        # Promote route should remain inaccessible for non-admin users
        # without extra roles or admin flag.
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


REFRESH_COOKIE_NAME = "valuadis_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"


def _register_and_login(client: TestClient, test_user_data) -> dict:
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    return response


def _get_refresh_set_cookie(response) -> str:
    cookies = [
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith(f"{REFRESH_COOKIE_NAME}=")
    ]
    assert cookies, f"No {REFRESH_COOKIE_NAME} Set-Cookie header in response"
    return cookies[0]


class TestRefreshCookieSession:
    """httpOnly refresh cookie: set on login, rotated on refresh, cleared on logout"""

    def test_login_sets_httponly_refresh_cookie(self, client: TestClient, test_user_data):
        """Login sets valuadis_refresh as httpOnly SameSite=Lax cookie scoped to refresh path"""
        response = _register_and_login(client, test_user_data)

        set_cookie = _get_refresh_set_cookie(response).lower()
        assert "httponly" in set_cookie
        assert "samesite=lax" in set_cookie
        assert f"path={REFRESH_COOKIE_PATH}" in set_cookie

    def test_login_cookie_value_matches_refresh_token(self, client: TestClient, test_user_data):
        """Cookie carries the same refresh token as the JSON body"""
        response = _register_and_login(client, test_user_data)

        cookie_value = client.cookies.get(REFRESH_COOKIE_NAME)
        assert cookie_value == response.json()["data"]["refresh_token"]

    def test_login_response_body_unchanged(self, client: TestClient, test_user_data):
        """Mobile contract: login body keeps exactly the existing token fields"""
        response = _register_and_login(client, test_user_data)

        data = response.json()["data"]
        assert set(data.keys()) == {"access_token", "refresh_token", "token_type", "expires_in"}

    def test_refresh_via_cookie_returns_new_access_token(self, client: TestClient, test_user_data):
        """Refresh works with only the httpOnly cookie (no Authorization header)"""
        _register_and_login(client, test_user_data)

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["access_token"]

    def test_refresh_via_cookie_rotates_cookie(self, client: TestClient, test_user_data):
        """Refresh sets a new valuadis_refresh cookie different from the old one"""
        login_response = _register_and_login(client, test_user_data)
        old_cookie = login_response.json()["data"]["refresh_token"]

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        new_cookie_header = _get_refresh_set_cookie(response)
        new_cookie = new_cookie_header.split(";")[0].split("=", 1)[1]
        assert new_cookie != old_cookie

    def test_refresh_without_cookie_or_header_fails(self, client: TestClient):
        """Refresh with neither cookie nor bearer token is rejected"""
        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    def test_refresh_with_invalid_cookie_fails(self, client: TestClient):
        """Garbage cookie value is rejected"""
        client.cookies.set(REFRESH_COOKIE_NAME, "not-a-jwt", path=REFRESH_COOKIE_PATH)

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    def test_refresh_cookie_rejects_access_token(self, client: TestClient, test_user_data):
        """An access token smuggled into the refresh cookie is rejected"""
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = register_response.json()["data"]["access_token"]
        client.cookies.set(REFRESH_COOKIE_NAME, access_token, path=REFRESH_COOKIE_PATH)

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    def test_refresh_bearer_header_still_works_without_cookie(self, client: TestClient, test_user_data):
        """Mobile contract: body-less bearer refresh keeps working with no cookie"""
        login_response = _register_and_login(client, test_user_data)
        refresh_token = login_response.json()["data"]["refresh_token"]
        client.cookies.clear()

        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 200

    def test_logout_clears_refresh_cookie(self, client: TestClient, test_user_data):
        """Logout expires the valuadis_refresh cookie"""
        _register_and_login(client, test_user_data)

        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        set_cookie = _get_refresh_set_cookie(response).lower()
        assert 'max-age=0' in set_cookie or "expires=" in set_cookie

    def test_refresh_after_logout_fails_without_header(self, client: TestClient, test_user_data):
        """After logout the cookie is gone, so cookie-only refresh fails"""
        _register_and_login(client, test_user_data)
        client.post("/api/v1/auth/logout")

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
