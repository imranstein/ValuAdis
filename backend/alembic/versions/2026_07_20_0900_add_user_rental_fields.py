"""add fayda_id_number and owner_verified to users

Citizen self-registration (renters and property owners) per
plans/valuadis-rentals/plan.mdx Phase B: registration captures a Fayda ID
number, and a property_owner account must be verified by a rental_officer
before their first listing can publish (see rental_listings.status gating
in app/modules/rentals/services.py).

Revision ID: 2026_07_20_0900_user_rental
Revises: 2026_07_19_0903_rent_ratios
Create Date: 2026-07-20 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_20_0900_user_rental"
down_revision: Union[str, None] = "2026_07_19_0903_rent_ratios"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("fayda_id_number", sa.String(length=50), nullable=True))
    op.add_column(
        "users",
        sa.Column("owner_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("users", sa.Column("owner_verified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "owner_verified_at")
    op.drop_column("users", "owner_verified")
    op.drop_column("users", "fayda_id_number")
