"""VA-119: User feedback system

Revision ID: 2026_03_07_1430
Revises: 2026_03_07_1420
Create Date: 2026-03-07 14:30:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision = '2026_03_07_1430'
down_revision = '2026_03_07_1420'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('page', sa.String(200), nullable=True),
        sa.Column('context', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_feedback_user_id', 'user_feedback', ['user_id'])
    op.create_index('idx_user_feedback_created_at', 'user_feedback', ['created_at'])


def downgrade() -> None:
    op.drop_table('user_feedback')
