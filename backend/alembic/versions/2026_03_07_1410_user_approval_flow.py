"""VA-118: User registration approval flow

Revision ID: 2026_03_07_1410
Revises: 2026_03_07_1400
Create Date: 2026-03-07 14:10:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision = '2026_03_07_1410'
down_revision = '2026_03_07_1400'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # New users default to pending; existing users remain approved via server_default for migration
    op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    op.create_index('idx_users_is_approved', 'users', ['is_approved'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_users_is_approved', table_name='users')
    op.drop_column('users', 'is_approved')
