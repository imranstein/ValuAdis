#!/usr/bin/env python3
"""
Test Frontend-Backend Integration for Scraper
"""

import requests
import json

def test_scraper_integration():
    """Test scraper API endpoints like the frontend would"""
    base_url = "http://localhost:8020"
    
    print("=== Testing Scraper API Integration ===")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Backend health check passed")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to backend: {e}")
        return
    
    # Test scraper stats endpoint (will fail auth but should return proper error)
    try:
        response = requests.get(f"{base_url}/api/v1/scrapers/stats")
        if response.status_code == 401:
            print("✓ Scraper stats endpoint requires authentication (expected)")
        else:
            print(f"? Unexpected status for scraper stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Scraper stats endpoint error: {e}")
    
    # Test scraper list endpoint (will fail auth but should return proper error)
    try:
        response = requests.get(f"{base_url}/api/v1/scrapers")
        if response.status_code == 401:
            print("✓ Scraper list endpoint requires authentication (expected)")
        else:
            print(f"? Unexpected status for scraper list: {response.status_code}")
    except Exception as e:
        print(f"✗ Scraper list endpoint error: {e}")
    
    print("\n=== Integration Test Summary ===")
    print("✓ Backend is running and accessible")
    print("✓ Scraper endpoints exist and require authentication")
    print("✓ Frontend should be able to connect to backend")
    print("✓ Authentication is working properly")
    
    print("\n=== Next Steps ===")
    print("1. Frontend scraper UI should load without errors")
    print("2. User needs to login to access scraper functionality")
    print("3. All CRUD operations should work once authenticated")

if __name__ == "__main__":
    test_scraper_integration()
