"""
Rentals Module Models

The SQLAlchemy model remains registered in app.data.models (shared metadata
and Alembic migrations live there). This module re-exports it as the rentals
module's model surface, mirroring modules/property/models.py.
"""

from app.data.models.rental_application import (
    ACTIVE_APPLICATION_STATUSES,
    RentalApplication,
    RentalApplicationStatus,
)
from app.data.models.rental_listing import RentalListing, RentalListingStatus
from app.data.models.tenancy_contract import (
    RentalContractSequence,
    TenancyContract,
    TenancyContractStatus,
)

__all__ = [
    "RentalListing",
    "RentalListingStatus",
    "RentalApplication",
    "RentalApplicationStatus",
    "ACTIVE_APPLICATION_STATUSES",
    "TenancyContract",
    "TenancyContractStatus",
    "RentalContractSequence",
]
