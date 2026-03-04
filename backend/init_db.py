#!/usr/bin/env python3
"""
Simple database initialization script for ValuAdis
"""

import asyncio
from sqlalchemy import create_engine
from urllib.parse import urlparse
from app.core.config import settings
from app.data.models import User, Property, Valuation, RawMarketListing
from app.data.models.scraper import ScraperTarget, ScraperLog
from app.data.models.role import Role, Permission, UserRole
from app.core.database import Base

def init_database():
    """Initialize database tables"""
    # Parse DATABASE_URL to extract non-sensitive parts
    parsed_url = urlparse(settings.DATABASE_URL)
    safe_db_info = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port or '5432'}/{parsed_url.path.lstrip('/')}"
    print(f"Connecting to database: {safe_db_info}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise  # Re-raise to ensure non-zero exit code
    
    # Close engine
    engine.dispose()

if __name__ == "__main__":
    init_database()
