"""
Alembic Migration Tests

Test-Driven Development for database migrations
Following RED-GREEN-REFACTOR cycle
"""

import pytest
import os
import tempfile
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from app.core.database import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI_PATH = BACKEND_DIR / "alembic.ini"


requires_postgres_migrations = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_MIGRATION_TESTS") != "1",
    reason="requires a local PostgreSQL/PostGIS database",
)


class TestAlembicMigrations:
    """Test Alembic migrations with TDD approach"""
    
    def test_alembic_configuration_exists(self):
        """
        GREEN: Test Alembic configuration file exists
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (GREEN: Test should pass with correct implementation)
        assert alembic_ini_path.exists(), "alembic.ini file should exist"
        
        # Verify configuration has required sections
        config = Config(str(alembic_ini_path))
        assert config.get_main_option("script_location") == "alembic"
        assert config.get_main_option("sqlalchemy.url") is not None
    
    @requires_postgres_migrations
    def test_migration_environment_setup(self):
        """
        RED: Test migration environment is properly configured
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            config = Config(str(alembic_ini_path))
            # This should work when alembic is properly configured
            command.revision(config, autogenerate=True, message="Test migration")
    
    @requires_postgres_migrations
    def test_postgis_extension_migration(self):
        """
        RED: Test PostGIS extension is created in migration
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            # Create test database
            engine = create_engine("sqlite:///:memory:")
            
            # Run migrations
            config = Config(str(alembic_ini_path))
            command.upgrade(config, "head")
            
            # Verify PostGIS extension exists
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'"))
                assert result.fetchone() is not None, "PostGIS extension should be created"
    
    @requires_postgres_migrations
    def test_valuation_table_migration(self):
        """
        RED: Test valuation table is created with correct schema
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            # Create test database
            engine = create_engine("sqlite:///:memory:")
            
            # Run migrations
            config = Config(str(alembic_ini_path))
            command.upgrade(config, "head")
            
            # Verify valuation table exists
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'valuations'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                # Verify required columns exist
                column_names = [col[0] for col in columns]
                required_columns = [
                    'id', 'property_id', 'user_id', 'property_type',
                    'municipality', 'area_sqm', 'market_value', 'taxable_value',
                    'status', 'coordinates', 'valuation_date', 'notes',
                    'created_at', 'updated_at'
                ]
                
                for required_col in required_columns:
                    assert required_col in column_names, f"Column {required_col} should exist"
    
    @requires_postgres_migrations
    def test_spatial_index_creation(self):
        """
        RED: Test spatial indexes are created for performance
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            # Create test database
            engine = create_engine("sqlite:///:memory:")
            
            # Run migrations
            config = Config(str(alembic_ini_path))
            command.upgrade(config, "head")
            
            # Verify spatial index exists
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'valuations' AND indexname LIKE '%coordinates%'
                """))
                indexes = result.fetchall()
                assert len(indexes) > 0, "Spatial index should be created for coordinates"
    
    @requires_postgres_migrations
    def test_migration_downgrade(self):
        """
        RED: Test migration can be safely downgraded
        """
        # Arrange
        alembic_ini_path = ALEMBIC_INI_PATH
        
        # Act & Assert (RED - This should fail initially)
        with pytest.raises(NotImplementedError):
            # Create test database
            engine = create_engine("sqlite:///:memory:")
            
            # Run migrations
            config = Config(str(alembic_ini_path))
            command.upgrade(config, "head")
            
            # Verify tables exist
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'valuations'"))
                assert result.fetchone()[0] > 0, "Valuation table should exist after migration"
            
            # Downgrade
            command.downgrade(config, "base")
            
            # Verify tables are removed
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'valuations'"))
                assert result.fetchone()[0] == 0, "Valuation table should not exist after downgrade"
