"""
ValuAdis API v1 Router

Main API router for Ethiopian Property Valuation Platform
"""

from fastapi import APIRouter

# Import all endpoint routers
from app.api.v1.endpoints import health, scrapers, vehicle_data
from app.api.v1.endpoints import validation
from app.modules.property import property_router
from app.modules.vehicle import vehicle_router
from app.modules.valuation import valuation_router, valuation_feedback_router
from app.modules.analytics import analytics_router
from app.modules.audit import audit_router
from app.modules.auth import auth_router
from app.modules.users import users_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    property_router,
    prefix="/properties",
    tags=["Properties"]
)

api_router.include_router(
    valuation_router,
    prefix="/valuations",
    tags=["Valuations"]
)

api_router.include_router(
    audit_router,
    prefix="/audit",
    tags=["Audit"]
)

api_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    scrapers.router,
    prefix="/scrapers",
    tags=["Scrapers"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    valuation_feedback_router,
    prefix="/valuation-feedback",
    tags=["Valuation Feedback"],
)

# vehicle_router already has prefix="/vehicles" defined internally
api_router.include_router(vehicle_router)
api_router.include_router(vehicle_data.router)

api_router.include_router(
    validation.router,
    prefix="/validate",
    tags=["Validation"]
)
