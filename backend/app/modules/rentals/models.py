"""
Rentals Module Models

The SQLAlchemy model remains registered in app.data.models (shared metadata
and Alembic migrations live there). This module re-exports it as the rentals
module's model surface, mirroring modules/property/models.py.
"""

from app.data.models.rental_listing import RentalListing, RentalListingStatus

__all__ = ["RentalListing", "RentalListingStatus"]
