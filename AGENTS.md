# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

ValuAdis is an Ethiopian Property & Vehicle Valuation Platform — a monorepo with a FastAPI backend and Nuxt 3 frontend, orchestrated via Docker Compose.

### Services

| Service | Port | Technology |
|---------|------|------------|
| Backend API | 8020 (host) → 8000 (container) | FastAPI (Python 3.11) |
| Frontend | 3020 | Nuxt 3 (Vue 3, Node 20) |
| PostgreSQL + PostGIS | 5433 (host) → 5432 (container) | postgis/postgis:15-3.3 |
| Redis | 6379 | redis:7-alpine |

### Starting Services

All four services run via Docker Compose from the repo root:

```bash
docker compose up -d
```

After first start, you must create the database tables. The Alembic migration chain has conflicts (multiple heads, missing tables). Instead, create tables directly from models:

```bash
docker exec valuadis_backend pip install psycopg2-binary
docker exec valuadis_backend python -c "
from app.core.database import engine, Base
from app.data.models.user import User
from app.data.models.property import Property
from app.data.models.valuation import Valuation
from app.data.models.role import Role, Permission, UserRole
from app.data.models.scraper import ScraperTarget, ScraperLog
from app.data.models.market_listing import RawMarketListing
from app.data.models.valuation_feedback import ValuationFeedback
Base.metadata.create_all(bind=engine)
"
```

**Important:** `psycopg2` / `psycopg2-binary` is not listed in `backend/requirements.txt` but is required for PostgreSQL connections. Install it inside the backend container after `docker compose up`.

### Running Tests

**Backend:** Tests use SQLite (configured in `tests/conftest.py`), so they don't need Docker services. Exclude `test_migration_pipeline.py` (imports a non-existent `get_db_url` function):

```bash
cd backend && source venv/bin/activate
DATABASE_URL=sqlite:///./test.db python -m pytest tests/ --ignore=tests/test_migration_pipeline.py -v
```

Expect ~121 passed, ~33 failed (failures are mostly due to SQLite vs PostgreSQL differences — tests that require PostGIS features or specific PostgreSQL behavior).

**Frontend:** No unit test files exist yet. Lint passes cleanly:

```bash
cd frontend/app && npx eslint .
```

### Gotchas

- **Python version:** Backend requires Python 3.11 (numpy 1.24.4 is incompatible with Python 3.12+). Use `python3.11` from deadsnakes PPA.
- **Frontend build:** `nuxt build` fails due to missing `leaflet.markercluster` dependency (pre-existing). Dev server (`nuxt dev`) works fine.
- **Docker node_modules permissions:** If you install frontend deps locally, the Docker container's anonymous volume for `node_modules` may conflict. Run `sudo rm -rf frontend/app/node_modules` before `npm install` if you hit EACCES errors.
- **Frontend working directory:** The Nuxt app is at `frontend/app/` (not `frontend/`). Run `npm` commands from `frontend/app/`.
- **Swagger docs:** Available at `http://localhost:8020/docs` in development mode.
- **Default `.env`:** Copy `.env.example` to `.env` at repo root and `frontend/app/.env.example` to `frontend/app/.env`. Default passwords are `changeme`.
