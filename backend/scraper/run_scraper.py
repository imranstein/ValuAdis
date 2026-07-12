"""
Scraper run worker.

Fetches portal pages with Playwright (thin driver), extracts listings
with the pure site-specific extractors, and stores results in the
raw_market_listings table with dedup on listing_url. The scrape path
never writes Property rows.
"""

import argparse
import asyncio
import logging
import os
import random
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.scraper_limits import SCRAPER_HEALTH_LOG_WINDOW
from app.core.sentry import sentry_manager
from app.data.models.market_listing import RawMarketListing
from app.data.models.scraper import ScraperLog
from app.services.scraper_service import ScraperService
from playwright.async_api import async_playwright

from scraper.extractors import get_extractor
from scraper.quality import (
    CONSECUTIVE_FAILURE_THRESHOLD,
    count_consecutive_failures,
    filter_outliers,
)
from scraper.robots import fetch_robots_txt, is_path_allowed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("ValuAdis_Scraper")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

MAX_FETCH_ATTEMPTS = 3
RETRY_BACKOFF_BASE_SECONDS = 2
PAGE_DELAY_MIN_SECONDS = 2
PAGE_DELAY_MAX_SECONDS = 5
PAGE_NAVIGATION_TIMEOUT_MS = 30000
MAX_TITLE_LENGTH = 500

DEFAULT_MAX_PAGES = 5
DEFAULT_TARGET_ITEMS = 100


async def fetch_page_html(page, url: str) -> str:
    """Fetch a page's HTML with exponential-backoff retries."""
    last_error = None
    for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
        try:
            await page.goto(
                url, wait_until="domcontentloaded", timeout=PAGE_NAVIGATION_TIMEOUT_MS
            )
            return await page.content()
        except Exception as error:
            last_error = error
            if attempt < MAX_FETCH_ATTEMPTS:
                backoff = RETRY_BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                logger.warning(
                    f"Fetch attempt {attempt}/{MAX_FETCH_ATTEMPTS} failed for {url}: "
                    f"{error}; retrying in {backoff}s"
                )
                await asyncio.sleep(backoff)
    raise last_error


class ScraperRunner:
    def __init__(
        self,
        scraper_id: int,
        max_pages: int = DEFAULT_MAX_PAGES,
        target_items: int = DEFAULT_TARGET_ITEMS,
        db=None,
    ):
        self.scraper_id = scraper_id
        self.max_pages = max_pages
        self.target_items = target_items
        self._owns_db = db is None
        self.db = db if db is not None else SessionLocal()

    async def run_scraper(self):
        """Run a specific scraper by ID, always leaving its log in a terminal state."""
        scraper = ScraperService.get_scraper_by_id(self.db, self.scraper_id)
        if not scraper:
            logger.error(f"Scraper {self.scraper_id} not found")
            if self._owns_db:
                self.db.close()
            return

        logger.info(f"Starting scraper: {scraper.domain}")
        log = ScraperService.create_log(
            self.db,
            scraper_id=self.scraper_id,
            started_at=datetime.utcnow(),
            status="running",
        )

        total_found = 0
        total_saved = 0
        try:
            extractor = get_extractor(scraper.domain)
            if extractor is None:
                raise RuntimeError(
                    f"No extractor registered for domain {scraper.domain}"
                )

            user_agent = random.choice(USER_AGENTS)
            first_url = scraper.url_template.format(page=1)
            robots_txt = fetch_robots_txt(first_url)
            if robots_txt is not None and not is_path_allowed(
                robots_txt, user_agent, first_url
            ):
                raise RuntimeError(
                    f"robots.txt disallows scraping {first_url}"
                )
            if robots_txt is None:
                logger.warning(
                    f"robots.txt unavailable for {scraper.domain}; proceeding"
                )

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                try:
                    context = await browser.new_context(
                        user_agent=user_agent,
                        viewport={"width": 1280, "height": 720},
                    )
                    page = await context.new_page()

                    for page_num in range(1, self.max_pages + 1):
                        url = scraper.url_template.format(page=page_num)
                        logger.info(f"Scraping page {page_num}: {url}")

                        html = await fetch_page_html(page, url)
                        records = extractor(html)
                        logger.info(f"Found {len(records)} listings on page {page_num}")
                        total_found += len(records)

                        saved = self.save_listings(records)
                        total_saved += saved
                        logger.info(f"Saved {saved} new raw listings from page {page_num}")

                        if not records:
                            logger.info("No listings found, stopping pagination")
                            break
                        if total_saved >= self.target_items:
                            logger.info("Target item count reached, stopping pagination")
                            break
                        if page_num < self.max_pages:
                            await asyncio.sleep(
                                random.uniform(PAGE_DELAY_MIN_SECONDS, PAGE_DELAY_MAX_SECONDS)
                            )
                finally:
                    await browser.close()

            scraper.total_listings = (scraper.total_listings or 0) + total_saved
            scraper.last_run = datetime.utcnow()
            scraper.last_status = "success" if total_saved > 0 else "no_data"

            log.completed_at = datetime.utcnow()
            log.status = "success"
            log.listings_found = total_found
            log.listings_saved = total_saved
            self.db.commit()

            logger.info(f"Scraper completed. Found: {total_found}, Saved: {total_saved}")

        except Exception as error:
            logger.error(f"Scraper failed: {error}")
            self.db.rollback()

            log.completed_at = datetime.utcnow()
            log.status = "failed"
            log.error_message = str(error)
            log.listings_found = total_found
            log.listings_saved = total_saved

            scraper.last_run = datetime.utcnow()
            scraper.last_status = "failed"
            self.db.commit()

            self._alert_failure(scraper, error)

        finally:
            self._ensure_terminal_log(log)
            if self._owns_db:
                self.db.close()

    def _alert_failure(self, scraper, error):
        """Report a failed run to Sentry, escalating on consecutive failures.

        Guarded so a missing/misconfigured Sentry (or an alerting error)
        never masks the run's terminal failed state.
        """
        try:
            extra = {"scraper_id": self.scraper_id, "domain": scraper.domain}
            sentry_manager.capture_exception(error, extra_data=extra)

            recent_statuses = [
                log.status
                for log in self.db.query(ScraperLog)
                .filter(ScraperLog.scraper_id == self.scraper_id)
                .order_by(ScraperLog.created_at.desc())
                .limit(SCRAPER_HEALTH_LOG_WINDOW)
                .all()
            ]
            consecutive = count_consecutive_failures(recent_statuses)
            if consecutive >= CONSECUTIVE_FAILURE_THRESHOLD:
                sentry_manager.capture_message(
                    f"Scraper {scraper.domain} has {consecutive} consecutive "
                    "failed runs",
                    level="error",
                    extra_data={**extra, "consecutive_failures": consecutive},
                )
        except Exception as alert_error:
            logger.error(f"Failed to send scraper failure alert: {alert_error}")

    def _ensure_terminal_log(self, log):
        """Guarantee the run log never stays stuck in 'running'."""
        try:
            if log.status == "running":
                log.status = "failed"
                log.completed_at = datetime.utcnow()
                log.error_message = log.error_message or "Scraper terminated unexpectedly"
                self.db.commit()
        except Exception as error:
            logger.error(f"Could not finalize scraper log: {error}")

    def save_listings(self, records) -> int:
        """Insert listings into raw_market_listings, skipping existing listing_urls.

        Obvious price/area outliers are dropped before insert so misparsed
        rows never pollute the AVM training data.
        """
        kept, dropped = filter_outliers(records)
        if dropped:
            logger.info(f"Dropped {len(dropped)} outlier listings before save")

        saved_count = 0
        seen_urls = set()
        for record in kept:
            listing_url = record.get("listing_url")
            title = record.get("title")
            if not listing_url or not title or listing_url in seen_urls:
                continue
            seen_urls.add(listing_url)

            exists = (
                self.db.query(RawMarketListing)
                .filter(RawMarketListing.listing_url == listing_url)
                .first()
            )
            if exists:
                continue

            self.db.add(
                RawMarketListing(
                    title=title[:MAX_TITLE_LENGTH],
                    asking_price_etb=record.get("asking_price_etb"),
                    location_subcity=record.get("location_subcity"),
                    area_sqm=record.get("area_sqm"),
                    property_type=record.get("property_type"),
                    bedrooms=record.get("bedrooms"),
                    bathrooms=record.get("bathrooms"),
                    listing_url=listing_url,
                )
            )
            saved_count += 1

        self.db.commit()
        return saved_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ValuAdis Scraper")
    parser.add_argument("--scraper-id", type=int, required=True, help="Scraper ID to run")
    parser.add_argument(
        "--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="Maximum pages to scrape"
    )
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_TARGET_ITEMS, help="Maximum items to collect"
    )

    args = parser.parse_args()

    runner = ScraperRunner(
        scraper_id=args.scraper_id,
        max_pages=args.max_pages,
        target_items=args.limit,
    )

    asyncio.run(runner.run_scraper())
