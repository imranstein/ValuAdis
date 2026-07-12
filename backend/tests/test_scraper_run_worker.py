"""
Scraper run worker tests.

Verify the run path stores raw market listings (never Property rows),
retries fetches with backoff, and always leaves ScraperLog in a
terminal state. No network and no real Playwright browser is used.
"""

import asyncio
import os

import pytest

from app.data.models.market_listing import RawMarketListing
from app.data.models.property import Property
from app.data.models.scraper import ScraperLog, ScraperTarget
from scraper import run_scraper as run_scraper_module
from scraper.run_scraper import (
    MAX_FETCH_ATTEMPTS,
    RETRY_BACKOFF_BASE_SECONDS,
    ScraperRunner,
    fetch_page_html,
)

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "scraper", "epc_listing_page.html"
)

EPC_FIXTURE_LISTING_COUNT = 20


def _sample_records(count: int = 3):
    return [
        {
            "title": f"Listing {index}",
            "asking_price_etb": 1000000.0 + index,
            "location_subcity": "Bole, Addis Ababa",
            "area_sqm": 100.0,
            "property_type": "Apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "listing_url": f"https://ethiopiapropertycentre.com/listing/{index}",
        }
        for index in range(count)
    ]


def _create_epc_scraper(db_session) -> ScraperTarget:
    scraper = ScraperTarget(
        domain="ethiopiapropertycentre.com",
        url_template="https://ethiopiapropertycentre.com/for-sale?page={page}",
        enabled=True,
        selectors={"title": ".wp-block-title", "price": ".price"},
        schedule="daily",
        max_pages=5,
    )
    db_session.add(scraper)
    db_session.commit()
    return scraper


class _FakePage:
    def __init__(self, html: str, failures_before_success: int = 0):
        self.html = html
        self.failures_before_success = failures_before_success
        self.goto_attempts = 0

    async def goto(self, url, wait_until=None, timeout=None):
        self.goto_attempts += 1
        if self.goto_attempts <= self.failures_before_success:
            raise RuntimeError(f"simulated fetch failure {self.goto_attempts}")

    async def content(self):
        return self.html


class _FakeContext:
    def __init__(self, page):
        self._page = page

    async def new_page(self):
        return self._page


class _FakeBrowser:
    def __init__(self, page):
        self._page = page
        self.closed = False

    async def new_context(self, **_kwargs):
        return _FakeContext(self._page)

    async def close(self):
        self.closed = True


class _FakeChromium:
    def __init__(self, page):
        self._page = page

    async def launch(self, headless=True):
        return _FakeBrowser(self._page)


class _FakePlaywright:
    def __init__(self, page):
        self.chromium = _FakeChromium(page)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_save_listings_writes_raw_market_listings(db_session):
    runner = ScraperRunner(scraper_id=1, db=db_session)

    saved = runner.save_listings(_sample_records(3))

    assert saved == 3
    assert db_session.query(RawMarketListing).count() == 3


def test_save_listings_skips_duplicate_listing_urls(db_session):
    runner = ScraperRunner(scraper_id=1, db=db_session)
    runner.save_listings(_sample_records(3))

    second_saved = runner.save_listings(_sample_records(3))

    assert second_saved == 0
    assert db_session.query(RawMarketListing).count() == 3


def test_save_listings_skips_records_without_listing_url(db_session):
    runner = ScraperRunner(scraper_id=1, db=db_session)
    records = _sample_records(2)
    records[0]["listing_url"] = None

    saved = runner.save_listings(records)

    assert saved == 1


def test_save_listings_never_creates_property_rows(db_session):
    runner = ScraperRunner(scraper_id=1, db=db_session)

    runner.save_listings(_sample_records(3))

    assert db_session.query(Property).count() == 0


def test_fetch_page_html_retries_with_exponential_backoff(monkeypatch):
    sleeps = []

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr(run_scraper_module.asyncio, "sleep", fake_sleep)
    page = _FakePage("<html></html>", failures_before_success=2)

    html = asyncio.run(fetch_page_html(page, "https://example.com/1"))

    assert html == "<html></html>"
    assert page.goto_attempts == MAX_FETCH_ATTEMPTS
    assert sleeps == [
        RETRY_BACKOFF_BASE_SECONDS,
        RETRY_BACKOFF_BASE_SECONDS * 2,
    ]


def test_fetch_page_html_raises_after_max_attempts(monkeypatch):
    async def fake_sleep(_seconds):
        pass

    monkeypatch.setattr(run_scraper_module.asyncio, "sleep", fake_sleep)
    page = _FakePage("<html></html>", failures_before_success=99)

    with pytest.raises(RuntimeError):
        asyncio.run(fetch_page_html(page, "https://example.com/1"))

    assert page.goto_attempts == MAX_FETCH_ATTEMPTS


def test_run_saves_epc_fixture_listings_to_raw_table(db_session, monkeypatch):
    scraper = _create_epc_scraper(db_session)
    with open(FIXTURE_PATH, encoding="utf-8") as fixture_file:
        page = _FakePage(fixture_file.read())
    monkeypatch.setattr(
        run_scraper_module, "async_playwright", lambda: _FakePlaywright(page)
    )
    runner = ScraperRunner(scraper_id=scraper.id, max_pages=1, db=db_session)

    asyncio.run(runner.run_scraper())

    assert db_session.query(RawMarketListing).count() == EPC_FIXTURE_LISTING_COUNT


def test_run_marks_log_success_with_found_and_saved_counts(db_session, monkeypatch):
    scraper = _create_epc_scraper(db_session)
    with open(FIXTURE_PATH, encoding="utf-8") as fixture_file:
        page = _FakePage(fixture_file.read())
    monkeypatch.setattr(
        run_scraper_module, "async_playwright", lambda: _FakePlaywright(page)
    )
    runner = ScraperRunner(scraper_id=scraper.id, max_pages=1, db=db_session)

    asyncio.run(runner.run_scraper())

    log = db_session.query(ScraperLog).filter_by(scraper_id=scraper.id).one()
    assert log.status == "success"
    assert log.completed_at is not None
    assert log.listings_found == EPC_FIXTURE_LISTING_COUNT
    assert log.listings_saved == EPC_FIXTURE_LISTING_COUNT


def test_run_never_creates_property_rows(db_session, monkeypatch):
    scraper = _create_epc_scraper(db_session)
    with open(FIXTURE_PATH, encoding="utf-8") as fixture_file:
        page = _FakePage(fixture_file.read())
    monkeypatch.setattr(
        run_scraper_module, "async_playwright", lambda: _FakePlaywright(page)
    )
    runner = ScraperRunner(scraper_id=scraper.id, max_pages=1, db=db_session)

    asyncio.run(runner.run_scraper())

    assert db_session.query(Property).count() == 0


def test_run_marks_log_failed_when_browser_crashes(db_session, monkeypatch):
    scraper = _create_epc_scraper(db_session)

    def broken_playwright():
        raise RuntimeError("playwright browser missing")

    monkeypatch.setattr(run_scraper_module, "async_playwright", broken_playwright)
    runner = ScraperRunner(scraper_id=scraper.id, max_pages=1, db=db_session)

    asyncio.run(runner.run_scraper())

    log = db_session.query(ScraperLog).filter_by(scraper_id=scraper.id).one()
    assert log.status == "failed"
    assert log.completed_at is not None
    assert "playwright browser missing" in log.error_message


def test_run_marks_log_failed_for_domain_without_extractor(db_session):
    scraper = ScraperTarget(
        domain="unknown-portal.example.com",
        url_template="https://unknown-portal.example.com/listings?page={page}",
        enabled=True,
        selectors={"title": ".title"},
        schedule="daily",
        max_pages=5,
    )
    db_session.add(scraper)
    db_session.commit()
    runner = ScraperRunner(scraper_id=scraper.id, max_pages=1, db=db_session)

    asyncio.run(runner.run_scraper())

    log = db_session.query(ScraperLog).filter_by(scraper_id=scraper.id).one()
    assert log.status == "failed"
    assert "No extractor registered" in log.error_message
