"""
Notifications (U7).

Derives a live activity feed from real backend state — pending valuations
awaiting review, recently approved valuations, and recent scraper failures —
so the app-shell bell reflects actual events instead of a static placeholder.
Read-only and derived: nothing is fabricated, and an empty list is honest.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.data.models.valuation import Valuation, ValuationStatus
from app.data.models.scraper import ScraperLog, ScraperTarget

router = APIRouter()

RECENT_DAYS = 7
MAX_NOTIFICATIONS = 30


def _iso(dt):
    return dt.isoformat() if dt else None


@router.get("", tags=["Notifications"])
async def list_notifications(
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """Return derived notifications, most recent first, with an unread count."""
    since = datetime.utcnow() - timedelta(days=RECENT_DAYS)
    items = []

    # Valuations awaiting review.
    pending = (
        db.query(Valuation)
        .filter(Valuation.status == ValuationStatus.PENDING)
        .order_by(Valuation.updated_at.desc())
        .limit(MAX_NOTIFICATIONS)
        .all()
    )
    for v in pending:
        items.append({
            "type": "valuation_pending",
            "severity": "action",
            "title": "Valuation awaiting review",
            "message": f"Valuation #{v.id} ({v.municipality}) is pending approval.",
            "timestamp": _iso(v.updated_at or v.created_at),
            "link": "/valuations",
        })

    # Recently approved valuations.
    approved = (
        db.query(Valuation)
        .filter(Valuation.status == ValuationStatus.APPROVED, Valuation.updated_at >= since)
        .order_by(Valuation.updated_at.desc())
        .limit(MAX_NOTIFICATIONS)
        .all()
    )
    for v in approved:
        items.append({
            "type": "valuation_approved",
            "severity": "success",
            "title": "Valuation approved",
            "message": f"Valuation #{v.id} ({v.municipality}) was approved.",
            "timestamp": _iso(v.updated_at),
            "link": "/valuations",
        })

    # Recent scraper failures.
    failures = (
        db.query(ScraperLog, ScraperTarget)
        .join(ScraperTarget, ScraperLog.scraper_id == ScraperTarget.id)
        .filter(ScraperLog.status == "failed", ScraperLog.started_at >= since)
        .order_by(ScraperLog.started_at.desc())
        .limit(MAX_NOTIFICATIONS)
        .all()
    )
    for log, target in failures:
        items.append({
            "type": "scraper_failed",
            "severity": "error",
            "title": "Scraper run failed",
            "message": f"{target.domain}: {(log.error_message or 'run failed')[:140]}",
            "timestamp": _iso(log.started_at),
            "link": "/scrapers",
        })

    items.sort(key=lambda i: i["timestamp"] or "", reverse=True)
    items = items[:MAX_NOTIFICATIONS]

    return {"count": len(items), "notifications": items}
