# ValuAdis Technical Documentation (VA-111)

## Architecture Overview

ValuAdis is an Ethiopian property valuation platform with:

- **Backend**: FastAPI (Python 3.11+), PostgreSQL + PostGIS, Redis
- **Frontend**: Nuxt 3, Vue 3, Pinia, PrimeVue, Tailwind
- **Auth**: JWT (access + refresh tokens), role-based access control

## API Structure

Base URL: `/api/v1`

| Prefix | Description |
|--------|-------------|
| `/auth` | Login, register, refresh, /me |
| `/properties` | CRUD, export, bulk import, custom attributes |
| `/valuations` | CRUD, calculate, override, export |
| `/audit` | Logs, reports, export |
| `/analytics` | Dashboard stats, property types |
| `/health` | ping, database, redis, full |
| `/users` | User management, approval (admin) |
| `/valuation-feedback` | Feedback on valuations |

## Authentication

- **POST**: `/auth/register` – User registration (requires admin approval)
- **POST**: `/auth/login` – Returns `access_token`, `refresh_token`
- **POST**: `/auth/refresh` – Refresh tokens
- **GET**: `/auth/me` – Current user info (Bearer token required)

Header: `Authorization: Bearer <access_token>`

## Database

- **PostgreSQL** with PostGIS extension
- **Models**: users, properties, valuations, audit_logs, roles, permissions
- **Migrations**: Alembic (`backend/alembic`)
- **Spatial**: `properties.boundary` (POLYGON), `valuations.coordinates` (POLYGON)

## Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| AuthService | `app/services/auth_service.py` | Auth, user creation |
| PropertyService | `app/services/property_service.py` | Properties, bulk import |
| ValuationService | `app/services/valuation_service.py` | Valuations, override |
| NotificationService | `app/services/notification_service.py` | Email, SMS (placeholder) |
| AuditService | `app/services/audit_service.py` | Audit logging |

## Configuration

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection |
| `REDIS_URL` | Redis URL |
| `SECRET_KEY` | JWT signing |
| `NOTIFICATIONS_ENABLED` | Enable email notifications |
| `SMTP_*` | SMTP for email |

## Deployment

- **Docker**: `docker-compose.yml` (dev), `docker-compose.prod.yml` (prod)
- **Backup**: `scripts/backup.sh`, `scripts/verify_backup.sh`
- **Docs**: `docs/DB_BACKUP_STRATEGY.md`, `docs/MONITORING_LOGGING.md`, `docs/NOTIFICATIONS.md`
