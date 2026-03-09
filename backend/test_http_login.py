#!/usr/bin/env python3
"""Test HTTP login to get valid token"""

import requests
import json

def test_http_login():
    """Test login via HTTP to get valid token"""
    
    login_data = {
        "email": "admin@valuadis.com", 
        "password": "Admin123!"
    }
    
    response = requests.post(
        "http://localhost:8020/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token: {token}")
        
        # Test the token
        headers = {"Authorization": f"Bearer {token}"}
        test_response = requests.get(
            "http://localhost:8020/api/v1/scrapers/",
            headers=headers
        )
        print(f"Scrapers Test Status: {test_response.status_code}")
        print(f"Scrapers Response: {test_response.text}")
    else:
        print("Login failed")

if __name__ == "__main__":
    test_http_login()
