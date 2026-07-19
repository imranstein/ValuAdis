"""SQLite spatial stubs for lightweight unit tests ONLY.

These stubs register no-op / minimal Python implementations of a handful of
PostGIS/SpatiaLite functions so parts of the schema can be created on an
in-memory or file-based SQLite database for fast, dependency-free unit tests.

They are NOT a substitute for a real database. The supported dev, staging, and
production path is Postgres + PostGIS:

* Migration ``001`` runs ``CREATE EXTENSION postgis``, so the full Alembic
  chain is Postgres-only and never exercises these stubs.
* For local development, run the Dockerized Postgres + PostGIS database:
  ``./scripts/dev-db-up.sh`` (or ``docker compose up -d db`` then
  ``alembic upgrade head``). See the "Local database (Docker)" section of the
  top-level ``README.md``.

Do not extend these stubs to chase parity with PostGIS behavior — if a test
needs real spatial semantics, point it at the Postgres + PostGIS engine
instead. Retiring reliance on these stubs from any release-confidence path is
intentional; the code stays because unit tests still import it.
"""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from shapely import wkb, wkt

from app.core.database import Base
from app.data import models  # noqa: F401


def _as_ewkb(value):
    if not value:
        return value

    geometry = value.split(";", 1)[1] if isinstance(value, str) and value.startswith("SRID=") else value
    return wkb.dumps(wkt.loads(geometry), hex=True, srid=4326)


def _register_sqlite_spatial_stubs(dbapi_connection, _connection_record=None) -> None:
    dbapi_connection.create_function("RecoverGeometryColumn", 5, lambda *args: 1)
    dbapi_connection.create_function("CreateSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("CheckSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("DisableSpatialIndex", 2, lambda *args: 1)
    dbapi_connection.create_function("DiscardGeometryColumn", 2, lambda *args: 1)
    dbapi_connection.create_function("GeomFromEWKT", 1, lambda value: value)
    dbapi_connection.create_function("AsEWKB", 1, _as_ewkb)


def ensure_development_sqlite_schema(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return

    event.listen(engine, "connect", _register_sqlite_spatial_stubs)
    engine.dispose()
    Base.metadata.create_all(bind=engine)
