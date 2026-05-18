from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.dev_schema import ensure_development_sqlite_schema
from app.data.models.property import Property


def test_dev_sqlite_schema_creates_missing_model_tables(tmp_path):
    db_path = tmp_path / "valuadis.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as connection:
      connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)"))
      connection.execute(text("INSERT INTO users (id, email) VALUES (1, 'admin@valuadis.com')"))

    ensure_development_sqlite_schema(engine)

    tables = set(inspect(engine).get_table_names())
    assert {"users", "valuations", "vehicles", "vehicle_valuations"}.issubset(tables)
    with engine.connect() as connection:
      user_count = connection.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
    assert user_count == 1


def test_dev_sqlite_schema_reads_spatial_columns_as_ewkb(tmp_path):
    db_path = tmp_path / "valuadis.db"
    engine = create_engine(f"sqlite:///{db_path}")

    ensure_development_sqlite_schema(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
      property_record = Property(
          user_id=1,
          address="Market Ready Test Parcel",
          municipality="Addis Ababa",
          property_type="commercial",
          area_sqm=250,
          boundary="SRID=4326;POLYGON((38.7466 9.0318,38.747 9.0318,38.747 9.0322,38.7466 9.0322,38.7466 9.0318))",
      )
      session.add(property_record)
      session.commit()
      session.refresh(property_record)

      assert property_record.id is not None
    finally:
      session.close()
