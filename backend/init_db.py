#!/usr/bin/env python3
"""
Simple database initialization script for ValuAdis
"""

import asyncio
from sqlalchemy import create_engine
from app.core.config import settings
from app.data.models import User, Property, Valuation, RawMarketListing
from app.data.models.scraper import ScraperTarget, ScraperLog
from app.data.models.role import Role, Permission, UserRole
from app.core.database import Base

def init_database():
    """Initialize database tables"""
    print(f"Connecting to database: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Close engine
    engine.dispose()

if __name__ == "__main__":
    init_database()
