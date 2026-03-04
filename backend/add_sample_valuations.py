#!/usr/bin/env python3
"""
Add sample valuation data for testing reports
"""

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.data.models import User, Property, Valuation
from app.data.models.valuation import PropertyType, ValuationStatus
from datetime import datetime, timedelta
import random

def add_sample_valuations():
    """Add sample valuation data"""
    # Parse DATABASE_URL to extract non-sensitive parts
    from urllib.parse import urlparse
    parsed_url = urlparse(settings.DATABASE_URL)
    safe_db_info = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port or '5432'}/{parsed_url.path.lstrip('/')}"
    print(f"Connecting to database: {safe_db_info}")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get the first user (created earlier)
        user = db.query(User).first()
        if not user:
            print("No user found. Please create a user first.")
            return
        
        # Create sample properties first
        properties = []
        municipalities = ["Addis Ababa", "Mekelle", "Gondar", "Bahirdar", "Hawassa"]
        property_types = ["residential", "commercial", "agricultural"]
        
        for i in range(10):
            # Create a simple polygon for the property boundary
            # Using a simple square around a random point in Ethiopia
            lat = 9.0 + random.uniform(-2, 2)  # Ethiopia latitude range
            lng = 40.0 + random.uniform(-3, 3)  # Ethiopia longitude range
            size = 0.001  # Small square ~100m
            
            boundary_wkt = f"POLYGON(({lng} {lat}, {lng+size} {lat}, {lng+size} {lat+size}, {lng} {lat+size}, {lng} {lat}))"
            
            prop = Property(
                user_id=user.id,
                address=f"Property {i+1} Street, {random.choice(municipalities)}",
                municipality=random.choice(municipalities),
                property_type=random.choice(property_types),
                area_sqm=random.uniform(100, 1000),
                boundary=func.ST_GeomFromText(boundary_wkt, 4326),
                status="valued"
            )
            db.add(prop)
            properties.append(prop)
        
        db.commit()
        print(f"Created {len(properties)} sample properties")
        
        # Convert string property type to enum (moved outside loop)
        prop_type_map = {
            "residential": PropertyType.RESIDENTIAL,
            "commercial": PropertyType.COMMERCIAL,
            "agricultural": PropertyType.AGRICULTURAL
        }
        
        # Now create valuations for these properties
        valuations = []
        for i, prop in enumerate(properties):
            # Generate realistic Ethiopian property values (in Birr)
            base_value = random.uniform(500000, 5000000)  # 500K to 5M Birr
            
            valuation = Valuation(
                property_id=prop.id,
                user_id=user.id,
                property_type=prop_type_map.get(prop.property_type, PropertyType.RESIDENTIAL),
                municipality=prop.municipality,
                area_sqm=prop.area_sqm,
                market_value=base_value,
                taxable_value=base_value * 0.25,  # 25% per Proclamation 1365/2025
                status=random.choice(list(ValuationStatus)),
                valuation_date=datetime.now() - timedelta(days=random.randint(0, 365)),
                notes=f"Valuation for property at {prop.address}"
            )
            db.add(valuation)
            valuations.append(valuation)
        
        db.commit()
        print(f"Created {len(valuations)} sample valuations")
        
        # Print summary statistics
        total_valuations = db.query(Valuation).count()
        total_value = db.query(Valuation).with_entities(func.sum(Valuation.market_value)).scalar() or 0
        avg_value = total_value / total_valuations if total_valuations > 0 else 0
        
        print(f"\n📊 Valuation Summary:")
        print(f"   Total Valuations: {total_valuations}")
        print(f"   Total Market Value: ETB {total_value:,.0f}")
        print(f"   Average Value: ETB {avg_value:,.0f}")
        
    except Exception as e:
        print(f"Error adding valuations: {e}")
        db.rollback()
        raise  # Re-raise exception to ensure non-zero exit code
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    add_sample_valuations()
