#!/usr/bin/env python3
"""
Add sample scraper data for testing
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.data.models.scraper import ScraperTarget
from datetime import datetime, timezone

def add_sample_scrapers():
    """Add sample scraper data"""
    # Create a single timezone-aware timestamp for all records
    now = datetime.now(tz=timezone.utc)
    print("Connecting to database")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Sample property scrapers
        property_scrapers = [
            {
                'domain': 'addisproperty.gov.et',
                'url_template': 'https://addisproperty.gov.et/listings?page={page}',
                'enabled': True,
                'selectors': {
                    'property_title': '.property-title',
                    'price': '.price',
                    'location': '.location',
                    'bedrooms': '.bedrooms',
                    'bathrooms': '.bathrooms'
                },
                'schedule': 'daily',
                'max_pages': 50,
                'last_status': 'success',
                'total_listings': 156,
                'last_run': now
            },
            {
                'domain': 'ethioproperty.com',
                'url_template': 'https://ethioproperty.com/properties?page={page}',
                'enabled': True,
                'selectors': {
                    'property_title': '.listing-title',
                    'price': '.listing-price',
                    'location': '.listing-location',
                    'bedrooms': '.beds',
                    'bathrooms': '.baths'
                },
                'schedule': 'twice_daily',
                'max_pages': 30,
                'last_status': 'success',
                'total_listings': 89,
                'last_run': now
            },
            {
                'domain': 'mekelleproperty.et',
                'url_template': 'https://mekelleproperty.et/listings?page={page}',
                'enabled': False,
                'selectors': {
                    'property_title': '.title',
                    'price': '.price-tag',
                    'location': '.address'
                },
                'schedule': 'daily',
                'max_pages': 20,
                'last_status': 'error',
                'total_listings': 45,
                'last_run': now
            }
        ]
        
        # Sample vehicle scrapers
        vehicle_scrapers = [
            {
                'domain': 'ethiocar.com',
                'url_template': 'https://ethiocar.com/vehicles?page={page}',
                'enabled': True,
                'selectors': {
                    'make': '.vehicle-make',
                    'model': '.vehicle-model',
                    'price': '.vehicle-price',
                    'year': '.vehicle-year',
                    'mileage': '.mileage'
                },
                'schedule': 'every_4_hours',
                'max_pages': 100,
                'last_status': 'success',
                'total_listings': 234,
                'last_run': now
            },
            {
                'domain': 'addisauto.et',
                'url_template': 'https://addisauto.et/cars?page={page}',
                'enabled': True,
                'selectors': {
                    'make': '.car-make',
                    'model': '.car-model',
                    'price': '.car-price',
                    'year': '.car-year'
                },
                'schedule': 'every_6_hours',
                'max_pages': 80,
                'last_status': 'success',
                'total_listings': 178,
                'last_run': now
            }
        ]
        
        # Add property scrapers (check for duplicates)
        for scraper_data in property_scrapers:
            existing = db.query(ScraperTarget).filter_by(domain=scraper_data['domain']).first()
            if existing:
                print(f"Property scraper for {scraper_data['domain']} already exists, skipping")
                continue
            scraper = ScraperTarget(**scraper_data)
            scraper.last_run = now
            db.add(scraper)
        
        # Add vehicle scrapers (check for duplicates)
        for scraper_data in vehicle_scrapers:
            existing = db.query(ScraperTarget).filter_by(domain=scraper_data['domain']).first()
            if existing:
                print(f"Vehicle scraper for {scraper_data['domain']} already exists, skipping")
                continue
            scraper = ScraperTarget(**scraper_data)
            scraper.last_run = now
            db.add(scraper)
        
        db.commit()
        print(f"Added {len(property_scrapers)} property scrapers and {len(vehicle_scrapers)} vehicle scrapers")
        
    except Exception as e:
        print(f"Error adding scrapers: {e}")
        db.rollback()
        raise  # Re-raise exception to ensure non-zero exit code
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    add_sample_scrapers()
