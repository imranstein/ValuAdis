#!/usr/bin/env python3
"""Test authentication with database"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User
from app.core.security import verify_password, get_password_hash

async def check_admin():
    """Check admin user in database"""
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.email == "admin@valuadis.com").first()
        
        if admin:
            print(f"Admin user found:")
            print(f"  Email: {admin.email}")
            print(f"  Full Name: {admin.full_name}")
            print(f"  Is Admin: {admin.is_admin}")
            print(f"  Is Active: {admin.is_active}")
            print(f"  Password Hash: {admin.password_hash[:50]}...")
            
            # Test password verification
            test_passwords = ["password123", "admin", "password", "123456"]
            for pwd in test_passwords:
                if verify_password(pwd, admin.password_hash):
                    print(f"✅ Password '{pwd}' is correct!")
                    return pwd
                else:
                    print(f"❌ Password '{pwd}' is incorrect")
        else:
            print("❌ Admin user not found in database")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
    
    return None

if __name__ == "__main__":
    asyncio.run(check_admin())
