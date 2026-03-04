#!/usr/bin/env python3
"""
Create Test User for Authentication Testing
"""

from app.core.database import SessionLocal
from app.data.models.user import User
from app.core.security import get_password_hash
import sys

def create_test_user():
    """Create a test user for scraper UI testing"""
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "scraper@test.com").first()
        if existing_user:
            print("✓ Test user already exists: scraper@test.com")
            print(f"  ID: {existing_user.id}")
            print(f"  Name: {existing_user.full_name}")
            return existing_user
        
        # Create new test user
        test_user = User(
            email="scraper@test.com",
            full_name="Scraper Test User",
            phone="0911000002",
            password_hash=get_password_hash("testpass123"),
            municipality="Addis Ababa",
            license_number="SCRAPER123",
            is_active=True,
            is_verified=True,
            is_admin=False,
            is_valuer=True  # Give valuer permissions for testing
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✓ Created test user successfully:")
        print(f"  Email: scraper@test.com")
        print(f"  Password: testpass123")
        print(f"  ID: {test_user.id}")
        print(f"  Name: {test_user.full_name}")
        print(f"  Is Valuer: {test_user.is_valuer}")
        
        return test_user
        
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    user = create_test_user()
    if user:
        print("\n=== Test User Ready for Login ===")
        print("Use these credentials to test the scraper UI:")
        print("Email: scraper@test.com")
        print("Password: testpass123")
    else:
        print("Failed to create test user")
        sys.exit(1)
