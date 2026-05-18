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
