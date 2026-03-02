import asyncio
from app.core.database import AsyncSessionLocal
from app.data.models.market_listing import RawMarketListing
from sqlalchemy import select

async def fetch():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(RawMarketListing))
        return res.scalars().all()

if __name__ == "__main__":
    records = asyncio.run(fetch())
    print(f"Found {len(records)} records in DB.")
    for r in records:
        print(f"Title: {r.title}")
        print(f"URL: {r.listing_url}")
        print(f"Location: {r.location_subcity}")
        print("---")
