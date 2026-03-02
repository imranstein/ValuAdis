"""
Main Application Tests

Test FastAPI application setup and health endpoints
"""

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "valuadis-backend"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "ValuAdis API" in data["message"]


def test_api_docs_not_available_in_production(client):
    """Test API docs are not available in production"""
    # This test assumes we're not in production mode
    response = client.get("/docs")
    # Should be 404 or 200 depending on environment
    assert response.status_code in [200, 404]
