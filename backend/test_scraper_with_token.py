#!/usr/bin/env python3
"""Test scraper endpoints with valid token"""

import asyncio
import sys
import os
import json

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

async def test_scraper_endpoints():
    """Test scraper endpoints with valid token"""
    client = TestClient(app)
    
    # First login to get token
    login_data = {
        "email": "admin@valuadis.com",
        "password": "Admin123!"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Got authentication token")
    
    # Test 1: Create scraper
    scraper_data = {
        "domain": "ethiopianrealestate.et",
        "url_template": "https://ethiopianrealestate.et/properties?page={page}",
        "selectors": {
            "title": ".property-title",
            "price": ".price",
            "location": ".location",
            "listing_url": ".property-link"
        },
        "schedule": "daily",
        "max_pages": 50,
        "enabled": True
    }
    
    create_response = client.post("/api/v1/scrapers", json=scraper_data, headers=headers)
    print(f"\n1. Scraper Creation: {create_response.status_code}")
    if create_response.status_code == 201:
        scraper_id = create_response.json()["id"]
        print(f"   ✅ Created scraper ID: {scraper_id}")
    else:
        print(f"   ❌ Failed: {create_response.text}")
        return
    
    # Test 2: Get all scrapers
    scrapers_response = client.get("/api/v1/scrapers", headers=headers)
    print(f"\n2. Get Scrapers: {scrapers_response.status_code}")
    if scrapers_response.status_code == 200:
        print(f"   ✅ Retrieved {len(scrapers_response.json())} scrapers")
    else:
        print(f"   ❌ Failed: {scrapers_response.text}")
    
    # Test 3: Get scraper stats
    stats_response = client.get("/api/v1/scrapers/stats", headers=headers)
    print(f"\n3. Scraper Statistics: {stats_response.status_code}")
    if stats_response.status_code == 200:
        print(f"   ✅ Stats: {json.dumps(stats_response.json(), indent=2)}")
    else:
        print(f"   ❌ Failed: {stats_response.text}")
    
    # Test 4: Get scraper logs
    logs_response = client.get("/api/v1/scrapers/logs", headers=headers)
    print(f"\n4. Scraper Logs: {logs_response.status_code}")
    if logs_response.status_code == 200:
        logs_data = logs_response.json()
        logs_count = len(logs_data) if isinstance(logs_data, list) else len(logs_data.get('logs', []))
        print(f"   ✅ Retrieved {logs_count} logs")
    else:
        print(f"   ❌ Failed: {logs_response.text}")
    
    # Test 5: Run scraper
    run_response = client.post(f"/api/v1/scrapers/{scraper_id}/run", headers=headers)
    print(f"\n5. Run Scraper: {run_response.status_code}")
    if run_response.status_code == 200:
        print(f"   ✅ Started scraper execution")
    else:
        print(f"   ❌ Failed: {run_response.text}")
    
    # Test 6: Toggle scraper status
    toggle_response = client.patch(f"/api/v1/scrapers/{scraper_id}/toggle", headers=headers)
    print(f"\n6. Toggle Status: {toggle_response.status_code}")
    if toggle_response.status_code == 200:
        print(f"   ✅ Toggled scraper status")
    else:
        print(f"   ❌ Failed: {toggle_response.text}")
    
    # Test 7: Update scraper schedule
    schedule_data = {
        "schedule": "weekly",
        "max_pages": 25
    }
    update_response = client.put(f"/api/v1/scrapers/{scraper_id}", json=schedule_data, headers=headers)
    print(f"\n7. Update Schedule: {update_response.status_code}")
    if update_response.status_code == 200:
        print(f"   ✅ Updated scraper schedule")
    else:
        print(f"   ❌ Failed: {update_response.text}")
    
    # Test 8: Error handling - invalid scraper ID
    error_response = client.post("/api/v1/scrapers/99999/run", headers=headers)
    print(f"\n8. Error Handling: {error_response.status_code}")
    if error_response.status_code == 404:
        print(f"   ✅ Correctly returned 404 for invalid scraper")
    else:
        print(f"   ⚠️ Expected 404, got {error_response.status_code}: {error_response.text}")
    
    print("\n✅ All scraper endpoint tests completed!")

if __name__ == "__main__":
    asyncio.run(test_scraper_endpoints())
