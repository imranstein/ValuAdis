"""
Health Check Endpoints

Monitoring and health check endpoints for ValuAdis API
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import settings
import redis

router = APIRouter()


@router.get("", tags=["Health"])
async def api_health():
    """API-scoped health endpoint."""
    return {
        "status": "healthy",
        "service": "valuadis-api",
        "version": settings.VERSION if hasattr(settings, "VERSION") else "1.0.0",
    }


@router.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint"""
    return {"status": "pong", "service": "valuadis-api"}


@router.get("/database", tags=["Health"])
async def check_database(db: Session = Depends(get_db)):
    """Check database connection"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "postgresql"}
    except Exception:
        # Suppress error details — don't leak connection info
        return {"status": "unhealthy", "service": "postgresql"}


@router.get("/redis", tags=["Health"])
async def check_redis(redis_client = Depends(get_redis)):
    """Check Redis connection"""
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "service": "redis",
            "message": "Redis connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "redis",
            "message": f"Redis connection failed: {str(e)}"
        }


@router.get("/full", tags=["Health"])
async def full_health_check(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Complete health check of all services"""
    checks = {}
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception:
        checks["database"] = {"status": "unhealthy"}
    
    # Redis check
    try:
        redis_client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception:
        checks["redis"] = {"status": "unhealthy"}
    
    # Overall status
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "service": "valuadis-api",
        "checks": checks
    }


@router.get("/detailed", tags=["Health"])
async def detailed_health_check(db: Session = Depends(get_db)):
    """Deploy smoke-test probe: DB ping, migration state (current vs head), version.

    Used by scripts/deploy smoke checks to confirm a deployment is live AND
    on the expected schema in a single request.
    """
    version = settings.VERSION if hasattr(settings, "VERSION") else "1.0.0"

    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    current_rev = None
    try:
        row = db.execute(text("SELECT version_num FROM alembic_version")).fetchone()
        current_rev = row[0] if row else None
    except Exception:
        current_rev = None

    head_rev = None
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        alembic_cfg = Config("alembic.ini")
        head_rev = ScriptDirectory.from_config(alembic_cfg).get_current_head()
    except Exception:
        head_rev = None

    migrations_ok = bool(current_rev and head_rev and current_rev == head_rev)
    healthy = db_ok and migrations_ok

    return {
        "status": "healthy" if healthy else "unhealthy",
        "service": "valuadis-api",
        "version": version,
        "checks": {
            "database": {"status": "healthy" if db_ok else "unhealthy"},
            "migrations": {
                "status": "healthy" if migrations_ok else "unhealthy",
                "current": current_rev,
                "head": head_rev,
            },
        },
    }


@router.get("/ready", tags=["Health"])
async def readiness_check(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Readiness check for orchestrators and deployment checks."""
    checks = {}

    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception:
        checks["database"] = {"status": "unhealthy"}

    try:
        redis_client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as exc:
        checks["redis"] = {"status": "unhealthy", "error": str(exc)}

    all_ready = all(item["status"] == "healthy" for item in checks.values())

    return {
        "status": "ready" if all_ready else "not ready",
        "service": "valuadis-api",
        "checks": checks,
    }


@router.get("/live", tags=["Health"])
async def liveness_check():
    """Liveness check for container and platform health."""
    return {"status": "alive", "service": "valuadis-api"}
