"""
Rent Ratio Seeder Tests

Covers the district rent-to-price ratio seeder: idempotency, the
conservative citywide fallback when no rent-tagged listings exist for a
district, and correct derivation once real rent listings do exist.
"""

from app.data.models.district_rent_ratio import DistrictRentRatio
from app.data.models.market_listing import RawMarketListing
from app.data.seeders.rent_ratio_seeder import RentRatioSeeder, SEEDED_MUNICIPALITIES
from app.modules.valuation.services import ValuationService


class TestRentRatioSeederFallback:
    def test_seeds_a_row_per_municipality(self, db_session):
        rows = RentRatioSeeder.seed_ratios(db_session)
        assert len(rows) == len(SEEDED_MUNICIPALITIES)
        districts = {row.district for row in rows}
        assert districts == set(SEEDED_MUNICIPALITIES)

    def test_uses_citywide_fallback_when_no_rent_listings_exist(self, db_session):
        rows = RentRatioSeeder.seed_ratios(db_session)
        addis = next(r for r in rows if r.district == "Addis Ababa")

        assert addis.source == "fallback"
        assert addis.sample_size == 0
        assert addis.monthly_rent_to_price_ratio == float(ValuationService.RENT_RATIO_CITYWIDE_FALLBACK)

    def test_seeding_twice_is_idempotent(self, db_session):
        RentRatioSeeder.seed_ratios(db_session)
        RentRatioSeeder.seed_ratios(db_session)

        count = db_session.query(DistrictRentRatio).count()
        assert count == len(SEEDED_MUNICIPALITIES)


class TestRentRatioSeederDerivation:
    def test_derives_ratio_from_real_rent_and_sale_listings(self, db_session):
        # Sale comps: median 1,000,000
        for price in (900_000, 1_000_000, 1_100_000):
            db_session.add(RawMarketListing(
                title="Sale listing",
                asking_price_etb=price,
                location_subcity="Addis Ababa - Bole",
                listing_url=f"https://example.com/sale-{price}",
                listing_type="sale",
            ))
        # Rent comps: median 6,000
        for price in (5_500, 6_000, 6_500):
            db_session.add(RawMarketListing(
                title="Rent listing",
                asking_price_etb=price,
                location_subcity="Addis Ababa - Bole",
                listing_url=f"https://example.com/rent-{price}",
                listing_type="rent",
            ))
        db_session.commit()

        rows = RentRatioSeeder.seed_ratios(db_session)
        addis = next(r for r in rows if r.district == "Addis Ababa")

        assert addis.source == "scraped"
        assert addis.sample_size == 3
        # 6,000 / 1,000,000 = 0.006
        assert addis.monthly_rent_to_price_ratio == 0.006

    def test_other_districts_without_listings_still_fall_back(self, db_session):
        for price in (900_000, 1_000_000, 1_100_000):
            db_session.add(RawMarketListing(
                title="Sale listing",
                asking_price_etb=price,
                location_subcity="Addis Ababa - Bole",
                listing_url=f"https://example.com/sale-only-{price}",
                listing_type="sale",
            ))
        db_session.add(RawMarketListing(
            title="Rent listing",
            asking_price_etb=6_000,
            location_subcity="Addis Ababa - Bole",
            listing_url="https://example.com/rent-only",
            listing_type="rent",
        ))
        db_session.commit()

        rows = RentRatioSeeder.seed_ratios(db_session)
        mekelle = next(r for r in rows if r.district == "Mekelle")

        assert mekelle.source == "fallback"
        assert mekelle.sample_size == 0
