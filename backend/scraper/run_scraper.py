import asyncio
import logging
import argparse
import random
import urllib.robotparser
from urllib.parse import urlparse
from collections import deque
from playwright.async_api import async_playwright, Browser, Page

from scraper.extractors import EXTRACTORS
from app.core.database import SessionLocal, engine, Base
from app.data.models.market_listing import RawMarketListing
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AVM_Scraper")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

TARGETS = [
    {
        "url": "https://livingethio.com/site/property/list?page={page}",
        "domain": "livingethio.com",
        "extractor": EXTRACTORS["livingethio.com"]
    },
    {
        "url": "https://ethiopiapropertycentre.com/for-sale?page={page}",
        "domain": "ethiopiapropertycentre.com",
        "extractor": EXTRACTORS["ethiopiapropertycentre.com"]
    },
    {
        "url": "https://ethiopianproperties.com/rent/page/{page}/",
        "domain": "ethiopianproperties.com",
        "extractor": EXTRACTORS["ethiopianproperties.com"]
    },
    {
        "url": "https://zegebeya.com/properties-grid-fullwidth/page/{page}/",
        "domain": "zegebeya.com",
        "extractor": EXTRACTORS["zegebeya.com"]
    },
    {
        "url": "https://jiji.com.et/real-estate?page={page}",
        "domain": "jiji.com.et",
        "extractor": EXTRACTORS["jiji.com.et"]
    }
]

class Crawler:
    def __init__(self, headless=True, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.robots_cache = {}
        self.db = SessionLocal()

    async def get_random_ua(self) -> str:
        return random.choice(USER_AGENTS)

    def is_allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            try:
                rp.set_url(f"{base}/robots.txt")
                rp.read()
                self.robots_cache[base] = rp
            except Exception as e:
                logger.warning(f"Failed to read robots.txt for {base}: {e}")
                # Assume allowed if we can't read it
                return True
        return self.robots_cache[base].can_fetch("*", url)

    def save_listings(self, listings):
        if not listings:
            return 0
        saved_count = 0
        try:
            for item in listings:
                if not item.get("listing_url"):
                    continue
                # Upsert query
                stmt = insert(RawMarketListing).values(
                    title=item.get("title", "")[:500],
                    asking_price_etb=item.get("asking_price_etb"),
                    location_subcity=item.get("location_subcity", "")[:200],
                    area_sqm=item.get("area_sqm"),
                    property_type=item.get("property_type", "")[:100],
                    bedrooms=item.get("bedrooms"),
                    bathrooms=item.get("bathrooms"),
                    listing_url=item.get("listing_url", "")[:1000]
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=['listing_url'],
                    set_={
                        'asking_price_etb': stmt.excluded.asking_price_etb,
                        'title': stmt.excluded.title
                    }
                )
                self.db.execute(stmt)
                saved_count += 1
            self.db.commit()
            return saved_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving batch: {e}")
            return 0

    async def scrape(self, target_items=1000):
        Base.metadata.create_all(bind=engine)
        logger.info("Ensuring database tables exist...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                executable_path='/tmp/chrome-bin/chrome-headless-shell-mac-arm64/chrome-headless-shell'
            )
            
            total_saved = 0
            
            for target in TARGETS:
                if total_saved >= target_items:
                    break
                    
                context = await browser.new_context(
                    user_agent=await self.get_random_ua(),
                    viewport={'width': 1280, 'height': 720}
                )
                page = await context.new_page()
                
                domain = target["domain"]
                logger.info(f"Starting scraping for {domain}")
                
                for page_num in range(1, 51):  # Check up to 50 pages per site
                    if total_saved >= target_items:
                        break
                        
                    url = target["url"].format(page=page_num)
                    
                    if not self.is_allowed_by_robots(url):
                        logger.warning(f"robots.txt prevents scraping: {url}")
                        continue
                    
                    logger.info(f"Fetching: {url}")
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        # Wait 5 to 10 seconds organically
                        delay = random.uniform(5.0, 10.0)
                        logger.debug(f"Sleeping for {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
                        
                        # Extract items
                        items = await target["extractor"](page)
                        logger.info(f"Found {len(items)} items on page {page_num}")
                        
                        if not items:
                            logger.info(f"No items found on page {page_num}, stopping pagination for {domain}")
                            break
                            
                        # Filter bad urls:
                        filtered_items = [i for i in items if domain in i['listing_url']]
                        
                        # Save
                        saved = self.save_listings(filtered_items)
                        total_saved += saved
                        logger.info(f"Saved {saved} listings from {domain}. Total overall: {total_saved}/{target_items}")
                        
                    except Exception as e:
                        logger.error(f"Failed processing page {url}: {e}")
                        break # Stop pagination for this domain if there is continuous failure
                        
                await context.close()
                
            await browser.close()
            logger.info(f"Scraping completed. Target: {target_items}. Processed (inserted/upserted): {total_saved}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AVM Real Estate Scraper")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum listings to scrape")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless mode")
    parser.add_argument("--test", action="store_true", help="Run 1 page test mode")
    
    args = parser.parse_args()
    
    crawler = Crawler(headless=args.headless)
    limit = 20 if args.test else args.limit
    
    asyncio.run(crawler.scrape(target_items=limit))
