#!/usr/bin/env python3
"""Create fresh admin user with known password"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User
from app.core.security import get_password_hash

async def create_fresh_admin():
    """Create fresh admin user"""
    db = SessionLocal()
    try:
        # Delete existing admin user
        existing_admin = db.query(User).filter(User.email == "admin@valuadis.com").first()
        if existing_admin:
            # Delete properties first to avoid foreign key issues
            from app.data.models.property import Property
            db.query(Property).filter(Property.user_id == existing_admin.id).delete()
            db.delete(existing_admin)
            db.commit()
            print("Deleted existing admin user and their properties")
        
        # Create new admin user
        user = User(
            email="admin@valuadis.com",
            password_hash=get_password_hash("admin123"),
            full_name="System Admin",
            phone="+251911000001",
            municipality="Addis Ababa",
            license_number="ADMIN-001",
            is_active=True,
            is_verified=True,
            is_admin=True,
            is_valuer=True,
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Created fresh admin user:")
        print(f"   Email: admin@valuadis.com")
        print(f"   Password: admin123")
        print(f"   ID: {user.id}")
        print(f"   Is Admin: {user.is_admin}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_fresh_admin())
