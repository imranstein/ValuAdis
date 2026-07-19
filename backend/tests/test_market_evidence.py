"""Market-evidence endpoint tests: comparables from raw_market_listings."""

import pytest
from fastapi.testclient import TestClient

from app.data.models.market_listing import RawMarketListing


@pytest.fixture
def auth_headers(client: TestClient, test_user_data) -> dict:
    token = client.post("/api/v1/auth/register", json=test_user_data).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def property_id(client: TestClient, auth_headers, test_property_data) -> int:
    payload = {**test_property_data, "subcity": "Bole"}
    return client.post("/api/v1/properties", json=payload, headers=auth_headers).json()["data"]["id"]


def _seed_listings(db_session, area, subcity="Bole", ptype="residential"):
    for i in range(3):
        db_session.add(RawMarketListing(
            title=f"Comparable {i}",
            asking_price_etb=10_000_000 + i * 1_000_000,
            location_subcity=subcity,
            area_sqm=area + i,  # within the subject's ±40% band
            property_type=ptype,
            bedrooms=3, bathrooms=2,
            listing_url=f"https://example.et/listing/{i}",
        ))
    db_session.commit()


def _subject_area(client, auth_headers, property_id):
    r = client.get(f"/api/v1/properties/{property_id}", headers=auth_headers)
    return r.json()["data"]["area_sqm"]


def test_market_evidence_requires_auth(client, property_id):
    assert client.get(f"/api/v1/properties/{property_id}/market-evidence").status_code == 401


def test_market_evidence_missing_property_404(client, auth_headers):
    r = client.get("/api/v1/properties/999999/market-evidence", headers=auth_headers)
    assert r.status_code == 404


def test_market_evidence_empty_is_honest(client, auth_headers, property_id):
    r = client.get(f"/api/v1/properties/{property_id}/market-evidence", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["comparables"] == []
    assert data["statistics"] is None


def test_market_evidence_returns_comparables_and_stats(client, auth_headers, property_id, db_session):
    _seed_listings(db_session, area=_subject_area(client, auth_headers, property_id))
    r = client.get(f"/api/v1/properties/{property_id}/market-evidence", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["comparables"]) == 3
    stats = data["statistics"]
    assert stats["count"] == 3
    assert stats["min_price_per_sqm"] <= stats["median_price_per_sqm"] <= stats["max_price_per_sqm"]
    assert stats["implied_value_etb"] > 0
