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
        # Real Ethiopian property portals. Domains must match the keys in
        # scraper/extractors.py EXTRACTORS so the run worker uses the
        # site-specific extractor. Selectors are informational fallbacks only.
        property_scrapers = [
            {
                'domain': 'ethiopiapropertycentre.com',
                'url_template': 'https://ethiopiapropertycentre.com/for-sale?page={page}',
                'enabled': True,
                'selectors': {
                    'item': 'div.wp-block.property.list',
                    'title': '.wp-block-title h3',
                    'price': 'span.price',
                    'location': 'address'
                },
                'schedule': 'daily',
                'max_pages': 10
            },
            {
                'domain': 'jiji.com.et',
                'url_template': 'https://jiji.com.et/real-estate?page={page}',
                'enabled': False,
                'selectors': {
                    'item': '.b-list-advert-base',
                    'title': '.qa-advert-title',
                    'price': '.qa-advert-price'
                },
                'schedule': 'daily',
                'max_pages': 10
            },
            {
                'domain': 'zegebeya.com',
                'url_template': 'https://zegebeya.com/property-search/page/{page}/',
                'enabled': False,
                'selectors': {
                    'item': '.rh_list_card__wrap',
                    'title': 'h3 a',
                    'price': '.rh_prop_card__price'
                },
                'schedule': 'daily',
                'max_pages': 10
            },
            {
                'domain': 'ethiopianproperties.com',
                'url_template': 'https://www.ethiopianproperties.com/property-search/page/{page}/',
                'enabled': False,
                'selectors': {
                    'item': 'article.property',
                    'title': 'h3 a',
                    'price': '.price'
                },
                'schedule': 'daily',
                'max_pages': 10
            },
            {
                'domain': 'livingethio.com',
                'url_template': 'https://livingethio.com/properties?page={page}',
                'enabled': False,
                'selectors': {
                    'item': '.p-card',
                    'title': '.p-card-title',
                    'price': '.price'
                },
                'schedule': 'daily',
                'max_pages': 10
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
            db.add(scraper)
        
        # Add vehicle scrapers (check for duplicates)
        for scraper_data in vehicle_scrapers:
            existing = db.query(ScraperTarget).filter_by(domain=scraper_data['domain']).first()
            if existing:
                print(f"Vehicle scraper for {scraper_data['domain']} already exists, skipping")
                continue
            scraper = ScraperTarget(**scraper_data)
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
