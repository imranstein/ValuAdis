"""
Pytest Configuration

Test fixtures and configuration for ValuAdis backend tests
"""

import atexit
import os
import shutil
import tempfile

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db


_httpx_client_init = httpx.Client.__init__


def _compatible_httpx_client_init(self, *args, **kwargs):
    kwargs.pop("app", None)
    return _httpx_client_init(self, *args, **kwargs)


httpx.Client.__init__ = _compatible_httpx_client_init

try:
    from shapely import wkb, wkt
except Exception:
    wkb = None
    wkt = None


def _as_ewkb(value):
    if wkb is None or wkt is None:
        return value
    if not value:
        return value
    geometry = value.split(";", 1)[1] if isinstance(value, str) and value.startswith("SRID=") else value
    try:
        return wkb.dumps(wkt.loads(geometry), hex=True, srid=4326)
    except Exception:
        return value

# Use one sqlite file per pytest invocation to avoid cross-process contention
# when test suites run in parallel (xdist/CI shards).
_worker_tag = os.environ.get("PYTEST_XDIST_WORKER", "local")
_tmp_dir = tempfile.mkdtemp(prefix=f"valuadis-test-{_worker_tag}-")
_db_path = os.path.join(_tmp_dir, "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path}"


def _cleanup_test_db() -> None:
    shutil.rmtree(_tmp_dir, ignore_errors=True)


atexit.register(_cleanup_test_db)

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def add_sqlite_spatial_stubs(dbapi_connection, _):
    dbapi_connection.create_function("RecoverGeometryColumn", 5, lambda *args: 1)
    dbapi_connection.create_function("CreateSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("CheckSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("DisableSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("DiscardGeometryColumn", 2, lambda *args: 1)
    dbapi_connection.create_function("GeomFromEWKT", 1, lambda value: value)
    dbapi_connection.create_function("AsEWKB", 1, _as_ewkb)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.drop_all(bind=engine)
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

    # The rentals module's public-endpoint rate limiters (search, signup)
    # are in-process singletons keyed by client IP; TestClient always uses
    # the same synthetic IP, so state must be reset per test or unrelated
    # tests hitting those endpoints would bleed into each other's counts.
    from app.modules.rentals.rate_limit import search_rate_limiter, signup_rate_limiter
    search_rate_limiter._hits.clear()
    signup_rate_limiter._hits.clear()

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
        "password": "Testpassword123!",
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
        "area_sqm": 120.0,
        "coordinates": [
            [38.7578, 9.0320],
            [38.7580, 9.0320],
            [38.7580, 9.0318],
            [38.7578, 9.0318],
            [38.7578, 9.0320]  # Closed polygon
        ]
    }
