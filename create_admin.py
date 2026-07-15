import asyncio
import os
import sys

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.modules.auth.schemas import UserCreate

async def main():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@valuadis.com")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        sys.exit("Error: ADMIN_PASSWORD environment variable must be set")

    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        user_in = UserCreate(
            email=admin_email,
            password=admin_password,
            full_name="System Admin",
            phone="+251911000000",
            municipality="Addis Ababa",
            license_number="ADMIN-001"
        )
        user = await auth_service.register_user(user_in)
        print(f"Created user: {user.email}")

        # Verify the user
        user.is_verified = True
        user.is_active = True
        db.commit()
        print("Activated and verified user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
