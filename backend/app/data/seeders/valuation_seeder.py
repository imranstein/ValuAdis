"""
Valuation Seeder

Creates test valuations for Ethiopian properties
"""

from sqlalchemy.orm import Session
from app.data.models.valuation import Valuation, PropertyType, ValuationStatus
from app.core.database import get_db


class ValuationSeeder:
    """Seeder for creating test valuations"""
    
    ETHIOPIAN_TEST_VALUATIONS = [
        {
            "property_type": PropertyType.RESIDENTIAL,
            "municipality": "Addis Ababa",
            "area_sqm": 120.0,
            "market_value": 150000.0,
            "taxable_value": 37500.0,
            "status": ValuationStatus.APPROVED,
            "coordinates_wkt": "SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))",
            "notes": "Residential property in Bole area with modern amenities"
        },
        {
            "property_type": PropertyType.COMMERCIAL,
            "municipality": "Dire Dawa",
            "area_sqm": 250.0,
            "market_value": 500000.0,
            "taxable_value": 125000.0,
            "status": ValuationStatus.PENDING,
            "coordinates_wkt": "SRID=4326;POLYGON((41.8667 9.6000, 41.8670 9.6000, 41.8670 9.5998, 41.8667 9.5998, 41.8667 9.6000))",
            "notes": "Commercial property in Piassa business district"
        },
        {
            "property_type": PropertyType.AGRICULTURAL,
            "municipality": "Mekelle",
            "area_sqm": 5000.0,
            "market_value": 200000.0,
            "taxable_value": 50000.0,
            "status": ValuationStatus.DRAFT,
            "coordinates_wkt": "SRID=4326;POLYGON((39.4733 13.4967, 39.4740 13.4967, 39.4740 13.4960, 39.4733 13.4960, 39.4733 13.4967))",
            "notes": "Agricultural land suitable for farming"
        }
    ]
    
    @staticmethod
    def seed_valuations(db: Session, users: list, properties: list) -> list[Valuation]:
        """Create test valuations for users and properties"""
        from geoalchemy2.elements import WKTElement
        
        created_valuations = []
        
        for i, valuation_data in enumerate(ValuationSeeder.ETHIOPIAN_TEST_VALUATIONS):
            # Assign to user and property (cycle through)
            user = users[i % len(users)]
            property = properties[i % len(properties)]
            
            # Check if valuation already exists
            existing_valuation = db.query(Valuation).filter(
                Valuation.user_id == user.id,
                Valuation.property_id == property.id
            ).first()
            
            if existing_valuation:
                created_valuations.append(existing_valuation)
                continue
            
            # Create geometry from WKT
            geometry = WKTElement(valuation_data["coordinates_wkt"], srid=4326)
            
            # Create valuation
            valuation = Valuation(
                property_id=property.id,
                user_id=user.id,
                property_type=valuation_data["property_type"],
                municipality=valuation_data["municipality"],
                area_sqm=valuation_data["area_sqm"],
                market_value=valuation_data["market_value"],
                taxable_value=valuation_data["taxable_value"],
                status=valuation_data["status"],
                coordinates=geometry,
                notes=valuation_data["notes"]
            )
            
            db.add(valuation)
            db.commit()
            db.refresh(valuation)
            created_valuations.append(valuation)
            
            print(f"✅ Created valuation: {valuation.property_type.value} ({valuation.municipality}) for {user.email}")
        
        return created_valuations
    
    @staticmethod
    def clear_valuations(db: Session) -> None:
        """Clear all test valuations"""
        db.query(Valuation).delete()
        db.commit()
        print("🧹 Cleared all valuations")


def run_valuation_seeder():
    """Run valuation seeder"""
    from .user_seeder import UserSeeder
    from .property_seeder import PropertySeeder
    
    db = next(get_db())
    try:
        # Get users and properties first
        users = UserSeeder.seed_users(db)
        properties = PropertySeeder.seed_properties(db, users)
        
        # Clear and seed valuations
        ValuationSeeder.clear_valuations(db)
        valuations = ValuationSeeder.seed_valuations(db, users, properties)
        print(f"🌱 Seeded {len(valuations)} Ethiopian test valuations")
        return valuations
    finally:
        db.close()


if __name__ == "__main__":
    run_valuation_seeder()
