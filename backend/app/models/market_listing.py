from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Index
from sqlalchemy.sql import func
from app.db.base_class import Base
from datetime import datetime
import enum

class MarketListing(Base):
    __tablename__ = "raw_market_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    asking_price_etb = Column(Float, index=True)
    location_subcity = Column(String, index=True)
    area_sqm = Column(Float)
    property_type = Column(String, index=True)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    listing_url = Column(String, unique=True, index=True, nullable=False)
    scrape_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite Index for faster queries
    __table_args__ = (
        Index('ix_raw_market_listings_location_price', 'location_subcity', 'asking_price_etb'),
    )
