"""
Rent Index Endpoint + Aggregation Job (Phase D, integration)

Builds real active contracts through the full owner -> officer -> renter ->
deposit chain (same pattern as test_tenancy_contracts.py), runs the
aggregation job, and asserts: a district with enough active contracts
appears in the public API with a real median; a district with too few stays
suppressed (absent, not zeroed); and rerunning the job for the same period
does not duplicate rows.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.data.models.role import Role
from app.data.models.rent_index_snapshot import RentIndexSnapshot
from app.data.models.user import User
from app.modules.rentals.index_service import MIN_SAMPLE_SIZE, RentIndexService

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


def _active_contract(
    client: TestClient, db_session, officer_token: str, subcity: str, unit: int, band_position: float = 0.5
) -> float:
    """Full chain: owner lists a property in `subcity` -> officer publishes
    -> renter applies within the frozen band (at `band_position` between
    band_min=0.0 and band_max=1.0, so distinct calls yield distinct but
    always-valid rents) -> owner accepts -> officer registers the contract
    -> deposit recorded (contract becomes active). Returns the contract's
    monthly_rent."""
    owner_signup = {
        "email": f"owner{unit}@example.com",
        "full_name": f"Owner {unit}",
        "phone": f"+2519111{unit:05d}",
        "password": "Ownerpass1!",
        "municipality": "Addis Ababa",
        "fayda_id_number": f"1000000{unit:05d}",
        "account_type": "property_owner",
    }
    renter_signup = {
        "email": f"renter{unit}@example.com",
        "full_name": f"Renter {unit}",
        "phone": f"+2519222{unit:05d}",
        "password": "Renterpass1!",
        "municipality": "Addis Ababa",
        "fayda_id_number": f"2000000{unit:05d}",
        "account_type": "renter",
    }
    owner_token = _signup(client, owner_signup)
    renter_token = _signup(client, renter_signup)

    prop = client.post(
        "/api/v1/properties",
        json={
            "address": f"{subcity} Unit {unit}, Addis Ababa",
            "municipality": "Addis Ababa",
            "subcity": subcity,
            "property_type": "residential",
            "property_subtype": "apartment",
            "area_sqm": 100.0,
            "number_of_bedrooms": 2,
            "owner_name": f"Owner {unit}",
            "owner_phone": f"+2519111{unit:05d}",
            "coordinates": [
                [38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320],
            ],
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
    offered_rent = round(
        published["band_min"] + band_position * (published["band_max"] - published["band_min"]), 2
    )
    application_response = client.post(
        f"/api/v1/rentals/listings/{published['public_id']}/applications",
        json={"offered_rent": offered_rent}, headers=_headers(renter_token),
    )
    assert application_response.status_code == 201, application_response.text
    application = application_response.json()["data"]
    client.post(
        f"/api/v1/rentals/applications/{application['id']}/decision",
        json={"action": "accept"}, headers=_headers(owner_token),
    )
    contract = client.post(
        "/api/v1/rentals/contracts",
        json={"application_id": application["id"], "start_date": START, "end_date": END},
        headers=_headers(officer_token),
    ).json()["data"]
    client.post(
        f"/api/v1/rentals/contracts/{contract['contract_no']}/deposit",
        json={"deposit_receipt_ref": f"TELE-{unit}", "amount": contract["deposit_amount"]},
        headers=_headers(officer_token),
    )
    return contract["monthly_rent"]


@pytest.fixture
def officer_token(client, db_session):
    return _make_officer(client, db_session)


class TestAggregationAndSuppression:
    def test_district_with_enough_contracts_is_published(self, client, db_session, officer_token):
        from statistics import median

        rents = [
            _active_contract(client, db_session, officer_token, "Bole", unit, position)
            for unit, position in enumerate([0.0, 0.5, 1.0], start=1)
        ]

        rows = RentIndexService(db_session).run_aggregation()
        assert any(r.district == "Bole" and r.sample_size == 3 for r in rows)

        response = client.get("/api/v1/rentals/index?district=Bole")
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["district"] == "Bole"
        assert data[0]["median_rent"] == median(rents)
        assert data[0]["sample_size"] >= MIN_SAMPLE_SIZE
        assert data[0]["source"] == "contracts"

    def test_district_below_threshold_is_suppressed_from_public_api(self, client, db_session, officer_token):
        _active_contract(client, db_session, officer_token, "Yeka", 1)

        RentIndexService(db_session).run_aggregation()

        response = client.get("/api/v1/rentals/index?district=Yeka")
        assert response.status_code == 200
        assert response.json()["data"] == []

        # The row exists internally (officer/audit visibility) even though
        # it is suppressed from the public endpoint.
        stored = db_session.query(RentIndexSnapshot).filter(RentIndexSnapshot.district == "Yeka").first()
        assert stored is not None
        assert stored.sample_size < MIN_SAMPLE_SIZE

    def test_aggregation_is_idempotent_per_period(self, client, db_session, officer_token):
        for unit, position in enumerate([0.0, 0.5, 1.0], start=1):
            _active_contract(client, db_session, officer_token, "Bole", unit, position)

        service = RentIndexService(db_session)
        first_run = service.run_aggregation(period="2026-07")
        second_run = service.run_aggregation(period="2026-07")

        stored = db_session.query(RentIndexSnapshot).filter(RentIndexSnapshot.period == "2026-07").all()
        assert len(first_run) == len(second_run) == len(stored)

    def test_index_response_has_cache_control_header(self, client):
        response = client.get("/api/v1/rentals/index")
        assert response.headers.get("cache-control", "").startswith("public")
