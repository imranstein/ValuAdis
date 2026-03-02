"""
User Seeder

Creates test users for Ethiopian property valuation system
"""

import bcrypt
from sqlalchemy.orm import Session
from app.data.models.user import User
from app.core.database import get_db


class UserSeeder:
    """Seeder for creating test users"""
    
    ETHIOPIAN_TEST_USERS = [
        {
            "email": "tesfaye@valuadis.et",
            "full_name": "Tesfaye Alemu",
            "phone": "+251911234567",
            "municipality": "Addis Ababa",
            "license_number": "VAL-ET-2024-001"
        },
        {
            "email": "hanna@valuadis.et", 
            "full_name": "Hanna Tesfaye",
            "phone": "+251912345678",
            "municipality": "Dire Dawa",
            "license_number": "VAL-ET-2024-002"
        },
        {
            "email": "bekele@valuadis.et",
            "full_name": "Bekele Mekonnen", 
            "phone": "+251913456789",
            "municipality": "Mekelle",
            "license_number": "VAL-ET-2024-003"
        }
    ]
    
    @staticmethod
    def seed_users(db: Session) -> list[User]:
        """Create test users"""
        created_users = []
        
        for user_data in UserSeeder.ETHIOPIAN_TEST_USERS:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                created_users.append(existing_user)
                continue
            
            # Hash password
            password_hash = bcrypt.hashpw("test123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                password_hash=password_hash,
                municipality=user_data["municipality"],
                license_number=user_data["license_number"],
                is_active=True,
                is_verified=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            
            print(f"✅ Created user: {user.email} ({user.municipality})")
        
        return created_users
    
    @staticmethod
    def clear_users(db: Session) -> None:
        """Clear all test users"""
        db.query(User).delete()
        db.commit()
        print("🧹 Cleared all users")


def run_user_seeder():
    """Run user seeder"""
    db = next(get_db())
    try:
        UserSeeder.clear_users(db)
        users = UserSeeder.seed_users(db)
        print(f"🌱 Seeded {len(users)} Ethiopian test users")
        return users
    finally:
        db.close()


if __name__ == "__main__":
    run_user_seeder()
