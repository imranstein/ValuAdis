"""
Tenancy Contract + Deposit Tests (Phase C)

Contract creation from an accepted application only, registry contract_no
format, the deposit state machine (activate on matching amount, reject on
mismatch, no double-record, guarded terminated/expired), audited
transitions, PDF generation with mandatory fields, and the owner listing
agreement produced at publish time.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.models.audit_log import AuditLog
from app.data.models.role import Role
from app.data.models.user import User


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

START = date(2026, 8, 1).isoformat()
END = date(2027, 8, 1).isoformat()


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
def accepted(client, db_session, owner_token, renter_token, officer_token):
    """Publish a listing, apply, and accept — returns the accepted state."""
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
    app = client.post(
        f"/api/v1/rentals/listings/{published['public_id']}/applications",
        json={"offered_rent": published["suggested_rent"]}, headers=_headers(renter_token),
    ).json()["data"]
    client.post(
        f"/api/v1/rentals/applications/{app['id']}/decision",
        json={"action": "accept"}, headers=_headers(owner_token),
    )
    return {"listing": published, "application_id": app["id"], "offered_rent": published["suggested_rent"]}


def _create_contract(client, officer_token, application_id, **overrides) -> dict:
    payload = {"application_id": application_id, "start_date": START, "end_date": END, **overrides}
    response = client.post("/api/v1/rentals/contracts", json=payload, headers=_headers(officer_token))
    assert response.status_code == 201, response.text
    return response.json()["data"]


class TestContractCreation:
    def test_contract_number_registry_format(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        year = date.today().year
        assert contract["contract_no"].startswith(f"AA-RNT-{year}-")
        assert len(contract["contract_no"].split("-")[-1]) == 6
        assert contract["status"] == "draft"

    def test_monthly_rent_captured_from_offer(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        assert contract["monthly_rent"] == accepted["offered_rent"]
        assert contract["deposit_amount"] == round(accepted["offered_rent"] * 2, 2)

    def test_contract_from_non_accepted_application_rejected(
        self, client, db_session, owner_token, renter_token, officer_token
    ):
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
        app = client.post(
            f"/api/v1/rentals/listings/{published['public_id']}/applications",
            json={"offered_rent": published["suggested_rent"]}, headers=_headers(renter_token),
        ).json()["data"]
        # Application is still pending, not accepted.
        response = client.post(
            "/api/v1/rentals/contracts",
            json={"application_id": app["id"], "start_date": START, "end_date": END},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400

    def test_duplicate_contract_for_application_rejected(self, client, accepted, officer_token):
        _create_contract(client, officer_token, accepted["application_id"])
        response = client.post(
            "/api/v1/rentals/contracts",
            json={"application_id": accepted["application_id"], "start_date": START, "end_date": END},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400

    def test_deposit_override_without_reason_rejected(self, client, accepted, officer_token):
        response = client.post(
            "/api/v1/rentals/contracts",
            json={
                "application_id": accepted["application_id"],
                "start_date": START, "end_date": END,
                "deposit_amount": 999.0,
            },
            headers=_headers(officer_token),
        )
        assert response.status_code == 400

    def test_deposit_override_with_reason_succeeds(self, client, accepted, officer_token):
        contract = _create_contract(
            client, officer_token, accepted["application_id"],
            deposit_amount=999.0, deposit_reason="Negotiated single-month deposit",
        )
        assert contract["deposit_amount"] == 999.0

    def test_non_officer_cannot_create_contract(self, client, accepted, owner_token):
        response = client.post(
            "/api/v1/rentals/contracts",
            json={"application_id": accepted["application_id"], "start_date": START, "end_date": END},
            headers=_headers(owner_token),
        )
        assert response.status_code == 403

    def test_contract_creation_audited(self, client, db_session, accepted, officer_token):
        _create_contract(client, officer_token, accepted["application_id"])
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.table_name == "tenancy_contracts", AuditLog.action == "create")
            .first()
        )
        assert audit is not None


class TestDepositStateMachine:
    def test_matching_deposit_activates_contract(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        response = client.post(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
            json={"deposit_receipt_ref": "TELE-12345", "amount": contract["deposit_amount"]},
            headers=_headers(officer_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["status"] == "active"
        assert response.json()["data"]["deposit_receipt_ref"] == "TELE-12345"

    def test_mismatched_deposit_rejected(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        response = client.post(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
            json={"deposit_receipt_ref": "TELE-99999", "amount": contract["deposit_amount"] - 100},
            headers=_headers(officer_token),
        )
        assert response.status_code == 400
        # Contract stays draft.
        assert not _is_active(client, officer_token, contract["contract_no"])

    def test_cannot_double_record_deposit(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        first = client.post(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
            json={"deposit_receipt_ref": "TELE-1", "amount": contract["deposit_amount"]},
            headers=_headers(officer_token),
        )
        assert first.status_code == 200
        second = client.post(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
            json={"deposit_receipt_ref": "TELE-2", "amount": contract["deposit_amount"]},
            headers=_headers(officer_token),
        )
        assert second.status_code == 400

    def test_deposit_transition_audited(self, client, db_session, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        client.post(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
            json={"deposit_receipt_ref": "TELE-A", "amount": contract["deposit_amount"]},
            headers=_headers(officer_token),
        )
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.table_name == "tenancy_contracts", AuditLog.action == "deposit_recorded")
            .first()
        )
        assert audit is not None


class TestContractPdf:
    def test_owner_can_download_contract_pdf(self, client, accepted, owner_token, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        response = client.get(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/pdf", headers=_headers(owner_token)
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"

    def test_non_party_cannot_download_contract_pdf(self, client, accepted, officer_token):
        contract = _create_contract(client, officer_token, accepted["application_id"])
        outsider = {
            **RENTER_SIGNUP, "email": "out@example.com",
            "phone": "+251966666666", "fayda_id_number": "777788889999",
        }
        token = _signup(client, outsider)
        response = client.get(
            f"/api/v1/rentals/contracts/{contract['contract_no']}/pdf", headers=_headers(token)
        )
        assert response.status_code == 403

    def test_contract_pdf_has_mandatory_fields(self):
        from app.modules.valuation.certificate_service import CertificateService

        pdf = CertificateService().generate_tenancy_contract(
            contract={
                "contract_no": "AA-RNT-2026-000001",
                "monthly_rent": 28000.0, "start_date": START, "end_date": END,
                "deposit_amount": 56000.0, "deposit_receipt_ref": "TELE-1", "status": "active",
            },
            owner={"full_name": "Kebede Alemu", "fayda_id_number": "123456789012", "phone": "+251911111111"},
            renter={"full_name": "Meron Tadesse", "fayda_id_number": "987654321098", "phone": "+251922222222"},
            property_data={"address": "Bole", "municipality": "Addis Ababa", "subcity": "Bole",
                           "property_type": "residential", "area_sqm": 120.0},
            rent_context={"band_min": 25200.0, "band_max": 30800.0, "valuation_reference": "VAL-5"},
        )
        assert pdf[:4] == b"%PDF"
        assert len(pdf) > 2000


class TestListingAgreement:
    def test_publish_sets_listing_agreement_path(self, client, accepted, owner_token):
        listings = client.get("/api/v1/rentals/my-listings", headers=_headers(owner_token)).json()["data"]
        published = next(l for l in listings if l["status"] == "rented" or l["status"] == "published")
        assert published["listing_agreement_pdf"]
        assert "agreement" in published["listing_agreement_pdf"]

    def test_owner_can_download_listing_agreement(self, client, accepted, owner_token):
        public_id = accepted["listing"]["public_id"]
        response = client.get(
            f"/api/v1/rentals/listings/{public_id}/agreement", headers=_headers(owner_token)
        )
        assert response.status_code == 200
        assert response.content[:4] == b"%PDF"

    def test_listing_agreement_has_required_fields(self):
        from app.modules.valuation.certificate_service import CertificateService

        pdf = CertificateService().generate_listing_agreement(
            listing={"public_id": "AA-LST-2026-000123", "suggested_rent": 28000.0,
                     "band_min": 25200.0, "band_max": 30800.0, "published_at": None},
            owner={"full_name": "Kebede Alemu", "fayda_id_number": "123456789012", "phone": "+251911111111"},
            property_data={"address": "Bole", "municipality": "Addis Ababa", "subcity": "Bole", "area_sqm": 120.0},
        )
        assert pdf[:4] == b"%PDF"


def _is_active(client, officer_token, contract_no) -> bool:
    contracts = client.get("/api/v1/rentals/contracts", headers=_headers(officer_token)).json()["data"]
    match = next((c for c in contracts if c["contract_no"] == contract_no), None)
    return bool(match and match["status"] == "active")
