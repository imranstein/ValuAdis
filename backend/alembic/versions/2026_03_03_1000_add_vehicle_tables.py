"""Add vehicle and vehicle valuation tables

Revision ID: 2026_03_03_1000
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 10:00:00.000000

NOTE: The vehicle table schema in this migration was superseded by
2026_03_05_1000 which creates the canonical vehicle tables with the
correct INTEGER foreign keys. This migration is intentionally a no-op;
2026_03_05_1000 handles the actual table creation.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2026_03_03_1000'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Vehicle tables are created by the superseding migration 2026_03_05_1000.
    pass


def downgrade() -> None:
    # Vehicle tables are dropped by the superseding migration 2026_03_05_1000.
    pass
