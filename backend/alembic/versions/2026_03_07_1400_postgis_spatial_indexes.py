"""VA-107: Optimize PostGIS spatial indexes

Revision ID: 2026_03_07_1400
Revises: 2026_03_07_1200_merge
Create Date: 2026-03-07 14:00:00.000000

"""
from typing import Union
from alembic import op

revision = '2026_03_07_1400'
down_revision = '2026_03_07_1200_merge'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # GIST index on properties.boundary for spatial queries
    op.execute("CREATE INDEX IF NOT EXISTS idx_properties_boundary_gist ON properties USING GIST (boundary)")
    # Index on latitude/longitude for point-based lookups when boundary is null
    op.execute("CREATE INDEX IF NOT EXISTS idx_properties_lat_lon ON properties (latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_properties_boundary_gist")
    op.execute("DROP INDEX IF EXISTS idx_properties_lat_lon")
