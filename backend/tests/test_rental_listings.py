"""
Rental Listings Endpoint Tests (Phase B)

Covers: citizen signup with Fayda ID, role guards (owner-only creation,
officer-only review), auto rent valuation wiring, officer review actions
(publish / adjust_band with mandatory reason / reject), the owner
verification gate, audit rows for publish/verify, and the public
PII-redacted browse surface (published-only, 404 for unpublished).
"""

import pytest
from fastapi.testclient import TestClient

from app.data.models.audit_log import AuditLog
from app.data.models.role import Role
from app.data.models.user import User
from app.data.models.valuation import Valuation


OWNER_SIGNUP = {
    "email": "owner@example.com",
    "full_name": "Kebede Alemu",
    "phone": "+251911111111",
    "password": "Ownerpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "123456789012",
    "account_type": "property_owner",
}

RENTER_SIGNUP = {
    "email": "renter@example.com",
    "full_name": "Meron Tadesse",
    "phone": "+251922222222",
    "password": "Renterpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "987654321098",
    "account_type": "renter",
}

PROPERTY_PAYLOAD = {
    "address": "Bole, Addis Ababa",
    "municipality": "Addis Ababa",
    "subcity": "Bole",
    "property_type": "residential",
    "property_subtype": "apartment",
    "area_sqm": 120.0,
    "number_of_bedrooms": 2,
    "owner_name": "Kebede Alemu",
    "owner_phone": "+251911111111",
    "coordinates": [
        [38.7578, 9.0320],
        [38.7580, 9.0320],
        [38.7580, 9.0318],
        [38.7578, 9.0318],
        [38.7578, 9.0320],
    ],
}


def _signup(client: TestClient, payload: dict) -> str:
    response = client.post("/api/v1/rentals/signup", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]["access_token"]


def _make_officer(client: TestClient, db_session) -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "officer@example.com",
            "full_name": "Officer Worku",
            "phone": "+251933333333",
            "password": "Officerpass1!",
            "municipality": "Addis Ababa",
            "license_number": "OFF-2026-001",
        },
    )
    token = response.json()["data"]["access_token"]
    user = db_session.query(User).filter(User.email == "officer@example.com").first()
    role = db_session.query(Role).filter(Role.name == "rental_officer").first()
    if role is None:
        role = Role(name="rental_officer", display_name="Rental Officer", is_active=True)
        db_session.add(role)
        db_session.commit()
    user.roles.append(role)
    db_session.commit()
    return token


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_property(client: TestClient, token: str) -> int:
    response = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(token))
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def _create_listing(client: TestClient, token: str, property_id: int) -> dict:
    response = client.post(
        "/api/v1/rentals/listings",
        json={"property_id": property_id},
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


@pytest.fixture
def owner_token(client):
    return _signup(client, OWNER_SIGNUP)


@pytest.fixture
def renter_token(client):
    return _signup(client, RENTER_SIGNUP)


@pytest.fixture
def officer_token(client, db_session):
    return _make_officer(client, db_session)


class TestCitizenSignup:
    def test_signup_assigns_renter_role_by_default(self, client, db_session):
        payload = {**RENTER_SIGNUP}
        payload.pop("account_type")
        response = client.post("/api/v1/rentals/signup", json=payload)
        assert response.status_code == 201
        user = db_session.query(User).filter(User.email == payload["email"]).first()
        assert [r.name for r in user.roles] == ["renter"]

    def test_owner_signup_starts_unverified(self, client, db_session):
        _signup(client, OWNER_SIGNUP)
        user = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
        assert user.owner_verified is False
        assert user.fayda_id_number == OWNER_SIGNUP["fayda_id_number"]

    def test_duplicate_fayda_id_rejected(self, client):
        _signup(client, OWNER_SIGNUP)
        duplicate = {**RENTER_SIGNUP, "fayda_id_number": OWNER_SIGNUP["fayda_id_number"]}
        response = client.post("/api/v1/rentals/signup", json=duplicate)
        assert response.status_code == 400

    def test_invalid_account_type_rejected(self, client):
        response = client.post(
            "/api/v1/rentals/signup",
            json={**RENTER_SIGNUP, "account_type": "broker"},
        )
        assert response.status_code == 422


class TestRoleGuards:
    def test_renter_cannot_create_listing(self, client, renter_token):
        response = client.post(
            "/api/v1/rentals/listings",
            json={"property_id": 1},
            headers=_headers(renter_token),
        )
        assert response.status_code == 403

    def test_owner_cannot_access_review_queue(self, client, owner_token):
        response = client.get(
            "/api/v1/rentals/listings?status=pending_review",
            headers=_headers(owner_token),
        )
        assert response.status_code == 403

    def test_owner_cannot_review_listing(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={"action": "publish"},
            headers=_headers(owner_token),
        )
        assert response.status_code == 403

    def test_renter_cannot_verify_owner(self, client, renter_token):
        response = client.post(
            "/api/v1/rentals/owners/verify",
            json={"user_id": 1},
            headers=_headers(renter_token),
        )
        assert response.status_code == 403

    def test_unauthenticated_queue_request_rejected(self, client):
        response = client.get("/api/v1/rentals/listings?status=pending_review")
        assert response.status_code == 401

    def test_status_param_is_officer_only_even_for_published(self, client):
        # The explicit status param is the officer queue; public browsing
        # always uses the redacted no-param path.
        response = client.get("/api/v1/rentals/listings?status=published")
        assert response.status_code == 401


class TestOwnerListingFlow:
    def test_create_listing_auto_creates_rent_valuation(self, client, db_session, owner_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        assert listing["status"] == "pending_review"
        assert listing["suggested_rent"] > 0
        assert listing["band_min"] < listing["suggested_rent"] < listing["band_max"]
        assert listing["public_id"].startswith("AA-LST-")

        valuation = db_session.query(Valuation).filter(Valuation.property_id == property_id).first()
        assert valuation is not None
        assert valuation.purpose == "rent"

    def test_low_confidence_marks_officer_review_required(self, client, owner_token):
        # Fresh test DB has no rent comps, so confidence stays below the floor
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        assert listing["requires_officer_review"] is True

    def test_duplicate_active_listing_rejected(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)
        response = client.post(
            "/api/v1/rentals/listings",
            json={"property_id": property_id},
            headers=_headers(owner_token),
        )
        assert response.status_code == 400

    def test_cannot_list_someone_elses_property(self, client, owner_token, db_session):
        second_owner = {
            **OWNER_SIGNUP,
            "email": "owner2@example.com",
            "phone": "+251944444444",
            "fayda_id_number": "555566667777",
        }
        other_token = _signup(client, second_owner)
        property_id = _create_property(client, owner_token)
        response = client.post(
            "/api/v1/rentals/listings",
            json={"property_id": property_id},
            headers=_headers(other_token),
        )
        assert response.status_code == 400


class TestOfficerReview:
    def test_band_adjust_without_reason_rejected(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={"action": "adjust_band", "band_min": 20000, "band_max": 30000},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400

    def test_band_adjust_with_reason_succeeds(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={
                "action": "adjust_band",
                "band_min": 20000,
                "band_max": 30000,
                "reason": "Neighborhood comparables support a lower band",
            },
            headers=_headers(officer_token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["band_min"] == 20000
        assert data["band_max"] == 30000

    def test_publish_blocked_for_unverified_owner(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={"action": "publish"},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400
        assert "not verified" in response.json()["detail"]

    def test_verify_owner_is_audited(self, client, db_session, owner_token, officer_token):
        owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
        response = client.post(
            "/api/v1/rentals/owners/verify",
            json={"user_id": owner.id},
            headers=_headers(officer_token),
        )
        assert response.status_code == 200
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.table_name == "users", AuditLog.action == "owner_verify")
            .first()
        )
        assert audit is not None
        assert audit.record_id == owner.id

    def test_publish_writes_audit_row(self, client, db_session, owner_token, officer_token):
        listing = _publish_flow(client, db_session, owner_token, officer_token)
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.table_name == "rental_listings", AuditLog.action == "publish")
            .first()
        )
        assert audit is not None
        assert audit.new_values["public_id"] == listing["public_id"]

    def test_adjust_after_publish_requires_withdraw(self, client, db_session, owner_token, officer_token):
        listing = _publish_flow(client, db_session, owner_token, officer_token)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={
                "action": "adjust_band",
                "band_min": 1000,
                "band_max": 2000,
                "reason": "post-publish drift attempt",
            },
            headers=_headers(officer_token),
        )
        assert response.status_code == 400
        assert "withdrawn" in response.json()["detail"]

    def test_reject_requires_reason(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.patch(
            f"/api/v1/rentals/listings/{listing['public_id']}/review",
            json={"action": "reject"},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400


def _publish_flow(client, db_session, owner_token, officer_token) -> dict:
    """Owner creates a listing, officer verifies the owner and publishes."""
    property_id = _create_property(client, owner_token)
    listing = _create_listing(client, owner_token, property_id)
    owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
    verify = client.post(
        "/api/v1/rentals/owners/verify",
        json={"user_id": owner.id},
        headers=_headers(officer_token),
    )
    assert verify.status_code == 200
    response = client.patch(
        f"/api/v1/rentals/listings/{listing['public_id']}/review",
        json={"action": "publish"},
        headers=_headers(officer_token),
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]


class TestPublicBrowse:
    def test_unpublished_listing_is_public_404(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.get(f"/api/v1/rentals/listings/{listing['public_id']}")
        assert response.status_code == 404

    def test_public_search_returns_published_only(self, client, db_session, owner_token, officer_token):
        _publish_flow(client, db_session, owner_token, officer_token)
        response = client.get("/api/v1/rentals/listings")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["data"][0]["property"]["subcity"] == "Bole"

    def test_public_search_empty_before_publish(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)
        response = client.get("/api/v1/rentals/listings")
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_public_payload_has_no_owner_pii(self, client, db_session, owner_token, officer_token):
        _publish_flow(client, db_session, owner_token, officer_token)
        response = client.get("/api/v1/rentals/listings")
        flat = response.text
        assert "owner_name" not in flat
        assert "owner_user_id" not in flat
        assert "Kebede" not in flat
        assert "+251911111111" not in flat
        assert "owner@example.com" not in flat
        assert "fayda" not in flat.lower()

    def test_public_detail_after_publish(self, client, db_session, owner_token, officer_token):
        listing = _publish_flow(client, db_session, owner_token, officer_token)
        response = client.get(f"/api/v1/rentals/listings/{listing['public_id']}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["public_id"] == listing["public_id"]
        assert data["band_min"] < data["suggested_rent"] < data["band_max"]

    def test_district_filter(self, client, db_session, owner_token, officer_token):
        _publish_flow(client, db_session, owner_token, officer_token)
        hit = client.get("/api/v1/rentals/listings?district=Bole")
        miss = client.get("/api/v1/rentals/listings?district=Yeka")
        assert hit.json()["total"] == 1
        assert miss.json()["total"] == 0

    def test_officer_published_queue_keeps_officer_detail(
        self, client, db_session, owner_token, officer_token
    ):
        _publish_flow(client, db_session, owner_token, officer_token)
        response = client.get(
            "/api/v1/rentals/listings?status=published",
            headers=_headers(officer_token),
        )
        assert response.status_code == 200
        record = response.json()["data"][0]
        assert record["owner_name"] == OWNER_SIGNUP["full_name"]
        assert record["property_address"] == PROPERTY_PAYLOAD["address"]

    def test_bedrooms_filter(self, client, db_session, owner_token, officer_token):
        _publish_flow(client, db_session, owner_token, officer_token)
        hit = client.get("/api/v1/rentals/listings?bedrooms=2")
        miss = client.get("/api/v1/rentals/listings?bedrooms=4")
        assert hit.json()["total"] == 1
        assert miss.json()["total"] == 0


class TestOwnerListings:
    def test_my_listings_returns_owner_records(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)
        response = client.get("/api/v1/rentals/my-listings", headers=_headers(owner_token))
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["data"][0]["status"] == "pending_review"

    def test_withdraw_own_listing(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.post(
            f"/api/v1/rentals/listings/{listing['public_id']}/withdraw",
            json={"reason": "changed my mind"},
            headers=_headers(owner_token),
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "withdrawn"

    def test_renter_cannot_withdraw_someone_elses_listing(self, client, owner_token, renter_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)
        response = client.post(
            f"/api/v1/rentals/listings/{listing['public_id']}/withdraw",
            json={},
            headers=_headers(renter_token),
        )
        assert response.status_code == 403


class TestReviewCheckpointFixes:
    """Regression tests for the review-1 checkpoint fixes."""

    def test_signup_sets_refresh_cookie_and_omits_body_token(self, client):
        response = client.post("/api/v1/rentals/signup", json=OWNER_SIGNUP)
        assert response.status_code == 201
        data = response.json()["data"]
        assert "refresh_token" not in data
        assert response.cookies.get("valuadis_refresh")

    def test_fayda_id_unique_at_database_level(self, client, db_session):
        from sqlalchemy.exc import IntegrityError

        _signup(client, OWNER_SIGNUP)
        _signup(client, RENTER_SIGNUP)
        second = db_session.query(User).filter(User.email == RENTER_SIGNUP["email"]).first()
        second.fayda_id_number = OWNER_SIGNUP["fayda_id_number"]
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_commercial_property_cannot_be_listed(self, client, owner_token):
        payload = {**PROPERTY_PAYLOAD, "property_type": "commercial", "property_subtype": "office"}
        response = client.post("/api/v1/properties", json=payload, headers=_headers(owner_token))
        assert response.status_code == 201, response.text
        property_id = response.json()["data"]["id"]

        response = client.post(
            "/api/v1/rentals/listings",
            json={"property_id": property_id},
            headers=_headers(owner_token),
        )
        assert response.status_code == 400
        assert "residential" in response.json()["detail"].lower()
