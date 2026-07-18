"""
Renewal Cap — configured-value lookup + endpoint (Phase D, integration)

RenewalCapService.get_active_cap() must pick the config row whose effective
period covers the date being checked (not just "the latest row"), and fall
back to the documented default when nothing is seeded. The renewal endpoint
wires the check into a contract-shape stub: 200 inside the cap, 422 over it,
403 for non-officers.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.data.models.renewal_cap_config import RenewalCapConfig
from app.data.models.role import Role
from app.data.models.user import User
from app.modules.rentals.renewal_cap_service import FALLBACK_CAP_PCT, RenewalCapService

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


class TestConfigLookup:
    def test_no_config_row_uses_documented_fallback(self, db_session):
        cap = RenewalCapService(db_session).get_active_cap(as_of=date(2026, 8, 1))
        assert cap["cap_pct"] == FALLBACK_CAP_PCT
        assert cap["source"] == "fallback"

    def test_picks_row_covering_the_as_of_date(self, db_session):
        db_session.add(
            RenewalCapConfig(
                region="Addis Ababa", cap_pct=0.115,
                effective_from=date(2026, 7, 1), effective_until=None,
                directive_reference="2026/27 directive",
            )
        )
        db_session.commit()
        cap = RenewalCapService(db_session).get_active_cap(as_of=date(2026, 9, 1))
        assert float(cap["cap_pct"]) == 0.115
        assert cap["source"] == "configured"

    def test_superseded_directive_is_not_picked_after_its_period_ends(self, db_session):
        db_session.add_all(
            [
                RenewalCapConfig(
                    region="Addis Ababa", cap_pct=0.10,
                    effective_from=date(2025, 7, 1), effective_until=date(2026, 7, 1),
                ),
                RenewalCapConfig(
                    region="Addis Ababa", cap_pct=0.115,
                    effective_from=date(2026, 7, 1), effective_until=None,
                ),
            ]
        )
        db_session.commit()
        old_period = RenewalCapService(db_session).get_active_cap(as_of=date(2026, 1, 1))
        new_period = RenewalCapService(db_session).get_active_cap(as_of=date(2026, 8, 1))
        assert float(old_period["cap_pct"]) == 0.10
        assert float(new_period["cap_pct"]) == 0.115


@pytest.fixture
def officer_token(client, db_session):
    return _make_officer(client, db_session)


@pytest.fixture
def active_contract(client, db_session, officer_token):
    owner_signup = {
        "email": "owner@example.com", "full_name": "Kebede Alemu", "phone": "+251911111111",
        "password": "Ownerpass1!", "municipality": "Addis Ababa", "fayda_id_number": "123456789012",
        "account_type": "property_owner",
    }
    renter_signup = {
        "email": "renter@example.com", "full_name": "Meron Tadesse", "phone": "+251922222222",
        "password": "Renterpass1!", "municipality": "Addis Ababa", "fayda_id_number": "987654321098",
        "account_type": "renter",
    }
    owner_token = _signup(client, owner_signup)
    renter_token = _signup(client, renter_signup)
    prop = client.post(
        "/api/v1/properties",
        json={
            "address": "Bole, Addis Ababa", "municipality": "Addis Ababa", "subcity": "Bole",
            "property_type": "residential", "property_subtype": "apartment", "area_sqm": 120.0,
            "number_of_bedrooms": 2, "owner_name": "Kebede Alemu", "owner_phone": "+251911111111",
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]],
        },
        headers=_headers(owner_token),
    )
    property_id = prop.json()["data"]["id"]
    listing = client.post(
        "/api/v1/rentals/listings", json={"property_id": property_id}, headers=_headers(owner_token)
    ).json()["data"]
    owner = db_session.query(User).filter(User.email == owner_signup["email"]).first()
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
    contract = client.post(
        "/api/v1/rentals/contracts",
        json={"application_id": application["id"], "start_date": START, "end_date": END},
        headers=_headers(officer_token),
    ).json()["data"]
    return contract


class TestRenewalEndpoint:
    def test_renewal_within_cap_returns_200(self, client, officer_token, active_contract):
        max_allowed = active_contract["monthly_rent"] * 1.115
        response = client.post(
            f"/api/v1/rentals/contracts/{active_contract['contract_no']}/renewal",
            json={"proposed_rent": round(max_allowed, 2)},
            headers=_headers(officer_token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["allowed"] is True

    def test_renewal_over_cap_returns_422(self, client, officer_token, active_contract):
        over_cap = active_contract["monthly_rent"] * 1.2
        response = client.post(
            f"/api/v1/rentals/contracts/{active_contract['contract_no']}/renewal",
            json={"proposed_rent": over_cap},
            headers=_headers(officer_token),
        )
        assert response.status_code == 422

    def test_non_officer_cannot_check_renewal(self, client, active_contract):
        renter_token = _signup(
            client,
            {
                "email": "outsider@example.com", "full_name": "Outsider", "phone": "+251966666666",
                "password": "Outsider1!", "municipality": "Addis Ababa", "fayda_id_number": "555566667777",
                "account_type": "renter",
            },
        )
        response = client.post(
            f"/api/v1/rentals/contracts/{active_contract['contract_no']}/renewal",
            json={"proposed_rent": 1.0},
            headers=_headers(renter_token),
        )
        assert response.status_code == 403

    def test_unknown_contract_is_404(self, client, officer_token):
        response = client.post(
            "/api/v1/rentals/contracts/AA-RNT-2026-999999/renewal",
            json={"proposed_rent": 1000.0},
            headers=_headers(officer_token),
        )
        assert response.status_code == 404
