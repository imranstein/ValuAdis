"""
Rental Application Tests (Phase C)

Server-side band enforcement (edges accepted, ±1 birr rejected as 422),
one active application per renter per listing, accept auto-rejects siblings
and moves the listing to `rented`, and state guards (no applying to
withdrawn/rented listings). Rate limiting is covered separately.
"""

import pytest
from fastapi.testclient import TestClient

from app.data.models.audit_log import AuditLog
from app.data.models.role import Role
from app.data.models.user import User
from app.modules.rentals.application_service import RATE_LIMIT_MAX_APPLICATIONS


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


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


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


def _publish_listing(client, db_session, owner_token, officer_token) -> dict:
    prop = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(owner_token))
    property_id = prop.json()["data"]["id"]
    listing = client.post(
        "/api/v1/rentals/listings", json={"property_id": property_id}, headers=_headers(owner_token)
    ).json()["data"]
    owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
    client.post("/api/v1/rentals/owners/verify", json={"user_id": owner.id}, headers=_headers(officer_token))
    published = client.patch(
        f"/api/v1/rentals/listings/{listing['public_id']}/review",
        json={"action": "publish"},
        headers=_headers(officer_token),
    )
    assert published.status_code == 200, published.text
    return published.json()["data"]


@pytest.fixture
def owner_token(client):
    return _signup(client, OWNER_SIGNUP)


@pytest.fixture
def renter_token(client):
    return _signup(client, RENTER_SIGNUP)


@pytest.fixture
def officer_token(client, db_session):
    return _make_officer(client, db_session)


@pytest.fixture
def published(client, db_session, owner_token, officer_token):
    return _publish_listing(client, db_session, owner_token, officer_token)


class TestBandEnforcement:
    def test_offer_at_band_min_accepted(self, client, published, renter_token):
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["band_min"]},
            headers=_headers(renter_token),
        )
        assert response.status_code == 201, response.text
        assert response.json()["data"]["status"] == "pending"

    def test_offer_at_band_max_accepted(self, client, published, renter_token):
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["band_max"]},
            headers=_headers(renter_token),
        )
        assert response.status_code == 201, response.text

    def test_offer_below_band_is_422(self, client, published, renter_token):
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["band_min"] - 1},
            headers=_headers(renter_token),
        )
        assert response.status_code == 422

    def test_offer_above_band_is_422(self, client, published, renter_token):
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["band_max"] + 1},
            headers=_headers(renter_token),
        )
        assert response.status_code == 422


class TestApplicationGuards:
    def test_double_apply_blocked(self, client, published, renter_token):
        payload = {"offered_rent": published["suggested_rent"]}
        first = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json=payload, headers=_headers(renter_token),
        )
        assert first.status_code == 201
        second = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json=payload, headers=_headers(renter_token),
        )
        assert second.status_code == 400

    def test_cannot_apply_to_unpublished_listing(self, client, owner_token, renter_token):
        prop = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(owner_token))
        property_id = prop.json()["data"]["id"]
        listing = client.post(
            "/api/v1/rentals/listings", json={"property_id": property_id}, headers=_headers(owner_token)
        ).json()["data"]
        response = client.post(
            f"/api/v1/rentals/listings/{listing['public_id']}/applications",
            json={"offered_rent": listing["suggested_rent"]},
            headers=_headers(renter_token),
        )
        assert response.status_code == 400

    def test_owner_cannot_apply_to_own_listing(self, client, db_session, published, owner_token):
        # Give the owner account a renter role so the role guard passes; the
        # service must still reject applying to your own listing.
        owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
        renter_role = db_session.query(Role).filter(Role.name == "renter").first()
        if renter_role is None:
            renter_role = Role(name="renter", display_name="Renter", is_active=True)
            db_session.add(renter_role)
            db_session.commit()
        owner.roles.append(renter_role)
        db_session.commit()
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]},
            headers=_headers(owner_token),
        )
        assert response.status_code == 400

    def test_property_owner_role_alone_cannot_apply(self, client, published, owner_token):
        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]},
            headers=_headers(owner_token),
        )
        assert response.status_code == 403


class TestAcceptCascade:
    def _apply_as(self, client, public_id, signup, offered):
        token = _signup(client, signup)
        response = client.post(
            f"/api/v1/rentals/listings/{public_id}/applications",
            json={"offered_rent": offered},
            headers=_headers(token),
        )
        assert response.status_code == 201, response.text
        return response.json()["data"]["id"]

    def test_accept_rejects_siblings_and_rents_listing(
        self, client, db_session, published, owner_token
    ):
        app1 = self._apply_as(client, published["public_id"], RENTER_SIGNUP, published["suggested_rent"])
        second_renter = {
            **RENTER_SIGNUP,
            "email": "renter2@example.com",
            "phone": "+251944444444",
            "fayda_id_number": "111122223333",
        }
        app2 = self._apply_as(client, published["public_id"], second_renter, published["band_max"])

        accept = client.post(
            f"/api/v1/rentals/applications/{app1}/decision",
            json={"action": "accept"},
            headers=_headers(owner_token),
        )
        assert accept.status_code == 200, accept.text
        assert accept.json()["data"]["status"] == "accepted"

        # Sibling auto-rejected.
        from app.data.models.rental_application import RentalApplication

        sibling = db_session.query(RentalApplication).filter(RentalApplication.id == app2).first()
        assert sibling.status == "rejected"

        # Listing moved to rented; further applications are blocked.
        third_renter = {
            **RENTER_SIGNUP,
            "email": "renter3@example.com",
            "phone": "+251955555555",
            "fayda_id_number": "444455556666",
        }
        token = _signup(client, third_renter)
        blocked = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]},
            headers=_headers(token),
        )
        assert blocked.status_code == 400

    def test_reject_keeps_listing_published(self, client, published, owner_token):
        app1 = self._apply_as(client, published["public_id"], RENTER_SIGNUP, published["suggested_rent"])
        reject = client.post(
            f"/api/v1/rentals/applications/{app1}/decision",
            json={"action": "reject", "reason": "prefers another applicant"},
            headers=_headers(owner_token),
        )
        assert reject.status_code == 200
        assert reject.json()["data"]["status"] == "rejected"
        detail = client.get(f"/api/v1/rentals/listings/{published['public_id']}")
        assert detail.status_code == 200  # still published

    def test_apply_is_audited(self, client, db_session, published, renter_token):
        client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]},
            headers=_headers(renter_token),
        )
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.table_name == "rental_applications", AuditLog.action == "apply")
            .first()
        )
        assert audit is not None


class TestRateLimit:
    def test_rate_limit_blocks_excess_applications(self, client, db_session, published, renter_token):
        # Seed applications up to the limit on other listings is overkill;
        # applications on distinct listings all count toward the per-account
        # window. Create enough published listings to exhaust the limit.
        renter = db_session.query(User).filter(User.email == RENTER_SIGNUP["email"]).first()
        from app.data.models.rental_application import RentalApplication

        for i in range(RATE_LIMIT_MAX_APPLICATIONS):
            db_session.add(
                RentalApplication(
                    listing_id=99000 + i,
                    renter_user_id=renter.id,
                    offered_rent=1000.0,
                    status="rejected",
                )
            )
        db_session.commit()

        response = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]},
            headers=_headers(renter_token),
        )
        assert response.status_code == 429
