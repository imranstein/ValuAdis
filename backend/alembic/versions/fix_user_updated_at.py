"""fix user updated_at default value

Revision ID: fix_user_updated_at
Revises: add_user_fields
Create Date: 2026-03-03 11:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_user_updated_at'
down_revision = 'add_user_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add server_default to updated_at column
    op.alter_column('users', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'),
                   existing_nullable=False)


def downgrade() -> None:
    # Remove server_default from updated_at column
    op.alter_column('users', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=None,
                   existing_nullable=False)
