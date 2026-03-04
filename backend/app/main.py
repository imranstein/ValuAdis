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
from starlette.middleware.base import BaseHTTPMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import ValuAdisException
from app.core.sentry import init_sentry, get_sentry_manager


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP-recommended security headers to every response."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response


# ---------------------------------------------------------------------------
# Initialize Sentry
# ---------------------------------------------------------------------------

init_sentry()
sentry_manager = get_sentry_manager()

# ---------------------------------------------------------------------------
# FastAPI app
# Swagger / ReDoc are only enabled in development.
# ---------------------------------------------------------------------------

_is_dev = settings.ENVIRONMENT == "development"

app = FastAPI(
    title="ValuAdis API",
    description="Ethiopian Property Valuation Platform API with PostGIS spatial support",
    version="1.0.0",
    docs_url="/docs" if _is_dev else None,
    redoc_url="/redoc" if _is_dev else None,
    openapi_url="/openapi.json" if _is_dev else None,
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

# ---------------------------------------------------------------------------
# Middleware (order matters: added last = runs first)
# ---------------------------------------------------------------------------

# Security headers on all responses
app.add_middleware(SecurityHeadersMiddleware)

# CORS — restrict to known allowed origins, specific methods and headers only
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(ValuAdisException)
async def valuadis_exception_handler(request: Request, exc: ValuAdisException):
    """Handle ValuAdis-specific exceptions"""
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc)}
    )


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "valuadis-backend",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ValuAdis API - Ethiopian Property Valuation Platform",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=_is_dev,
    )
