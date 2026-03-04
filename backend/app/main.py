"""
ValuAdis FastAPI Main Application

Ethiopian Property Valuation Platform Backend
- FastAPI 0.104+
- PostgreSQL + PostGIS
- Redis caching
- JWT Authentication
- M-Pesa Integration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import ValuAdisException
from app.core.sentry import init_sentry, get_sentry_manager

# Initialize Sentry
init_sentry()
sentry_manager = get_sentry_manager()

# Create FastAPI application
app = FastAPI(
    title="ValuAdis API",
    description="Ethiopian Property Valuation Platform API with PostGIS spatial support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "JWT authentication for Ethiopian property valuers"
        },
        {
            "name": "Properties",
            "description": "Property management with spatial data support"
        },
        {
            "name": "Valuations",
            "description": "Ethiopian property valuation calculations and management"
        },
        {
            "name": "Health",
            "description": "System health and monitoring endpoints"
        }
    ],
    contact={
        "name": "ValuAdis Support",
        "email": "support@valuadis.et",
        "url": "https://valuadis.et"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(ValuAdisException)
async def valuadis_exception_handler(request: Request, exc: ValuAdisException):
    """Handle ValuAdis-specific exceptions"""
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc)}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "valuadis-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ValuAdis API - Ethiopian Property Valuation Platform",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "Documentation not available",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
