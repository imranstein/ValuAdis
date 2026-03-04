#!/usr/bin/env python3
"""
Test Authentication Flow for Scraper UI
"""

import requests
import json

def test_authentication():
    """Test the complete authentication flow"""
    base_url = "http://localhost:8020"
    
    print("=== Testing Authentication Flow ===")
    
    # Test login with test user
    login_data = {
        "email": "scraper@test.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            print("✓ Login successful")
            print(f"  Success: {login_result.get('success')}")
            print(f"  Token type: {login_result.get('token_type')}")
            
            token = login_result.get('access_token')
            if token:
                print(f"  Token received (length: {len(token)})")
                
                # Test authenticated scraper endpoints
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test get all scrapers
                scrapers_response = requests.get(f"{base_url}/api/v1/scrapers", headers=headers)
                if scrapers_response.status_code == 200:
                    scrapers = scrapers_response.json()
                    print(f"✓ Get scrapers successful: {len(scrapers)} scrapers found")
                    
                    # Show first scraper details
                    if scrapers:
                        scraper = scrapers[0]
                        print(f"  First scraper: {scraper.get('domain')} - Enabled: {scraper.get('enabled')}")
                else:
                    print(f"✗ Get scrapers failed: {scrapers_response.status_code}")
                    print(f"  Error: {scrapers_response.text}")
                
                # Test scraper stats
                stats_response = requests.get(f"{base_url}/api/v1/scrapers/stats", headers=headers)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print("✓ Get scraper stats successful")
                    print(f"  Total scrapers: {stats.get('total_scrapers')}")
                    print(f"  Active scrapers: {stats.get('active_scrapers')}")
                else:
                    print(f"✗ Get scraper stats failed: {stats_response.status_code}")
                    print(f"  Error: {stats_response.text}")
                
                # Test create new scraper
                new_scraper = {
                    "domain": "test-ethio-property.com",
                    "url_template": "https://test-ethio-property.com/listings?page={page}",
                    "enabled": True,
                    "selectors": {
                        "title": ".property-title",
                        "price": ".property-price",
                        "location": ".property-location",
                        "listing_url": ".property-link"
                    },
                    "schedule": "daily",
                    "max_pages": 25
                }
                
                create_response = requests.post(f"{base_url}/api/v1/scrapers", json=new_scraper, headers=headers)
                if create_response.status_code == 201:
                    created_scraper = create_response.json()
                    print("✓ Create scraper successful")
                    print(f"  Created: {created_scraper.get('domain')} (ID: {created_scraper.get('id')})")
                    
                    # Test update scraper
                    update_data = {"max_pages": 30}
                    update_response = requests.put(f"{base_url}/api/v1/scrapers/{created_scraper.get('id')}", json=update_data, headers=headers)
                    if update_response.status_code == 200:
                        print("✓ Update scraper successful")
                    else:
                        print(f"✗ Update scraper failed: {update_response.status_code}")
                    
                    # Test toggle scraper
                    toggle_response = requests.patch(f"{base_url}/api/v1/scrapers/{created_scraper.get('id')}/toggle", headers=headers)
                    if toggle_response.status_code == 200:
                        print("✓ Toggle scraper successful")
                    else:
                        print(f"✗ Toggle scraper failed: {toggle_response.status_code}")
                    
                    # Test delete scraper
                    delete_response = requests.delete(f"{base_url}/api/v1/scrapers/{created_scraper.get('id')}", headers=headers)
                    if delete_response.status_code == 204:
                        print("✓ Delete scraper successful")
                    else:
                        print(f"✗ Delete scraper failed: {delete_response.status_code}")
                        
                else:
                    print(f"✗ Create scraper failed: {create_response.status_code}")
                    print(f"  Error: {create_response.text}")
                
            else:
                print("✗ No token received in login response")
                
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Authentication test error: {e}")
    
    print("\n=== Authentication Test Complete ===")

if __name__ == "__main__":
    test_authentication()
