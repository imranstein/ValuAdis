"""
Health Check Endpoints

Monitoring and health check endpoints for ValuAdis API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import get_redis
import redis

router = APIRouter()


@router.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint"""
    return {"status": "pong", "service": "valuadis-api"}


@router.get("/database", tags=["Health"])
async def check_database(db: Session = Depends(get_db)):
    """Check database connection"""
    try:
        # Execute simple query to test connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "postgresql",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "postgresql",
            "message": f"Database connection failed: {str(e)}"
        }


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
        db.execute("SELECT 1")
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis check
    try:
        redis_client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "service": "valuadis-api",
        "checks": checks
    }
