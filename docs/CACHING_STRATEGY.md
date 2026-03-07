# ValuAdis Caching Strategy (VA-116)

## Overview

Redis is used for caching to reduce database load and improve response times.

## Cached Endpoints

| Endpoint | TTL | Key Pattern |
|----------|-----|-------------|
| `GET /analytics/dashboard` | 5 min | `analytics:dashboard:{user_id}:{period}:{municipality}:{property_type}` |

## Cache Manager

- **Location**: `app/core/performance.py`
- **Methods**: `get`, `set`, `delete`, `clear_pattern`
- **Decorator**: `@cache_result(key_prefix, ttl)` for sync functions

## Configuration

- `REDIS_URL` – Redis connection string
- Cache is optional: if Redis is unavailable, endpoints run without cache

## Invalidation

- Use `clear_cache_pattern("analytics:*")` to invalidate analytics cache
- TTL-based expiry (no manual invalidation for dashboard)
