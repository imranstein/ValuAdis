"""Add vehicle and vehicle valuation tables

Revision ID: 2026_03_03_1000
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_03_03_1000'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vehicles table
    op.create_table('vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('vin', sa.String(length=17), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('body_type', sa.String(length=50), nullable=True),
        sa.Column('fuel_type', sa.String(length=20), nullable=True),
        sa.Column('transmission', sa.String(length=20), nullable=True),
        sa.Column('engine_capacity', sa.Float(), nullable=True),
        sa.Column('mileage', sa.Float(), nullable=True),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('custom_duty_paid', sa.Boolean(), nullable=True),
        sa.Column('import_year', sa.Integer(), nullable=True),
        sa.Column('previous_owners', sa.Integer(), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vin'),
        sa.UniqueConstraint('plate_number')
    )
    op.create_index(op.f('ix_vehicles_is_active'), 'vehicles', ['is_active'], unique=False)
    op.create_index(op.f('ix_vehicles_make'), 'vehicles', ['make'], unique=False)
    op.create_index(op.f('ix_vehicles_model'), 'vehicles', ['model'], unique=False)
    op.create_index(op.f('ix_vehicles_owner_id'), 'vehicles', ['owner_id'], unique=False)
    op.create_index(op.f('ix_vehicles_plate_number'), 'vehicles', ['plate_number'], unique=False)
    op.create_index(op.f('ix_vehicles_region'), 'vehicles', ['region'], unique=False)
    op.create_index(op.f('ix_vehicles_vin'), 'vehicles', ['vin'], unique=False)
    op.create_index(op.f('ix_vehicles_year'), 'vehicles', ['year'], unique=False)

    # Create vehicle_valuations table
    op.create_table('vehicle_valuations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('valuation_date', sa.DateTime(), nullable=True),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('taxable_value', sa.Float(), nullable=False),
        sa.Column('valuation_method', sa.String(length=50), nullable=False),
        sa.Column('depreciation_rate', sa.Float(), nullable=True),
        sa.Column('condition_factor', sa.Float(), nullable=True),
        sa.Column('comparable_vehicles', sa.Text(), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('ai_market_trends', sa.Text(), nullable=True),
        sa.Column('local_demand_factor', sa.Float(), nullable=True),
        sa.Column('import_tax_adjustment', sa.Float(), nullable=True),
        sa.Column('regional_price_adjustment', sa.Float(), nullable=True),
        sa.Column('valuer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('certificate_number', sa.String(length=50), nullable=True),
        sa.Column('certificate_issued_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['valuer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('certificate_number')
    )
    op.create_index(op.f('ix_vehicle_valuations_approved_by'), 'vehicle_valuations', ['approved_by'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_certificate_number'), 'vehicle_valuations', ['certificate_number'], unique=True)
    op.create_index(op.f('ix_vehicle_valuations_status'), 'vehicle_valuations', ['status'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_valuation_date'), 'vehicle_valuations', ['valuation_date'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_valuer_id'), 'vehicle_valuations', ['valuer_id'], unique=False)
    op.create_index(op.f('ix_vehicle_valuations_vehicle_id'), 'vehicle_valuations', ['vehicle_id'], unique=False)

    # Add vehicles relationship to users table
    op.add_column('users', sa.Column('is_valuer', sa.Boolean(), nullable=True, default=False))
    op.create_index(op.f('ix_users_is_valuer'), 'users', ['is_valuer'], unique=False)


def downgrade() -> None:
    # Remove vehicles relationship from users
    op.drop_index(op.f('ix_users_is_valuer'), table_name='users')
    op.drop_column('users', 'is_valuer')

    # Drop vehicle_valuations table
    op.drop_index(op.f('ix_vehicle_valuations_vehicle_id'), table_name='vehicle_valuations')
    op.drop_index(op.f('ix_vehicle_valuations_valuer_id'), table_name='vehicle_valuations')
    op.drop_index(op.f('ix_vehicle_valuations_valuation_date'), table_name='vehicle_valuations')
    op.drop_index(op.f('ix_vehicle_valuations_status'), table_name='vehicle_valuations')
    op.drop_index(op.f('ix_vehicle_valuations_certificate_number'), table_name='vehicle_valuations')
    op.drop_index(op.f('ix_vehicle_valuations_approved_by'), table_name='vehicle_valuations')
    op.drop_table('vehicle_valuations')

    # Drop vehicles table
    op.drop_index(op.f('ix_vehicles_year'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_vin'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_region'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_plate_number'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_owner_id'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_model'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_make'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_is_active'), table_name='vehicles')
    op.drop_table('vehicles')
