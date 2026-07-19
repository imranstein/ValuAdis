"""add rental_listings table

New table for Phase B (listings + public browse) of
plans/valuadis-rentals/plan.mdx. A rental listing wraps an existing
property + an auto-generated rent Valuation (purpose='rent', added in
Phase A) with a frozen suggested-rent band, officer review status, and a
server-generated public_id used everywhere instead of the integer PK.

Revision ID: 2026_07_20_0901_rental_listings
Revises: 2026_07_20_0900_user_rental
Create Date: 2026-07-20 09:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_20_0901_rental_listings"
down_revision: Union[str, None] = "2026_07_20_0900_user_rental"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rental_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.String(length=20), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("valuation_id", sa.Integer(), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("suggested_rent", sa.Float(), nullable=False),
        sa.Column("band_min", sa.Float(), nullable=False),
        sa.Column("band_max", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("requires_officer_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending_review"),
        sa.Column("listing_agreement_pdf", sa.String(length=500), nullable=True),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["valuation_id"], ["valuations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="rental_listings_pkey"),
        sa.UniqueConstraint("public_id", name="uq_rental_listings_public_id"),
        sa.CheckConstraint(
            "status IN ('draft','pending_review','published','rented','withdrawn')",
            name="ck_rental_listings_status",
        ),
    )
    op.create_index("ix_rental_listings_public_id", "rental_listings", ["public_id"], unique=True)
    op.create_index("ix_rental_listings_property_id", "rental_listings", ["property_id"], unique=False)
    op.create_index("ix_rental_listings_owner_user_id", "rental_listings", ["owner_user_id"], unique=False)
    op.create_index("ix_rental_listings_status", "rental_listings", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rental_listings_status", table_name="rental_listings")
    op.drop_index("ix_rental_listings_owner_user_id", table_name="rental_listings")
    op.drop_index("ix_rental_listings_property_id", table_name="rental_listings")
    op.drop_index("ix_rental_listings_public_id", table_name="rental_listings")
    op.drop_table("rental_listings")
