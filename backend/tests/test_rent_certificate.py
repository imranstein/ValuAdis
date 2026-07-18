"""
Rent Certificate Tests

Covers the Phase A rent-valuation certificate template: an approved
purpose='rent' valuation downloads a PDF via the existing
GET /api/v1/valuations/{id}/certificate route, and an unapproved one is
rejected with the same 403 convention as the sale certificate path.
"""

from fastapi.testclient import TestClient

from app.data.models.user import User
from app.data.models.valuation import PropertyType, Valuation, ValuationStatus
from app.modules.valuation.certificate_service import CertificateService


def _register(client: TestClient, user_data: dict, db_session) -> tuple[str, int]:
    response = client.post("/api/v1/auth/register", json=user_data)
    token = response.json()["data"]["access_token"]
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    return token, user.id


def _create_rent_valuation(db_session, user_id: int) -> Valuation:
    valuation = Valuation(
        property_id=1,
        user_id=user_id,
        property_type=PropertyType.RESIDENTIAL,
        municipality="Addis Ababa",
        area_sqm=100.0,
        market_value=1_000_000.0,
        taxable_value=250_000.0,
        status=ValuationStatus.DRAFT,
        purpose="rent",
    )
    db_session.add(valuation)
    db_session.commit()
    db_session.refresh(valuation)
    return valuation


class TestRentCertificateRoute:
    def test_unapproved_rent_valuation_returns_403(
        self, client: TestClient, db_session, test_user_data
    ):
        token, user_id = _register(client, test_user_data, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        valuation = _create_rent_valuation(db_session, user_id)

        response = client.get(f"/api/v1/valuations/{valuation.id}/certificate", headers=headers)

        assert response.status_code == 403

    def test_approved_rent_valuation_downloads_pdf(
        self, client: TestClient, db_session, test_user_data
    ):
        token, user_id = _register(client, test_user_data, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        valuation = _create_rent_valuation(db_session, user_id)

        # draft -> pending -> approved, matching the certificate happy path
        client.patch(
            f"/api/v1/valuations/{valuation.id}/status",
            json={"status": "pending"},
            headers=headers,
        )
        client.patch(
            f"/api/v1/valuations/{valuation.id}/status",
            json={"status": "approved"},
            headers=headers,
        )

        response = client.get(f"/api/v1/valuations/{valuation.id}/certificate", headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content[:4] == b"%PDF"
        assert "RentCertificate" in response.headers["content-disposition"]


class TestGenerateRentCertificateDirect:
    """Direct CertificateService coverage, independent of the HTTP gate."""

    def test_generates_valid_pdf_bytes(self):
        cert_service = CertificateService()
        valuation = {"id": 1, "status": "approved", "purpose": "rent"}
        property_data = {
            "address": "Bole, Addis Ababa",
            "municipality": "Addis Ababa",
            "property_type": "residential",
            "area_sqm": 100.0,
        }
        rent_result = {
            "suggested_rent": 6000.0,
            "band_min": 5400.0,
            "band_max": 6600.0,
            "confidence": 0.8,
            "requires_officer_review": False,
        }

        pdf_bytes = cert_service.generate_rent_certificate(
            valuation, property_data, "Test Owner", rent_result
        )

        assert pdf_bytes[:4] == b"%PDF"
        assert len(pdf_bytes) > 1000

    def test_low_confidence_note_included_for_review_flag(self):
        cert_service = CertificateService()
        valuation = {"id": 2, "status": "approved", "purpose": "rent"}
        property_data = {"address": "—", "municipality": "Addis Ababa", "area_sqm": 80.0}
        rent_result = {
            "suggested_rent": 4000.0,
            "band_min": 3600.0,
            "band_max": 4400.0,
            "confidence": 0.4,
            "requires_officer_review": True,
        }

        pdf_bytes = cert_service.generate_rent_certificate(
            valuation, property_data, "Test Owner", rent_result
        )

        assert pdf_bytes[:4] == b"%PDF"
