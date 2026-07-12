from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.data.models.scraper import ScraperTarget, ScraperLog
from app.api.schemas.scraper import (
    ScraperTargetCreate,
    ScraperTargetUpdate,
    ScraperStatsResponse,
    ScraperTestRequest,
    ScraperTestResponse
)
from app.core.scraper_limits import (
    SCRAPER_HEALTH_LOG_WINDOW,
    SCRAPER_TEST_SAMPLE_LIMIT,
    SCRAPER_TEST_NAVIGATION_TIMEOUT_MS,
    SCRAPER_TEST_SELECTOR_WAIT_MS,
)
from scraper.quality import count_consecutive_failures
import asyncio
from playwright.async_api import async_playwright


class ScraperService:
    """Service for managing scraper targets and logs"""

    @staticmethod
    def get_all_scrapers(db: Session, skip: int = 0, limit: int = 100) -> List[ScraperTarget]:
        """Get all scraper targets"""
        return db.query(ScraperTarget).offset(skip).limit(limit).all()

    @staticmethod
    def get_scraper_by_id(db: Session, scraper_id: int) -> Optional[ScraperTarget]:
        """Get scraper by ID"""
        return db.query(ScraperTarget).filter(ScraperTarget.id == scraper_id).first()

    @staticmethod
    def get_scraper_by_domain(db: Session, domain: str) -> Optional[ScraperTarget]:
        """Get scraper by domain"""
        return db.query(ScraperTarget).filter(ScraperTarget.domain == domain).first()

    @staticmethod
    def create_scraper(db: Session, scraper_data: ScraperTargetCreate) -> ScraperTarget:
        """Create new scraper target"""
        scraper = ScraperTarget(
            domain=scraper_data.domain,
            url_template=scraper_data.url_template,
            enabled=scraper_data.enabled,
            selectors=scraper_data.selectors,
            schedule=scraper_data.schedule,
            max_pages=scraper_data.max_pages
        )
        db.add(scraper)
        db.commit()
        db.refresh(scraper)
        return scraper

    @staticmethod
    def update_scraper(
        db: Session,
        scraper_id: int,
        scraper_data: ScraperTargetUpdate
    ) -> Optional[ScraperTarget]:
        """Update scraper target"""
        scraper = db.query(ScraperTarget).filter(ScraperTarget.id == scraper_id).first()
        if not scraper:
            return None

        update_data = scraper_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scraper, field, value)

        scraper.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(scraper)
        return scraper

    @staticmethod
    def delete_scraper(db: Session, scraper_id: int) -> bool:
        """Delete scraper target"""
        scraper = db.query(ScraperTarget).filter(ScraperTarget.id == scraper_id).first()
        if not scraper:
            return False

        db.delete(scraper)
        db.commit()
        return True

    @staticmethod
    def toggle_scraper(db: Session, scraper_id: int) -> Optional[ScraperTarget]:
        """Toggle scraper enabled status"""
        scraper = db.query(ScraperTarget).filter(ScraperTarget.id == scraper_id).first()
        if not scraper:
            return None

        scraper.enabled = not scraper.enabled
        scraper.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(scraper)
        return scraper

    @staticmethod
    def get_scraper_stats(db: Session) -> ScraperStatsResponse:
        """Get scraper statistics"""
        total_scrapers = db.query(func.count(ScraperTarget.id)).scalar()
        active_scrapers = db.query(func.count(ScraperTarget.id)).filter(
            ScraperTarget.enabled == True
        ).scalar()
        inactive_scrapers = total_scrapers - active_scrapers

        total_listings = db.query(func.sum(ScraperTarget.total_listings)).scalar() or 0

        # Last 24 hours listings
        yesterday = datetime.utcnow() - timedelta(days=1)
        last_24h_logs = db.query(func.sum(ScraperLog.listings_saved)).filter(
            ScraperLog.created_at >= yesterday
        ).scalar() or 0

        # Last run
        last_run = db.query(func.max(ScraperTarget.last_run)).scalar()

        # Average success rate
        total_runs = db.query(func.count(ScraperLog.id)).scalar() or 1
        successful_runs = db.query(func.count(ScraperLog.id)).filter(
            ScraperLog.status == "success"
        ).scalar() or 0
        avg_success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0

        return ScraperStatsResponse(
            total_scrapers=total_scrapers,
            active_scrapers=active_scrapers,
            inactive_scrapers=inactive_scrapers,
            total_listings=total_listings,
            last_24h_listings=last_24h_logs,
            last_run=last_run,
            avg_success_rate=round(avg_success_rate, 2)
        )

    @staticmethod
    def get_scraper_health(db: Session) -> List[Dict[str, Any]]:
        """Per-source health: last run, status, and consecutive failures."""
        health: List[Dict[str, Any]] = []
        scrapers = db.query(ScraperTarget).order_by(ScraperTarget.id).all()
        for scraper in scrapers:
            recent_logs = (
                db.query(ScraperLog)
                .filter(ScraperLog.scraper_id == scraper.id)
                .order_by(desc(ScraperLog.created_at))
                .limit(SCRAPER_HEALTH_LOG_WINDOW)
                .all()
            )
            statuses = [log.status for log in recent_logs]
            last_error_message = next(
                (log.error_message for log in recent_logs if log.error_message),
                None,
            )
            health.append({
                "id": scraper.id,
                "domain": scraper.domain,
                "enabled": scraper.enabled,
                "last_run": scraper.last_run,
                "last_status": scraper.last_status,
                "consecutive_failures": count_consecutive_failures(statuses),
                "total_listings": scraper.total_listings or 0,
                "last_error_message": last_error_message,
            })
        return health

    @staticmethod
    def get_scraper_logs(
        db: Session,
        scraper_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ScraperLog]:
        """Get scraper logs"""
        query = db.query(ScraperLog)
        if scraper_id:
            query = query.filter(ScraperLog.scraper_id == scraper_id)

        return query.order_by(desc(ScraperLog.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def create_log(
        db: Session,
        scraper_id: int,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        status: Optional[str] = None,
        listings_found: int = 0,
        listings_saved: int = 0,
        error_message: Optional[str] = None
    ) -> ScraperLog:
        """Create scraper log entry"""
        log = ScraperLog(
            scraper_id=scraper_id,
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            listings_found=listings_found,
            listings_saved=listings_saved,
            error_message=error_message
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update_scraper_stats(
        db: Session,
        scraper_id: int,
        last_run: datetime,
        last_status: str,
        total_listings: int
    ) -> Optional[ScraperTarget]:
        """Update scraper statistics after run"""
        scraper = db.query(ScraperTarget).filter(ScraperTarget.id == scraper_id).first()
        if not scraper:
            return None

        scraper.last_run = last_run
        scraper.last_status = last_status
        scraper.total_listings = total_listings
        scraper.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(scraper)
        return scraper

    @staticmethod
    async def test_scraper_config(test_data: ScraperTestRequest) -> ScraperTestResponse:
        """Test scraper configuration by attempting to scrape a single page"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                page = await context.new_page()

                url = test_data.url_template.format(page=test_data.test_page)
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=SCRAPER_TEST_NAVIGATION_TIMEOUT_MS
                )
                await page.wait_for_timeout(SCRAPER_TEST_SELECTOR_WAIT_MS)

                # Try to extract items using provided selectors
                items = []
                selectors = test_data.selectors

                # Find all listing containers (assuming they have a common parent)
                # This is a simplified test - actual extraction would be more complex
                try:
                    # Try to get sample data
                    if 'title' in selectors:
                        titles = await page.query_selector_all(selectors['title'])
                        prices = await page.query_selector_all(selectors.get('price', '')) if 'price' in selectors else []
                        locations = await page.query_selector_all(selectors.get('location', '')) if 'location' in selectors else []

                        for i, title_elem in enumerate(titles[:SCRAPER_TEST_SAMPLE_LIMIT]):
                            item = {}
                            item['title'] = await title_elem.inner_text() if title_elem else None

                            # Try to get other fields
                            if 'price' in selectors:
                                item['price'] = (
                                    await prices[i].inner_text()
                                    if i < len(prices) and prices[i] is not None
                                    else None
                                )

                            if 'location' in selectors:
                                item['location'] = (
                                    await locations[i].inner_text()
                                    if i < len(locations) and locations[i] is not None
                                    else None
                                )

                            items.append(item)

                    await browser.close()

                    return ScraperTestResponse(
                        success=True,
                        items_found=len(items),
                        sample_items=items,
                        error_message=None
                    )

                except Exception as e:
                    await browser.close()
                    return ScraperTestResponse(
                        success=False,
                        items_found=0,
                        sample_items=[],
                        error_message=f"Selector error: {str(e)}"
                    )

        except Exception as e:
            return ScraperTestResponse(
                success=False,
                items_found=0,
                sample_items=[],
                error_message=f"Test failed: {str(e)}"
            )
