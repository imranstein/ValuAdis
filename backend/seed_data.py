"""
Complete Database Seeder

Run all seeders to populate Ethiopian test data
"""

from app.data.seeders.user_seeder import UserSeeder
from app.data.seeders.property_seeder import PropertySeeder
from app.data.seeders.valuation_seeder import ValuationSeeder
from app.core.database import get_db


def seed_all_data():
    """Seed all test data for Ethiopian property valuation system"""
    print("🌱 Starting Ethiopian property valuation system data seeding...")
    
    db = next(get_db())
    try:
        # Clear existing data
        print("🧹 Clearing existing data...")
        ValuationSeeder.clear_valuations(db)
        PropertySeeder.clear_properties(db)
        UserSeeder.clear_users(db)
        
        # Seed users
        print("👥 Seeding Ethiopian users...")
        users = UserSeeder.seed_users(db)
        
        # Seed properties
        print("🏠 Seeding Ethiopian properties...")
        properties = PropertySeeder.seed_properties(db, users)
        
        # Seed valuations
        print("💰 Seeding Ethiopian valuations...")
        valuations = ValuationSeeder.seed_valuations(db, users, properties)
        
        print(f"\n🎉 Successfully seeded Ethiopian test data:")
        print(f"   👥 Users: {len(users)}")
        print(f"   🏠 Properties: {len(properties)}")
        print(f"   💰 Valuations: {len(valuations)}")
        print(f"\n📋 Test Credentials:")
        print(f"   Email: tesfaye@valuadis.et")
        print(f"   Password: test123456")
        print(f"   Municipality: Addis Ababa")
        
        return {
            "users": users,
            "properties": properties,
            "valuations": valuations
        }
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_data()
