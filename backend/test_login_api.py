#!/usr/bin/env python3
"""Test login API directly"""

import asyncio
import sys
import os
import json

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.api.v1.endpoints.auth import login
from app.schemas.auth import UserLogin
from fastapi.testclient import TestClient
from app.main import app

async def test_login_api():
    """Test login API directly"""
    print("=== Testing Login API ===")
    
    client = TestClient(app)
    
    # Test login
    login_data = {
        "email": "admin@valuadis.com",
        "password": "password123"
    }
    
    print(f"\nSending login request with: {login_data}")
    
    response = client.post(
        "/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Login API successful!")
        data = response.json()
        print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
    else:
        print("❌ Login API failed!")

if __name__ == "__main__":
    asyncio.run(test_login_api())
