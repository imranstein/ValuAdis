#!/usr/bin/env python3
"""Fix admin user privileges"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User

async def fix_admin():
    """Fix admin user to have admin privileges"""
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.email == "admin@valuadis.com").first()
        
        if admin:
            print(f"Updating admin user: {admin.email}")
            print(f"  Current is_admin: {admin.is_admin}")
            print(f"  Current is_valuer: {admin.is_valuer}")
            
            # Update to be both admin and valuer
            admin.is_admin = True
            admin.is_valuer = True
            admin.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(admin)
            
            print(f"✅ Updated admin user:")
            print(f"  New is_admin: {admin.is_admin}")
            print(f"  New is_valuer: {admin.is_valuer}")
        else:
            print("❌ Admin user not found")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fix_admin())
