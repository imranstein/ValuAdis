"""
Redis Configuration

Redis connection and caching for ValuAdis
"""

import redis
from app.core.config import settings

# Create Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)


def get_redis():
    """Dependency to get Redis client"""
    return redis_client
