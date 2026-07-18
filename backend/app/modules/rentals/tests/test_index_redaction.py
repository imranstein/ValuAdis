"""
Rent index public serializer — redaction (Phase D hardening sweep).

RentIndexRow is a closed model (extra='forbid') like PublicListing: it can
only ever carry the aggregate fields declared on it, so no per-contract or
owner/renter identity can leak through it by construction.
"""

import pytest
from pydantic import ValidationError

from app.modules.rentals.schemas import RentIndexRow


class TestRentIndexRedaction:
    def test_valid_row_serializes_aggregate_fields_only(self):
        row = RentIndexRow(
            district="Bole", property_subtype="apartment", bedrooms=2,
            median_rent=21000.0, sample_size=3, source="contracts", period="2026-07",
        )
        payload = row.model_dump()
        assert set(payload.keys()) == {
            "district", "property_subtype", "bedrooms", "median_rent",
            "sample_size", "source", "period",
        }

    def test_model_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            RentIndexRow(
                district="Bole", property_subtype="apartment", bedrooms=2,
                median_rent=21000.0, sample_size=3, source="contracts", period="2026-07",
                owner_name="leak",
            )
