"""add rental_applications table

Phase C of plans/valuadis-rentals/plan.mdx. A renter's application to a
published listing; the offered rent is validated server-side against the
listing's frozen band before insert. Accepting one application auto-rejects
siblings and moves the listing to `rented`.

Revision ID: 2026_07_21_0900_rental_apps
Revises: 2026_07_20_0903_fayda_unique
Create Date: 2026-07-21 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_21_0900_rental_apps"
down_revision: Union[str, None] = "2026_07_20_0903_fayda_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rental_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("renter_user_id", sa.Integer(), nullable=False),
        sa.Column("offered_rent", sa.Float(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["rental_listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["renter_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="rental_applications_pkey"),
        sa.CheckConstraint(
            "status IN ('pending','accepted','rejected','withdrawn')",
            name="ck_rental_applications_status",
        ),
        sa.CheckConstraint("offered_rent > 0", name="ck_rental_applications_offered_rent_positive"),
    )
    op.create_index("ix_rental_applications_listing_id", "rental_applications", ["listing_id"], unique=False)
    op.create_index("ix_rental_applications_renter_user_id", "rental_applications", ["renter_user_id"], unique=False)
    op.create_index("ix_rental_applications_status", "rental_applications", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rental_applications_status", table_name="rental_applications")
    op.drop_index("ix_rental_applications_renter_user_id", table_name="rental_applications")
    op.drop_index("ix_rental_applications_listing_id", table_name="rental_applications")
    op.drop_table("rental_applications")
