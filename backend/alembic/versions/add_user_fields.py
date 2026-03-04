"""add user admin and valuer fields

Revision ID: add_user_fields
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 11:38:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_fields'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin and is_valuer columns to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_valuer', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_admin and is_valuer columns
    op.drop_column('users', 'is_valuer')
    op.drop_column('users', 'is_admin')
