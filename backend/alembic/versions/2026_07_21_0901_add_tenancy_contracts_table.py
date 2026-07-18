"""add tenancy_contracts and rental_contract_sequences tables

Phase C of plans/valuadis-rentals/plan.mdx. The registered tenancy contract
from an accepted application, with a per-year registry contract number
(AA-RNT-<year>-<seq>) allocated from rental_contract_sequences under a row
lock. A contract activates only when a matching deposit receipt is recorded
(money evidenced, never held in v1).

Revision ID: 2026_07_21_0901_contracts
Revises: 2026_07_21_0900_rental_apps
Create Date: 2026-07-21 09:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_21_0901_contracts"
down_revision: Union[str, None] = "2026_07_21_0900_rental_apps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rental_contract_sequences",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("year", name="rental_contract_sequences_pkey"),
    )

    op.create_table(
        "tenancy_contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_no", sa.String(length=30), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("monthly_rent", sa.Float(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("deposit_amount", sa.Float(), nullable=False),
        sa.Column("deposit_receipt_ref", sa.String(length=120), nullable=True),
        sa.Column("deposit_paid_on", sa.Date(), nullable=True),
        sa.Column("deposit_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contract_pdf", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["rental_listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_id"], ["rental_applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="tenancy_contracts_pkey"),
        sa.UniqueConstraint("contract_no", name="uq_tenancy_contracts_contract_no"),
        sa.UniqueConstraint("application_id", name="uq_tenancy_contracts_application_id"),
        sa.CheckConstraint(
            "status IN ('draft','active','terminated','expired')",
            name="ck_tenancy_contracts_status",
        ),
        sa.CheckConstraint("deposit_amount > 0", name="ck_tenancy_contracts_deposit_positive"),
        sa.CheckConstraint("end_date > start_date", name="ck_tenancy_contracts_dates"),
    )
    op.create_index("ix_tenancy_contracts_contract_no", "tenancy_contracts", ["contract_no"], unique=True)
    op.create_index("ix_tenancy_contracts_listing_id", "tenancy_contracts", ["listing_id"], unique=False)
    op.create_index("ix_tenancy_contracts_status", "tenancy_contracts", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tenancy_contracts_status", table_name="tenancy_contracts")
    op.drop_index("ix_tenancy_contracts_listing_id", table_name="tenancy_contracts")
    op.drop_index("ix_tenancy_contracts_contract_no", table_name="tenancy_contracts")
    op.drop_table("tenancy_contracts")
    op.drop_table("rental_contract_sequences")
