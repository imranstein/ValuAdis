#!/usr/bin/env python3
"""
End-to-End Scraper Workflow Test
Simulates the complete frontend scraper UI interaction
"""

import requests
import json
import time

class ScraperE2ETest:
    def __init__(self):
        self.base_url = "http://localhost:8020"
        self.token = None
        self.test_scraper_id = None
        
    def login(self):
        """Login as test user"""
        print("=== Step 1: User Login ===")
        
        login_data = {
            "email": "scraper@test.com",
            "password": "testpass123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('access_token')
                print("✓ User login successful")
                print(f"  Token received: {len(self.token)} characters")
                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(f"  Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def load_scraper_dashboard(self):
        """Simulate loading the scraper dashboard"""
        print("\n=== Step 2: Load Scraper Dashboard ===")
        
        try:
            headers = self.get_headers()
            
            # Get scraper stats (like the dashboard would)
            stats_response = requests.get(f"{self.base_url}/api/v1/scrapers/stats", headers=headers)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print("✓ Scraper stats loaded")
                print(f"  Total scrapers: {stats.get('total_scrapers')}")
                print(f"  Active scrapers: {stats.get('active_scrapers')}")
                print(f"  Total listings: {stats.get('total_listings')}")
            else:
                print(f"✗ Failed to load stats: {stats_response.status_code}")
                return False
            
            # Get all scrapers (like the scraper table would)
            scrapers_response = requests.get(f"{self.base_url}/api/v1/scrapers", headers=headers)
            if scrapers_response.status_code == 200:
                scrapers = scrapers_response.json()
                print("✓ Scraper list loaded")
                print(f"  Found {len(scrapers)} scrapers")
                
                # Display scrapers like the UI would
                for i, scraper in enumerate(scrapers[:3]):  # Show first 3
                    print(f"    {i+1}. {scraper.get('domain')} - {'Active' if scraper.get('enabled') else 'Inactive'}")
                    
            else:
                print(f"✗ Failed to load scrapers: {scrapers_response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            print(f"✗ Dashboard loading error: {e}")
            return False
    
    def create_new_scraper(self):
        """Simulate creating a new scraper via the UI"""
        print("\n=== Step 3: Create New Scraper ===")
        
        try:
            headers = self.get_headers()
            
            # Simulate form data from the AddScraperModal
            new_scraper_data = {
                "domain": "ethio-realestate-test.com",
                "url_template": "https://ethio-realestate-test.com/properties?page={page}",
                "enabled": True,
                "selectors": {
                    "title": ".property-title",
                    "price": ".property-price",
                    "location": ".property-location", 
                    "area": ".property-area",
                    "bedrooms": ".bedrooms",
                    "bathrooms": ".bathrooms",
                    "listing_url": ".property-link"
                },
                "schedule": "daily",
                "max_pages": 25
            }
            
            response = requests.post(f"{self.base_url}/api/v1/scrapers", json=new_scraper_data, headers=headers)
            
            if response.status_code == 201:
                scraper = response.json()
                self.test_scraper_id = scraper.get('id')
                print("✓ New scraper created successfully")
                print(f"  Domain: {scraper.get('domain')}")
                print(f"  ID: {scraper.get('id')}")
                print(f"  Enabled: {scraper.get('enabled')}")
                print(f"  Max pages: {scraper.get('max_pages')}")
                return True
            else:
                print(f"✗ Failed to create scraper: {response.status_code}")
                print(f"  Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Create scraper error: {e}")
            return False
    
    def test_scraper_operations(self):
        """Test scraper CRUD operations like the UI would"""
        print("\n=== Step 4: Test Scraper Operations ===")
        
        if not self.test_scraper_id:
            print("✗ No test scraper ID available")
            return False
            
        try:
            headers = self.get_headers()
            scraper_id = self.test_scraper_id
            
            # Test update scraper (like editing in the modal)
            print("  Testing update scraper...")
            update_data = {
                "max_pages": 30,
                "schedule": "weekly"
            }
            
            update_response = requests.put(f"{self.base_url}/api/v1/scrapers/{scraper_id}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                updated = update_response.json()
                print("  ✓ Scraper updated successfully")
                print(f"    New max_pages: {updated.get('max_pages')}")
                print(f"    New schedule: {updated.get('schedule')}")
            else:
                print(f"  ✗ Update failed: {update_response.status_code}")
                return False
            
            # Test toggle scraper (like clicking the toggle button)
            print("  Testing toggle scraper...")
            toggle_response = requests.patch(f"{self.base_url}/api/v1/scrapers/{scraper_id}/toggle", headers=headers)
            if toggle_response.status_code == 200:
                toggled = toggle_response.json()
                print("  ✓ Scraper toggled successfully")
                print(f"    New enabled status: {toggled.get('enabled')}")
            else:
                print(f"  ✗ Toggle failed: {toggle_response.status_code}")
                return False
            
            # Test get scraper by ID (like viewing details)
            print("  Testing get scraper details...")
            get_response = requests.get(f"{self.base_url}/api/v1/scrapers/{scraper_id}", headers=headers)
            if get_response.status_code == 200:
                details = get_response.json()
                print("  ✓ Scraper details retrieved")
                print(f"    Domain: {details.get('domain')}")
                print(f"    Last run: {details.get('last_run')}")
            else:
                print(f"  ✗ Get details failed: {get_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Scraper operations error: {e}")
            return False
    
    def test_scraper_execution(self):
        """Test scraper execution functionality"""
        print("\n=== Step 5: Test Scraper Execution ===")
        
        if not self.test_scraper_id:
            print("✗ No test scraper ID available")
            return False
            
        try:
            headers = self.get_headers()
            scraper_id = self.test_scraper_id
            
            # Test scraper configuration test (like clicking "Test" button)
            print("  Testing scraper configuration...")
            test_data = {
                "url_template": "https://ethio-realestate-test.com/properties?page=1",
                "selectors": {
                    "title": ".property-title",
                    "price": ".property-price"
                },
                "test_page": 1
            }
            
            test_response = requests.post(f"{self.base_url}/api/v1/scrapers/{scraper_id}/test", json=test_data, headers=headers)
            if test_response.status_code == 200:
                result = test_response.json()
                print("  ✓ Scraper test completed")
                print(f"    Success: {result.get('success')}")
                print(f"    Items found: {result.get('items_found', 0)}")
                if result.get('error_message'):
                    print(f"    Note: {result.get('error_message')}")
                    if "ERR_NAME_NOT_RESOLVED" in result.get('error_message', ''):
                        print("    (Expected: Test domain doesn't exist)")
            else:
                print(f"  ✗ Scraper test failed: {test_response.status_code}")
                return False
            
            # Re-enable scraper before running it
            print("  Re-enabling scraper for run test...")
            toggle_response = requests.patch(f"{self.base_url}/api/v1/scrapers/{scraper_id}/toggle", headers=headers)
            if toggle_response.status_code == 200:
                print("  ✓ Scraper re-enabled")
            else:
                print(f"  ✗ Failed to re-enable scraper: {toggle_response.status_code}")
                return False
            
            # Test manual scraper run (like clicking "Run" button)
            print("  Testing manual scraper run...")
            run_data = {
                "max_pages": 2,
                "target_items": 10
            }
            
            run_response = requests.post(f"{self.base_url}/api/v1/scrapers/{scraper_id}/run", json=run_data, headers=headers)
            if run_response.status_code == 200:
                result = run_response.json()
                print("  ✓ Scraper run initiated")
                print(f"    Message: {result.get('message')}")
                print(f"    Log ID: {result.get('log_id')}")
            else:
                print(f"  ✗ Scraper run failed: {run_response.status_code}")
                print(f"    Error: {run_response.text}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Scraper execution error: {e}")
            return False
    
    def cleanup_test_scraper(self):
        """Clean up the test scraper"""
        print("\n=== Step 6: Cleanup Test Scraper ===")
        
        if not self.test_scraper_id:
            print("✓ No test scraper to cleanup")
            return True
            
        try:
            headers = self.get_headers()
            
            response = requests.delete(f"{self.base_url}/api/v1/scrapers/{self.test_scraper_id}", headers=headers)
            
            if response.status_code == 204:
                print("✓ Test scraper deleted successfully")
                return True
            else:
                print(f"✗ Failed to delete test scraper: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Cleanup error: {e}")
            return False
    
    def run_full_e2e_test(self):
        """Run the complete end-to-end test"""
        print("🚀 Starting End-to-End Scraper Workflow Test")
        print("=" * 60)
        
        steps = [
            ("Login", self.login),
            ("Load Dashboard", self.load_scraper_dashboard),
            ("Create Scraper", self.create_new_scraper),
            ("Test Operations", self.test_scraper_operations),
            ("Test Execution", self.test_scraper_execution),
            ("Cleanup", self.cleanup_test_scraper)
        ]
        
        passed = 0
        total = len(steps)
        
        for step_name, step_func in steps:
            if step_func():
                passed += 1
            else:
                print(f"\n❌ E2E Test Failed at: {step_name}")
                break
        
        print("\n" + "=" * 60)
        print(f"📊 E2E Test Results: {passed}/{total} steps passed")
        
        if passed == total:
            print("🎉 All E2E Tests Passed! Scraper workflow is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed == total

if __name__ == "__main__":
    tester = ScraperE2ETest()
    success = tester.run_full_e2e_test()
    exit(0 if success else 1)
