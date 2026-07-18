"""add rental_renewal_cap_configs table

Phase D of plans/valuadis-rentals/plan.mdx. The legal renewal rent-increase
cap (11.5% for the Addis Ababa 2026/27 directive under Proclamation
1320/2024) as a configured value with an effective period, mirroring the
district_rent_ratios seeded-config pattern from Phase A. Schema only — the
initial directive row is inserted by the dedicated seeder script
(app.data.seeders.renewal_cap_seeder), not by this migration, per the
project's "no production data in migrations" rule. RenewalCapService falls
back to a documented in-code default when no config row is seeded yet.

Revision ID: 2026_07_22_0901_renewal_cap
Revises: 2026_07_22_0900_rent_index
Create Date: 2026-07-22 09:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_22_0901_renewal_cap"
down_revision: Union[str, None] = "2026_07_22_0900_rent_index"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rental_renewal_cap_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False, server_default="Addis Ababa"),
        sa.Column("cap_pct", sa.Float(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.Column("directive_reference", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="rental_renewal_cap_configs_pkey"),
        sa.CheckConstraint("cap_pct >= 0", name="ck_renewal_cap_configs_cap_pct_non_negative"),
        sa.CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="ck_renewal_cap_configs_period",
        ),
    )
    op.create_index(
        "ix_renewal_cap_configs_effective_from", "rental_renewal_cap_configs", ["effective_from"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_renewal_cap_configs_effective_from", table_name="rental_renewal_cap_configs")
    op.drop_table("rental_renewal_cap_configs")
