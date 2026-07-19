"""Notifications endpoint: derived from real valuation + scraper state."""

import pytest
from fastapi.testclient import TestClient

from app.data.models.valuation import Valuation, ValuationStatus
from app.data.models.scraper import ScraperLog, ScraperTarget


@pytest.fixture
def auth_headers(client: TestClient, test_user_data) -> dict:
    token = client.post("/api/v1/auth/register", json=test_user_data).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_notifications_require_auth(client):
    assert client.get("/api/v1/notifications").status_code == 401


def test_empty_state_is_honest(client, auth_headers):
    r = client.get("/api/v1/notifications", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 0
    assert body["notifications"] == []


def test_pending_valuation_produces_notification(client, auth_headers, db_session):
    db_session.add(Valuation(
        property_id=1, user_id=1, property_type="residential", municipality="Addis Ababa",
        area_sqm=120, market_value=1_000_000, taxable_value=250_000,
        status=ValuationStatus.PENDING,
    ))
    db_session.commit()

    body = client.get("/api/v1/notifications", headers=auth_headers).json()
    types = [n["type"] for n in body["notifications"]]
    assert "valuation_pending" in types
    assert body["count"] >= 1


def test_scraper_failure_produces_notification(client, auth_headers, db_session):
    target = ScraperTarget(
        domain="example.et", url_template="https://example.et/p={page}",
        enabled=True, selectors={}, schedule="daily", max_pages=1,
    )
    db_session.add(target)
    db_session.commit()
    from datetime import datetime
    db_session.add(ScraperLog(
        scraper_id=target.id, started_at=datetime.utcnow(),
        status="failed", error_message="robots.txt disallows scraping",
    ))
    db_session.commit()

    body = client.get("/api/v1/notifications", headers=auth_headers).json()
    scraper_notes = [n for n in body["notifications"] if n["type"] == "scraper_failed"]
    assert scraper_notes
    assert "example.et" in scraper_notes[0]["message"]
