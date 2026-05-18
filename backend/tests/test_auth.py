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
