import asyncio
import random
import urllib.robotparser
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

class Crawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.robot_parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        await self._new_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _new_context(self):
        """Creates a new browser context with a random User-Agent."""
        if self.context:
            await self.context.close()
        
        ua = random.choice(USER_AGENTS)
        self.context = await self.browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            accept_downloads=False
        )
        logger.info(f"Created new browser context with UA: {ua[:50]}...")

    async def check_robots_txt(self, url: str) -> bool:
        """Checks if parsing the URL is allowed by robots.txt."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        if base_url not in self.robot_parsers:
            robots_url = f"{base_url}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                # Using run_in_executor since robotparser is synchronous
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, rp.read)
                self.robot_parsers[base_url] = rp
                logger.info(f"Loaded robots.txt for {base_url}")
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {base_url}: {e}")
                # If robots.txt fails, assume we can crawl (or fail-closed, depending on strictness)
                self.robot_parsers[base_url] = None 
        
        rp = self.robot_parsers.get(base_url)
        if rp:
            # We use '*' as User-agent for robots.txt check as we rotate explicitly 
            # and don't want to parse robots.txt for every single random UA we use.
            return rp.can_fetch('*', url)
        return True

    async def random_delay(self, min_sec: int = 5, max_sec: int = 10):
        """Adds a random delay to respect server load and avoid detection."""
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"Sleeping for {delay:.2f} seconds...")
        await asyncio.sleep(delay)

    async def fetch_page(self, url: str) -> Optional[Page]:
        """Fetches a page, checking robots.txt and applying delays."""
        if not await self.check_robots_txt(url):
            logger.warning(f"Scraping {url} blocked by robots.txt")
            return None

        # Rotate context (User-Agent, cookies, etc) periodically
        # (Could do this every N requests, hardcoding it per-request for max stealth here isn't great, better to do per batch)

        page = await self.context.new_page()
        try:
            logger.info(f"Navigating to {url}")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            if response and response.status in [403, 429, 503]:
                logger.error(f"Failed to fetch {url} - Status: {response.status}")
                await page.close()
                return None

            await self.random_delay()
            return page
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            await page.close()
            return None
