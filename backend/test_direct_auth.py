#!/usr/bin/env python3
"""Direct authentication test"""

import requests
import json
import sqlite3
from app.core.security import get_password_hash, verify_password

def create_working_user():
    """Create user directly and test password verification"""
    
    # Connect to database
    conn = sqlite3.connect('valuadis.db')
    cursor = conn.cursor()
    
    try:
        # Drop and recreate users table
        cursor.execute("DROP TABLE IF EXISTS users")
        
        cursor.execute('''
        CREATE TABLE users (
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
        
        # Create admin user
        password = "admin123"
        password_hash = get_password_hash(password)
        
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
        
        # Test password verification
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", ("admin@valuadis.com",))
        result = cursor.fetchone()
        
        if result and verify_password(password, result[0]):
            print("✅ User created and password verified successfully")
            return True
        else:
            print("❌ Password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

def test_login():
    """Test login via HTTP"""
    
    login_data = {
        "email": "admin@valuadis.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8020/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ HTTP Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating working user...")
    if create_working_user():
        print("\n🔐 Testing HTTP login...")
        if test_login():
            print("✅ Authentication working!")
        else:
            print("❌ HTTP login still failing")
    else:
        print("❌ User creation failed")
