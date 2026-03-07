"""Add vehicle and vehicle valuation tables

Revision ID: 2026_03_05_1000
Revises: 2026_03_03_1000
Create Date: 2026-03-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_05_1000'
down_revision = '2026_03_03_1000'
branch_labels = None
depends_on = None


def upgrade():
    """Create vehicle and vehicle valuation tables"""
    
    # Create vehicle_types enum (idempotent — silently skips if already exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vehicle_type AS ENUM (
                'sedan', 'suv', 'hatchback', 'pickup', 'truck',
                'van', 'coupe', 'convertible', 'station_wagon'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create fuel_types enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE fuel_type AS ENUM (
                'gasoline', 'diesel', 'hybrid', 'electric', 'lpg', 'cng'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create transmission_types enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transmission_type AS ENUM ('manual', 'automatic', 'cvt');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    
    # Create vehicles table
    op.create_table('vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('vin', sa.String(length=17), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('body_type', postgresql.ENUM('sedan', 'suv', 'hatchback', 'pickup', 'truck', 'van', 'coupe', 'convertible', 'station_wagon', name='vehicle_type', create_type=False), nullable=True),
        sa.Column('fuel_type', postgresql.ENUM('gasoline', 'diesel', 'hybrid', 'electric', 'lpg', 'cng', name='fuel_type', create_type=False), nullable=True),
        sa.Column('transmission', postgresql.ENUM('manual', 'automatic', 'cvt', name='transmission_type', create_type=False), nullable=True),
        sa.Column('engine_capacity', sa.Integer(), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('previous_owners', sa.Integer(), nullable=False),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('purchase_price', sa.Float(), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('import_year', sa.Integer(), nullable=True),
        sa.Column('custom_duty_paid', sa.Boolean(), nullable=False),
        sa.Column('customs_declaration_number', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_listed_for_sale', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for vehicles table
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], unique=False)
    op.create_index(op.f('ix_vehicles_user_id'), 'vehicles', ['user_id'], unique=False)
    op.create_index(op.f('ix_vehicles_make'), 'vehicles', ['make'], unique=False)
    op.create_index(op.f('ix_vehicles_model'), 'vehicles', ['model'], unique=False)
    op.create_index(op.f('ix_vehicles_year'), 'vehicles', ['year'], unique=False)
    op.create_index(op.f('ix_vehicles_vin'), 'vehicles', ['vin'], unique=True)
    op.create_index(op.f('ix_vehicles_plate_number'), 'vehicles', ['plate_number'], unique=True)
    op.create_index(op.f('ix_vehicles_body_type'), 'vehicles', ['body_type'], unique=False)
    op.create_index(op.f('ix_vehicles_fuel_type'), 'vehicles', ['fuel_type'], unique=False)
    op.create_index(op.f('ix_vehicles_region'), 'vehicles', ['region'], unique=False)
    op.create_index(op.f('ix_vehicles_city'), 'vehicles', ['city'], unique=False)
    op.create_index(op.f('ix_vehicles_import_year'), 'vehicles', ['import_year'], unique=False)
    op.create_index(op.f('ix_vehicles_custom_duty_paid'), 'vehicles', ['custom_duty_paid'], unique=False)
    
    # Create vehicle_valuation_status enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vehicle_valuation_status AS ENUM (
                'draft', 'pending', 'approved', 'rejected', 'expired', 'under_review'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    
    # Create vehicle_valuations table
    op.create_table('vehicle_valuations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_make', sa.String(length=100), nullable=False),
        sa.Column('vehicle_model', sa.String(length=100), nullable=False),
        sa.Column('vehicle_year', sa.Integer(), nullable=False),
        sa.Column('vehicle_vin', sa.String(length=17), nullable=False),
        sa.Column('vehicle_plate', sa.String(length=20), nullable=False),
        sa.Column('vehicle_mileage', sa.Integer(), nullable=True),
        sa.Column('vehicle_region', sa.String(length=100), nullable=True),
        sa.Column('base_value', sa.Float(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('taxable_value', sa.Float(), nullable=False),
        sa.Column('condition_factor', sa.Float(), nullable=False),
        sa.Column('regional_multiplier', sa.Float(), nullable=False),
        sa.Column('import_year_adjustment', sa.Float(), nullable=False),
        sa.Column('customs_duty_factor', sa.Float(), nullable=False),
        sa.Column('make_reliability', sa.Float(), nullable=False),
        sa.Column('fuel_type_adjustment', sa.Float(), nullable=False),
        sa.Column('body_type_demand', sa.Float(), nullable=False),
        sa.Column('ethiopian_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('market_position', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('comparable_vehicles_count', sa.Integer(), nullable=True),
        sa.Column('condition_rating', sa.String(length=20), nullable=False),
        sa.Column('age_depreciation', sa.Float(), nullable=False),
        sa.Column('mileage_depreciation', sa.Float(), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'approved', 'rejected', 'expired', 'under_review', name='vehicle_valuation_status', create_type=False), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('valuation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('valuation_method', sa.String(length=50), nullable=False),
        sa.Column('data_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for vehicle_valuations table
    op.create_index(op.f('ix_vehicle_valuations_id'), 'vehicle_valuations', ['id'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_id'), 'vehicle_valuations', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_user_id'), 'vehicle_valuations', ['user_id'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_make'), 'vehicle_valuations', ['vehicle_make'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_model'), 'vehicle_valuations', ['vehicle_model'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_year'), 'vehicle_valuations', ['vehicle_year'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_vin'), 'vehicle_valuations', ['vehicle_vin'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_region'), 'vehicle_valuations', ['vehicle_region'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_status'), 'vehicle_valuations', ['status'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_market_position'), 'vehicle_valuations', ['market_position'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_condition_rating'), 'vehicle_valuations', ['condition_rating'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_expires_at'), 'vehicle_valuations', ['expires_at'], unique=False)


def downgrade():
    """Drop vehicle and vehicle valuation tables"""
    
    # Drop vehicle_valuations table
    op.drop_table('vehicle_valuations')
    
    # Drop vehicle_valuation_status enum
    op.execute("DROP TYPE IF EXISTS vehicle_valuation_status")
    
    # Drop vehicles table
    op.drop_table('vehicles')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS vehicle_type")
    op.execute("DROP TYPE IF EXISTS fuel_type")
    op.execute("DROP TYPE IF EXISTS transmission_type")
