"""
License Validation API Tests

Tests for the Ethiopian business license validation API endpoint
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestLicenseValidationAPI:
    """Test cases for POST /api/v1/validate/license endpoint"""

    def test_valid_license_returns_success(self):
        """Test that valid Ethiopian license format returns valid=true"""
        valid_licenses = [
            "AA-1234567890",
            "AD-1234567890",
            "BA-1234567890",
            "DD-1234567890",
            "HA-1234567890",
            "ME-1234567890",
            "OR-1234567890",
            "AM-1234567890",
            "SN-1234567890"
        ]

        for license in valid_licenses:
            response = client.post("/api/v1/validate/license", json={"license": license})
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert "error" not in data or data["error"] is None
            assert "prefix" in data
            assert "region" in data

    def test_invalid_license_returns_error(self):
        """Test that invalid license formats return valid=false with error"""
        invalid_licenses = [
            ("", "License number is required"),
            ("AA", "License number must be at least 9 characters"),
            ("AA1234567890", "Invalid Ethiopian license format"),
            ("aa-1234567890", "Invalid Ethiopian license format"),
            ("A-1234567890", "Invalid Ethiopian license format"),
            ("AAAAA-1234567890", "Invalid Ethiopian license format"),
            ("AA-12345", "Invalid Ethiopian license format"),
            ("AA-1234567890123", "Invalid Ethiopian license format"),
            ("INVALID", "License number must be at least 9 characters"),
            ("1234567890", "License number must be at least 9 characters")
        ]

        for license, expected_error in invalid_licenses:
            response = client.post("/api/v1/validate/license", json={"license": license})
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "error" in data
            assert data["error"] is not None

    def test_license_region_lookup(self):
        """Test that recognized prefixes return correct region information"""
        test_cases = [
            ("AA-1234567890", "Addis Ababa City Administration"),
            ("AD-1234567890", "Adama City Administration"),
            ("BA-1234567890", "Bahir Dar City Administration"),
            ("ME-1234567890", "Mekelle City Administration"),
            ("ZZ-1234567890", None)  # Unknown prefix
        ]

        for license, expected_region in test_cases:
            response = client.post("/api/v1/validate/license", json={"license": license})
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True

            if expected_region:
                assert data["region"] == expected_region
            else:
                assert data["region"] is None or data["region"] == "Unknown Region"

    def test_license_prefix_extraction(self):
        """Test that prefix is correctly extracted from license"""
        test_cases = [
            ("AA-1234567890", "AA"),
            ("ABC-1234567890", "ABC"),
            ("ABCD-1234567890", "ABCD")
        ]

        for license, expected_prefix in test_cases:
            response = client.post("/api/v1/validate/license", json={"license": license})
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["prefix"] == expected_prefix

    def test_license_prefixes_endpoint(self):
        """Test GET /api/v1/validate/license/prefixes returns prefix mappings"""
        response = client.get("/api/v1/validate/license/prefixes")
        assert response.status_code == 200
        data = response.json()

        assert "prefixes" in data
        assert "count" in data
        assert data["count"] > 0
        assert "AA" in data["prefixes"]
        assert data["prefixes"]["AA"] == "Addis Ababa City Administration"

    def test_whitespace_handling(self):
        """Test that whitespace is trimmed from license input"""
        response = client.post("/api/v1/validate/license", json={"license": "  AA-1234567890  "})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_uppercase_conversion(self):
        """Test that lowercase letters are handled correctly (should fail)"""
        response = client.post("/api/v1/validate/license", json={"license": "aa-1234567890"})
        assert response.status_code == 200
        data = response.json()
        # Lowercase should be rejected
        assert data["valid"] is False

    def test_edge_case_licenses(self):
        """Test edge case license numbers"""
        edge_cases = [
            ("AA-0000000000", True, "All zeros should be valid format"),
            ("AA-9999999999", True, "All nines should be valid format"),
            ("AA-000001", False, "Too few digits"),
            ("AA-0000000000001", False, "Too many digits"),
        ]

        for license, should_be_valid, description in edge_cases:
            response = client.post("/api/v1/validate/license", json={"license": license})
            assert response.status_code == 200, f"Failed for {description}"
            data = response.json()
            assert data["valid"] == should_be_valid, f"{description}: expected {should_be_valid}, got {data['valid']}"

    def test_malformed_json_request(self):
        """Test handling of malformed JSON request"""
        response = client.post(
            "/api/v1/validate/license",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error

    def test_missing_license_field(self):
        """Test request without license field"""
        response = client.post("/api/v1/validate/license", json={})
        assert response.status_code == 422  # Validation error

    def test_null_license_value(self):
        """Test request with null license value"""
        response = client.post("/api/v1/validate/license", json={"license": None})
        assert response.status_code == 422  # Validation error
