"""
Valuation Feedback Endpoints

Handles reviewer approval/modification decisions for AI trust scoring.
POST /valuation-feedback     - Submit reviewer decision
GET  /valuation-feedback/metrics  - Get current trust metrics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_id
from . import feedback_service as svc

router = APIRouter()


class FeedbackCreate(BaseModel):
    property_id: int
    valuation_id: Optional[int] = None
    ai_estimate: float
    final_value: float
    approved_without_change: bool
    comments: Optional[str] = None
    property_context: Optional[dict] = Field(default_factory=dict)


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Submit reviewer feedback on an AI valuation."""
    if payload.final_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="final_value must be greater than 0",
        )

    feedback = svc.record_feedback(
        db=db,
        property_id=payload.property_id,
        reviewer_id=current_user_id,
        ai_estimate=payload.ai_estimate,
        final_value=payload.final_value,
        approved_without_change=payload.approved_without_change,
        comments=payload.comments,
        property_context=payload.property_context or {},
        valuation_id=payload.valuation_id,
    )

    metrics = svc.get_trust_metrics()
    return {
        "success": True,
        "feedback_id": feedback.id,
        "trust_score": metrics["trust_score"],
        "delta_percentage": feedback.delta_percentage,
        "approved": feedback.approved_without_change,
    }


@router.get("/metrics")
def get_metrics(_: int = Depends(get_current_user_id)):
    """Get current AI trust metrics."""
    return svc.get_trust_metrics()
