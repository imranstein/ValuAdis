"""
Valuation Endpoint Gap Tests

Freezes behavior that the module extraction (P2-valuations) must preserve and
that is not already covered by test_valuations_api.py / test_valuation_status.py /
test_integration_contracts.py: API-level status transitions (including invalid
transition rejection), certificate issuance rules, and CSV export headers.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient, test_user_data) -> dict:
    response = client.post("/api/v1/auth/register", json=test_user_data)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valuation_id(client: TestClient, auth_headers, test_property_data) -> int:
    property_resp = client.post(
        "/api/v1/properties", json=test_property_data, headers=auth_headers
    )
    property_id = property_resp.json()["data"]["id"]
    valuation_payload = {
        "property_id": property_id,
        "property_type": test_property_data["property_type"],
        "municipality": test_property_data["municipality"],
        "area_sqm": 120.0,
        "coordinates": test_property_data["coordinates"],
    }
    create_resp = client.post(
        "/api/v1/valuations", json=valuation_payload, headers=auth_headers
    )
    return create_resp.json()["data"]["id"]


def _transition(client: TestClient, headers: dict, valuation_id: int, new_status: str):
    return client.patch(
        f"/api/v1/valuations/{valuation_id}/status",
        json={"status": new_status},
        headers=headers,
    )


class TestStatusTransitionEndpoint:
    def test_draft_to_pending_returns_200(self, client, auth_headers, valuation_id):
        response = _transition(client, auth_headers, valuation_id, "pending")
        assert response.status_code == 200

    def test_pending_to_approved_returns_200(self, client, auth_headers, valuation_id):
        _transition(client, auth_headers, valuation_id, "pending")
        response = _transition(client, auth_headers, valuation_id, "approved")
        assert response.status_code == 200

    def test_transition_response_reports_new_status(
        self, client, auth_headers, valuation_id
    ):
        response = _transition(client, auth_headers, valuation_id, "pending")
        assert "pending" in response.json()["message"]

    def test_draft_to_approved_is_rejected_with_400(
        self, client, auth_headers, valuation_id
    ):
        response = _transition(client, auth_headers, valuation_id, "approved")
        assert response.status_code == 400

    def test_transition_requires_authentication(self, client, auth_headers, valuation_id):
        response = client.patch(
            f"/api/v1/valuations/{valuation_id}/status", json={"status": "pending"}
        )
        assert response.status_code == 401


class TestCertificateEndpoint:
    def _approve(self, client, headers, valuation_id):
        _transition(client, headers, valuation_id, "pending")
        _transition(client, headers, valuation_id, "approved")

    def test_certificate_returns_200_for_approved_valuation(
        self, client, auth_headers, valuation_id
    ):
        self._approve(client, auth_headers, valuation_id)
        response = client.get(
            f"/api/v1/valuations/{valuation_id}/certificate", headers=auth_headers
        )
        assert response.status_code == 200

    def test_certificate_is_pdf_attachment(self, client, auth_headers, valuation_id):
        self._approve(client, auth_headers, valuation_id)
        response = client.get(
            f"/api/v1/valuations/{valuation_id}/certificate", headers=auth_headers
        )
        assert response.headers["content-type"] == "application/pdf"

    def test_certificate_payload_is_pdf_bytes(self, client, auth_headers, valuation_id):
        self._approve(client, auth_headers, valuation_id)
        response = client.get(
            f"/api/v1/valuations/{valuation_id}/certificate", headers=auth_headers
        )
        assert response.content.startswith(b"%PDF")

    def test_certificate_rejected_for_draft_valuation(
        self, client, auth_headers, valuation_id
    ):
        response = client.get(
            f"/api/v1/valuations/{valuation_id}/certificate", headers=auth_headers
        )
        assert response.status_code == 403

    def test_certificate_missing_valuation_returns_404(self, client, auth_headers):
        response = client.get(
            "/api/v1/valuations/999999/certificate", headers=auth_headers
        )
        assert response.status_code == 404


class TestCsvExportEndpoint:
    def test_export_returns_200(self, client, auth_headers, valuation_id):
        response = client.get("/api/v1/valuations/export", headers=auth_headers)
        assert response.status_code == 200

    def test_export_media_type_is_csv(self, client, auth_headers, valuation_id):
        response = client.get("/api/v1/valuations/export", headers=auth_headers)
        assert response.headers["content-type"].startswith("text/csv")

    def test_export_has_attachment_disposition(self, client, auth_headers, valuation_id):
        response = client.get("/api/v1/valuations/export", headers=auth_headers)
        assert (
            response.headers["content-disposition"]
            == "attachment; filename=valuations_export.csv"
        )

    def test_export_header_row_matches_contract(self, client, auth_headers, valuation_id):
        response = client.get("/api/v1/valuations/export", headers=auth_headers)
        header_row = response.text.splitlines()[0]
        assert header_row == (
            "id,property_id,property_type,municipality,area_sqm,"
            "market_value,taxable_value,status,valuation_date,created_at"
        )

    def test_export_rejects_non_csv_format(self, client, auth_headers):
        response = client.get(
            "/api/v1/valuations/export?format=xlsx", headers=auth_headers
        )
        assert response.status_code == 400

    def test_export_requires_authentication(self, client):
        response = client.get("/api/v1/valuations/export")
        assert response.status_code == 401
