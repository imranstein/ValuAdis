"""
Contracts CSV Export (Phase D)

The tax-base deliverable: rental_officer only, columns include party Fayda
IDs (PII allowed here by design — this is the one export surface that is
officer-gated, unlike every public serializer in the module). Renter/owner
roles get 403, not a redacted CSV.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.data.models.role import Role
from app.data.models.user import User

START = date(2026, 8, 1).isoformat()
END = date(2027, 8, 1).isoformat()

OWNER_SIGNUP = {
    "email": "owner@example.com", "full_name": "Kebede Alemu", "phone": "+251911111111",
    "password": "Ownerpass1!", "municipality": "Addis Ababa", "fayda_id_number": "123456789012",
    "account_type": "property_owner",
}
RENTER_SIGNUP = {
    "email": "renter@example.com", "full_name": "Meron Tadesse", "phone": "+251922222222",
    "password": "Renterpass1!", "municipality": "Addis Ababa", "fayda_id_number": "987654321098",
    "account_type": "renter",
}
PROPERTY_PAYLOAD = {
    "address": "Bole, Addis Ababa", "municipality": "Addis Ababa", "subcity": "Bole",
    "property_type": "residential", "property_subtype": "apartment", "area_sqm": 120.0,
    "number_of_bedrooms": 2, "owner_name": "Kebede Alemu", "owner_phone": "+251911111111",
    "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]],
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
            "email": "officer@example.com", "full_name": "Officer Worku", "phone": "+251933333333",
            "password": "Officerpass1!", "municipality": "Addis Ababa", "license_number": "OFF-2026-001",
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
def registered_contract(client, db_session, owner_token, renter_token, officer_token):
    prop = client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=_headers(owner_token))
    property_id = prop.json()["data"]["id"]
    listing = client.post(
        "/api/v1/rentals/listings", json={"property_id": property_id}, headers=_headers(owner_token)
    ).json()["data"]
    owner = db_session.query(User).filter(User.email == OWNER_SIGNUP["email"]).first()
    client.post("/api/v1/rentals/owners/verify", json={"user_id": owner.id}, headers=_headers(officer_token))
    published = client.patch(
        f"/api/v1/rentals/listings/{listing['public_id']}/review",
        json={"action": "publish"}, headers=_headers(officer_token),
    ).json()["data"]
    application = client.post(
        f"/api/v1/rentals/listings/{published['public_id']}/applications",
        json={"offered_rent": published["suggested_rent"]}, headers=_headers(renter_token),
    ).json()["data"]
    client.post(
        f"/api/v1/rentals/applications/{application['id']}/decision",
        json={"action": "accept"}, headers=_headers(owner_token),
    )
    return client.post(
        "/api/v1/rentals/contracts",
        json={"application_id": application["id"], "start_date": START, "end_date": END},
        headers=_headers(officer_token),
    ).json()["data"]


class TestContractsExport:
    def test_officer_export_has_expected_columns(self, client, officer_token, registered_contract):
        response = client.get("/api/v1/rentals/contracts/export", headers=_headers(officer_token))
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")

        lines = response.text.strip().splitlines()
        header = lines[0].split(",")
        assert header == [
            "contract_no", "property_address", "municipality", "subcity",
            "owner_name", "owner_fayda_id", "renter_name", "renter_fayda_id",
            "monthly_rent", "deposit_amount", "deposit_receipt_ref",
            "status", "start_date", "end_date", "created_at",
        ]
        assert registered_contract["contract_no"] in response.text
        assert "123456789012" in response.text  # owner fayda id, PII allowed on this officer-gated export

    def test_renter_cannot_export_contracts(self, client, renter_token, registered_contract):
        response = client.get("/api/v1/rentals/contracts/export", headers=_headers(renter_token))
        assert response.status_code == 403

    def test_owner_cannot_export_contracts(self, client, owner_token, registered_contract):
        response = client.get("/api/v1/rentals/contracts/export", headers=_headers(owner_token))
        assert response.status_code == 403

    def test_anonymous_cannot_export_contracts(self, client, registered_contract):
        response = client.get("/api/v1/rentals/contracts/export")
        assert response.status_code in (401, 403)
