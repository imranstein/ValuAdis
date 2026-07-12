from app.core.database import SessionLocal
from app.data.models.market_listing import RawMarketListing

def fetch():
    with SessionLocal() as session:
        return session.query(RawMarketListing).all()

if __name__ == "__main__":
    records = fetch()
    print(f"Found {len(records)} records in DB.")
    for r in records:
        print(f"Title: {r.title}")
        print(f"URL: {r.listing_url}")
        print(f"Location: {r.location_subcity}")
        print("---")
