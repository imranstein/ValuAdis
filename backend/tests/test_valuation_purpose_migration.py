"""
Valuation Purpose Column Tests

Verifies the valuations.purpose migration: NOT NULL with a server default
of 'sale' for rows that don't set it, 'rent' round-trips correctly, and
the CHECK constraint rejects any other value.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.data.models.property import Property
from app.data.models.user import User
from app.data.models.valuation import PropertyType, Valuation, ValuationStatus


def _make_user(db) -> User:
    user = User(
        email="purpose-test@example.com",
        full_name="Purpose Tester",
        password_hash="x",
        phone="+251911000000",
        municipality="Addis Ababa",
        license_number="VAL-TEST-001",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _base_valuation_kwargs(user_id: int) -> dict:
    return {
        "property_id": 1,
        "user_id": user_id,
        "property_type": PropertyType.RESIDENTIAL,
        "municipality": "Addis Ababa",
        "area_sqm": 100.0,
        "market_value": 100000.00,
        "taxable_value": 25000.00,
        "status": ValuationStatus.DRAFT,
    }


class TestValuationPurposeColumn:
    def test_omitted_purpose_defaults_to_sale_after_persist(self, db_session):
        user = _make_user(db_session)
        valuation = Valuation(**_base_valuation_kwargs(user.id))
        db_session.add(valuation)
        db_session.commit()
        db_session.refresh(valuation)

        assert valuation.purpose == "sale"

    def test_explicit_rent_purpose_round_trips(self, db_session):
        user = _make_user(db_session)
        valuation = Valuation(**_base_valuation_kwargs(user.id), purpose="rent")
        db_session.add(valuation)
        db_session.commit()
        db_session.refresh(valuation)

        assert valuation.purpose == "rent"

    def test_invalid_purpose_violates_check_constraint(self, db_session):
        user = _make_user(db_session)
        valuation = Valuation(**_base_valuation_kwargs(user.id), purpose="lease")
        db_session.add(valuation)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_to_dict_includes_purpose(self, db_session):
        user = _make_user(db_session)
        valuation = Valuation(**_base_valuation_kwargs(user.id), purpose="rent")
        db_session.add(valuation)
        db_session.commit()
        db_session.refresh(valuation)

        assert valuation.to_dict()["purpose"] == "rent"

    def test_existing_valuations_untouched_by_purpose_default(self, db_session):
        """Regression: adding purpose must not change sale-valuation behavior."""
        user = _make_user(db_session)
        valuation = Valuation(**_base_valuation_kwargs(user.id))
        db_session.add(valuation)
        db_session.commit()
        db_session.refresh(valuation)

        assert valuation.market_value == 100000.00
        assert valuation.status == ValuationStatus.DRAFT
        assert valuation.purpose == "sale"
