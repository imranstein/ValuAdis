"""
Valuation model calibration (S10).

The valuation engine is rule-based, so "retraining" here means recomputing
trust/calibration metrics from the full valuation_feedback history (reviewer
decisions comparing the AI estimate to the final approved value) — a batch
recalibration versus the incremental per-decision drift the feedback service
keeps. Run on a schedule via `python -m app.services.ml_calibration`.

Outputs (and persists into the trust store the /valuation-feedback/metrics
endpoint reads): overall accuracy, signed bias, approved-unchanged rate, and a
per-municipality error breakdown, so systematic over/under-estimation surfaces.
"""

import logging
from statistics import mean, median
from typing import Optional

from sqlalchemy.orm import Session

from app.data.models.valuation_feedback import ValuationFeedback

logger = logging.getLogger("ValuAdis_MLCalibration")


def _error_pct(row: ValuationFeedback) -> Optional[float]:
    """Signed error % of the AI estimate vs the final approved value."""
    if row.delta_percentage is not None:
        return float(row.delta_percentage)
    try:
        ai = float(row.ai_estimate)
        final = float(row.final_approved_value)
    except (TypeError, ValueError):
        return None
    if final == 0:
        return None
    return (ai - final) / final * 100.0


def recompute_calibration(db: Session) -> dict:
    """Recompute trust/calibration metrics from all feedback rows."""
    rows = db.query(ValuationFeedback).all()
    total = len(rows)
    if total == 0:
        return {
            "total_reviews": 0,
            "trust_score": 75.0,
            "avg_error_pct": 0.0,
            "median_error_pct": 0.0,
            "bias_pct": 0.0,
            "approved_unchanged": 0,
            "approved_unchanged_rate": 0.0,
            "by_municipality": {},
        }

    signed = [e for e in (_error_pct(r) for r in rows) if e is not None]
    abs_errors = [abs(e) for e in signed]
    approved_unchanged = sum(1 for r in rows if r.approved_without_change)

    avg_err = mean(abs_errors) if abs_errors else 0.0
    trust_score = round(max(0.0, min(100.0, 100.0 - avg_err)), 1)

    # Per-municipality bias, pulled from the stored property context.
    by_muni: dict = {}
    for r in rows:
        ctx = r.property_context or {}
        muni = ctx.get("municipality") or "Unknown"
        e = _error_pct(r)
        if e is None:
            continue
        by_muni.setdefault(muni, []).append(e)
    by_municipality = {
        muni: {
            "count": len(errs),
            "bias_pct": round(mean(errs), 2),
            "avg_error_pct": round(mean(abs(e) for e in errs), 2),
        }
        for muni, errs in by_muni.items()
    }

    report = {
        "total_reviews": total,
        "trust_score": trust_score,
        "avg_error_pct": round(avg_err, 2),
        "median_error_pct": round(median(abs_errors), 2) if abs_errors else 0.0,
        "bias_pct": round(mean(signed), 2) if signed else 0.0,
        "approved_unchanged": approved_unchanged,
        "modified_reviews": total - approved_unchanged,
        "approved_unchanged_rate": round(approved_unchanged / total * 100, 1),
        "by_municipality": by_municipality,
    }
    logger.info(
        "calibration: %s reviews, trust %.1f, avg error %.2f%%, bias %.2f%%",
        total, report["trust_score"], report["avg_error_pct"], report["bias_pct"],
    )
    return report


def recompute_and_persist(db: Session) -> dict:
    """Recompute and write the headline metrics into the trust store."""
    report = recompute_calibration(db)
    try:
        from app.modules.valuation import feedback_service

        data = feedback_service._load_learning()
        data.update({
            "trust_score": report["trust_score"],
            "total_reviews": report["total_reviews"],
            "approved_unchanged": report["approved_unchanged"],
            "modified_reviews": report["modified_reviews"],
            "avg_error_pct": report["avg_error_pct"],
        })
        feedback_service._save_learning(data)
    except Exception as error:  # persistence is best-effort; the report still returns
        logger.warning("could not persist calibration to trust store: %s", error)
    return report


def main() -> None:  # pragma: no cover - thin runner
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        recompute_and_persist(db)
    finally:
        db.close()


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    main()
