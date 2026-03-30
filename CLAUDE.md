# ValuAdis Project Instructions

## Commands

Frontend (Nuxt 3):
```bash
cd frontend/app
npm run dev              # start dev server (localhost:3000)
npm run build            # build for production
npm test                 # run Vitest unit tests
npm test -- path/to/file # run single test file
npm run test:e2e         # run Playwright E2E tests
npm run lint             # check ESLint
npm run lint:fix         # auto-fix style
npm run typecheck        # TypeScript check
```

Backend (FastAPI):
```bash
cd backend
python -m pytest         # run all tests
python -m pytest path/to/file # run single test file
python -m uvicorn app.main:app --reload  # dev server (localhost:8000)
```

## Architecture

**Frontend** (`frontend/app/` — Nuxt 3 + Vue 3 + TypeScript):
- `pages/` — file-based routing (Nuxt auto-routes)
- `components/` — reusable Vue components
- `composables/` — Vue 3 composition API utilities
- `layouts/` — page templates
- `middleware/` — route guards and auth

**Backend** (`backend/app/` — FastAPI + Python):
- `api/v1/endpoints/` — REST routes (versioned API)
- `services/` — business logic and state machines
- `schemas/` — Pydantic models (request/response validation)
- `data/models/` — SQLAlchemy models (database)
- `core/` — auth, config, dependencies

**Testing**:
- `frontend/tests/e2e/` — Playwright E2E (flows, performance, security)
- `backend/tests/` — pytest unit/integration tests
- `.planning/` — testing standards and runbooks

## Workflow

- Always run `npm run typecheck` in frontend after making TypeScript changes
- Run single test file (`npm test -- file.spec.ts`) for fast feedback, not full suite
- E2E tests validate real workflows end-to-end; unit tests validate isolated logic
- Use `.tmp/tasks/` subtask JSON files for complex features (see .planning/parraleltask.md)

## Don'ts

- Don't modify `.nuxt/`, `.output/`, `node_modules/`, or `__pycache__/`
- Don't modify generated files (`*.gen.ts`, `*.generated.*`)
- Don't commit `CLAUDE.local.md` (use it for local overrides)
