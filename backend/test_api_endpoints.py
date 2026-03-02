"""
API Endpoint Testing Script

Test ValuAdis API endpoints without database dependencies
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_health_endpoints():
    """Test health check endpoints"""
    print("🏥 Testing Health Endpoints")
    
    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Root endpoint: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test health endpoint
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health endpoint: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test ping endpoint
    response = requests.get(f"{BASE_URL}/api/v1/health/ping")
    print(f"✅ Ping endpoint: {response.status_code}")
    print(f"   Response: {response.json()}")


def test_swagger_ui():
    """Test Swagger UI accessibility"""
    print("\n📚 Testing Swagger UI")
    
    # Test docs endpoint
    response = requests.get(f"{BASE_URL}/docs")
    print(f"✅ Swagger UI: {response.status_code}")
    
    # Test OpenAPI spec
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"✅ OpenAPI spec: {response.status_code}")
    if response.status_code == 200:
        spec = response.json()
        print(f"   API Title: {spec.get('info', {}).get('title')}")
        print(f"   Version: {spec.get('info', {}).get('version')}")
        print(f"   Tags: {[tag['name'] for tag in spec.get('tags', [])]}")


def test_valuation_calculation_preview():
    """Test valuation calculation preview endpoint (no auth required)"""
    print("\n💰 Testing Valuation Calculation Preview")
    
    valuation_data = {
        "property_id": 1,
        "property_type": "residential",
        "municipality": "Addis Ababa",
        "area_sqm": 120.0,
        "coordinates": "SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/valuations/calculate",
            json=valuation_data,
            headers={"accept": "application/json"}
        )
        print(f"✅ Valuation calculation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Market Value: {result.get('market_value')}")
            print(f"   Taxable Value: {result.get('taxable_value')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error testing valuation: {e}")


def test_api_structure():
    """Test API structure and endpoints"""
    print("\n🔍 Testing API Structure")
    
    # Test OpenAPI spec for endpoint analysis
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        spec = response.json()
        
        # List all endpoints
        paths = spec.get('paths', {})
        print(f"✅ Total endpoints: {len(paths)}")
        
        for path, methods in paths.items():
            for method, details in methods.items():
                tags = details.get('tags', [])
                operation_id = details.get('operationId', 'N/A')
                print(f"   {method.upper()} {path} -> {tags} ({operation_id})")
    
    print(f"\n📊 API Summary:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print(f"   OpenAPI Spec: {BASE_URL}/openapi.json")


def main():
    """Run all API tests"""
    print("🚀 Starting ValuAdis API Testing")
    print("=" * 50)
    
    try:
        test_health_endpoints()
        test_swagger_ui()
        test_valuation_calculation_preview()
        test_api_structure()
        
        print("\n🎉 API Testing Complete!")
        print("📝 Note: Database-dependent endpoints require PostgreSQL + PostGIS setup")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
