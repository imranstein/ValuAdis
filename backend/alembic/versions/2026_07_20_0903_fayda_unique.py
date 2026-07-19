"""unique index on users.fayda_id_number

The signup flow checks Fayda uniqueness before insert, but without a DB
constraint two concurrent signups can both pass the check. The index is
the actual guarantee; NULLs stay allowed (existing valuer accounts have
no Fayda ID).

Revision ID: 2026_07_20_0903_fayda_unique
Revises: 2026_07_20_0902_rental_roles
"""

from typing import Sequence, Union

from alembic import op

revision: str = "2026_07_20_0903_fayda_unique"
down_revision: Union[str, None] = "2026_07_20_0902_rental_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_NAME = "uq_users_fayda_id_number"


def upgrade() -> None:
    op.create_index(INDEX_NAME, "users", ["fayda_id_number"], unique=True)


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name="users")
