# ValuAdis Monitoring & Logging (VA-85)

## Overview

Sentry is configured for error tracking and application monitoring in production.

## Backend (FastAPI)

- **Location**: `backend/app/core/sentry.py`
- **Integrations**: FastAPI, Starlette, SQLAlchemy, Redis, Logging
- **Environment**: Enabled when `SENTRY_DSN` is set and `ENVIRONMENT != "development"`
- **Exclusions**: `/health`, `/metrics`, `/favicon.ico` (no error reporting for health checks)

### Configuration

Set in production `.env`:

```
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
ENVIRONMENT=production
```

## Frontend (Nuxt)

- **Environment variable**: `NUXT_PUBLIC_SENTRY_DSN`
- Configure in `docker-compose.prod.yml` or deployment env

## Structured Logging

- **Backend**: structlog for request/audit logging
- **Audit**: AuditService logs valuation and user actions

## Health Checks

- `GET /health` - Basic liveness
- `GET /api/v1/health/ping` - API ping
- `GET /api/v1/health/database` - PostgreSQL connectivity
- `GET /api/v1/health/redis` - Redis connectivity
- `GET /api/v1/health/full` - Full system health

Use these for load balancer health checks and monitoring dashboards.
