import asyncio
import logging
import argparse
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.services.scraper_service import ScraperService
from app.data.models.scraper import ScraperLog
from app.data.models.property import Property
from playwright.async_api import async_playwright

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ValuAdis_Scraper")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

class ScraperRunner:
    def __init__(self, scraper_id: int, max_pages: int = 5, target_items: int = 100):
        self.scraper_id = scraper_id
        self.max_pages = max_pages
        self.target_items = target_items
        self.db = SessionLocal()

    async def run_scraper(self):
        """Run a specific scraper by ID"""
        scraper = ScraperService.get_scraper_by_id(self.db, self.scraper_id)
        if not scraper:
            logger.error(f"Scraper {self.scraper_id} not found")
            return

        logger.info(f"Starting scraper: {scraper.domain}")
        
        # Create log entry
        log = ScraperService.create_log(
            self.db,
            scraper_id=self.scraper_id,
            started_at=datetime.utcnow(),
            status="running"
        )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=USER_AGENTS[0],
                    viewport={'width': 1280, 'height': 720}
                )
                page = await context.new_page()

                total_found = 0
                total_saved = 0

                for page_num in range(1, self.max_pages + 1):
                    url = scraper.url_template.format(page=page_num)
                    logger.info(f"Scraping page {page_num}: {url}")

                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await asyncio.sleep(2)  # Wait for content to load

                        # Extract items using the scraper's selectors
                        items = await self.extract_items(page, scraper.selectors)
                        logger.info(f"Found {len(items)} items on page {page_num}")
                        total_found += len(items)

                        # Save items as properties
                        saved = await self.save_items(items, scraper.domain)
                        total_saved += saved
                        logger.info(f"Saved {saved} properties from page {page_num}")

                        if not items:
                            logger.info(f"No items found on page {page_num}, stopping pagination")
                            break

                    except Exception as e:
                        logger.error(f"Error scraping page {page_num}: {e}")
                        continue

                await browser.close()

            # Update scraper stats
            scraper.total_listings += total_saved
            scraper.last_run = datetime.utcnow()
            scraper.last_status = "success" if total_saved > 0 else "no_data"
            self.db.commit()

            # Update log
            log.completed_at = datetime.utcnow()
            log.status = "success"
            log.listings_found = total_found
            log.listings_saved = total_saved
            self.db.commit()

            logger.info(f"Scraper completed. Found: {total_found}, Saved: {total_saved}")

        except Exception as e:
            logger.error(f"Scraper failed: {e}")
            
            # Update log with error
            log.completed_at = datetime.utcnow()
            log.status = "failed"
            log.error_message = str(e)
            log.listings_found = total_found
            log.listings_saved = total_saved
            self.db.commit()

            # Update scraper status
            scraper.last_run = datetime.utcnow()
            scraper.last_status = "failed"
            self.db.commit()

        finally:
            self.db.close()

    async def extract_items(self, page, selectors):
        """Extract items from page using selectors"""
        items = []
        
        try:
            # Find all potential listing containers
            title_selector = selectors.get('title', 'h1')
            title_elements = await page.query_selector_all(title_selector)
            
            if not title_elements:
                logger.warning(f"No elements found for title selector: {title_selector}")
                return items

            for i, title_elem in enumerate(title_elements):
                if i >= 50:  # Limit to 50 items per page
                    break
                    
                item = {}
                
                # Extract title
                item['title'] = await title_elem.inner_text()
                
                # Extract other fields
                for field, selector in selectors.items():
                    if field == 'title':
                        continue
                    
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            item[field] = await elem.inner_text()
                    except Exception as e:
                        logger.debug(f"Could not extract {field}: {e}")
                        item[field] = None
                
                # Add URL if available
                if 'listing_url' in selectors:
                    try:
                        link_elem = await title_elem.query_selector('a')
                        if link_elem:
                            item['listing_url'] = await link_elem.get_attribute('href')
                    except:
                        pass
                
                items.append(item)

        except Exception as e:
            logger.error(f"Error extracting items: {e}")

        return items

    async def save_items(self, items, domain):
        """Save scraped items as properties"""
        saved_count = 0
        
        try:
            for item in items:
                if not item.get('title'):
                    continue
                
                # Create property from scraped data
                property_data = {
                    'user_id': 2,  # Real user
                    'address': item.get('location', f"Scraped from {domain}"),
                    'municipality': 'Addis Ababa',  # Default
                    'property_type': item.get('property_type', 'residential'),
                    'area_sqm': self.parse_number(item.get('area', '0')) or 100,  # Default 100 sqm
                    'market_value': self.parse_price(item.get('price', '0')),
                    'taxable_value': self.parse_price(item.get('price', '0')) * 0.25,  # 25% of market value
                    'status': 'scraped',
                    'boundary': 'SRID=4326;POLYGON((38.7468 9.0202, 38.7468 9.0242, 38.7508 9.0242, 38.7508 9.0202, 38.7468 9.0202))'  # Default Addis Ababa boundary
                }
                
                # Check if property already exists (by address)
                existing = self.db.query(Property).filter(
                    Property.address == property_data['address']
                ).first()
                
                if not existing:
                    prop = Property(**property_data)
                    self.db.add(prop)
                    saved_count += 1

            self.db.commit()
            logger.info(f"Saved {saved_count} new properties")
            
        except Exception as e:
            logger.error(f"Error saving properties: {e}")
            self.db.rollback()

        return saved_count

    def parse_number(self, text):
        """Parse number from text"""
        try:
            import re
            numbers = re.findall(r'[\d,]+', str(text))
            if numbers:
                return int(numbers[0].replace(',', ''))
        except:
            pass
        return 0

    def parse_price(self, text):
        """Parse price from text"""
        try:
            import re
            # Extract numbers from price text
            numbers = re.findall(r'[\d,]+', str(text))
            if numbers:
                return int(numbers[0].replace(',', ''))
        except:
            pass
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ValuAdis Scraper")
    parser.add_argument("--scraper-id", type=int, required=True, help="Scraper ID to run")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to scrape")
    parser.add_argument("--limit", type=int, default=100, help="Maximum items to collect")
    
    args = parser.parse_args()
    
    runner = ScraperRunner(
        scraper_id=args.scraper_id,
        max_pages=args.max_pages,
        target_items=args.limit
    )
    
    asyncio.run(runner.run_scraper())
