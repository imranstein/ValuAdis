"""Initial migration with PostGIS extension and valuation tables

Revision ID: 001
Revises: 
Create Date: 2026-02-26 18:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create PostGIS extension and valuation tables"""
    
    # Create PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('municipality', sa.String(length=100), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=False)
    
    # Create properties table
    op.create_table('properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('municipality', sa.String(length=100), nullable=False),
        sa.Column('property_type', sa.String(length=50), nullable=False),
        sa.Column('boundary', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('area_sqm', sa.Float(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=True),
        sa.Column('taxable_value', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_municipality'), 'properties', ['municipality'], unique=False)
    op.create_index(op.f('ix_properties_property_type'), 'properties', ['property_type'], unique=False)
    op.create_index(op.f('ix_properties_status'), 'properties', ['status'], unique=False)
    op.create_index(op.f('ix_properties_user_id'), 'properties', ['user_id'], unique=False)
    
    # Create valuations table
    op.create_table('valuations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('property_type', sa.Enum('RESIDENTIAL', 'COMMERCIAL', 'AGRICULTURAL', name='propertytype'), nullable=False),
        sa.Column('municipality', sa.String(length=100), nullable=False),
        sa.Column('area_sqm', sa.Float(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('taxable_value', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', name='valuationstatus'), nullable=False),
        sa.Column('coordinates', Geometry('POLYGON', srid=4326, spatial_index=True, dimension=2), nullable=True),
        sa.Column('valuation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_valuations_municipality'), 'valuations', ['municipality'], unique=False)
    op.create_index(op.f('ix_valuations_property_id'), 'valuations', ['property_id'], unique=False)
    op.create_index(op.f('ix_valuations_status'), 'valuations', ['status'], unique=False)
    op.create_index(op.f('ix_valuations_user_id'), 'valuations', ['user_id'], unique=False)
    
    # Create spatial index for coordinates
    op.execute("CREATE INDEX IF NOT EXISTS idx_valuations_coordinates ON valuations USING GIST (coordinates)")


def downgrade() -> None:
    """Drop valuation tables and PostGIS extension"""
    
    # Drop tables in reverse order
    op.drop_table('valuations')
    op.drop_table('properties')
    op.drop_table('users')
    
    # Drop PostGIS extensions
    op.execute("DROP EXTENSION IF EXISTS postgis_topology")
    op.execute("DROP EXTENSION IF EXISTS postgis")
