"""
District Rent Ratio Seeder

Derives per-district monthly rent-to-price ratios from scraped
raw_market_listings rows tagged listing_type='rent', falling back to
ValuationService.RENT_RATIO_CITYWIDE_FALLBACK where a district has no
rent-tagged listings yet (true for every district until the scraper is
extended to capture rental listings — see
plans/valuadis-rentals/tasks/phase-a.md).
"""

from decimal import Decimal
from statistics import median
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.data.models.district_rent_ratio import DistrictRentRatio
from app.data.models.market_listing import RawMarketListing
from app.modules.valuation.services import ValuationService

# Same municipalities covered by ValuationService._base_rates, so every
# district the sale engine supports also has a rent ratio.
SEEDED_MUNICIPALITIES = [
    "Addis Ababa", "Dire Dawa", "Mekelle", "Bahir Dar", "Adama", "Hawassa",
    "Gonder", "Jimma", "Dessie", "Jijiga", "Shashamane", "Arba Minch",
    "Harar", "Nekemte", "Debre Markos", "Debre Birhan",
]


class RentRatioSeeder:
    """Seeder for district_rent_ratios; idempotent — upserts per municipality."""

    @staticmethod
    def _listing_prices(db: Session, municipality: str, listing_type: str) -> List[Decimal]:
        rows = (
            db.query(RawMarketListing.asking_price_etb)
            .filter(
                RawMarketListing.listing_type == listing_type,
                RawMarketListing.location_subcity.ilike(f"%{municipality}%"),
                RawMarketListing.asking_price_etb.isnot(None),
                RawMarketListing.asking_price_etb > 0,
            )
            .all()
        )
        return [Decimal(str(row[0])) for row in rows]

    @staticmethod
    def _derive_ratio(db: Session, municipality: str) -> Tuple[Decimal, int, str]:
        """
        Ratio = median rent listing price / median sale listing price for
        the district. Falls back to the citywide conservative estimate
        when either side has no data (currently true for 'rent' on every
        district, since the scraper does not yet tag rental listings).
        """
        rents = RentRatioSeeder._listing_prices(db, municipality, "rent")
        sales = RentRatioSeeder._listing_prices(db, municipality, "sale")
        if rents and sales:
            ratio = (Decimal(str(median(rents))) / Decimal(str(median(sales)))).quantize(Decimal("0.0001"))
            return ratio, len(rents), "scraped"
        return ValuationService.RENT_RATIO_CITYWIDE_FALLBACK, 0, "fallback"

    @staticmethod
    def seed_ratios(db: Session) -> List[DistrictRentRatio]:
        """Create or refresh a DistrictRentRatio row per seeded municipality."""
        seeded: List[DistrictRentRatio] = []
        for municipality in SEEDED_MUNICIPALITIES:
            ratio, sample_size, source = RentRatioSeeder._derive_ratio(db, municipality)
            row = db.query(DistrictRentRatio).filter(DistrictRentRatio.district == municipality).first()
            if row is None:
                row = DistrictRentRatio(district=municipality)
                db.add(row)
            row.monthly_rent_to_price_ratio = float(ratio)
            row.sample_size = sample_size
            row.source = source
            seeded.append(row)
        db.commit()
        for row in seeded:
            db.refresh(row)
        return seeded

    @staticmethod
    def clear_ratios(db: Session) -> None:
        """Clear all seeded ratios."""
        db.query(DistrictRentRatio).delete()
        db.commit()


def run_rent_ratio_seeder():
    from app.core.database import get_db

    db = next(get_db())
    try:
        rows = RentRatioSeeder.seed_ratios(db)
        print(f"🌱 Seeded {len(rows)} district rent-to-price ratios")
        return rows
    finally:
        db.close()


if __name__ == "__main__":
    run_rent_ratio_seeder()
