"""
ValuationFeedbackService

Manages AI trust scoring and the valuation learning feedback loop.
Each reviewer decision updates the global trust score and appends to valuation_learning.json
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.data.models.valuation_feedback import ValuationFeedback

# Path to learning file - stored in backend/data/
LEARNING_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "valuation_learning.json"
)

APPROVAL_BOOST = 2.0        # +2.0 pts on unchanged approval (out of 100)
MODIFICATION_PENALTY = 0.05  # -(delta_pct * 0.05) penalty


def _load_learning() -> dict:
    """Load the learning JSON, return defaults if file not found."""
    try:
        with open(LEARNING_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "version": "1.0",
            "trust_score": 75.0,
            "total_reviews": 0,
            "approved_unchanged": 0,
            "modified_reviews": 0,
            "avg_error_pct": 0.0,
            "last_30d_accuracy": 0.0,
            "feedback_history": [],
            "patterns": {
                "overestimated_when": [],
                "underestimated_when": [],
            },
        }


def _save_learning(data: dict) -> None:
    """Persist the learning JSON file."""
    os.makedirs(os.path.dirname(LEARNING_FILE), exist_ok=True)
    with open(LEARNING_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_trust_metrics() -> dict:
    """Return current trust metrics (public API)."""
    data = _load_learning()
    return {
        "trust_score": data.get("trust_score", 75.0),
        "total_reviews": data.get("total_reviews", 0),
        "approved_unchanged": data.get("approved_unchanged", 0),
        "modified_reviews": data.get("modified_reviews", 0),
        "avg_error_pct": data.get("avg_error_pct", 0.0),
        "last_30d_accuracy": data.get("last_30d_accuracy", 0.0),
    }


def record_feedback(
    db: Session,
    property_id: int,
    reviewer_id: int,
    ai_estimate: float,
    final_value: float,
    approved_without_change: bool,
    comments: Optional[str],
    property_context: dict,
    valuation_id: Optional[int] = None,
) -> ValuationFeedback:
    """
    Record a reviewer decision, update trust score, and persist to learning JSON.
    """
    # Calculate deviation percentage
    delta_pct = (
        abs((final_value - ai_estimate) / ai_estimate * 100)
        if ai_estimate and ai_estimate != 0
        else 0.0
    )

    # Compute trust score impact
    if approved_without_change:
        trust_impact = APPROVAL_BOOST
    else:
        trust_impact = -(delta_pct * MODIFICATION_PENALTY)

    # Persist feedback record to DB
    feedback = ValuationFeedback(
        property_id=property_id,
        valuation_id=valuation_id,
        reviewer_id=reviewer_id,
        ai_estimate=ai_estimate,
        final_approved_value=final_value,
        delta_percentage=round(delta_pct, 4),
        approved_without_change=approved_without_change,
        reviewer_comments=comments,
        trust_impact=round(trust_impact, 4),
        property_context=property_context,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Update learning JSON
    learning = _load_learning()
    old_score = learning.get("trust_score", 75.0)
    new_score = max(0.0, min(100.0, old_score + trust_impact))

    learning["trust_score"] = round(new_score, 2)
    learning["total_reviews"] = learning.get("total_reviews", 0) + 1

    if approved_without_change:
        learning["approved_unchanged"] = learning.get("approved_unchanged", 0) + 1
    else:
        learning["modified_reviews"] = learning.get("modified_reviews", 0) + 1

    # Running average error percentage
    n = learning["total_reviews"]
    prev_avg = learning.get("avg_error_pct", 0.0)
    learning["avg_error_pct"] = round((prev_avg * (n - 1) + delta_pct) / n, 4)

    # Append to history
    learning.setdefault("feedback_history", []).append({
        "feedback_id": feedback.id,
        "property_id": property_id,
        "ai_estimate": ai_estimate,
        "final_value": final_value,
        "delta_pct": round(delta_pct, 2),
        "approved": approved_without_change,
        "comments": comments,
        "trust_impact": round(trust_impact, 3),
        "score_before": round(old_score, 2),
        "score_after": round(new_score, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context_snapshot": {
            k: property_context.get(k)
            for k in ["property_type", "municipality", "condition", "area_sqm"]
            if k in property_context
        },
    })

    _save_learning(learning)
    return feedback
