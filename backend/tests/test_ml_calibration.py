"""ML calibration job tests: recompute trust metrics from feedback rows."""

from decimal import Decimal

from app.data.models.valuation_feedback import ValuationFeedback
from app.services.ml_calibration import recompute_calibration


def _add_feedback(db, ai, final, municipality="Addis Ababa", unchanged=False):
    db.add(ValuationFeedback(
        property_id=1, valuation_id=1, reviewer_id=1,
        ai_estimate=Decimal(str(ai)), final_approved_value=Decimal(str(final)),
        delta_percentage=(ai - final) / final * 100,
        approved_without_change=unchanged,
        property_context={"municipality": municipality},
    ))


def test_empty_feedback_returns_neutral_defaults(db_session):
    report = recompute_calibration(db_session)
    assert report["total_reviews"] == 0
    assert report["trust_score"] == 75.0
    assert report["by_municipality"] == {}


def test_perfect_predictions_give_full_trust(db_session):
    _add_feedback(db_session, 1_000_000, 1_000_000, unchanged=True)
    _add_feedback(db_session, 2_000_000, 2_000_000, unchanged=True)
    db_session.commit()

    report = recompute_calibration(db_session)

    assert report["total_reviews"] == 2
    assert report["avg_error_pct"] == 0.0
    assert report["trust_score"] == 100.0
    assert report["approved_unchanged_rate"] == 100.0


def test_errors_lower_trust_and_surface_bias(db_session):
    # AI overestimates by 10% and 20%.
    _add_feedback(db_session, 1_100_000, 1_000_000)
    _add_feedback(db_session, 1_200_000, 1_000_000)
    db_session.commit()

    report = recompute_calibration(db_session)

    assert report["total_reviews"] == 2
    assert report["avg_error_pct"] == 15.0
    assert report["trust_score"] == 85.0
    # Positive bias = systematic overestimation.
    assert report["bias_pct"] == 15.0


def test_per_municipality_breakdown(db_session):
    _add_feedback(db_session, 1_100_000, 1_000_000, municipality="Bahir Dar")
    _add_feedback(db_session, 900_000, 1_000_000, municipality="Mekelle")
    db_session.commit()

    report = recompute_calibration(db_session)

    assert set(report["by_municipality"]) == {"Bahir Dar", "Mekelle"}
    assert report["by_municipality"]["Bahir Dar"]["bias_pct"] == 10.0
    assert report["by_municipality"]["Mekelle"]["bias_pct"] == -10.0
