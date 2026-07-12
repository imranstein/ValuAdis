"""
Scraper API Integration Contracts

Tests for scraper lifecycle endpoints used by the web scraper tab.
"""

import sys
from unittest.mock import Mock

from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

import asyncio
from app.core.scraper_limits import (
    SCRAPER_TEST_NAVIGATION_TIMEOUT_MS,
    SCRAPER_TEST_SELECTOR_WAIT_MS,
    SCRAPER_TEST_SAMPLE_LIMIT,
)
from app.core.security import get_current_user, get_current_user_id
from app.api.v1.endpoints import scrapers as scraper_endpoints
from app.api.schemas.scraper import ScraperTestRequest, ScraperTestResponse
from app.services import scraper_service as scraper_service_module
from app.data.models.scraper import ScraperLog


VALID_SCRAPER = {
    "domain": "livingethio.com",
    "url_template": "https://livingethio.com/listings?page={page}",
    "selectors": {
        "title": ".listing-title",
        "price": ".listing-price",
        "location": ".listing-location",
        "listing_url": ".listing-link",
    },
    "schedule": "daily",
    "max_pages": 5,
    "enabled": True,
}


def _mock_auth(client: TestClient):
    client.app.dependency_overrides[get_current_user] = lambda: 1
    client.app.dependency_overrides[get_current_user_id] = lambda: 1


def _clear_auth(client: TestClient):
    client.app.dependency_overrides.clear()


def _create_scraper(client: TestClient) -> dict:
    response = client.post("/api/v1/scrapers/", json=VALID_SCRAPER)
    assert response.status_code == 201
    return response.json()


def _create_scraper_logs(db_session, scraper_id: int, count: int = 3):
    now = datetime.utcnow()
    for offset in range(count):
        db_session.add(
            ScraperLog(
                scraper_id=scraper_id,
                started_at=now + timedelta(minutes=offset),
                completed_at=now + timedelta(minutes=offset, seconds=10),
                created_at=now + timedelta(minutes=offset),
                status="success" if offset % 2 == 0 else "failed",
                listings_found=offset * 3,
                listings_saved=offset * 2,
            )
        )
    db_session.commit()


def test_scraper_create_and_list_end_to_end(client: TestClient):
    _mock_auth(client)
    try:
        payload = _create_scraper(client)
        assert payload["id"] > 0
        assert payload["domain"] == VALID_SCRAPER["domain"]

        response = client.get("/api/v1/scrapers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["domain"] == VALID_SCRAPER["domain"]
    finally:
        _clear_auth(client)


def test_scraper_duplicate_domain_is_rejected(client: TestClient):
    _mock_auth(client)
    try:
        _create_scraper(client)
        duplicate = client.post("/api/v1/scrapers/", json=VALID_SCRAPER)
        assert duplicate.status_code == 400
        assert "already exists" in duplicate.text
    finally:
        _clear_auth(client)


def test_scraper_toggle_and_stats(client: TestClient):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        toggle_response = client.patch(f"/api/v1/scrapers/{scraper_id}/toggle")
        assert toggle_response.status_code == 200
        assert toggle_response.json()["enabled"] is False

        stats_response = client.get("/api/v1/scrapers/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_scrapers"] == 1
        assert stats["inactive_scrapers"] == 1

        toggle_response = client.patch(f"/api/v1/scrapers/{scraper_id}/toggle")
        assert toggle_response.status_code == 200
        assert toggle_response.json()["enabled"] is True
    finally:
        _clear_auth(client)


def test_scraper_run_rejects_disabled_scraper(client: TestClient):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        client.patch(f"/api/v1/scrapers/{scraper_id}/toggle")
        run_response = client.post(f"/api/v1/scrapers/{scraper_id}/run")
        assert run_response.status_code == 400
        assert "Cannot run disabled scraper" in run_response.text
    finally:
        _clear_auth(client)


def test_scraper_run_starts_background_job(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        popen_calls = []
        fake_process = Mock(pid=12345)

        def fake_popen(cmd, stdout=None, stderr=None, cwd=None):
            popen_calls.append({"cmd": cmd, "cwd": cwd})
            return fake_process

        monkeypatch.setattr(scraper_endpoints.subprocess, "Popen", fake_popen)

        run_response = client.post(f"/api/v1/scrapers/{scraper_id}/run")
        assert run_response.status_code == 200

        body = run_response.json()
        assert body["success"] is True
        assert body["log_id"] is not None
        assert popen_calls and popen_calls[0]["cmd"][0] == sys.executable

        logs = client.get(f"/api/v1/scrapers/logs?scraper_id={scraper_id}")
        assert logs.status_code == 200
        assert len(logs.json()) == 1
        assert logs.json()[0]["status"] == "running"
    finally:
        _clear_auth(client)


def test_scraper_invalid_payload_is_rejected(client: TestClient):
    _mock_auth(client)
    try:
        invalid_payload = dict(VALID_SCRAPER)
        invalid_payload["url_template"] = "https://invalid.com/listings?page"

        response = client.post("/api/v1/scrapers/", json=invalid_payload)
        assert response.status_code == 422
    finally:
        _clear_auth(client)


def test_scraper_update_rejects_duplicate_domain(client: TestClient):
    _mock_auth(client)
    try:
        _create_scraper(client)
        other = dict(VALID_SCRAPER)
        other["domain"] = "zemenproperty.com"
        other["url_template"] = "https://zemenproperty.com/listings?page={page}"
        _create_scraper_payload = client.post("/api/v1/scrapers/", json=other)
        assert _create_scraper_payload.status_code == 201
        other_id = _create_scraper_payload.json()["id"]

        duplicate_update = client.put(f"/api/v1/scrapers/{other_id}", json={"domain": "livingethio.com"})
        assert duplicate_update.status_code == 400
        assert "already exists" in duplicate_update.text
    finally:
        _clear_auth(client)


def test_scraper_delete_removes_target_and_404_when_missing(client: TestClient):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        delete_response = client.delete(f"/api/v1/scrapers/{scraper_id}")
        assert delete_response.status_code == 204

        get_response = client.get(f"/api/v1/scrapers/{scraper_id}")
        assert get_response.status_code == 404

        missing_delete = client.delete(f"/api/v1/scrapers/{scraper_id}")
        assert missing_delete.status_code == 404
    finally:
        _clear_auth(client)


def test_scraper_test_endpoint_accepts_override_payload(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        async def fake_test_scraper_config(test_data: ScraperTestRequest):
            assert test_data.url_template == created["url_template"]
            return ScraperTestResponse(
                success=True,
                items_found=3,
                sample_items=[
                    {"title": "sample", "price": "1000"},
                    {"title": "sample2", "price": "2000"},
                ],
                error_message=None,
            )

        monkeypatch.setattr(
            scraper_endpoints.ScraperService,
            "test_scraper_config",
            fake_test_scraper_config
        )

        test_response = client.post(
            f"/api/v1/scrapers/{scraper_id}/test",
            json={
                "url_template": created["url_template"],
                "selectors": created["selectors"],
                "test_page": 2,
            },
        )
        assert test_response.status_code == 200
        assert test_response.json()["items_found"] == 3
        assert test_response.json()["success"] is True
    finally:
        _clear_auth(client)


def test_scraper_run_failure_marks_log_as_failed(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        def fake_popen(*_args, **_kwargs):
            raise RuntimeError("simulated process failure")

        monkeypatch.setattr(scraper_endpoints.subprocess, "Popen", fake_popen)

        run_response = client.post(f"/api/v1/scrapers/{scraper_id}/run")
        assert run_response.status_code == 500
        assert "Failed to start scraper" in run_response.text

        logs = client.get(f"/api/v1/scrapers/logs?scraper_id={scraper_id}")
        assert logs.status_code == 200
        payload = logs.json()
        assert len(payload) == 1
        assert payload[0]["status"] == "failed"
    finally:
        _clear_auth(client)


def test_scraper_stats_reflects_totals_and_success_rate(
    client: TestClient,
    db_session
):
    _mock_auth(client)
    try:
        first = _create_scraper(client)
        second_payload = dict(VALID_SCRAPER)
        second_payload["domain"] = "zemenproperty.com"
        second_payload["url_template"] = "https://zemenproperty.com/listings?page={page}"
        second_response = client.post("/api/v1/scrapers/", json=second_payload)
        assert second_response.status_code == 201

        _create_scraper_logs(db_session, first["id"], count=3)
        _create_scraper_logs(db_session, second_response.json()["id"], count=1)

        stats_response = client.get("/api/v1/scrapers/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_scrapers"] == 2
        assert stats["active_scrapers"] == 2
        assert stats["inactive_scrapers"] == 0
        assert stats["last_24h_listings"] == 6
        assert stats["avg_success_rate"] == 75.0
    finally:
        _clear_auth(client)


def test_scraper_logs_pagination_and_ordering(
    client: TestClient,
    db_session
):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]
        _create_scraper_logs(db_session, scraper_id, count=5)

        full_response = client.get(f"/api/v1/scrapers/logs?scraper_id={scraper_id}&limit=5")
        assert full_response.status_code == 200
        full_payload = full_response.json()
        assert len(full_payload) == 5
        assert full_payload[0]["started_at"] > full_payload[1]["started_at"]

        paged_response = client.get(
            f"/api/v1/scrapers/logs?scraper_id={scraper_id}&skip=1&limit=2"
        )
        assert paged_response.status_code == 200
        paged_payload = paged_response.json()
        assert len(paged_payload) == 2
        assert paged_payload[0]["started_at"] == full_payload[1]["started_at"]
        assert paged_payload[1]["started_at"] == full_payload[2]["started_at"]
    finally:
        _clear_auth(client)


def test_scraper_health_reports_per_source_shape(client: TestClient, db_session):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        now = datetime.utcnow()
        # Two most-recent runs failed, an older run succeeded.
        db_session.add_all([
            ScraperLog(
                scraper_id=scraper_id,
                started_at=now,
                completed_at=now + timedelta(seconds=5),
                created_at=now,
                status="success",
            ),
            ScraperLog(
                scraper_id=scraper_id,
                started_at=now + timedelta(minutes=1),
                completed_at=now + timedelta(minutes=1, seconds=5),
                created_at=now + timedelta(minutes=1),
                status="failed",
                error_message="first boom",
            ),
            ScraperLog(
                scraper_id=scraper_id,
                started_at=now + timedelta(minutes=2),
                completed_at=now + timedelta(minutes=2, seconds=5),
                created_at=now + timedelta(minutes=2),
                status="failed",
                error_message="latest boom",
            ),
        ])
        db_session.commit()

        response = client.get("/api/v1/scrapers/health")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, list)
        assert len(payload) == 1

        entry = payload[0]
        assert set(entry.keys()) == {
            "id",
            "domain",
            "enabled",
            "last_run",
            "last_status",
            "consecutive_failures",
            "total_listings",
            "last_error_message",
        }
        assert entry["domain"] == VALID_SCRAPER["domain"]
        assert entry["enabled"] is True
        assert entry["consecutive_failures"] == 2
        assert entry["last_error_message"] == "latest boom"
    finally:
        _clear_auth(client)


def test_scraper_health_returns_empty_list_without_targets(client: TestClient):
    _mock_auth(client)
    try:
        response = client.get("/api/v1/scrapers/health")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        _clear_auth(client)


def test_scraper_routes_require_authentication(client: TestClient):
    endpoints = [
        ("get", "/api/v1/scrapers/"),
        ("post", "/api/v1/scrapers/"),
        ("get", "/api/v1/scrapers/stats"),
        ("get", "/api/v1/scrapers/health"),
        ("get", "/api/v1/scrapers/logs"),
        ("get", "/api/v1/scrapers/1"),
        ("put", "/api/v1/scrapers/1"),
        ("patch", "/api/v1/scrapers/1/toggle"),
        ("post", "/api/v1/scrapers/1/test"),
        ("post", "/api/v1/scrapers/1/run"),
        ("delete", "/api/v1/scrapers/1"),
    ]

    for method, endpoint in endpoints:
        response = getattr(client, method)(endpoint)
        assert response.status_code == 401


def test_scraper_api_responses_include_security_headers(client: TestClient):
    _mock_auth(client)
    try:
        _create_scraper(client)

        response = client.get("/api/v1/scrapers/")
        assert response.status_code == 200
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["x-xss-protection"] == "1; mode=block"
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    finally:
        _clear_auth(client)


def test_scraper_list_limit_is_capped(client: TestClient):
    _mock_auth(client)
    try:
        for idx in range(205):
            payload = dict(VALID_SCRAPER)
            payload["domain"] = f"ethproperty{idx}.com"
            payload["url_template"] = f"https://ethproperty{idx}.com/listings?page={{page}}"
            create_response = client.post("/api/v1/scrapers/", json=payload)
            assert create_response.status_code == 201

        response = client.get("/api/v1/scrapers?limit=999")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 200
    finally:
        _clear_auth(client)


def test_scraper_run_payload_is_capped_to_safe_limits(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    _mock_auth(client)
    try:
        created = _create_scraper(client)
        scraper_id = created["id"]

        popen_calls = []

        def fake_popen(cmd, stdout=None, stderr=None, cwd=None):
            popen_calls.append({"cmd": cmd, "cwd": cwd})
            return Mock(pid=99999)

        monkeypatch.setattr(scraper_endpoints.subprocess, "Popen", fake_popen)

        run_response = client.post(
            f"/api/v1/scrapers/{scraper_id}/run",
            json={"max_pages": 100, "target_items": 1000},
        )
        assert run_response.status_code == 200

        assert popen_calls
        command = popen_calls[0]["cmd"]
        max_pages_index = command.index("--max-pages")
        target_items_index = command.index("--limit")
        assert command[max_pages_index + 1] == "50"
        assert command[target_items_index + 1] == "200"
    finally:
        _clear_auth(client)


def test_scraper_service_test_config_respects_sample_cap_and_timeouts(monkeypatch: pytest.MonkeyPatch):
    calls = {}

    class FakeElement:
        def __init__(self, value: str):
            self.value = value

        async def inner_text(self):
            return self.value

    class FakePage:
        async def goto(self, url, wait_until=None, timeout=None):
            calls["goto"] = {"url": url, "wait_until": wait_until, "timeout": timeout}

        async def wait_for_timeout(self, timeout):
            calls["wait_for_timeout"] = timeout

        async def query_selector_all(self, selector):
            calls["query_selectors"] = calls.get("query_selectors", [])
            calls["query_selectors"].append(selector)

            if selector == ".listing-title":
                return [FakeElement(f"title-{index}") for index in range(8)]
            if selector == ".listing-price":
                return [FakeElement(f"price-{index}") for index in range(8)]
            if selector == ".listing-location":
                return [FakeElement(f"location-{index}") for index in range(8)]
            return []

    class FakeContext:
        async def new_page(self):
            calls["page"] = FakePage()
            return calls["page"]

    class FakeBrowser:
        async def new_context(self, **_kwargs):
            return FakeContext()

        async def close(self):
            calls["browser_closed"] = True

    class FakeChromium:
        async def launch(self, headless=True):
            calls["launch_headless"] = headless
            return FakeBrowser()

    class FakePlaywright:
        def __init__(self):
            self.chromium = FakeChromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def fake_async_playwright():
        calls["playwright_ctx_enter"] = True
        return FakePlaywright()

    monkeypatch.setattr(
        scraper_service_module,
        "async_playwright",
        fake_async_playwright,
    )

    result = asyncio.run(
        scraper_service_module.ScraperService.test_scraper_config(
            ScraperTestRequest(
                url_template="https://example.com/listings?page={page}",
                selectors={
                    "title": ".listing-title",
                    "price": ".listing-price",
                    "location": ".listing-location",
                },
                test_page=2,
            )
        )
    )

    assert result.success is True
    assert result.items_found == SCRAPER_TEST_SAMPLE_LIMIT
    assert len(result.sample_items) == SCRAPER_TEST_SAMPLE_LIMIT
    assert calls["goto"]["timeout"] == SCRAPER_TEST_NAVIGATION_TIMEOUT_MS
    assert calls["wait_for_timeout"] == SCRAPER_TEST_SELECTOR_WAIT_MS
    assert calls["query_selectors"].count(".listing-title") == 1
    assert calls["query_selectors"].count(".listing-price") == 1
    assert calls["query_selectors"].count(".listing-location") == 1
    assert result.sample_items[0]["title"] == "title-0"
    assert result.sample_items[2]["location"] == "location-2"
    assert calls["browser_closed"] is True
