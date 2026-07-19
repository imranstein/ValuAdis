"""add property_photos table

Real property photo upload for citizen + staff (dev-completion task). Photos
are stored on local disk under settings.MEDIA_ROOT; only server-generated
filenames and byte metadata live in this table, never a client-supplied
filename or filesystem path. `position` orders a property's gallery.

Revision ID: 2026_07_23_0900_property_photos
Revises: 2026_07_22_0901_renewal_cap
Create Date: 2026-07-23 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_23_0900_property_photos"
down_revision: Union[str, None] = "2026_07_22_0901_renewal_cap"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "property_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="property_photos_pkey"),
        sa.CheckConstraint("byte_size > 0", name="ck_property_photos_byte_size_positive"),
    )
    op.create_index("ix_property_photos_property_id", "property_photos", ["property_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_property_photos_property_id", table_name="property_photos")
    op.drop_table("property_photos")
