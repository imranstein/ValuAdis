"""add district_rent_ratios table

Per-municipality monthly rent-to-price ratio used by the rent valuation
engine's ratio method. Seeded by app.data.seeders.rent_ratio_seeder.

Revision ID: 2026_07_19_0903_rent_ratios
Revises: 2026_07_19_0902_listing_type
Create Date: 2026-07-19 09:03:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_19_0903_rent_ratios"
down_revision: Union[str, None] = "2026_07_19_0902_listing_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "district_rent_ratios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("monthly_rent_to_price_ratio", sa.Float(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="fallback"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="district_rent_ratios_pkey"),
        sa.UniqueConstraint("district", name="uq_district_rent_ratios_district"),
    )
    op.create_index("ix_district_rent_ratios_district", "district_rent_ratios", ["district"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_district_rent_ratios_district", table_name="district_rent_ratios")
    op.drop_table("district_rent_ratios")
