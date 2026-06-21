import time
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.database import SessionLocal, engine, Base
from app.data.models.property import Property
from app.data.models.valuation import Valuation
from app.api.v1.endpoints.analytics import get_dashboard_stats

# Create test data
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if we already have data
    if db.query(Property).count() == 0:
        print("Inserting test data...")
        properties = []
        for i in range(1000):
            properties.append(Property(
                municipality=f"Mun_{i%10}",
                property_type=f"Type_{i%3}",
                market_value=100000 + i,
                status="active"
            ))
        db.bulk_save_objects(properties)
        db.commit()
    return db

async def run_benchmark():
    db = setup_db()

    # Warmup
    for _ in range(2):
        await get_dashboard_stats(period="month", municipality=None, property_type=None, db=db, current_user_id=1)

    start_time = time.time()
    for _ in range(10):
        await get_dashboard_stats(period="month", municipality=None, property_type=None, db=db, current_user_id=1)
    end_time = time.time()

    print(f"Total time for 10 calls: {end_time - start_time:.4f} seconds")
    print(f"Average time per call: {(end_time - start_time) / 10:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
