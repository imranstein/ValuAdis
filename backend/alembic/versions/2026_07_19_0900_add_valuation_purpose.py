"""add valuation purpose column

Adds valuations.purpose ('sale' | 'rent', NOT NULL, server default 'sale').
Rent valuations reuse the existing Valuation table and its draft -> pending
-> approved state machine instead of a new table — see
plans/valuadis-rentals/plan.mdx. No backfill needed: existing rows default
to 'sale' via the server default.

A plain String + CHECK constraint is used rather than a native DB enum
type: the existing status/property_type columns use SQLAlchemy's Enum
type, whose storage representation (member name vs. value) differs across
this codebase's SQLite dev path and Postgres prod path. A CHECK constraint
gives the same integrity guarantee without that ambiguity.

Revision ID: 2026_07_19_0900_val_purpose
Revises: 2026_07_12_1600_settings
Create Date: 2026-07-19 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision ids are capped at the alembic_version.version_num varchar(32)
# column width — keep new ids <= 32 chars.
revision: str = "2026_07_19_0900_val_purpose"
down_revision: Union[str, None] = "2026_07_12_1600_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "valuations",
        sa.Column("purpose", sa.String(length=10), nullable=False, server_default="sale"),
    )
    op.create_check_constraint(
        "ck_valuations_purpose",
        "valuations",
        "purpose IN ('sale', 'rent')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_valuations_purpose", "valuations", type_="check")
    op.drop_column("valuations", "purpose")
