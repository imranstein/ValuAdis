#!/usr/bin/env python3
"""
VA-115: Data Migration Script Template

Placeholder for data migration scripts. Run with:
  python scripts/migrate_data.py
  or: docker-compose exec backend python scripts/migrate_data.py

Add your migration logic in run_migration().
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

def run_migration():
    """Execute data migration. Add your logic here."""
    from sqlalchemy import create_engine, text
    from app.core.config import settings

    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    if "sqlite" in db_url:
        print("⚠️ SQLite detected - data migrations typically run against PostgreSQL")
        return 0

    engine = create_engine(db_url)
    with engine.connect() as conn:
        # Example: backfill custom_attributes if column exists
        try:
            result = conn.execute(text("""
                UPDATE properties SET custom_attributes = '{}'
                WHERE custom_attributes IS NULL
            """))
            conn.commit()
            rc = getattr(result, "rowcount", "?")
            print(f"✅ Migration completed (rows affected: {rc})")
        except Exception as e:
            if "does not exist" in str(e).lower() or "column" in str(e).lower():
                print("ℹ️ Column custom_attributes not found - run Alembic migrations first")
            else:
                raise
    return 0

if __name__ == "__main__":
    sys.exit(run_migration())
