"""VA-117: Property custom attributes (extensible key-value)

Revision ID: 2026_03_07_1420
Revises: 2026_03_07_1410
Create Date: 2026-03-07 14:20:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision = '2026_03_07_1420'
down_revision = '2026_03_07_1410'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('properties', sa.Column('custom_attributes', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('properties', 'custom_attributes')
