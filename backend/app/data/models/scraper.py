from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ScraperTarget(Base):
    __tablename__ = "scraper_targets"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    url_template = Column(String(500), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    selectors = Column(JSON, nullable=False)
    schedule = Column(String(50), default="daily")
    max_pages = Column(Integer, default=50)
    last_run = Column(DateTime(timezone=True), nullable=True)
    last_status = Column(String(50), nullable=True)
    total_listings = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    logs = relationship("ScraperLog", back_populates="scraper", cascade="all, delete-orphan")


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True, index=True)
    scraper_id = Column(Integer, ForeignKey("scraper_targets.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=True)
    listings_found = Column(Integer, default=0)
    listings_saved = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    scraper = relationship("ScraperTarget", back_populates="logs")
