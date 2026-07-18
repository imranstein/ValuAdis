"""
Rentals Module

Government-mediated rental registry (plans/valuadis-rentals/plan.mdx).
Phase B scope: owner listing registration with auto rent valuation, the
officer review/publish queue, and public PII-redacted browse. The
SQLAlchemy model stays registered in app.data.models (shared metadata and
Alembic migrations) and is re-exported via .models.
"""

from .routes import router as rentals_router
from .services import RentalListingService
from .repositories import RentalListingRepository
from .models import RentalListing, RentalListingStatus

__all__ = [
    "rentals_router",
    "RentalListingService",
    "RentalListingRepository",
    "RentalListing",
    "RentalListingStatus",
]
