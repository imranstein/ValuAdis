from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class RawMarketListing(Base):
    """
    Raw market listings scraped from Ethiopian property portals.
    Used for AVM training.
    """
    __tablename__ = "raw_market_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    asking_price_etb = Column(Float, nullable=True) # Sometimes price is negotiated or not listed
    location_subcity = Column(String(200), nullable=True)
    area_sqm = Column(Float, nullable=True)
    property_type = Column(String(100), nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    listing_url = Column(String(1000), unique=True, nullable=False, index=True)
    scrape_date = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "asking_price_etb": self.asking_price_etb,
            "location_subcity": self.location_subcity,
            "area_sqm": self.area_sqm,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "listing_url": self.listing_url,
            "scrape_date": self.scrape_date.isoformat() if self.scrape_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
