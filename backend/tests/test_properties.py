"""
Property Tests

Test property CRUD operations and spatial functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.property.services import PropertyService
from app.services.spatial_service import SpatialService

# Polygon whose spatial-service area is nowhere near the explicit area_sqm
# values used below, so any test asserting an exact area proves whichever
# value (explicit vs. polygon-derived) actually won.
_POLYGON = [
    [38.7578, 9.0320],
    [38.7580, 9.0320],
    [38.7580, 9.0318],
    [38.7578, 9.0318],
    [38.7578, 9.0320],
]


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

    def test_create_property_preserves_explicit_area_sqm(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """area_sqm entered by the user must survive create, not be
        silently overwritten by the polygon-derived area (regression:
        wrong areas were flowing into legal contract PDFs)."""
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {**test_property_data, "area_sqm": 987.5}
        response = client.post("/api/v1/properties", json=payload, headers=headers)

        assert response.status_code == 201
        assert response.json()["data"]["area_sqm"] == 987.5

    def test_update_property_preserves_explicit_area_sqm_with_new_coordinates(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Updating the boundary alongside an explicit area_sqm must keep
        the explicit value, not overwrite it with the recalculated one."""
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        property_id = create_response.json()["data"]["id"]

        update_data = {
            "area_sqm": 654.0,
            "coordinates": _POLYGON,
        }
        response = client.put(f"/api/v1/properties/{property_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["area_sqm"] == 654.0

    def test_update_property_recalculates_area_when_area_sqm_omitted(
        self, client: TestClient, test_user_data, test_property_data
    ):
        """Updating only the boundary (no area_sqm supplied) still falls
        back to the polygon-derived area."""
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        access_token = _access_token(register_response)
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = client.post("/api/v1/properties", json=test_property_data, headers=headers)
        property_id = create_response.json()["data"]["id"]
        # test_property_data sets an explicit area_sqm (120.0) unrelated to
        # what _POLYGON actually measures, so a match against the computed
        # value proves the fallback recalculation ran.
        expected_area = SpatialService().calculate_area(_POLYGON)

        update_data = {"coordinates": _POLYGON}
        response = client.put(f"/api/v1/properties/{property_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["area_sqm"] == expected_area


class TestPropertyServiceAreaFallback:
    """Service-level coverage for the area_sqm fallback that bulk-import
    and other non-schema-validated callers can exercise (PropertyCreate
    requires area_sqm, but PropertyService.create_property does not)."""

    @pytest.mark.asyncio
    async def test_create_property_falls_back_to_polygon_area_when_missing(self, db_session):
        service = PropertyService(db_session)
        property_data = {
            "address": "No Explicit Area, Addis Ababa",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "coordinates": _POLYGON,
        }

        created = await service.create_property(property_data, user_id=1)

        expected_area = service.spatial_service.calculate_area(_POLYGON)
        assert created.area_sqm == expected_area

    @pytest.mark.asyncio
    async def test_create_property_falls_back_to_polygon_area_when_zero(self, db_session):
        service = PropertyService(db_session)
        property_data = {
            "address": "Zero Area, Addis Ababa",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "area_sqm": 0,
            "coordinates": _POLYGON,
        }

        created = await service.create_property(property_data, user_id=1)

        expected_area = service.spatial_service.calculate_area(_POLYGON)
        assert created.area_sqm == expected_area
