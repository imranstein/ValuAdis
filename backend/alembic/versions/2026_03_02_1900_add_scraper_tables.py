"""add scraper tables

Revision ID: d4e5f6a7b8c9
Revises: c1250dc0f6b2
Create Date: 2026-03-02 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c1250dc0f6b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scraper_targets table
    op.create_table(
        'scraper_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('url_template', sa.String(length=500), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('selectors', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('schedule', sa.String(length=50), nullable=True, server_default='daily'),
        sa.Column('max_pages', sa.Integer(), nullable=True, server_default='50'),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_status', sa.String(length=50), nullable=True),
        sa.Column('total_listings', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_targets_id'), 'scraper_targets', ['id'], unique=False)
    op.create_index(op.f('ix_scraper_targets_domain'), 'scraper_targets', ['domain'], unique=True)

    # Create scraper_logs table
    op.create_table(
        'scraper_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scraper_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('listings_found', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('listings_saved', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['scraper_id'], ['scraper_targets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_logs_id'), 'scraper_logs', ['id'], unique=False)

    # Insert existing scrapers from run_scraper.py
    op.execute("""
        INSERT INTO scraper_targets (domain, url_template, enabled, selectors, schedule, max_pages)
        VALUES 
        ('livingethio.com', 'https://livingethio.com/site/property/list?page={page}', true, 
         '{"title": ".property-title", "price": ".property-price", "location": ".property-location", "area": ".property-area", "property_type": ".property-type", "bedrooms": ".bedrooms", "bathrooms": ".bathrooms", "listing_url": ".property-link"}', 
         'daily', 50),
        ('ethiopiapropertycentre.com', 'https://ethiopiapropertycentre.com/for-sale?page={page}', true,
         '{"title": ".listing-title", "price": ".listing-price", "location": ".listing-location", "area": ".listing-area", "property_type": ".listing-type", "bedrooms": ".bedrooms", "bathrooms": ".bathrooms", "listing_url": ".listing-link"}',
         'daily', 50),
        ('ethiopianproperties.com', 'https://ethiopianproperties.com/rent/page/{page}/', true,
         '{"title": ".property-title", "price": ".property-price", "location": ".property-location", "area": ".property-area", "property_type": ".property-type", "bedrooms": ".bedrooms", "bathrooms": ".bathrooms", "listing_url": ".property-link"}',
         'daily', 50),
        ('zegebeya.com', 'https://zegebeya.com/properties-grid-fullwidth/page/{page}/', true,
         '{"title": ".property-title", "price": ".property-price", "location": ".property-location", "area": ".property-area", "property_type": ".property-type", "bedrooms": ".bedrooms", "bathrooms": ".bathrooms", "listing_url": ".property-link"}',
         'daily', 50),
        ('jiji.com.et', 'https://jiji.com.et/real-estate?page={page}', true,
         '{"title": ".b-list-advert__title", "price": ".qa-advert-price", "location": ".b-list-advert__region", "area": ".b-list-advert__parameter", "property_type": ".b-list-advert__category", "bedrooms": ".bedrooms", "bathrooms": ".bathrooms", "listing_url": ".b-list-advert__link"}',
         'daily', 50)
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_scraper_logs_id'), table_name='scraper_logs')
    op.drop_table('scraper_logs')
    op.drop_index(op.f('ix_scraper_targets_domain'), table_name='scraper_targets')
    op.drop_index(op.f('ix_scraper_targets_id'), table_name='scraper_targets')
    op.drop_table('scraper_targets')
