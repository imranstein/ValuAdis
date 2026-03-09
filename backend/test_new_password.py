#!/usr/bin/env python3
"""Test new admin password"""

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

async def test_new_password():
    """Test new admin password"""
    db = SessionLocal()
    try:
        print("=== Testing New Password ===")
        
        # Step 1: Check user
        user = db.query(User).filter(User.email == "admin@valuadis.com").first()
        
        if user:
            print(f"✅ User found: {user.email}")
            
            # Step 2: Test password verification
            test_password = "Admin123!"
            if verify_password(test_password, user.password_hash):
                print(f"✅ Password '{test_password}' verification successful")
                
                # Step 3: Test AuthService
                auth_service = AuthService(db)
                
                try:
                    auth_user = await auth_service.authenticate_user("admin@valuadis.com", test_password)
                    print(f"✅ AuthService authentication successful")
                    print(f"   User ID: {auth_user.id}")
                    print(f"   Email: {auth_user.email}")
                    print(f"   Is Admin: {auth_user.is_admin}")
                    
                    # Generate token
                    from app.core.security import create_access_token
                    token = create_access_token(data={"sub": str(auth_user.id)})
                    print(f"✅ Generated token: {token[:50]}...")
                    
                except AuthenticationException as e:
                    print(f"❌ AuthService authentication failed: {e}")
                except Exception as e:
                    print(f"❌ AuthService error: {e}")
            else:
                print(f"❌ Password '{test_password}' verification failed")
        else:
            print("❌ User not found")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_new_password())
