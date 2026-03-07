"""
UserFeedback Model (VA-119)

General user feedback: ratings, comments, feature requests.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer)  # 1-5 or null
    comment = Column(Text)
    page = Column(String(200))  # e.g. /dashboard, /properties
    context = Column(String(100))  # e.g. bug_report, feature_request, general
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="feedback_submissions")
