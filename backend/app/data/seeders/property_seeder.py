"""
Property Seeder

Creates test properties with Ethiopian spatial data
"""

from sqlalchemy.orm import Session
from app.data.models.property import Property
from app.core.database import get_db


class PropertySeeder:
    """Seeder for creating test properties with Ethiopian coordinates"""
    
    ETHIOPIAN_TEST_PROPERTIES = [
        {
            "address": "Bole Subcity, Addis Ababa",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "area_sqm": 120.0,
            "boundary_wkt": "SRID=4326;POLYGON((38.7578 9.0320, 38.7580 9.0320, 38.7580 9.0318, 38.7578 9.0318, 38.7578 9.0320))",
            "market_value": 150000.0,
            "taxable_value": 37500.0
        },
        {
            "address": "Piassa, Dire Dawa",
            "municipality": "Dire Dawa", 
            "property_type": "commercial",
            "area_sqm": 250.0,
            "boundary_wkt": "SRID=4326;POLYGON((41.8667 9.6000, 41.8670 9.6000, 41.8670 9.5998, 41.8667 9.5998, 41.8667 9.6000))",
            "market_value": 500000.0,
            "taxable_value": 125000.0
        },
        {
            "address": "Mekelle City Center",
            "municipality": "Mekelle",
            "property_type": "agricultural", 
            "area_sqm": 5000.0,
            "boundary_wkt": "SRID=4326;POLYGON((39.4733 13.4967, 39.4740 13.4967, 39.4740 13.4960, 39.4733 13.4960, 39.4733 13.4967))",
            "market_value": 200000.0,
            "taxable_value": 50000.0
        }
    ]
    
    @staticmethod
    def seed_properties(db: Session, users: list) -> list[Property]:
        """Create test properties for users"""
        from geoalchemy2.elements import WKTElement
        
        created_properties = []
        
        for i, property_data in enumerate(PropertySeeder.ETHIOPIAN_TEST_PROPERTIES):
            # Assign to user (cycle through users)
            user = users[i % len(users)]
            
            # Check if property already exists for this user
            existing_property = db.query(Property).filter(
                Property.user_id == user.id,
                Property.address == property_data["address"]
            ).first()
            
            if existing_property:
                created_properties.append(existing_property)
                continue
            
            # Create geometry from WKT
            geometry = WKTElement(property_data["boundary_wkt"], srid=4326)
            
            # Create property
            property = Property(
                user_id=user.id,
                address=property_data["address"],
                municipality=property_data["municipality"],
                property_type=property_data["property_type"],
                boundary=geometry,
                area_sqm=property_data["area_sqm"],
                market_value=property_data["market_value"],
                taxable_value=property_data["taxable_value"],
                status="valued"
            )
            
            db.add(property)
            db.commit()
            db.refresh(property)
            created_properties.append(property)
            
            print(f"✅ Created property: {property.address} ({property.municipality}) for {user.email}")
        
        return created_properties
    
    @staticmethod
    def clear_properties(db: Session) -> None:
        """Clear all test properties"""
        db.query(Property).delete()
        db.commit()
        print("🧹 Cleared all properties")


def run_property_seeder():
    """Run property seeder"""
    from .user_seeder import UserSeeder
    
    db = next(get_db())
    try:
        # Get users first
        users = UserSeeder.seed_users(db)
        
        # Clear and seed properties
        PropertySeeder.clear_properties(db)
        properties = PropertySeeder.seed_properties(db, users)
        print(f"🌱 Seeded {len(properties)} Ethiopian test properties")
        return properties
    finally:
        db.close()


if __name__ == "__main__":
    run_property_seeder()
