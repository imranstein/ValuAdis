#!/usr/bin/env python3
"""
VA-106: DB Schema Validation Script

Validates that the database schema matches expected structure.
Run: python scripts/validate_schema.py
Uses DATABASE_URL from environment (or default).
"""
import os
import sys

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://valuadis:valuadis@localhost:5432/valuadis")
    if "sqlite" in db_url:
        print("⚠️ SQLite detected - schema validation skipped (PostgreSQL required)")
        return 0

    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return 1

    expected = {
        "users": ["id", "email", "full_name", "phone", "password_hash", "municipality", "license_number", "is_active", "is_admin", "created_at"],
        "properties": ["id", "user_id", "address", "municipality", "property_type", "area_sqm", "status", "created_at"],
        "valuations": ["id", "property_id", "user_id", "market_value", "taxable_value", "status", "created_at"],
    }

    errors = []
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        for table, columns in expected.items():
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s
            """, (table,))
            found = {r[0] for r in cur.fetchall()}
            if not found:
                errors.append(f"Table '{table}' does not exist")
            else:
                missing = set(columns) - found
                if missing:
                    errors.append(f"Table '{table}' missing columns: {missing}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1

    if errors:
        print("❌ Schema validation failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("✅ Schema validation passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
