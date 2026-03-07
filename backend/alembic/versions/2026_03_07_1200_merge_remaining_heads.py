"""merge remaining heads

Revision ID: 2026_03_07_1200_merge
Revises: merge_heads_2026_03_05, 2026_03_05_1000
Create Date: 2026-03-07 12:00:00.000000

"""
from typing import Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2026_03_07_1200_merge'
down_revision: Union[str, tuple] = ('merge_heads_2026_03_05', '2026_03_05_1000')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
