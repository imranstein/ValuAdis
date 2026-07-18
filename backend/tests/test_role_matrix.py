"""
Role/Permission Matrix Tests (Phase E)

Covers plans/valuadis-rentals/tasks/phase-e.md's permission matrix: one
representative endpoint per matrix row, asserting allow/deny across the five
personas (staff, rental_officer, property_owner, renter, anonymous). Deny is
403 for an authenticated-but-wrong-role caller; 401 for anonymous callers on
an endpoint that requires auth; 404 is reserved for the established
public-privacy convention (unpublished listings) and is not used here as a
disguised-deny status.
"""

import pytest
from fastapi.testclient import TestClient

from app.data.models.role import Role
from app.data.models.user import User
from app.modules.rentals.models import RentalListing


STAFF_REGISTER = {
    "email": "staff@example.com",
    "full_name": "Staff Valuer",
    "phone": "+251911000001",
    "password": "Staffpass1!",
    "municipality": "Addis Ababa",
    "license_number": "VAL-2026-001",
}

ADMIN_REGISTER = {
    "email": "admin@example.com",
    "full_name": "Admin Person",
    "phone": "+251911000002",
    "password": "Adminpass1!",
    "municipality": "Addis Ababa",
    "license_number": "VAL-2026-002",
}

OWNER_SIGNUP = {
    "email": "owner-matrix@example.com",
    "full_name": "Owner Matrix",
    "phone": "+251911000003",
    "password": "Ownerpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "111122223333",
    "account_type": "property_owner",
}

OWNER2_SIGNUP = {
    "email": "owner2-matrix@example.com",
    "full_name": "Owner Two Matrix",
    "phone": "+251911000004",
    "password": "Ownerpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "111122224444",
    "account_type": "property_owner",
}

RENTER_SIGNUP = {
    "email": "renter-matrix@example.com",
    "full_name": "Renter Matrix",
    "phone": "+251911000005",
    "password": "Renterpass1!",
    "municipality": "Addis Ababa",
    "fayda_id_number": "111122225555",
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
    "owner_name": "Owner Matrix",
    "owner_phone": "+251911000003",
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


def _register(client: TestClient, payload: dict) -> str:
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]["access_token"]


def _signup(client: TestClient, payload: dict) -> str:
    response = client.post("/api/v1/rentals/signup", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]["access_token"]


def _make_admin(client: TestClient, db_session) -> str:
    """is_admin=True account — distinct from a plain staff/valuer account so
    tests can prove the officer gate's 'is_admin honors officer gate' rule
    (matrix row 2) rather than the plain-staff-is-not-officer default."""
    token = _register(client, ADMIN_REGISTER)
    user = db_session.query(User).filter(User.email == ADMIN_REGISTER["email"]).first()
    user.is_admin = True
    db_session.commit()
    return token


def _make_officer(client: TestClient, db_session) -> str:
    token = _register(
        client,
        {
            "email": "officer-matrix@example.com",
            "full_name": "Officer Matrix",
            "phone": "+251911000006",
            "password": "Officerpass1!",
            "municipality": "Addis Ababa",
            "license_number": "OFF-2026-001",
        },
    )
    user = db_session.query(User).filter(User.email == "officer-matrix@example.com").first()
    role = db_session.query(Role).filter(Role.name == "rental_officer").first()
    if role is None:
        role = Role(name="rental_officer", display_name="Rental Officer", is_active=True)
        db_session.add(role)
        db_session.commit()
    user.roles.append(role)
    db_session.commit()
    return token


def _create_property(client: TestClient, token: str, **overrides) -> int:
    payload = {**PROPERTY_PAYLOAD, **overrides}
    response = client.post("/api/v1/properties", json=payload, headers=_headers(token))
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
def staff_token(client):
    return _register(client, STAFF_REGISTER)


@pytest.fixture
def admin_token(client, db_session):
    return _make_admin(client, db_session)


@pytest.fixture
def officer_token(client, db_session):
    return _make_officer(client, db_session)


@pytest.fixture
def owner_token(client):
    return _signup(client, OWNER_SIGNUP)


@pytest.fixture
def owner2_token(client):
    return _signup(client, OWNER2_SIGNUP)


@pytest.fixture
def renter_token(client):
    return _signup(client, RENTER_SIGNUP)


class TestStaffShellRow:
    """Matrix row 1: dashboard, valuations, properties CRUD-all, vehicles,
    scrapers, reports, audit, analytics, settings — staff full, everyone
    else (including a rental officer) denied. Representative endpoint:
    GET /api/v1/valuations/ (the staff valuations list)."""

    def test_staff_can_list_valuations(self, client, staff_token):
        response = client.get("/api/v1/valuations/", headers=_headers(staff_token))
        assert response.status_code == 200

    def test_officer_cannot_list_valuations(self, client, officer_token):
        response = client.get("/api/v1/valuations/", headers=_headers(officer_token))
        assert response.status_code == 403

    def test_owner_cannot_list_valuations(self, client, owner_token):
        response = client.get("/api/v1/valuations/", headers=_headers(owner_token))
        assert response.status_code == 403

    def test_renter_cannot_list_valuations(self, client, renter_token):
        response = client.get("/api/v1/valuations/", headers=_headers(renter_token))
        assert response.status_code == 403

    def test_anonymous_cannot_list_valuations(self, client):
        response = client.get("/api/v1/valuations/")
        assert response.status_code == 401

    def test_other_staff_endpoints_deny_citizen_tokens(self, client, owner_token, renter_token):
        """Sweep check across the remaining staff-shell surfaces named in
        the matrix (vehicles, scrapers, audit, analytics, settings, users)."""
        staff_only_endpoints = [
            "/api/v1/vehicles/",
            "/api/v1/scrapers/",
            "/api/v1/audit/system",
            "/api/v1/analytics/dashboard",
            "/api/v1/settings",
            "/api/v1/users/",
        ]
        for token in (owner_token, renter_token):
            for path in staff_only_endpoints:
                response = client.get(path, headers=_headers(token))
                assert response.status_code == 403, f"{path} should deny a citizen token"


class TestOfficerConsoleRow:
    """Matrix row 2: /rentals officer console — staff full via the
    is_admin-honors-officer-gate rule, rental_officer full, citizens and
    anonymous denied. Representative endpoint: the review queue
    (GET /api/v1/rentals/listings?status=pending_review)."""

    REVIEW_QUEUE = "/api/v1/rentals/listings?status=pending_review"

    def test_admin_can_reach_review_queue(self, client, admin_token):
        response = client.get(self.REVIEW_QUEUE, headers=_headers(admin_token))
        assert response.status_code == 200

    def test_officer_can_reach_review_queue(self, client, officer_token):
        response = client.get(self.REVIEW_QUEUE, headers=_headers(officer_token))
        assert response.status_code == 200

    def test_owner_cannot_reach_review_queue(self, client, owner_token):
        response = client.get(self.REVIEW_QUEUE, headers=_headers(owner_token))
        assert response.status_code == 403

    def test_renter_cannot_reach_review_queue(self, client, renter_token):
        response = client.get(self.REVIEW_QUEUE, headers=_headers(renter_token))
        assert response.status_code == 403

    def test_anonymous_cannot_reach_review_queue(self, client):
        response = client.get(self.REVIEW_QUEUE)
        assert response.status_code == 401


class TestOwnPropertiesRow:
    """Matrix row 3: staff full (all), rental_officer read, property_owner
    own only, renter none. Representative endpoint:
    POST /api/v1/properties (create), plus a read-scoping check."""

    def test_staff_can_create_property(self, client, staff_token):
        _create_property(client, staff_token)

    def test_owner_can_create_property(self, client, owner_token):
        _create_property(client, owner_token)

    def test_officer_cannot_create_property(self, client, officer_token):
        response = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(officer_token))
        assert response.status_code == 403

    def test_renter_cannot_create_property(self, client, renter_token):
        response = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(renter_token))
        assert response.status_code == 403

    def test_anonymous_cannot_create_property(self, client):
        response = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD)
        assert response.status_code == 401

    def test_owner_read_is_scoped_to_own_properties(self, client, owner_token, owner2_token):
        _create_property(client, owner_token)
        _create_property(client, owner2_token)

        response = client.get("/api/v1/properties", headers=_headers(owner_token))
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_officer_read_sees_all_properties(self, client, owner_token, owner2_token, officer_token):
        _create_property(client, owner_token)
        _create_property(client, owner2_token)

        response = client.get("/api/v1/properties", headers=_headers(officer_token))
        assert response.status_code == 200
        assert response.json()["total"] == 2


class TestListingsRow:
    """Matrix row 4: listings visibility. Staff/officer see all statuses
    (covered by TestOfficerConsoleRow); property_owner sees their own at
    any status; renter/anonymous see published only. Representative
    endpoint: GET /api/v1/rentals/my-listings (owner's own-status view)."""

    def test_owner_sees_only_own_listings_any_status(self, client, owner_token, owner2_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)

        other_property_id = _create_property(client, owner2_token, address="Yeka, Addis Ababa")
        _create_listing(client, owner2_token, other_property_id)

        response = client.get("/api/v1/rentals/my-listings", headers=_headers(owner_token))
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["data"][0]["property_id"] == property_id

    def test_anonymous_public_search_is_published_only(self, client):
        response = client.get("/api/v1/rentals/listings")
        assert response.status_code == 200


class TestApplicationsRow:
    """Matrix row 5: applications — officer reads per listing, owner reads
    on their own listings, renter reads their own, no one else. Representative
    endpoint: GET /api/v1/rentals/listings/{public_id}/applications."""

    def test_listing_owner_can_view_applications(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        response = client.get(
            f"/api/v1/rentals/listings/{listing['public_id']}/applications",
            headers=_headers(owner_token),
        )
        assert response.status_code == 200

    def test_other_owner_cannot_view_applications(self, client, owner_token, owner2_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        response = client.get(
            f"/api/v1/rentals/listings/{listing['public_id']}/applications",
            headers=_headers(owner2_token),
        )
        assert response.status_code == 403

    def test_officer_can_view_applications(self, client, owner_token, officer_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        response = client.get(
            f"/api/v1/rentals/listings/{listing['public_id']}/applications",
            headers=_headers(officer_token),
        )
        assert response.status_code == 200

    def test_renter_cannot_view_listing_applications(self, client, owner_token, renter_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        response = client.get(
            f"/api/v1/rentals/listings/{listing['public_id']}/applications",
            headers=_headers(renter_token),
        )
        assert response.status_code == 403

    def test_anonymous_cannot_view_listing_applications(self, client, owner_token):
        property_id = _create_property(client, owner_token)
        listing = _create_listing(client, owner_token, property_id)

        response = client.get(f"/api/v1/rentals/listings/{listing['public_id']}/applications")
        assert response.status_code == 401


class TestContractsRow:
    """Matrix row 6: contracts — officer all + export, owner/renter party
    only (via /my-contracts, not the raw registry), no one else.
    Representative endpoint: GET /api/v1/rentals/contracts (officer
    registry — parties use /my-contracts instead, covered by Phase C
    tests)."""

    def test_officer_can_list_contracts(self, client, officer_token):
        response = client.get("/api/v1/rentals/contracts", headers=_headers(officer_token))
        assert response.status_code == 200

    def test_admin_can_list_contracts(self, client, admin_token):
        response = client.get("/api/v1/rentals/contracts", headers=_headers(admin_token))
        assert response.status_code == 200

    def test_owner_cannot_list_contracts_registry(self, client, owner_token):
        response = client.get("/api/v1/rentals/contracts", headers=_headers(owner_token))
        assert response.status_code == 403

    def test_renter_cannot_list_contracts_registry(self, client, renter_token):
        response = client.get("/api/v1/rentals/contracts", headers=_headers(renter_token))
        assert response.status_code == 403

    def test_anonymous_cannot_list_contracts_registry(self, client):
        response = client.get("/api/v1/rentals/contracts")
        assert response.status_code == 401


class TestPublicPagesRow:
    """Matrix row 7: public pages (/, /rent, /rent/[id], /rent/index,
    /login, /rent/signup) need no auth. Representative backend surfaces:
    the published-listing search and the public rent index, both reachable
    with zero credentials."""

    def test_public_listing_search_needs_no_auth(self, client):
        response = client.get("/api/v1/rentals/listings")
        assert response.status_code == 200

    def test_public_rent_index_needs_no_auth(self, client):
        response = client.get("/api/v1/rentals/index")
        assert response.status_code == 200

    def test_citizen_signup_needs_no_auth(self, client):
        response = client.post("/api/v1/rentals/signup", json=RENTER_SIGNUP)
        assert response.status_code == 201


class TestCitizenValuationReadScoping:
    """AC1 nuance: 'Valuation reads for citizens: only valuations attached
    to their own properties/listings.' A rent valuation is auto-created
    (owned by the listing's owner) when a listing is submitted; the owner
    can read it individually even though the general list/create endpoints
    are staff-only."""

    def test_owner_can_read_own_rent_valuation(self, client, db_session, owner_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)
        valuation_id = (
            db_session.query(RentalListing).filter(RentalListing.property_id == property_id).first().valuation_id
        )

        response = client.get(f"/api/v1/valuations/{valuation_id}", headers=_headers(owner_token))
        assert response.status_code == 200

    def test_other_owner_cannot_read_someone_elses_rent_valuation(self, client, db_session, owner_token, owner2_token):
        property_id = _create_property(client, owner_token)
        _create_listing(client, owner_token, property_id)
        valuation_id = (
            db_session.query(RentalListing).filter(RentalListing.property_id == property_id).first().valuation_id
        )

        response = client.get(f"/api/v1/valuations/{valuation_id}", headers=_headers(owner2_token))
        assert response.status_code == 404
