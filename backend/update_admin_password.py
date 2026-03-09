#!/usr/bin/env python3
"""Update admin password to admin123"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User
from app.core.security import get_password_hash

async def update_admin_password():
    """Update admin password"""
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.email == "admin@valuadis.com").first()
        
        if admin:
            # Update password
            admin.password_hash = get_password_hash("admin123")
            admin.is_admin = True
            admin.is_valuer = True
            admin.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(admin)
            
            print(f"✅ Updated admin user:")
            print(f"   Email: admin@valuadis.com")
            print(f"   Password: admin123")
            print(f"   ID: {admin.id}")
            print(f"   Is Admin: {admin.is_admin}")
            print(f"   Is Valuer: {admin.is_valuer}")
        else:
            print("❌ Admin user not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(update_admin_password())
