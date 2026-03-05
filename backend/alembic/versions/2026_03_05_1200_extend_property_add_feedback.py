"""extend property add feedback

Revision ID: a1b2c3d4e5f6
Revises: 2026_03_03_1000
Create Date: 2026-03-05 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = '2026_03_03_1000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to properties table
    op.add_column('properties', sa.Column('property_ref', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('parcel_number', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('title_deed_number', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('properties', sa.Column('region', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('subcity', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('woreda', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('kebele', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('zone', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('neighborhood', sa.String(200), nullable=True))
    op.add_column('properties', sa.Column('property_subtype', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('building_area_sqm', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('number_of_floors', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('number_of_rooms', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('number_of_bedrooms', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('number_of_bathrooms', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('year_built', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('construction_material', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('roof_material', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('floor_material', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('construction_quality', sa.String(20), nullable=True))
    op.add_column('properties', sa.Column('condition', sa.String(20), nullable=True))
    op.add_column('properties', sa.Column('parking_spaces', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('properties', sa.Column('amenities', sa.JSON(), nullable=True))
    op.add_column('properties', sa.Column('utilities', sa.JSON(), nullable=True))
    op.add_column('properties', sa.Column('additional_features', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('owner_name', sa.String(200), nullable=True))
    op.add_column('properties', sa.Column('owner_phone', sa.String(30), nullable=True))
    op.add_column('properties', sa.Column('owner_email', sa.String(200), nullable=True))
    op.add_column('properties', sa.Column('owner_id_type', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('owner_id_number', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('ownership_type', sa.String(50), nullable=True))
    op.add_column('properties', sa.Column('legal_description', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('valuation_method', sa.String(30), nullable=True))
    op.add_column('properties', sa.Column('land_value', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('building_value', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('valuation_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('properties', sa.Column('valuer_name', sa.String(200), nullable=True))
    op.add_column('properties', sa.Column('valuer_license_number', sa.String(100), nullable=True))
    op.add_column('properties', sa.Column('valuer_phone', sa.String(30), nullable=True))
    op.add_column('properties', sa.Column('comparable_properties', sa.JSON(), nullable=True))
    op.add_column('properties', sa.Column('valuation_notes', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('ai_estimated_value', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('ai_confidence_score', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('ai_trust_score_at_time', sa.Float(), nullable=True))

    # Create unique index for property_ref
    op.create_index('ix_properties_property_ref', 'properties', ['property_ref'], unique=True)

    # Create valuation_feedback table
    op.create_table(
        'valuation_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('properties.id'), nullable=False),
        sa.Column('valuation_id', sa.Integer(), sa.ForeignKey('valuations.id'), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ai_estimate', sa.Float(), nullable=False),
        sa.Column('final_approved_value', sa.Float(), nullable=False),
        sa.Column('delta_percentage', sa.Float(), nullable=True),
        sa.Column('approved_without_change', sa.Boolean(), nullable=True),
        sa.Column('reviewer_comments', sa.Text(), nullable=True),
        sa.Column('trust_impact', sa.Float(), nullable=True),
        sa.Column('property_context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_valuation_feedback_id', 'valuation_feedback', ['id'], unique=False)
    op.create_index('ix_valuation_feedback_property_id', 'valuation_feedback', ['property_id'], unique=False)


def downgrade() -> None:
    op.drop_table('valuation_feedback')
    op.drop_index('ix_properties_property_ref', table_name='properties')
    # Drop all added columns
    cols = [
        'property_ref', 'parcel_number', 'title_deed_number', 'registration_date',
        'region', 'subcity', 'woreda', 'kebele', 'zone', 'neighborhood',
        'property_subtype', 'latitude', 'longitude', 'building_area_sqm',
        'number_of_floors', 'number_of_rooms', 'number_of_bedrooms', 'number_of_bathrooms',
        'year_built', 'construction_material', 'roof_material', 'floor_material',
        'construction_quality', 'condition', 'parking_spaces', 'amenities', 'utilities',
        'additional_features', 'owner_name', 'owner_phone', 'owner_email', 'owner_id_type',
        'owner_id_number', 'ownership_type', 'legal_description', 'valuation_method',
        'land_value', 'building_value', 'valuation_date', 'valuer_name',
        'valuer_license_number', 'valuer_phone', 'comparable_properties', 'valuation_notes',
        'ai_estimated_value', 'ai_confidence_score', 'ai_trust_score_at_time',
    ]
    for col in cols:
        op.drop_column('properties', col)
