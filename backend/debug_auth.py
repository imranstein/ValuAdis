#!/usr/bin/env python3
"""Debug authentication flow"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User
from app.services.auth_service import AuthService
from app.core.security import verify_password
from app.core.exceptions import AuthenticationException

async def debug_auth():
    """Debug authentication flow step by step"""
    db = SessionLocal()
    try:
        print("=== Authentication Debug ===")
        
        # Step 1: Check if user exists in database
        print("\n1. Checking user in database...")
        user = db.query(User).filter(User.email == "admin@valuadis.com").first()
        
        if user:
            print(f"✅ User found:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Is Admin: {user.is_admin}")
            print(f"   Is Valuer: {user.is_valuer}")
        else:
            print("❌ User not found")
            return
        
        # Step 2: Test password verification
        print("\n2. Testing password verification...")
        if verify_password("password123", user.password_hash):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            return
        
        # Step 3: Test AuthService
        print("\n3. Testing AuthService...")
        auth_service = AuthService(db)
        
        try:
            auth_user = await auth_service.authenticate_user("admin@valuadis.com", "password123")
            print(f"✅ AuthService authentication successful")
            print(f"   User ID: {auth_user.id}")
            print(f"   Email: {auth_user.email}")
        except AuthenticationException as e:
            print(f"❌ AuthService authentication failed: {e}")
            return
        except Exception as e:
            print(f"❌ AuthService error: {e}")
            return
        
        print("\n=== Authentication Debug Complete ===")
        print("✅ All authentication steps passed!")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_auth())
