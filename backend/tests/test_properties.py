"""
Property Tests

Test property CRUD operations and spatial functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def _access_token(response):
    body = response.json()
    return body.get("access_token") or body["data"]["access_token"]


class TestProperties:
    """Test property CRUD operations"""
    
    def test_create_property_success(self, client: TestClient, test_user_data, test_property_data):
        """Test successful property creation"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Create property
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["address"] == test_property_data["address"]
        assert data["data"]["area_sqm"] > 0

    def test_bulk_import_properties_success(self, client: TestClient, test_user_data):
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        headers = {"Authorization": f"Bearer {access_token}"}
        csv_body = (
            "address,municipality,property_type,latitude,longitude,area_sqm,market_value,taxable_value\n"
            "Bole Atlas,Addis Ababa,residential,9.0320,38.7578,120,1000000,250000\n"
        )

        response = client.post(
            "/api/v1/properties/bulk-import",
            headers=headers,
            files={"file": ("properties.csv", csv_body, "text/csv")},
        )

        assert response.status_code == 200
        assert response.json()["imported_count"] == 1

    def test_bulk_import_properties_rejects_invalid_taxable_value(self, client: TestClient, test_user_data):
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        headers = {"Authorization": f"Bearer {access_token}"}
        csv_body = (
            "address,municipality,property_type,latitude,longitude,area_sqm,market_value,taxable_value\n"
            "Kazanchis Tower,Addis Ababa,commercial,9.0320,38.7578,120,1000000,300000\n"
        )

        response = client.post(
            "/api/v1/properties/bulk-import",
            headers=headers,
            files={"file": ("properties.csv", csv_body, "text/csv")},
        )

        assert response.status_code == 422
        assert "25%" in response.json()["detail"][0]["message"]
    
    def test_create_property_invalid_coordinates(self, client: TestClient, test_user_data):
        """Test property creation with invalid coordinates fails"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Invalid coordinates (not closed polygon)
        invalid_property_data = {
            "address": "Invalid Address",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "area_sqm": 120.0,
            "coordinates": [
                [38.7578, 9.0320],
                [38.7580, 9.0320],
                [38.7580, 9.0318]
                # Missing closing point
            ]
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/properties", json=invalid_property_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "polygon" in data["detail"].lower()
    
    def test_get_properties(self, client: TestClient, test_user_data, test_property_data):
        """Test getting user's properties"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Create property
        headers = {"Authorization": f"Bearer {access_token}"}
        client.post("/api/v1/properties", json=test_property_data, headers=headers)
        
        # Get properties
        response = client.get("/api/v1/properties", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["total"] == 1
    
    def test_get_property_by_id(self, client: TestClient, test_user_data, test_property_data):
        """Test getting specific property by ID"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Create property
        headers = {"Authorization": f"Bearer {access_token}"}
        create_response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        property_id = create_response.json()["data"]["id"]
        
        # Get property
        response = client.get(f"/api/v1/properties/{property_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == property_id
    
    def test_get_property_unauthorized(self, client: TestClient, test_user_data, test_property_data):
        """Test getting property without authentication fails"""
        response = client.get("/api/v1/properties/1")
        
        assert response.status_code == 401
    
    def test_update_property(self, client: TestClient, test_user_data, test_property_data):
        """Test updating property"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Create property
        headers = {"Authorization": f"Bearer {access_token}"}
        create_response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        property_id = create_response.json()["data"]["id"]
        
        # Update property
        update_data = {
            "address": "Updated Address",
            "market_value": 1000000.0
        }
        response = client.put(f"/api/v1/properties/{property_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["address"] == "Updated Address"
        assert data["data"]["market_value"] == 1000000.0
    
    def test_delete_property(self, client: TestClient, test_user_data, test_property_data):
        """Test deleting property"""
        # Register and login
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        
        # Create property
        headers = {"Authorization": f"Bearer {access_token}"}
        create_response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        property_id = create_response.json()["data"]["id"]
        
        # Delete property
        response = client.delete(f"/api/v1/properties/{property_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify property is deleted
        get_response = client.get(f"/api/v1/properties/{property_id}", headers=headers)
        assert get_response.status_code == 404
