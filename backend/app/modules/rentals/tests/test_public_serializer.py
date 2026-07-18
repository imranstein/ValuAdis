"""
Public serializer redaction tests (pure unit, no DB).

The public listing surface must never expose owner identity. PublicListing
is a closed Pydantic model, so redaction is enforced by construction; these
tests prove the payload key set contains no PII fields and that the model
rejects extras.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.modules.rentals.schemas import PublicListing, PublicListingProperty
from app.modules.rentals.services import RentalListingService

PII_KEYS = {
    "owner_name",
    "owner_phone",
    "owner_email",
    "owner_id_number",
    "owner_id_type",
    "owner_user_id",
    "user_id",
    "fayda_id_number",
    "full_name",
    "email",
    "phone",
    "id",
    "property_id",
    "valuation_id",
}


def _fake_listing():
    prop = SimpleNamespace(
        id=7,
        user_id=42,
        address="Bole, Addis Ababa",
        municipality="Addis Ababa",
        subcity="Bole",
        property_type="residential",
        property_subtype="apartment",
        area_sqm=120.0,
        building_area_sqm=95.0,
        number_of_bedrooms=2,
        number_of_bathrooms=1,
        number_of_floors=1,
        year_built=2018,
        condition="good",
        latitude=9.01,
        longitude=38.76,
        owner_name="Kebede Alemu",
        owner_phone="+251911000000",
        owner_email="kebede@example.com",
        owner_id_number="FAYDA-123456789012",
    )
    return SimpleNamespace(
        id=3,
        public_id="AA-LST-2026-000123",
        property_id=7,
        valuation_id=11,
        owner_user_id=42,
        suggested_rent=28000.0,
        band_min=25200.0,
        band_max=30800.0,
        published_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
        property=prop,
    )


def _all_keys(payload: dict) -> set:
    keys = set()
    for key, value in payload.items():
        keys.add(key)
        if isinstance(value, dict):
            keys |= _all_keys(value)
    return keys


class TestPublicListingRedaction:
    def test_public_payload_contains_no_pii_keys(self):
        payload = RentalListingService.to_public_listing(_fake_listing()).model_dump()
        assert _all_keys(payload) & PII_KEYS == set()

    def test_public_payload_contains_no_pii_values(self):
        payload = RentalListingService.to_public_listing(_fake_listing()).model_dump()
        flat = str(payload)
        assert "Kebede" not in flat
        assert "+251911000000" not in flat
        assert "kebede@example.com" not in flat
        assert "FAYDA-" not in flat

    def test_public_payload_keeps_band_and_property_facts(self):
        listing = RentalListingService.to_public_listing(_fake_listing())
        assert listing.public_id == "AA-LST-2026-000123"
        assert listing.band_min < listing.suggested_rent < listing.band_max
        assert listing.property.subcity == "Bole"

    def test_public_model_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PublicListing(
                public_id="AA-LST-2026-000001",
                suggested_rent=1.0,
                band_min=0.9,
                band_max=1.1,
                owner_name="leak",
                property=PublicListingProperty(
                    address="x",
                    municipality="Addis Ababa",
                    property_type="residential",
                    area_sqm=10.0,
                ),
            )
