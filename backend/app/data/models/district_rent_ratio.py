"""
District Rent Ratio Model

Per-municipality monthly rent-to-price ratio used by the rent valuation
engine's ratio method (suggested_rent = market_value * ratio). Seeded by
app.data.seeders.rent_ratio_seeder from scraped rent listings where they
exist, falling back to a conservative citywide estimate otherwise.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func

from app.core.database import Base


class DistrictRentRatio(Base):
    """Monthly rent-to-price ratio for a municipality/district."""

    __tablename__ = "district_rent_ratios"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), unique=True, nullable=False, index=True)
    monthly_rent_to_price_ratio = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False, default=0)
    # 'scraped' (derived from real rent listings) or 'fallback' (citywide
    # conservative estimate, used while no rent listings exist for the
    # district yet).
    source = Column(String(20), nullable=False, default="fallback")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "district": self.district,
            "monthly_rent_to_price_ratio": self.monthly_rent_to_price_ratio,
            "sample_size": self.sample_size,
            "source": self.source,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
