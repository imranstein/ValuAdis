#!/usr/bin/env python3
"""Simple authentication test without spatial dependencies"""

import requests
import json
import sqlite3
from app.core.security import get_password_hash

def create_simple_user():
    """Create user directly in SQLite without spatial dependencies"""
    
    # Connect to SQLite database
    conn = sqlite3.connect('valuadis.db')
    cursor = conn.cursor()
    
    try:
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            municipality TEXT,
            license_number TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0,
            is_valuer BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Delete existing admin user
        cursor.execute("DELETE FROM users WHERE email = ?", ("admin@valuadis.com",))
        
        # Create new admin user
        password_hash = get_password_hash("admin123")
        cursor.execute('''
        INSERT INTO users (
            email, full_name, phone, password_hash, municipality, 
            license_number, is_active, is_verified, is_admin, is_valuer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "admin@valuadis.com",
            "System Administrator", 
            "+251911000000",
            password_hash,
            "Addis Ababa",
            "ADMIN-001",
            1, 1, 1, 1
        ))
        
        conn.commit()
        print("✅ Created admin user successfully")
        
        # Verify user was created
        cursor.execute("SELECT id, email, is_admin FROM users WHERE email = ?", ("admin@valuadis.com",))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verified user: ID={user[0]}, Email={user[1]}, Admin={user[2]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def test_authentication():
    """Test authentication with the created user"""
    
    login_data = {
        "email": "admin@valuadis.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8020/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Login Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful!")
            print(f"Token: {token[:50]}...")
            
            # Test getting current user
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(
                "http://localhost:8020/api/v1/users/me",
                headers=headers,
                timeout=10
            )
            print(f"Current User Status: {user_response.status_code}")
            print(f"Current User: {user_response.text[:200]}...")
            
            return token
        else:
            print("❌ Login failed")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Creating simple user...")
    create_simple_user()
    
    print("\n🔐 Testing authentication...")
    token = test_authentication()
    
    if token:
        print("\n✅ Authentication fixed!")
    else:
        print("\n❌ Authentication still failing")
