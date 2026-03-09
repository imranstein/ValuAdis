#!/usr/bin/env python3
"""Fix authentication issues"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.data.models.user import User

def fix_auth():
    """Create a working admin user"""
    db = SessionLocal()
    try:
        # Delete existing admin user
        admin = db.query(User).filter(User.email == "admin@valuadis.com").first()
        if admin:
            db.delete(admin)
            db.commit()
            print("Deleted existing admin user")
        
        # Create new admin user with simple password
        admin_user = User(
            email="admin@valuadis.com",
            full_name="System Administrator",
            phone="+251911000000",
            password_hash=get_password_hash("admin123"),
            municipality="Addis Ababa",
            license_number="ADMIN-001",
            is_active=True,
            is_verified=True,
            is_admin=True,
            is_valuer=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Created new admin user:")
        print(f"   Email: admin@valuadis.com")
        print(f"   Password: admin123")
        print(f"   ID: {admin_user.id}")
        print(f"   Is Admin: {admin_user.is_admin}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_auth()
