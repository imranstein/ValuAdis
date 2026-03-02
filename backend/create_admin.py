import asyncio
import sys
import os
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.data.models.user import User

async def main():
    db = SessionLocal()
    try:
        from app.core.security import get_password_hash
        user = User(
            email="admin@valuadis.com",
            password_hash=get_password_hash("password123"),
            full_name="System Admin",
            phone="+251911000000",
            municipality="Addis Ababa",
            license_number="ADMIN-001",
            is_active=True,
            is_verified=True,
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
