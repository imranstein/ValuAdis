"""add rent_index_snapshots table

Phase D of plans/valuadis-rentals/plan.mdx. Public district rent index rows
computed by app.modules.rentals.index_service from active tenancy contracts
(falling back to published listing bands where the contract sample is
thin), one row per (district, property_subtype, bedrooms, period).

Revision ID: 2026_07_22_0900_rent_index
Revises: 2026_07_21_0901_contracts
Create Date: 2026-07-22 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_22_0900_rent_index"
down_revision: Union[str, None] = "2026_07_21_0901_contracts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rent_index_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("property_subtype", sa.String(length=50), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("median_rent", sa.Float(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="rent_index_snapshots_pkey"),
        sa.UniqueConstraint(
            "district", "property_subtype", "bedrooms", "period",
            name="uq_rent_index_snapshots_group_period",
        ),
        sa.CheckConstraint("sample_size >= 0", name="ck_rent_index_snapshots_sample_size"),
        sa.CheckConstraint(
            "source IN ('contracts','listings','blended')",
            name="ck_rent_index_snapshots_source",
        ),
    )
    op.create_index("ix_rent_index_snapshots_district", "rent_index_snapshots", ["district"], unique=False)
    op.create_index("ix_rent_index_snapshots_period", "rent_index_snapshots", ["period"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rent_index_snapshots_period", table_name="rent_index_snapshots")
    op.drop_index("ix_rent_index_snapshots_district", table_name="rent_index_snapshots")
    op.drop_table("rent_index_snapshots")
