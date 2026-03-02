"""
Pytest Configuration

Test fixtures and configuration for ValuAdis backend tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data for authentication tests"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "phone": "+251911234567",
        "password": "testpassword123",
        "municipality": "Addis Ababa",
        "license_number": "VAL-2023-001"
    }


@pytest.fixture
def test_property_data():
    """Test property data for property tests"""
    return {
        "address": "Bole, Addis Ababa",
        "municipality": "Addis Ababa",
        "property_type": "residential",
        "coordinates": [
            [38.7578, 9.0320],
            [38.7580, 9.0320],
            [38.7580, 9.0318],
            [38.7578, 9.0318],
            [38.7578, 9.0320]  # Closed polygon
        ]
    }
