"""add raw_market_listings.listing_type

Adds a 'sale' | 'rent' tag to scraped listings so the rent valuation
engine's direct-comps method can filter for rental asking prices once the
scraper is extended to capture them (out of scope for this migration —
see plans/valuadis-rentals/tasks/phase-a.md). All existing rows default to
'sale', matching how they have always been used (sale-price comps in
app/modules/property/routes.py).

Revision ID: 2026_07_19_0902_listing_type
Revises: 2026_07_19_0901_val_purpose_ix
Create Date: 2026-07-19 09:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_07_19_0902_listing_type"
down_revision: Union[str, None] = "2026_07_19_0901_val_purpose_ix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "raw_market_listings",
        sa.Column("listing_type", sa.String(length=10), nullable=False, server_default="sale"),
    )
    op.create_check_constraint(
        "ck_raw_market_listings_listing_type",
        "raw_market_listings",
        "listing_type IN ('sale', 'rent')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_raw_market_listings_listing_type", "raw_market_listings", type_="check")
    op.drop_column("raw_market_listings", "listing_type")
