"""index valuations.purpose

Separate migration for the index per the project's migration hygiene rule
(indexes are added in their own migration, not bundled with the column
add, so either can be rolled back independently).

Revision ID: 2026_07_19_0901_val_purpose_ix
Revises: 2026_07_19_0900_val_purpose
Create Date: 2026-07-19 09:01:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "2026_07_19_0901_val_purpose_ix"
down_revision: Union[str, None] = "2026_07_19_0900_val_purpose"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_valuations_purpose", "valuations", ["purpose"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_valuations_purpose", table_name="valuations")
