#!/usr/bin/env python3
"""Test login with new password"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

async def test_login():
    """Test login API with new password"""
    client = TestClient(app)
    
    # Test login with new password
    login_data = {
        "email": "admin@valuadis.com",
        "password": "Admin123!"
    }
    
    print(f"Testing login with: {login_data}")
    
    response = client.post(
        "/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Login API successful!")
        data = response.json()
        print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
        return data.get('access_token')
    else:
        print("❌ Login API failed!")
        return None

if __name__ == "__main__":
    asyncio.run(test_login())
