"""seed rentals module roles

Inserts the three rentals roles (property_owner, renter, rental_officer)
into the existing roles table, per plans/valuadis-rentals/plan.mdx Phase B.
Inserts are guarded with NOT EXISTS so re-running against a database that
already has any of these roles (e.g. created at runtime by the citizen
signup get-or-create path) is safe.

Revision ID: 2026_07_20_0902_rental_roles
Revises: 2026_07_20_0901_rental_listings
Create Date: 2026-07-20 09:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_20_0902_rental_roles"
down_revision: Union[str, None] = "2026_07_20_0901_rental_listings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RENTAL_ROLES = [
    ("property_owner", "Property Owner", "Citizen who lists properties on the rental registry"),
    ("renter", "Renter", "Citizen who browses and applies to rental listings"),
    ("rental_officer", "Rental Officer", "Sub-city housing officer who verifies and publishes rental listings"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for name, display_name, description in RENTAL_ROLES:
        conn.execute(
            sa.text(
                """
                INSERT INTO roles (name, display_name, description, is_active)
                SELECT :name, :display_name, :description, TRUE
                WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = :name)
                """
            ),
            {"name": name, "display_name": display_name, "description": description},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for name, _, _ in RENTAL_ROLES:
        conn.execute(sa.text("DELETE FROM roles WHERE name = :name"), {"name": name})
