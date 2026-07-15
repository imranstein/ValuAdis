"""
Property Endpoint Behavior Tests

Locks /api/v1/properties/* behavior not covered by test_properties.py before
the property stack moves into app/modules/property (v2 consolidation):
CSV export, spatial summary/overlap queries, auth requirements, and 404s.
"""

from fastapi.testclient import TestClient

SQUARE_A = [
    [38.7578, 9.0320],
    [38.7580, 9.0320],
    [38.7580, 9.0318],
    [38.7578, 9.0318],
    [38.7578, 9.0320],
]

# Shifted east so it does not intersect SQUARE_A
SQUARE_B = [
    [38.7590, 9.0320],
    [38.7592, 9.0320],
    [38.7592, 9.0318],
    [38.7590, 9.0318],
    [38.7590, 9.0320],
]

# Overlaps the eastern half of SQUARE_A
SQUARE_A_SHIFTED = [
    [38.7579, 9.0320],
    [38.7581, 9.0320],
    [38.7581, 9.0318],
    [38.7579, 9.0318],
    [38.7579, 9.0320],
]


def _auth_headers(client: TestClient, test_user_data) -> dict:
    response = client.post("/api/v1/auth/register", json=test_user_data)
    body = response.json()
    token = body.get("access_token") or body["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestPropertyExport:
    def test_export_requires_authentication(self, client: TestClient):
        response = client.get("/api/v1/properties/export")
        assert response.status_code == 401

    def test_export_rejects_non_csv_format(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)
        response = client.get("/api/v1/properties/export?format=json", headers=headers)
        assert response.status_code == 400

    def test_export_returns_csv_attachment(self, client: TestClient, test_user_data, test_property_data):
        headers = _auth_headers(client, test_user_data)
        client.post("/api/v1/properties", json=test_property_data, headers=headers)

        response = client.get("/api/v1/properties/export", headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert (
            response.headers["content-disposition"]
            == "attachment; filename=properties_export.csv"
        )

    def test_export_contains_header_row_and_created_property(self, client: TestClient, test_user_data, test_property_data):
        headers = _auth_headers(client, test_user_data)
        client.post("/api/v1/properties", json=test_property_data, headers=headers)

        response = client.get("/api/v1/properties/export", headers=headers)

        lines = response.text.strip().splitlines()
        assert lines[0].strip() == "id,address,municipality,property_type,area_sqm,market_value,status,created_at"
        assert len(lines) == 2
        assert test_property_data["municipality"] in lines[1]


class TestSpatialSummary:
    def test_spatial_summary_requires_authentication(self, client: TestClient):
        response = client.post(
            "/api/v1/properties/spatial/summary", json={"coordinates": SQUARE_A}
        )
        assert response.status_code == 401

    def test_spatial_summary_returns_metrics(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/spatial/summary",
            json={"coordinates": SQUARE_A},
            headers=headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["area_sqm"] > 0
        assert data["perimeter_m"] > 0
        assert data["in_ethiopia"] is True
        assert data["vertex_count"] == len(SQUARE_A)

    def test_spatial_summary_rejects_malformed_coordinates(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/spatial/summary",
            json={"coordinates": [[38.7578], [38.7580, 9.0320], [38.7580, 9.0318]]},
            headers=headers,
        )

        assert response.status_code == 400


class TestSpatialOverlap:
    def test_spatial_overlap_requires_authentication(self, client: TestClient):
        response = client.post(
            "/api/v1/properties/spatial/overlap",
            json={"coordinates_a": SQUARE_A, "coordinates_b": SQUARE_B},
        )
        assert response.status_code == 401

    def test_overlapping_polygons_report_overlap(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/spatial/overlap",
            json={"coordinates_a": SQUARE_A, "coordinates_b": SQUARE_A_SHIFTED},
            headers=headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["overlaps"] is True
        assert body["overlap_area_sqm"] > 0
        assert body["overlap_percentage"] > 0

    def test_disjoint_polygons_report_no_overlap(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/spatial/overlap",
            json={"coordinates_a": SQUARE_A, "coordinates_b": SQUARE_B},
            headers=headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["overlaps"] is False
        assert body["overlap_area_sqm"] == 0
        assert body["overlap_percentage"] == 0


class TestPropertyNotFound:
    def test_update_unknown_property_returns_404(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)
        response = client.put(
            "/api/v1/properties/999999", json={"address": "Nowhere Street 1"}, headers=headers
        )
        assert response.status_code == 404

    def test_delete_unknown_property_returns_404(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)
        response = client.delete("/api/v1/properties/999999", headers=headers)
        assert response.status_code == 404


class TestBulkImportValidation:
    def test_bulk_import_rejects_non_csv_file(self, client: TestClient, test_user_data):
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/bulk-import",
            headers=headers,
            files={"file": ("properties.txt", "not,a,csv\n", "text/plain")},
        )

        assert response.status_code == 400

    def test_bulk_import_rejects_oversized_file(self, client: TestClient, test_user_data, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "MAX_FILE_SIZE", 16)
        headers = _auth_headers(client, test_user_data)

        response = client.post(
            "/api/v1/properties/bulk-import",
            headers=headers,
            files={"file": ("properties.csv", "address,municipality\n" * 10, "text/csv")},
        )

        assert response.status_code == 413
