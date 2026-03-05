"""
ValuationFeedback Model

Stores reviewer decisions for AI trust scoring feedback loop.
Each approval/modification updates the global trust score in valuation_learning.json
"""

from sqlalchemy import Column, Integer, Float, Numeric, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ValuationFeedback(Base):
    __tablename__ = "valuation_feedback"

    id = Column(Integer, primary_key=True)  # PK has implicit index; no need for index=True
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    valuation_id = Column(Integer, ForeignKey("valuations.id", ondelete="SET NULL"), nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Use Numeric for monetary precision — Float risks rounding drift
    ai_estimate = Column(Numeric(precision=18, scale=2), nullable=False)
    final_approved_value = Column(Numeric(precision=18, scale=2), nullable=False)
    delta_percentage = Column(Float)
    approved_without_change = Column(Boolean, default=False)
    reviewer_comments = Column(Text)
    trust_impact = Column(Float)
    property_context = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="feedback")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
