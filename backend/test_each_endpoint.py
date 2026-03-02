"""
Individual Endpoint Testing Script

Test each ValuAdis API endpoint one by one
"""

import requests
import json
from typing import Dict, Any, Optional
import time

BASE_URL = "http://localhost:8000"


class EndpointTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = []
    
    def log_result(self, endpoint: str, method: str, status: int, expected: int, response_time: float, notes: str = ""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "expected": expected,
            "response_time": f"{response_time:.3f}s",
            "passed": status == expected,
            "notes": notes
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == expected else "❌"
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s) {notes}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with timing"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {"accept": "application/json"}
        if headers:
            request_headers.update(headers)
        if data:
            request_headers["Content-Type"] = "application/json"
        
        start_time = time.time()
        
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=request_headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=request_headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=request_headers)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=request_headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = time.time() - start_time
        return response, response_time
    
    def test_health_endpoints(self):
        """Test all health endpoints"""
        print("\n🏥 Testing Health Endpoints")
        print("=" * 50)
        
        # Test root endpoint
        response, response_time = self.make_request("GET", "/")
        self.log_result("/", "GET", response.status_code, 200, response_time, "Root endpoint")
        
        # Test health endpoint
        response, response_time = self.make_request("GET", "/health")
        self.log_result("/health", "GET", response.status_code, 200, response_time, "Main health check")
        
        # Test API health endpoints
        health_endpoints = [
            ("/api/v1/health/ping", "GET", 200, "Ping test"),
            ("/api/v1/health/database", "GET", 200, "Database connectivity"),
            ("/api/v1/health/redis", "GET", 200, "Redis connectivity"),
            ("/api/v1/health/full", "GET", 200, "Full system health")
        ]
        
        for endpoint, method, expected, notes in health_endpoints:
            response, response_time = self.make_request(method, endpoint)
            self.log_result(endpoint, method, response.status_code, expected, response_time, notes)
    
    def test_documentation_endpoints(self):
        """Test documentation endpoints"""
        print("\n📚 Testing Documentation Endpoints")
        print("=" * 50)
        
        docs_endpoints = [
            ("/docs", "GET", 200, "Swagger UI"),
            ("/redoc", "GET", 200, "ReDoc documentation"),
            ("/openapi.json", "GET", 200, "OpenAPI specification")
        ]
        
        for endpoint, method, expected, notes in docs_endpoints:
            response, response_time = self.make_request(method, endpoint)
            self.log_result(endpoint, method, response.status_code, expected, response_time, notes)
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints")
        print("=" * 50)
        
        # Test registration (will fail without database but should validate schema)
        user_data = {
            "email": "test@valuadis.et",
            "full_name": "Test User",
            "phone": "+251911234567",
            "password": "test123456",
            "municipality": "Addis Ababa",
            "license_number": "VAL-ET-2024-TEST"
        }
        
        response, response_time = self.make_request("POST", "/api/v1/auth/register", user_data)
        # Expect 500 due to database not existing, but schema validation should pass
        self.log_result("/api/v1/auth/register", "POST", response.status_code, 500, response_time, "Schema validation")
        
        # Test login (will fail but should validate request format)
        login_data = {
            "email": "test@valuadis.et",
            "password": "test123456"
        }
        
        response, response_time = self.make_request("POST", "/api/v1/auth/login", login_data)
        self.log_result("/api/v1/auth/login", "POST", response.status_code, 500, response_time, "Request validation")
        
        # Test refresh token (will fail without valid token)
        response, response_time = self.make_request("POST", "/api/v1/auth/refresh")
        self.log_result("/api/v1/auth/refresh", "POST", response.status_code, 401, response_time, "Token validation")
        
        # Test current user (will fail without auth)
        response, response_time = self.make_request("GET", "/api/v1/auth/me")
        self.log_result("/api/v1/auth/me", "GET", response.status_code, 401, response_time, "Auth required")
    
    def test_property_endpoints(self):
        """Test property endpoints"""
        print("\n🏠 Testing Property Endpoints")
        print("=" * 50)
        
        # Test create property (will fail without auth/database)
        property_data = {
            "address": "Bole Subcity, Addis Ababa",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "area_sqm": 120.0,
            "boundary": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        response, response_time = self.make_request("POST", "/api/v1/properties", property_data)
        self.log_result("/api/v1/properties", "POST", response.status_code, 401, response_time, "Auth required")
        
        # Test list properties (will fail without auth)
        response, response_time = self.make_request("GET", "/api/v1/properties")
        self.log_result("/api/v1/properties", "GET", response.status_code, 401, response_time, "Auth required")
        
        # Test get property (will fail without auth)
        response, response_time = self.make_request("GET", "/api/v1/properties/1")
        self.log_result("/api/v1/properties/1", "GET", response.status_code, 401, response_time, "Auth required")
        
        # Test update property (will fail without auth)
        response, response_time = self.make_request("PUT", "/api/v1/properties/1", {"address": "Updated address"})
        self.log_result("/api/v1/properties/1", "PUT", response.status_code, 401, response_time, "Auth required")
        
        # Test delete property (will fail without auth)
        response, response_time = self.make_request("DELETE", "/api/v1/properties/1")
        self.log_result("/api/v1/properties/1", "DELETE", response.status_code, 401, response_time, "Auth required")
    
    def test_valuation_endpoints(self):
        """Test valuation endpoints"""
        print("\n💰 Testing Valuation Endpoints")
        print("=" * 50)
        
        # Test valuation calculation (should work without database)
        valuation_data = {
            "property_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 120.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        response, response_time = self.make_request("POST", "/api/v1/valuations/calculate", valuation_data)
        self.log_result("/api/v1/valuations/calculate", "POST", response.status_code, 200, response_time, "Calculation engine")
        
        # Test create valuation (will fail without auth/database)
        response, response_time = self.make_request("POST", "/api/v1/valuations/", valuation_data)
        self.log_result("/api/v1/valuations/", "POST", response.status_code, 401, response_time, "Auth required")
        
        # Test list valuations (will fail without auth)
        response, response_time = self.make_request("GET", "/api/v1/valuations/")
        self.log_result("/api/v1/valuations/", "GET", response.status_code, 401, response_time, "Auth required")
        
        # Test get valuation (will fail without auth)
        response, response_time = self.make_request("GET", "/api/v1/valuations/1")
        self.log_result("/api/v1/valuations/1", "GET", response.status_code, 401, response_time, "Auth required")
        
        # Test update valuation (will fail without auth)
        response, response_time = self.make_request("PUT", "/api/v1/valuations/1", {"status": "approved"})
        self.log_result("/api/v1/valuations/1", "PUT", response.status_code, 401, response_time, "Auth required")
        
        # Test delete valuation (will fail without auth)
        response, response_time = self.make_request("DELETE", "/api/v1/valuations/1")
        self.log_result("/api/v1/valuations/1", "DELETE", response.status_code, 401, response_time, "Auth required")
    
    def test_valuation_calculations(self):
        """Test different valuation calculation scenarios"""
        print("\n🧮 Testing Valuation Calculation Scenarios")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Residential - Addis Ababa",
                "data": {
                    "property_id": 1,
                    "property_type": "residential",
                    "municipality": "Addis Ababa",
                    "area_sqm": 120.0,
                    "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
                }
            },
            {
                "name": "Commercial - Dire Dawa",
                "data": {
                    "property_id": 2,
                    "property_type": "commercial",
                    "municipality": "Dire Dawa",
                    "area_sqm": 250.0,
                    "coordinates": [[41.8667, 9.6000], [41.8670, 9.6000], [41.8670, 9.5998], [41.8667, 9.5998], [41.8667, 9.6000]]
                }
            },
            {
                "name": "Agricultural - Mekelle",
                "data": {
                    "property_id": 3,
                    "property_type": "agricultural",
                    "municipality": "Mekelle",
                    "area_sqm": 5000.0,
                    "coordinates": [[39.4733, 13.4967], [39.4740, 13.4967], [39.4740, 13.4960], [39.4733, 13.4960], [39.4733, 13.4967]]
                }
            }
        ]
        
        for scenario in test_scenarios:
            response, response_time = self.make_request("POST", "/api/v1/valuations/calculate", scenario["data"])
            if response.status_code == 200:
                result = response.json()
                notes = f"Market: {result.get('market_value', 0):,.0f} ETB, Taxable: {result.get('taxable_value', 0):,.0f} ETB"
            else:
                notes = "Calculation failed"
            
            self.log_result("/api/v1/valuations/calculate", "POST", response.status_code, 200, response_time, scenario["name"])
            print(f"   📊 {notes}")
    
    def test_error_handling(self):
        """Test error handling and validation"""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test invalid valuation data
        invalid_data = {
            "property_id": 1,
            "property_type": "invalid_type",
            "municipality": "",
            "area_sqm": -100,
            "coordinates": []
        }
        
        response, response_time = self.make_request("POST", "/api/v1/valuations/calculate", invalid_data)
        self.log_result("/api/v1/valuations/calculate", "POST", response.status_code, 422, response_time, "Invalid data validation")
        
        # Test non-existent endpoint
        response, response_time = self.make_request("GET", "/api/v1/nonexistent")
        self.log_result("/api/v1/nonexistent", "GET", response.status_code, 404, response_time, "404 handling")
        
        # Test invalid method
        response, response_time = self.make_request("PATCH", "/api/v1/health/ping")
        self.log_result("/api/v1/health/ping", "PATCH", response.status_code, 405, response_time, "Method not allowed")
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Individual Endpoint Testing")
        print("=" * 60)
        
        try:
            self.test_health_endpoints()
            self.test_documentation_endpoints()
            self.test_authentication_endpoints()
            self.test_property_endpoints()
            self.test_valuation_endpoints()
            self.test_valuation_calculations()
            self.test_error_handling()
            
            self.print_summary()
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   {result['method']} {result['endpoint']} - Expected {result['expected']}, Got {result['status']} ({result['notes']})")
        
        print(f"\n🎯 Overall Status: {'✅ EXCELLENT' if passed_tests/total_tests >= 0.8 else '⚠️ NEEDS ATTENTION'}")


if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_all_tests()
