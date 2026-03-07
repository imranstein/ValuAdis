"""
ValuAdis API v1 Router

Main API router for Ethiopian Property Valuation Platform
"""

from fastapi import APIRouter

# Import all endpoint routers
from app.api.v1.endpoints import auth, properties, health, valuations, audit, analytics, scrapers, users
from app.api.v1.endpoints import valuation_feedback, feedback
# from app.modules.vehicle.routes import router as vehicle_router  # Temporarily disabled

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    properties.router,
    prefix="/properties",
    tags=["Properties"]
)

api_router.include_router(
    valuations.router,
    prefix="/valuations",
    tags=["Valuations"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["Audit"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    scrapers.router,
    prefix="/scrapers",
    tags=["Scrapers"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    valuation_feedback.router,
    prefix="/valuation-feedback",
    tags=["Valuation Feedback"],
)

api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Feedback"],
)

# Temporarily disabled vehicle module
# api_router.include_router(
#     vehicle_router,
#     prefix="/vehicles",
#     tags=["Vehicles"]
# )
