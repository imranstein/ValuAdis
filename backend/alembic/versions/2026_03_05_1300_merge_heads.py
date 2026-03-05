"""Merge parallel migration heads into a single linear chain.

HEAD 1: a1b2c3d4e5f6 (extend_property_add_feedback, via 2026_03_03_1000)
HEAD 2: fix_user_updated_at (add_user_fields branch, forked from d4e5f6a7b8c9)

Revision ID: merge_heads_2026_03_05
Revises: a1b2c3d4e5f6, fix_user_updated_at
Create Date: 2026-03-05 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'merge_heads_2026_03_05'
down_revision: Union[str, tuple] = ('a1b2c3d4e5f6', 'fix_user_updated_at')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merge migration — no schema changes needed.
    # This simply rejoins two parallel migration branches into one head
    # so that `alembic upgrade head` works without the multiple-heads error.
    pass


def downgrade() -> None:
    pass
