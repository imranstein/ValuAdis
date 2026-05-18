"""
ValuAdis Data Migration Pipeline Tests

Comprehensive testing for database migrations, data integrity,
and Ethiopian property valuation data migration
"""

import pytest
import tempfile
import os
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from app.core.database import get_db_url
import time
from datetime import datetime


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_MIGRATION_TESTS") != "1",
    reason="requires a local PostgreSQL/PostGIS database",
)


class TestMigrationPipeline:
    """
    Test suite for ValuAdis data migration pipeline
    Validates Alembic migrations, data integrity, and Ethiopian compliance
    """
    
    @pytest.fixture(scope="class")
    def test_database(self):
        """Create temporary test database for migration testing"""
        
        # Connect to PostgreSQL (default postgres database)
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="valuadis",
            password="valuadis",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create test database
        test_db_name = f"valuadis_test_{int(time.time())}"
        cursor.execute(f"CREATE DATABASE {test_db_name}")
        conn.close()
        
        # Connect to test database and enable PostGIS
        test_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="valuadis", 
            password="valuadis",
            database=test_db_name
        )
        test_conn.autocommit = True
        test_cursor = test_conn.cursor()
        
        # Enable PostGIS extension
        test_cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        test_cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology")
        
        test_conn.close()
        
        yield test_db_name
        
        # Cleanup: Drop test database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="valuadis",
            password="valuadis", 
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Kill connections to test database
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
        """)
        
        # Drop database
        cursor.execute(f"DROP DATABASE {test_db_name}")
        conn.close()
    
    @pytest.fixture
    def alembic_config(self, test_database):
        """Create temporary Alembic configuration for test database"""
        
        config_content = f"""
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://valuadis:valuadis@localhost:5432/{test_database}

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
        """
        
        # Write temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        yield config_file
        
        # Cleanup
        os.unlink(config_file)
    
    def test_alembic_migration_success(self, test_database, alembic_config):
        """Test that Alembic migrations run successfully"""
        
        # Run Alembic upgrade
        result = subprocess.run([
            "alembic",
            "-c", alembic_config,
            "upgrade", "head"
        ], 
        capture_output=True, 
        text=True,
        cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
        )
        
        assert result.returncode == 0, f"Alembic upgrade failed: {result.stderr}"
        
        # Verify tables were created
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Check that all required tables exist
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            table_names = [row[0] for row in tables]
            
            expected_tables = [
                'users', 'properties', 'valuations', 
                'alembic_version'
            ]
            
            for table in expected_tables:
                assert table in table_names, f"Table {table} not created"
    
    def test_postgis_extension_creation(self, test_database, alembic_config):
        """Test that PostGIS extension is properly created"""
        
        # Run migration first
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Verify PostGIS extension
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Check PostGIS extension
            extensions = conn.execute(text("""
                SELECT extname 
                FROM pg_extension 
                WHERE extname IN ('postgis', 'postgis_topology')
            """)).fetchall()
            
            extension_names = [row[0] for row in extensions]
            
            assert 'postgis' in extension_names, "PostGIS extension not created"
    
    def test_ethiopian_spatial_columns(self, test_database, alembic_config):
        """Test that spatial columns are properly created for Ethiopian data"""
        
        # Run migration
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Check properties table spatial column
            spatial_info = conn.execute(text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'properties' 
                AND column_name = 'boundary'
            """)).fetchone()
            
            assert spatial_info is not None, "Boundary column not found"
            assert spatial_info[1] == 'USER-DEFINED', "Boundary column not spatial type"
            assert spatial_info[2] == 'geometry', "Boundary column not geometry type"
    
    def test_ethiopian_data_seeding(self, test_database, alembic_config):
        """Test that Ethiopian test data can be seeded successfully"""
        
        # Run migration
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Create temporary environment for seeding
        env_vars = os.environ.copy()
        env_vars['DATABASE_URL'] = get_db_url().replace("valuadis", test_database)
        
        # Run seeder
        result = subprocess.run([
            "python3", "seed_data.py"
        ], 
        env=env_vars,
        capture_output=True, 
        text=True,
        cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
        )
        
        assert result.returncode == 0, f"Seeding failed: {result.stderr}"
        
        # Verify seeded data
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Check users
            users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            assert users > 0, "No users seeded"
            
            # Check properties
            properties = conn.execute(text("SELECT COUNT(*) FROM properties")).scalar()
            assert properties > 0, "No properties seeded"
            
            # Check valuations
            valuations = conn.execute(text("SELECT COUNT(*) FROM valuations")).scalar()
            assert valuations > 0, "No valuations seeded"
    
    def test_ethiopian_data_integrity(self, test_database, alembic_config):
        """Test integrity of Ethiopian property valuation data"""
        
        # Run migration and seeding
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        env_vars = os.environ.copy()
        env_vars['DATABASE_URL'] = get_db_url().replace("valuadis", test_database)
        
        subprocess.run([
            "python3", "seed_data.py"
        ], env=env_vars, capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Test Ethiopian municipalities
            municipalities = conn.execute(text("""
                SELECT DISTINCT municipality FROM properties
            """)).fetchall()
            
            ethiopian_municipalities = [row[0] for row in municipalities]
            expected_municipalities = ['Addis Ababa', 'Dire Dawa', 'Mekelle']
            
            for municipality in expected_municipalities:
                assert municipality in ethiopian_municipalities, f"Municipality {municipality} not found"
            
            # Test property types
            property_types = conn.execute(text("""
                SELECT DISTINCT property_type FROM valuations
            """)).fetchall()
            
            types = [row[0] for row in property_types]
            expected_types = ['residential', 'commercial', 'agricultural']
            
            for prop_type in expected_types:
                assert prop_type in types, f"Property type {prop_type} not found"
            
            # Test Ethiopian coordinates (should be within Ethiopian bounds)
            coordinates = conn.execute(text("""
                SELECT ST_AsText(boundary) as wkt FROM properties LIMIT 5
            """)).fetchall()
            
            for coord_row in coordinates:
                wkt = coord_row[0]
                # Basic check that coordinates are in WKT format
                assert 'POLYGON' in wkt, f"Invalid WKT format: {wkt}"
                assert 'SRID=4326' in wkt, f"Missing SRID in WKT: {wkt}"
    
    def test_migration_rollback(self, test_database, alembic_config):
        """Test that migrations can be rolled back successfully"""
        
        # Run migration to head
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Verify tables exist
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).scalar()
            assert tables > 0, "No tables found after migration"
        
        # Rollback migration
        result = subprocess.run([
            "alembic", "-c", alembic_config, "downgrade", "base"
        ], 
        capture_output=True, 
        text=True,
        cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
        )
        
        assert result.returncode == 0, f"Rollback failed: {result.stderr}"
        
        # Verify tables are removed (except alembic_version)
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            table_names = [row[0] for row in tables]
            
            # Only alembic_version should remain
            assert len(table_names) <= 1, f"Tables not properly removed: {table_names}"
    
    def test_ethiopian_compliance_migration(self, test_database, alembic_config):
        """Test that migrations maintain Ethiopian compliance requirements"""
        
        # Run migration
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            # Check that required Ethiopian compliance columns exist
            users_columns = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                AND column_name IN ('municipality', 'license_number')
            """)).fetchall()
            
            user_column_names = [row[0] for row in users_columns]
            assert 'municipality' in user_column_names, "Municipality column missing from users"
            assert 'license_number' in user_column_names, "License number column missing from users"
            
            # Check valuation compliance columns
            valuation_columns = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'valuations'
                AND column_name IN ('municipality', 'property_type', 'market_value', 'taxable_value')
            """)).fetchall()
            
            valuation_column_names = [row[0] for row in valuation_columns]
            required_columns = ['municipality', 'property_type', 'market_value', 'taxable_value']
            
            for col in required_columns:
                assert col in valuation_column_names, f"Column {col} missing from valuations"
    
    def test_migration_performance(self, test_database, alembic_config):
        """Test migration performance and timing"""
        
        # Time the migration
        start_time = time.time()
        
        result = subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], 
        capture_output=True, 
        text=True,
        cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
        )
        
        end_time = time.time()
        migration_time = end_time - start_time
        
        assert result.returncode == 0, f"Migration failed: {result.stderr}"
        
        # Migration should complete within reasonable time (30 seconds)
        assert migration_time < 30, f"Migration too slow: {migration_time:.2f}s"
        
        print(f"✅ Migration completed in {migration_time:.2f}s")
    
    def test_data_migration_consistency(self, test_database, alembic_config):
        """Test data consistency across migrations"""
        
        # Run migration and seed data
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        env_vars = os.environ.copy()
        env_vars['DATABASE_URL'] = get_db_url().replace("valuadis", test_database)
        
        subprocess.run([
            "python3", "seed_data.py"
        ], env=env_vars, capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Get initial data counts
        engine = create_engine(get_db_url().replace("valuadis", test_database))
        
        with engine.connect() as conn:
            initial_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            initial_properties = conn.execute(text("SELECT COUNT(*) FROM properties")).scalar()
            initial_valuations = conn.execute(text("SELECT COUNT(*) FROM valuations")).scalar()
        
        # Perform rollback and re-migration
        subprocess.run([
            "alembic", "-c", alembic_config, "downgrade", "base"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        subprocess.run([
            "alembic", "-c", alembic_config, "upgrade", "head"
        ], capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Re-seed data
        subprocess.run([
            "python3", "seed_data.py"
        ], env=env_vars, capture_output=True, cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend")
        
        # Verify data consistency
        with engine.connect() as conn:
            final_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            final_properties = conn.execute(text("SELECT COUNT(*) FROM properties")).scalar()
            final_valuations = conn.execute(text("SELECT COUNT(*) FROM valuations")).scalar()
        
        assert initial_users == final_users, "User count inconsistent after re-migration"
        assert initial_properties == final_properties, "Property count inconsistent after re-migration"
        assert initial_valuations == final_valuations, "Valuation count inconsistent after re-migration"


class TestMigrationErrorHandling:
    """Test error handling in migration pipeline"""
    
    def test_invalid_migration_handling(self):
        """Test handling of invalid migration scenarios"""
        
        # Test with non-existent database
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], 
        capture_output=True, 
        text=True,
        cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
        )
        
        # Should fail gracefully with database connection error
        assert result.returncode != 0, "Should fail with invalid database"
        assert "connection" in result.stderr.lower() or "database" in result.stderr.lower(), \
            "Should show database connection error"
    
    def test_corrupted_migration_recovery(self):
        """Test recovery from corrupted migration state"""
        
        # This would test more complex scenarios
        # For now, just verify basic error handling
        pass


if __name__ == "__main__":
    # Run tests manually if needed
    pytest.main([__file__, "-v"])
