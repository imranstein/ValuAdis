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

## Session Learnings

### 2026-05-17

- Vehicle statistics routes must be declared before `/{vehicle_id}` in FastAPI; otherwise `/api/v1/vehicles/statistics/summary` is parsed as a vehicle id and fails before the handler runs.
- Public landing imagery should be project-local under `frontend/app/public/images/`; generated assets in `~/.codex/generated_images` are not deployable dependencies.
- Browser proof for pre-production should distinguish real backend rows from static UI examples. `/vehicles` now shows backend counts and the seeded VIN instead of fake portfolio totals.
- The seeded admin account may have `is_admin=True` with no role rows. Admin-only backend gates should honor the flag, not only role names.
- The in-app Browser can lose protected-route proof when its token expires; if storage/input automation is blocked, keep the distinction clear between API proof and authenticated Browser proof.
- Raw-SQL endpoints still need matching ORM metadata when SQLite dev schema is created from `Base.metadata`; `/api/v1/audit/logs` depends on `AuditLog` being imported through `app.data.models`.
- Profile/account pages should use `/api/v1/auth/me` and audit activity from `/api/v1/audit/logs`; do not leave invented names, activity history, or valuation counts in protected app pages.
- Compliance report UI should read `/api/v1/audit/compliance` directly. Keep service keys matched to `ComplianceReportResponse`, and normalize SQLite numeric/date values before returning the report.
- Local SQLite development databases can miss newer ORM tables while tests still pass against the fresh test database. Keep the dev-only schema sync active for SQLite and verify live endpoints after schema changes.
- Frontend API calls should use `runtimeConfig.public.apiBaseUrl` and the `valuadis_token` key consistently.
- Pinia stores and nested components are part of the same API contract; avoid `import.meta.env.VITE_API_BASE` there too.
- Quick valuation select values must match backend valuation service keys exactly, especially `Addis Ababa` and neighborhood quality values like `prime` and `developing`.
- The AI automation dashboard should stay connected to real backend services: valuation-feedback trust metrics and analytics market insights.
- Production Nuxt builds must be fail-closed: `npm run build` requires a non-local `NUXT_PUBLIC_API_BASE_URL`; use `npm run typecheck` for config-neutral type checking.
- Root `pytest -q` is intentionally scoped by `pytest.ini` to the maintained backend suites. Old ad-hoc scripts under `backend/test_*.py` are not release-confidence tests.
- App-shell identity fallbacks must stay neutral. Do not show invented admin names, admin emails, or fabricated notifications when token payload/user APIs do not provide them.
- Dashboard recent valuation tables must use `/api/v1/valuations/` or an honest empty/error state; do not ship hard-coded `VAL-*` sample records in protected routes.
- Settings controls for email delivery and API keys are local draft-only until backend settings/key-management endpoints exist. Label that explicitly instead of pretending values are production-backed.
- Protected analytics pages should use the shared admin shell. Avoid standalone duplicate navigation, fake analyst identities, Material Symbols-only shells, and footer/legal links inside authenticated app pages.
- `/valuations` and `/reports` are now shared-shell routes. Keep them that way; do not reintroduce duplicate sidebars, standalone footers, Material Symbols route chrome, fake operator identities, or links to missing detail pages.
- Chrome proof is possible through Computer Use even when the dedicated Chrome plugin is not exposed. Keep it distinct from in-app Browser proof if the user requested both.
- `/map` is now a backend-backed route using `/api/v1/properties`; keep it free of seed asset records and keep `/map/test` deleted.
- Nuxt page transitions can keep stale route bodies mounted if the page is not keyed. `app.vue` keys `NuxtPage` by `route.fullPath`; keep that guard unless the routing architecture changes.
- The legacy `components/map/PropertyMap.vue` must not fall back to `seedProperties`; empty input should remain empty so protected surfaces do not silently show fake assets.
- `/scrapers` should remain a restrained data-operations surface. Do not reintroduce emoji headers, page-load success toasts, or fake scraper rows; keep it tied to `scraperService` backend endpoints.
- Vehicle edit flows intentionally reuse `/vehicles/create?vehicle_id=...`; keep list/detail edit actions on that route unless a dedicated edit page is actually added. Vehicle detail valuation loading belongs on `/api/v1/vehicles/{id}/valuations`, not the property valuation list endpoint.
- The local demo login is only for local/dev proof and currently matches the running backend seed as `admin@valuadis.com` / `admin123`; do not expose or rely on demo credentials for production builds.
- Vehicle brand/model selection depends on `/api/v1/vehicle-data/*`. Keep that router mounted and keep the local fallback makes/models so the vehicle form still works when NHTSA is unavailable.
- Protected production UI should not leave `console.log` or blocking `alert()` handlers in user workflows. Use real downloads, inline validation, emitted component events, or honest disabled/empty states.
- Production deployment must run `bash scripts/validate-production-env.sh .env.production` before compose/cPanel deploy. `.env.production` and `.env.cpanel.template` are templates; real domains, secrets, database host, Redis host, and strict CORS origins are still externally supplied values.
- Valuation geometry helpers are expected to return real spatial output. `get_coordinates_wkt()` and `get_coordinates_geojson()` now support WKT/EWKT strings and GeoAlchemy values; keep regression coverage when touching spatial model behavior.
- Feedback relationships are active again between `Property`, `Valuation`, and `ValuationFeedback`. Do not disable relationship wiring to dodge metadata errors; fix model registration/import issues instead.
- Full backend release-confidence proof after this cleanup is `214 passed, 17 skipped`; the old duplicate vehicle metadata collection blocker is no longer present in the maintained backend suite.
- Frontend vehicle-data calls must include the mounted API prefix: `/api/v1/vehicle-data/*`. The shared axios service already returns the response body, so `vehicleDataService.js` should not read a second `.data` property.
- Property detail should stay as a self-contained dossier surface, not a stack of oversized generic cards. Keep the restrained hero, summary strip, map, valuation history, and download actions aligned to real backend property fields.
- Quick valuation property prefill must normalize backend subtype/type values into select-compatible valuation categories. Backend data like `villa` should map to `single_family`, and missing valuation assumptions should default to values accepted by the backend service.
- Audit report endpoints expose sensitive operational and compliance data. Keep `/api/v1/audit/system`, `/compliance`, `/summary`, `/metrics`, `/export/*`, and `/schedule` behind `get_current_user_id`; frontend audit/report pages must send the bearer token explicitly.
- Valuation preview and AI trust metrics are protected application data. Keep `/api/v1/valuations/quick`, `/api/v1/valuations/calculate`, and `/api/v1/valuation-feedback/metrics` authenticated, and keep dashboard/property wizard/property detail callers sending bearer tokens.
- `NUXT_PUBLIC_API_BASE_URL` must be the deployed API origin only. Frontend callers append `/api/v1`, so production templates, validators, and Nuxt production builds should reject values that already end in `/api` or `/api/v1`.
- Valuation certificate generation requires an approved valuation. The release happy path must create the valuation, transition draft to pending to approved, then request `/api/v1/valuations/{id}/certificate`.
- Do not reintroduce the old `backend/app/api/v1/endpoints/reports.py` path without replacing it with a property/valuation implementation. Active report downloads are valuation certificates, valuation CSV export, property CSV export, and audit compliance export.
- Keep settings honest until backend settings/key-management endpoints exist. The active `/settings` page is local-draft only; do not reintroduce components that post to `/api/v1/settings` unless that backend contract is implemented and tested.
- Keep legacy vehicle aliases as redirects unless they are rebuilt into the same shared-shell experience. `/vehicles/list` should route to `/vehicles`, and `/vehicles/register` should route to `/vehicles/create` with query params preserved.
- Public pages should not present exact-looking operational metrics unless they are backend-backed or clearly marked as product capability language. Demo login must not expose or hard-code local seed credentials; use explicit local env values only.
- Route-local toolbar styles are required when a page uses `.registry-toolbar`, `.search-field`, and `.filter-select`. Do not rely on scoped styles from another route; `/vehicles` previously collapsed its filter controls until it owned those styles directly.
- `/api/v1/audit/logs` must not hard-fail protected UI pages when a local/dev database is missing `audit_logs`; return an authenticated empty ledger and keep the real migration gap visible as deployment work. The Docker DB can have existing tables with no Alembic version, so `alembic current` alone is not proof of release migration health.
- Deployment must fail early when a database has ValuAdis application tables but no `alembic_version`; do not run `alembic upgrade head` into that partial state because it will hit duplicate baseline tables. Use a controlled baseline/stamp procedure or a fresh database, then verify current revision equals Alembic head.
- `scripts/check-migration-state.sh` is the reusable guard for migration state. Keep `scripts/deploy.sh` using it for both pre-upgrade partial-schema detection and post-upgrade current-vs-head verification.
- Fresh database migration proof should include `audit_logs`; the current head is `2026_05_18_1200_audit_logs`. A dirty local Docker app DB may still have no Alembic version, but a fresh DB migration chain now reaches head and creates the audit table.
- Latest backend happy-path proof used property `27` and valuation `23`; valuation `23` was approved and generated a certificate PDF plus valuations CSV export. Do not claim full browser happy-path completion until visible browser automation succeeds on the same chain.
- Chrome visible proof for the same happy-path records now covers `/login#demo`, `/dashboard`, `/valuations`, `/properties/27`, `/reports`, and `/valuations/quick?property_id=27`. It proves the created/approved records are visible across the app, but it is not the same as form-click E2E proof through the unavailable in-app Browser plugin.
- If the Nuxt preview turns blank after a build, restart the Node preview server before debugging route code. Rebuilding `.output` while `node .output/server/index.mjs` is still running can leave the server with a stale manifest and blank hard-loads.
- Use `backend/venv/bin/python -m pytest -q` for full backend release confidence on this machine. System Python currently fails before collection because it does not have `shapely`, while the project venv passes the maintained suite.

### 2026-07-15

- The refresh cookie path is `/api/v1/auth` (widened from `/api/v1/auth/refresh`) so browser logout can revoke server-side. Logout/rotation denylist the refresh jti via `backend/app/core/token_denylist.py` (Redis, in-process fallback); reusing a rotated or logged-out refresh token returns 401.
- `verify_password` is bcrypt-only and fails closed — no plaintext or SHA-256 fallback. Non-bcrypt stored hashes can no longer log in.
- Admin bootstrap scripts (`create_admin.py`, `backend/create_admin.py`, `backend/create_fresh_admin.py`) require `ADMIN_PASSWORD` (and accept `ADMIN_EMAIL`) from the environment; there are no hardcoded credentials anywhere.
- Frontend error reporting is `plugins/sentry.client.ts` — a zero-dependency Sentry envelope-API reporter gated on `NUXT_PUBLIC_SENTRY_DSN` (npm registry was unreachable when @sentry/vue was attempted; swap in the SDK if breadcrumbs/tracing are ever needed). Root `error.vue` exists and uses the civic-ledger tokens.
- Mobile application id is `com.valuadis.app` on both platforms (was `com.example.valuadis` — old `adb run-as com.example.valuadis` debug commands must use the new id). Android release builds use the `android/key.properties` signing pattern with debug fallback, minify+shrink+proguard enabled.
- Mobile release builds throw at startup unless `--dart-define=API_BASE_URL=<real origin>` is provided (localhost/10.0.2.2 rejected in release) — `AppConstants.resolveApiBaseUrl` is the tested guard.
- SyncBloc has an in-flight guard: concurrent `SyncTriggered` events during an active sync are ignored (fixes the double-push seen in live testing).
- Backend containers run as non-root `app` user; the scraper image relocates Playwright browsers to `/ms-playwright`. The prod scraper-worker has a `pgrep`-based healthcheck.
- Full 7-pillars audit + remediation record: `plans/valuadis-v2-refactor/7-pillars-audit.md`. Post-fix gates: backend 427 passed/17 skipped, frontend typecheck + 18 unit, flutter 58/58.

### 2026-07-12

- `nuxt dev` is broken on Nuxt 3.21.5 with `ssr: false`: the vite-node IPC env (`NUXT_VITE_NODE_OPTIONS`) is only set in the SSR `vite:serverCreated` hook, which never fires, so every route 500s with "Vite Node IPC socket path not configured". Local preview workflow is `npm run build` then `PORT=3000 node .output/server/index.mjs` (wired into `.claude/launch.json`).
- The runnable Nuxt app is `frontend/app/` with its own package.json; `npm run dev` from `frontend/` serves the default Nuxt welcome page.
- The Postgres dev database admin credential is `admin@valuadis.com` / `password123` (root `create_admin.py`), not the old SQLite `admin123` seed. Demo login needs `NUXT_PUBLIC_DEMO_LOGIN_EMAIL/PASSWORD` set when the preview server starts.
- Frontend auth tokens are memory-only (`frontend/app/utils/authToken.ts`): any hard reload or deep link logs the user out. Fixing this via an httpOnly refresh-cookie flow is Phase 1 of the v2 plan.
- The login form's Sign In button is `type="button"`, so Enter does not submit — click it. Flagged as a Phase 1 fix.
- The v2 stack decision and refactor plan (keep FastAPI, reject Laravel rewrite, strangler modularization into `backend/app/modules/`) lives at `plans/valuadis-v2-refactor/plan.mdx`; the user delegated all open decisions, and execution is underway (see the plan's Decisions callout and phase checklists).
- The live frontend auth service is `frontend/app/services/authService.ts`; a dead `.js` twin used to shadow it and was deleted. Bare `~/services/authService` imports resolve to `.ts` first — never reintroduce the duplicate.
- Browser sessions persist via an httpOnly `valuadis_refresh` cookie (set on login/refresh, rotated with a jti claim, cleared by `POST /api/v1/auth/logout`). The frontend boots through an idempotent `authStore.initialize()` awaited in `global-auth.global.ts`; logout must go through the store, not `clearAuthTokens()` alone, or the cookie resurrects the session.
- The `/api/v1` OpenAPI contract is frozen in `backend/tests/contract/openapi_v1_snapshot.json` and enforced by `backend/tests/test_openapi_contract.py`: additions allowed, removals/changes fail the suite. Regenerate the snapshot only for an intentional, reviewed contract change. Full-suite gate as of this session: 262 passed / 17 skipped.
- Civic-ledger rebrand pass 1: tokens live in `frontend/app/assets/css/main.css` `:root`, mirrored in `frontend/app/tailwind.config.ts` and `frontend/design-tokens.json`. Never rename legacy vars (`--green`, `--canvas`, `--line`, `--display`, `--amber`, ...) — 19+ unmigrated pages consume them; new palette values flow through the old names. `--amber` is now an alias of `--gold`.
- Rebrand font roles: `--serif` (Cormorant Garamond) only for landing/login/brand display; `--display` stays DM Sans for app headings; `--mono` for metric/ledger figures (`.metric-value` is mono now). Syne stays in the nuxt.config font link until `properties/import.vue` and `EnhancedWizardUI.vue` migrate.
- The admin sidebar is dark green-charcoal via `--shell-*` tokens purely in main.css; `layouts/default.vue` template was left untouched (nav structure, hrefs, `handleLogout` are E2E-sensitive). Restyled so far: landing, login, default layout, dashboard; all other routes await a consistency pass.
- Dashboard trend chart, distribution percentages (42/31/27), and the 98.2% compliance default are static placeholders retained under the rebrand functionality freeze — not backend-backed; flag for a data-integrity pass.

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
