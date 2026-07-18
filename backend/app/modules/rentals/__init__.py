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
from .application_service import RentalApplicationService
from .contract_service import TenancyContractService
from .repositories import (
    RentalApplicationRepository,
    RentalListingRepository,
    TenancyContractRepository,
)
from .models import (
    RentalApplication,
    RentalApplicationStatus,
    RentalListing,
    RentalListingStatus,
    TenancyContract,
    TenancyContractStatus,
)

__all__ = [
    "rentals_router",
    "RentalListingService",
    "RentalApplicationService",
    "TenancyContractService",
    "RentalListingRepository",
    "RentalApplicationRepository",
    "TenancyContractRepository",
    "RentalListing",
    "RentalListingStatus",
    "RentalApplication",
    "RentalApplicationStatus",
    "TenancyContract",
    "TenancyContractStatus",
]
