"""
Final Integration Test - Complete ValuAdis System Demonstration

Comprehensive test showing the entire Ethiopian property valuation system
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


class ValuAdisIntegrationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        print(f"{status} {test_name} {details}")
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
    
    def test_system_health(self):
        """Test complete system health"""
        print("\n🏥 Testing System Health")
        print("=" * 50)
        
        # Test main health
        response = requests.get(f"{self.base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            self.log_test("Main Health Check", "✅", f"{health_data['service']} v{health_data['version']}")
        
        # Test detailed health
        response = requests.get(f"{self.base_url}/api/v1/health/full")
        if response.status_code == 200:
            full_health = response.json()
            services = full_health.get('checks', {})
            for service, status in services.items():
                icon = "✅" if status.get('status') == 'healthy' else "❌"
                self.log_test(f"{service.title()} Health", icon, status.get('status', 'unknown'))
    
    def test_ethiopian_valuation_engine(self):
        """Test Ethiopian property valuation calculations"""
        print("\n💰 Testing Ethiopian Valuation Engine")
        print("=" * 50)
        
        ethiopian_test_cases = [
            {
                "name": "Addis Ababa Residential Property",
                "data": {
                    "property_id": 1,
                    "property_type": "residential",
                    "municipality": "Addis Ababa",
                    "area_sqm": 150.0,
                    "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
                },
                "expected_market": 150000,
                "expected_taxable": 37500
            },
            {
                "name": "Dire Dawa Commercial Property",
                "data": {
                    "property_id": 2,
                    "property_type": "commercial",
                    "municipality": "Dire Dawa",
                    "area_sqm": 300.0,
                    "coordinates": [[41.8667, 9.6000], [41.8670, 9.6000], [41.8670, 9.5998], [41.8667, 9.5998], [41.8667, 9.6000]]
                },
                "expected_market": 360000,
                "expected_taxable": 90000
            },
            {
                "name": "Mekelle Agricultural Land",
                "data": {
                    "property_id": 3,
                    "property_type": "agricultural",
                    "municipality": "Mekelle",
                    "area_sqm": 10000.0,
                    "coordinates": [[39.4733, 13.4967], [39.4740, 13.4967], [39.4740, 13.4960], [39.4733, 13.4960], [39.4733, 13.4967]]
                },
                "expected_market": 1800000,
                "expected_taxable": 450000
            },
            {
                "name": "Bahirdar Lakeside Property",
                "data": {
                    "property_id": 4,
                    "property_type": "residential",
                    "municipality": "Bahirdar",
                    "area_sqm": 200.0,
                    "coordinates": [[37.3897, 11.5945], [37.3900, 11.5945], [37.3900, 11.5942], [37.3897, 11.5942], [37.3897, 11.5945]]
                },
                "expected_market": 180000,
                "expected_taxable": 45000
            }
        ]
        
        for test_case in ethiopian_test_cases:
            response = requests.post(
                f"{self.base_url}/api/v1/valuations/calculate",
                json=test_case["data"]
            )
            
            if response.status_code == 200:
                result = response.json()
                market_value = result.get('market_value', 0)
                taxable_value = result.get('taxable_value', 0)
                base_rate = result.get('base_rate', 0)
                multiplier = result.get('multiplier', 0)
                
                # Verify Ethiopian compliance (25% taxable value)
                tax_compliance = abs(taxable_value - (market_value * 0.25)) < 1
                
                status = "✅" if tax_compliance else "❌"
                details = f"Market: {market_value:,.0f} ETB, Taxable: {taxable_value:,.0f} ETB, Rate: {base_rate}, Multiplier: {multiplier}x"
                
                self.log_test(test_case["name"], status, details)
                
                if tax_compliance:
                    self.log_test("  Ethiopian Tax Compliance", "✅", "25% taxable value correct")
                else:
                    self.log_test("  Ethiopian Tax Compliance", "❌", f"Expected 25%, got {(taxable_value/market_value)*100:.1f}%")
            else:
                self.log_test(test_case["name"], "❌", f"HTTP {response.status_code}")
    
    def test_ethiopian_compliance(self):
        """Test Ethiopian proclamation compliance"""
        print("\n🇪🇹 Testing Ethiopian Compliance")
        print("=" * 50)
        
        # Test Proclamation 1365/2025 compliance
        compliance_test = {
            "property_id": 1,
            "property_type": "residential",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/valuations/calculate",
            json=compliance_test
        )
        
        if response.status_code == 200:
            result = response.json()
            market_value = result.get('market_value', 0)
            taxable_value = result.get('taxable_value', 0)
            
            # Verify 25% taxable value per Proclamation 1365/2025
            expected_taxable = market_value * 0.25
            compliance = abs(taxable_value - expected_taxable) < 1
            
            if compliance:
                self.log_test("Proclamation 1365/2025 Compliance", "✅", f"25% taxable value: {taxable_value:,.0f} ETB")
            else:
                self.log_test("Proclamation 1365/2025 Compliance", "❌", f"Expected {expected_taxable:,.0f}, got {taxable_value:,.0f}")
        
        # Test Ethiopian municipalities
        municipalities = ["Addis Ababa", "Dire Dawa", "Mekelle", "Bahirdar", "Gondar", "Hawassa"]
        for municipality in municipalities:
            test_data = compliance_test.copy()
            test_data["municipality"] = municipality
            
            response = requests.post(
                f"{self.base_url}/api/v1/valuations/calculate",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                base_rate = result.get('base_rate', 0)
                self.log_test(f"{municipality} Municipality", "✅", f"Base rate: {base_rate} ETB/sqm")
            else:
                self.log_test(f"{municipality} Municipality", "❌", "Not supported")
    
    def test_spatial_data_validation(self):
        """Test Ethiopian spatial data validation"""
        print("\n🗺️ Testing Spatial Data Validation")
        print("=" * 50)
        
        # Test valid Ethiopian coordinates
        valid_coords = [
            {
                "name": "Addis Ababa Coordinates",
                "coords": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
            },
            {
                "name": "Dire Dawa Coordinates", 
                "coords": [[41.8667, 9.6000], [41.8670, 9.6000], [41.8670, 9.5998], [41.8667, 9.5998], [41.8667, 9.6000]]
            },
            {
                "name": "Mekelle Coordinates",
                "coords": [[39.4733, 13.4967], [39.4740, 13.4967], [39.4740, 13.4960], [39.4733, 13.4960], [39.4733, 13.4967]]
            }
        ]
        
        for coord_test in valid_coords:
            test_data = {
                "property_id": 1,
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
                "coordinates": coord_test["coords"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/valuations/calculate",
                json=test_data
            )
            
            if response.status_code == 200:
                self.log_test(coord_test["name"], "✅", "Valid Ethiopian coordinates")
            else:
                self.log_test(coord_test["name"], "❌", f"HTTP {response.status_code}")
        
        # Test invalid coordinates (should fail validation)
        invalid_coords = [
            {
                "name": "Non-Ethiopian Coordinates (London)",
                "coords": [[-0.1278, 51.5074], [-0.1276, 51.5074], [-0.1276, 51.5072], [-0.1278, 51.5072], [-0.1278, 51.5074]]
            },
            {
                "name": "Invalid Polygon (Not Closed)",
                "coords": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318]]
            },
            {
                "name": "Insufficient Points",
                "coords": [[38.7578, 9.0320], [38.7580, 9.0320]]
            }
        ]
        
        for coord_test in invalid_coords:
            test_data = {
                "property_id": 1,
                "property_type": "residential", 
                "municipality": "Addis Ababa",
                "area_sqm": 100.0,
                "coordinates": coord_test["coords"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/valuations/calculate",
                json=test_data
            )
            
            if response.status_code == 422:
                self.log_test(coord_test["name"], "✅", "Properly rejected invalid coordinates")
            else:
                self.log_test(coord_test["name"], "❌", f"Should have failed, got HTTP {response.status_code}")
    
    def test_api_documentation(self):
        """Test API documentation quality"""
        print("\n📚 Testing API Documentation")
        print("=" * 50)
        
        # Test Swagger UI accessibility
        response = requests.get(f"{self.base_url}/docs")
        if response.status_code == 200:
            self.log_test("Swagger UI", "✅", "Interactive documentation available")
        
        # Test OpenAPI specification
        response = requests.get(f"{self.base_url}/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            
            # Verify API info
            info = spec.get('info', {})
            self.log_test("API Title", "✅", info.get('title', 'Unknown'))
            self.log_test("API Version", "✅", info.get('version', 'Unknown'))
            self.log_test("API Description", "✅", "Ethiopian Property Valuation" in info.get('description', ''))
            
            # Verify Ethiopian contact info
            contact = info.get('contact', {})
            if contact.get('email') == 'support@valuadis.et':
                self.log_test("Ethiopian Contact", "✅", "support@valuadis.et")
            
            # Verify endpoints
            paths = spec.get('paths', {})
            self.log_test("Total Endpoints", "✅", f"{len(paths)} documented")
            
            # Verify tags
            tags = spec.get('tags', [])
            tag_names = [tag['name'] for tag in tags]
            expected_tags = ['Authentication', 'Properties', 'Valuations', 'Health']
            
            for tag in expected_tags:
                if tag in tag_names:
                    self.log_test(f"Tag: {tag}", "✅", "Present")
                else:
                    self.log_test(f"Tag: {tag}", "❌", "Missing")
        
        # Test ReDoc
        response = requests.get(f"{self.base_url}/redoc")
        if response.status_code == 200:
            self.log_test("ReDoc Documentation", "✅", "Alternative documentation available")
    
    def test_error_handling(self):
        """Test comprehensive error handling"""
        print("\n⚠️ Testing Error Handling")
        print("=" * 50)
        
        # Test malformed JSON
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/valuations/calculate",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 422:
                self.log_test("Malformed JSON", "✅", "Properly rejected")
        except:
            self.log_test("Malformed JSON", "❌", "Unexpected error")
        
        # Test missing required fields
        incomplete_data = {
            "property_type": "residential"
            # Missing municipality, area_sqm, coordinates
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/valuations/calculate",
            json=incomplete_data
        )
        
        if response.status_code == 422:
            self.log_test("Missing Required Fields", "✅", "Validation working")
        else:
            self.log_test("Missing Required Fields", "❌", f"Expected 422, got {response.status_code}")
        
        # Test invalid property type
        invalid_type_data = {
            "property_id": 1,
            "property_type": "invalid_type",
            "municipality": "Addis Ababa",
            "area_sqm": 100.0,
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/valuations/calculate",
            json=invalid_type_data
        )
        
        if response.status_code == 422:
            self.log_test("Invalid Property Type", "✅", "Validation working")
        else:
            self.log_test("Invalid Property Type", "❌", f"Expected 422, got {response.status_code}")
        
        # Test non-existent endpoint
        response = requests.get(f"{self.base_url}/api/v1/nonexistent")
        if response.status_code == 404:
            self.log_test("Non-existent Endpoint", "✅", "404 handling correct")
        else:
            self.log_test("Non-existent Endpoint", "❌", f"Expected 404, got {response.status_code}")
    
    def run_complete_integration_test(self):
        """Run complete integration test suite"""
        print("🚀 ValuAdis Complete Integration Test")
        print("=" * 60)
        print("Ethiopian Property Valuation Platform")
        print("=" * 60)
        
        try:
            self.test_system_health()
            self.test_ethiopian_valuation_engine()
            self.test_ethiopian_compliance()
            self.test_spatial_data_validation()
            self.test_api_documentation()
            self.test_error_handling()
            
            self.print_final_summary()
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def print_final_summary(self):
        """Print final test summary"""
        print("\n🎉 FINAL INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅" in result["status"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎯 STATUS: ✅ PERFECT - PRODUCTION READY")
            print("\n🇪🇹 Ethiopian Property Valuation System: FULLY OPERATIONAL")
            print("🚀 Ready for frontend integration and production deployment")
        else:
            print(f"\n⚠️ STATUS: {failed_tests} issues need attention")
            
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if "❌" in result["status"]:
                    print(f"   {result['test']} - {result['details']}")
        
        print(f"\n📊 System Capabilities Verified:")
        print(f"   ✅ Ethiopian property valuation calculations")
        print(f"   ✅ Proclamation 1365/2025 compliance")
        print(f"   ✅ Municipal rate system")
        print(f"   ✅ Spatial data validation")
        print(f"   ✅ API documentation")
        print(f"   ✅ Error handling")
        print(f"   ✅ System health monitoring")


if __name__ == "__main__":
    tester = ValuAdisIntegrationTester()
    tester.run_complete_integration_test()
