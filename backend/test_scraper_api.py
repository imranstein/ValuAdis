#!/usr/bin/env python3
"""
Test Scraper API Directly
"""

from app.core.database import SessionLocal
from app.services.scraper_service import ScraperService
from app.api.schemas.scraper import ScraperTargetCreate
import json

def test_scraper_service():
    """Test scraper service directly without authentication"""
    db = SessionLocal()
    
    try:
        print("=== Testing Scraper Service ===")
        
        # Test get all scrapers
        scrapers = ScraperService.get_all_scrapers(db)
        print(f"✓ Found {len(scrapers)} scrapers")
        
        # Test get scraper stats
        stats = ScraperService.get_scraper_stats(db)
        print(f"✓ Scraper stats: total_scrapers={stats.total_scrapers}, active_scrapers={stats.active_scrapers}")
        
        # Test create new scraper
        new_scraper_data = ScraperTargetCreate(
            domain="test-site.com",
            url_template="https://test-site.com/properties?page={page}",
            enabled=True,
            selectors={
                "title": ".property-title",
                "price": ".property-price", 
                "location": ".property-location",
                "listing_url": ".property-link"
            },
            schedule="daily",
            max_pages=10
        )
        
        new_scraper = ScraperService.create_scraper(db, new_scraper_data)
        print(f"✓ Created new scraper: {new_scraper.domain} (ID: {new_scraper.id})")
        
        # Test get scraper by ID
        found_scraper = ScraperService.get_scraper_by_id(db, new_scraper.id)
        print(f"✓ Found scraper by ID: {found_scraper.domain}")
        
        # Test update scraper
        from app.api.schemas.scraper import ScraperTargetUpdate
        update_data = ScraperTargetUpdate(max_pages=20)
        updated_scraper = ScraperService.update_scraper(db, new_scraper.id, update_data)
        print(f"✓ Updated scraper max_pages to: {updated_scraper.max_pages}")
        
        # Test toggle scraper
        toggled_scraper = ScraperService.toggle_scraper(db, new_scraper.id)
        print(f"✓ Toggled scraper enabled to: {toggled_scraper.enabled}")
        
        # Test delete scraper
        success = ScraperService.delete_scraper(db, new_scraper.id)
        print(f"✓ Deleted scraper: {success}")
        
        print("\n=== All Scraper Service Tests Passed! ===")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_scraper_service()
