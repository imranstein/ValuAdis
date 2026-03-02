"""
ValuAdis API Stress Testing Suite

Comprehensive load testing for Ethiopian Property Valuation Platform
Tests concurrent users, valuation calculations, and system performance
"""

from locust import HttpUser, task, between
import random
import json
from datetime import datetime


class ValuAdisUser(HttpUser):
    """
    Simulates Ethiopian property valuer using the ValuAdis API
    Tests valuation calculations, API endpoints, and system performance
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts testing"""
        print(f"👤 New valuer user started: {self.environment.parsed_options.host}")
    
    @task(3)
    def health_check(self):
        """Test health endpoints - most frequent operation"""
        self.client.get("/health")
        self.client.get("/api/v1/health/ping")
    
    @task(5)
    def valuation_calculation(self):
        """Test Ethiopian property valuation calculations - core business logic"""
        
        # Ethiopian test data scenarios
        ethiopian_scenarios = [
            {
                "name": "Addis Ababa Residential",
                "data": {
                    "property_id": random.randint(1, 1000),
                    "property_type": "residential",
                    "municipality": "Addis Ababa",
                    "area_sqm": random.uniform(50, 500),
                    "coordinates": self.generate_ethiopian_coordinates("addis_ababa")
                }
            },
            {
                "name": "Dire Dawa Commercial",
                "data": {
                    "property_id": random.randint(1, 1000),
                    "property_type": "commercial",
                    "municipality": "Dire Dawa",
                    "area_sqm": random.uniform(100, 1000),
                    "coordinates": self.generate_ethiopian_coordinates("dire_dawa")
                }
            },
            {
                "name": "Mekelle Agricultural",
                "data": {
                    "property_id": random.randint(1, 1000),
                    "property_type": "agricultural",
                    "municipality": "Mekelle",
                    "area_sqm": random.uniform(1000, 10000),
                    "coordinates": self.generate_ethiopian_coordinates("mekelle")
                }
            },
            {
                "name": "Hawassa Residential",
                "data": {
                    "property_id": random.randint(1, 1000),
                    "property_type": "residential",
                    "municipality": "Hawassa",
                    "area_sqm": random.uniform(80, 300),
                    "coordinates": self.generate_ethiopian_coordinates("hawassa")
                }
            }
        ]
        
        # Select random scenario
        scenario = random.choice(ethiopian_scenarios)
        
        with self.client.post("/api/v1/valuations/calculate", 
                             json=scenario["data"],
                             catch_response=True) as response:
            if response.status_code == 200:
                result = response.json()
                # Verify Ethiopian compliance (25% taxable value)
                market_value = result.get('market_value', 0)
                taxable_value = result.get('taxable_value', 0)
                expected_taxable = market_value * 0.25
                
                if abs(taxable_value - expected_taxable) < 1:
                    response.success()
                else:
                    response.failure(f"Ethiopian tax compliance failed: {taxable_value} vs {expected_taxable}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def api_documentation(self):
        """Test API documentation endpoints"""
        self.client.get("/docs")
        self.client.get("/openapi.json")
    
    @task(1)
    def root_endpoint(self):
        """Test root API endpoint"""
        self.client.get("/")
    
    def generate_ethiopian_coordinates(self, municipality):
        """Generate realistic Ethiopian coordinates for testing"""
        
        # Ethiopian municipality coordinates (approximate)
        coords = {
            "addis_ababa": (38.7578, 9.0320),
            "dire_dawa": (41.8667, 9.6000),
            "mekelle": (39.4733, 13.4967),
            "hawassa": (38.4833, 7.0583),
            "bahirdar": (37.3897, 11.5945),
            "gondar": (37.4667, 12.6000),
            "jimma": (36.8333, 7.6667)
        }
        
        base_lat, base_lon = coords.get(municipality, coords["addis_ababa"])
        
        # Generate small polygon around the base coordinates (within municipality bounds)
        polygon = []
        for i in range(5):  # 5 points for a simple polygon
            lat_offset = random.uniform(-0.01, 0.01)  # ~1km range
            lon_offset = random.uniform(-0.01, 0.01)
            polygon.append([base_lon + lon_offset, base_lat + lat_offset])
        
        # Close the polygon
        polygon.append(polygon[0])
        
        return polygon


class EthiopianValuerUser(ValuAdisUser):
    """
    Specialized user for Ethiopian property valuers
    Focuses on valuation calculations and compliance
    """
    
    wait_time = between(2, 5)  # Slower pace for detailed valuations
    
    @task(8)
    def complex_valuation_calculations(self):
        """Test complex Ethiopian valuation scenarios"""
        
        # Complex Ethiopian property scenarios
        complex_scenarios = [
            {
                "name": "Large Addis Ababa Commercial Complex",
                "data": {
                    "property_id": random.randint(1000, 2000),
                    "property_type": "commercial",
                    "municipality": "Addis Ababa",
                    "area_sqm": random.uniform(1000, 5000),
                    "coordinates": self.generate_complex_polygon("addis_ababa")
                }
            },
            {
                "name": "Mekelle Agricultural Estate",
                "data": {
                    "property_id": random.randint(1000, 2000),
                    "property_type": "agricultural",
                    "municipality": "Mekelle",
                    "area_sqm": random.uniform(10000, 50000),
                    "coordinates": self.generate_complex_polygon("mekelle")
                }
            },
            {
                "name": "Dire Dawa Industrial Property",
                "data": {
                    "property_id": random.randint(1000, 2000),
                    "property_type": "commercial",
                    "municipality": "Dire Dawa",
                    "area_sqm": random.uniform(2000, 10000),
                    "coordinates": self.generate_complex_polygon("dire_dawa")
                }
            }
        ]
        
        scenario = random.choice(complex_scenarios)
        
        with self.client.post("/api/v1/valuations/calculate",
                             json=scenario["data"],
                             catch_response=True) as response:
            if response.status_code == 200:
                result = response.json()
                
                # Verify Ethiopian compliance
                market_value = result.get('market_value', 0)
                taxable_value = result.get('taxable_value', 0)
                base_rate = result.get('base_rate', 0)
                multiplier = result.get('multiplier', 0)
                
                # Comprehensive validation
                compliance_checks = [
                    abs(taxable_value - (market_value * 0.25)) < 1,  # 25% tax rule
                    base_rate > 0,  # Valid base rate
                    multiplier > 0,  # Valid multiplier
                    market_value > 0,  # Valid market value
                ]
                
                if all(compliance_checks):
                    response.success()
                else:
                    response.failure(f"Compliance check failed: {compliance_checks}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    def generate_complex_polygon(self, municipality):
        """Generate more complex polygons for testing"""
        
        coords = {
            "addis_ababa": (38.7578, 9.0320),
            "dire_dawa": (41.8667, 9.6000),
            "mekelle": (39.4733, 13.4967)
        }
        
        base_lat, base_lon = coords.get(municipality, coords["addis_ababa"])
        
        # Generate 8-point polygon for more complex shapes
        polygon = []
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180  # 45-degree increments
            radius = random.uniform(0.005, 0.02)  # 500m-2km radius
            lat_offset = radius * 0.009 * 111  # Convert to degrees
            lon_offset = radius * 0.009 * 111 / 37  # Adjust for longitude
            
            lat = base_lat + lat_offset * (1 if i % 2 == 0 else -1)
            lon = base_lon + lon_offset * (1 if i % 3 == 0 else -1)
            polygon.append([lon, lat])
        
        polygon.append(polygon[0])  # Close polygon
        return polygon


class SystemAdminUser(HttpUser):
    """
    Simulates system administrators monitoring the ValuAdis platform
    Tests health monitoring, documentation, and system endpoints
    """
    
    wait_time = between(5, 10)  # Admins check less frequently
    
    @task(4)
    def system_health_monitoring(self):
        """Test comprehensive system health monitoring"""
        
        health_endpoints = [
            "/health",
            "/api/v1/health/ping",
            "/api/v1/health/database",
            "/api/v1/health/redis",
            "/api/v1/health/full"
        ]
        
        for endpoint in health_endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Health check failed: {endpoint}")
    
    @task(3)
    def api_documentation_access(self):
        """Test API documentation access"""
        
        doc_endpoints = [
            "/docs",
            "/redoc", 
            "/openapi.json"
        ]
        
        for endpoint in doc_endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Documentation failed: {endpoint}")
    
    @task(2)
    def system_information(self):
        """Test system information endpoints"""
        
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Root endpoint failed")


class LoadTestUser(HttpUser):
    """
    High-frequency user for maximum load testing
    Focuses on the most critical endpoint: valuation calculations
    """
    
    wait_time = between(0.5, 2)  # Very fast requests for load testing
    
    @task(10)
    def rapid_valuation_calculations(self):
        """Rapid valuation calculations for maximum load"""
        
        # Simple, fast valuation data
        quick_data = {
            "property_id": random.randint(1, 10000),
            "property_type": random.choice(["residential", "commercial", "agricultural"]),
            "municipality": random.choice(["Addis Ababa", "Dire Dawa", "Mekelle", "Hawassa"]),
            "area_sqm": random.uniform(50, 1000),
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        with self.client.post("/api/v1/valuations/calculate",
                             json=quick_data,
                             catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Load test failed: HTTP {response.status_code}")


# User class weights for different test scenarios
class WebsiteUser(HttpUser):
    """
    Mixed user types for comprehensive testing
    """
    
    wait_time = between(1, 3)
    
    @task(3)
    def valuation_calculation(self):
        """Standard valuation calculation"""
        data = {
            "property_id": random.randint(1, 1000),
            "property_type": random.choice(["residential", "commercial", "agricultural"]),
            "municipality": random.choice(["Addis Ababa", "Dire Dawa", "Mekelle"]),
            "area_sqm": random.uniform(100, 500),
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        self.client.post("/api/v1/valuations/calculate", json=data)
    
    @task(2)
    def health_check(self):
        """Health monitoring"""
        self.client.get("/health")
    
    @task(1)
    def documentation(self):
        """API documentation"""
        self.client.get("/docs")
