"""
VA-119: User Feedback API

Submit and list user feedback (ratings, comments, feature requests).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.data.models.user_feedback import UserFeedback

router = APIRouter(tags=["Feedback"])


class FeedbackCreate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    page: Optional[str] = Field(None, max_length=200)
    context: Optional[str] = Field(None, max_length=100)


class FeedbackResponse(BaseModel):
    id: int
    rating: Optional[int]
    comment: Optional[str]
    page: Optional[str]
    context: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Submit user feedback (rating, comment, page, context)."""
    fb = UserFeedback(
        user_id=user_id,
        rating=data.rating,
        comment=data.comment,
        page=data.page,
        context=data.context,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"success": True, "id": fb.id, "message": "Thank you for your feedback!"}


@router.get("", response_model=List[FeedbackResponse])
async def list_my_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """List current user's feedback submissions."""
    items = (
        db.query(UserFeedback)
        .filter(UserFeedback.user_id == user_id)
        .order_by(UserFeedback.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        FeedbackResponse(
            id=f.id,
            rating=f.rating,
            comment=f.comment,
            page=f.page,
            context=f.context,
            created_at=f.created_at.isoformat() if f.created_at else "",
        )
        for f in items
    ]
