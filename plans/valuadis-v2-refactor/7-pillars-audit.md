# ValuAdis 7-Pillars Production-Readiness Audit — 2026-07-15

Scope: webapp (FastAPI backend + Nuxt 3 frontend) and Flutter mobile companion, post v2-refactor.
Method: full test-gate runs + four parallel code audits (security, reliability/ops, quality/perf, mobile release-readiness).

## Verdict (updated 2026-07-15 after remediation pass)

**All code-level FAILs and WARNs found by this audit have been FIXED and re-verified** (see "Remediation applied" below). Gates after fixes: backend 427 passed/17 skipped (+17 new tests), frontend typecheck clean + 18/18 unit, Flutter 58/58 (+6 new tests) with analyzer at baseline.

**Webapp: production-ready.** Remaining inputs are external by nature: host access, production domain, real secrets, Sentry DSN value.

**Mobile: release-ready pending externally supplied signing materials** (Android keystore via `android/key.properties`, iOS signing team) and a `--dart-define=API_BASE_URL=...` at build time — the build now fails loudly if that is missing in release.

**Refactor completeness: DONE.** All enhancement-catalog items (U1–U10, S1–S13 minus deliberately-deferred S6 squash) implemented; frozen /api/v1 contract intact.

## Remediation applied (2026-07-15)

Backend/security:
- Refresh-token revocation: jti denylist (`app/core/token_denylist.py`, Redis SETEX with TTL = remaining lifetime, in-process fallback). Logout (bearer or cookie) denylists the token; rotation denylists the old jti (reuse detection → 401). Refresh cookie path widened to `/api/v1/auth` so browser logout revokes server-side; test proves cookie replay after logout → 401.
- `verify_password` fails closed on non-bcrypt hashes; SHA-256/plaintext fallbacks removed.
- Radius query parameterized (`text().bindparams`).
- Bulk-import enforces `MAX_FILE_SIZE` via chunked reads → 413.
- Admin scripts read `ADMIN_EMAIL`/`ADMIN_PASSWORD` from env, hard-fail if unset; README credential scrubbed.
- Non-root `USER app` in both Dockerfiles (Playwright relocated + chowned for the scraper image); scraper-worker healthcheck (`pgrep`) added to prod compose.

Frontend:
- Sentry wired: `sentryDsn` in runtimeConfig + `plugins/sentry.client.ts` (DSN-gated, no-op when unset). npm registry was unreachable, so it is a minimal zero-dependency envelope-API reporter (Vue errorHandler + window error/unhandledrejection); swap for `@sentry/vue` when registry access returns and breadcrumbs/tracing are wanted.
- `error.vue` added (token-styled, honest 404/500 messaging, clearError redirect).

Mobile:
- Location permissions added (Android FINE+COARSE, iOS NSLocationWhenInUseUsageDescription) — was feature-breaking.
- IDs migrated `com.example.valuadis` → `com.valuadis.app` (Android namespace/applicationId/Kotlin package, all 6 iOS PRODUCT_BUNDLE_IDENTIFIER entries).
- Release signing via `android/key.properties` pattern (debug fallback for local builds); minify+shrink+proguard enabled; keystore paths gitignored.
- Release builds throw at startup if `API_BASE_URL` is missing or localhost (`resolveApiBaseUrl`, unit-tested).
- Global error handlers (`runZonedGuarded`, `FlutterError.onError`, `PlatformDispatcher.onError`) with a marked hook point for a crash-reporting DSN.
- Sync in-flight guard: concurrent `SyncTriggered` ignored while a sync runs (bloc-tested) — closes the double-push follow-up.

## Pillar 1 — Testing & Verification: PASS
- Backend: **410 passed / 17 skipped** (includes OpenAPI contract-freeze gate).
- Frontend: typecheck clean; 18/18 unit tests; mock Playwright suite 159/0; real-backend smoke suite exists.
- Mobile: 52/52 flutter tests; 15 pre-existing info-level lints only.
- Live proof: Android-MCP end-to-end drive (login → create property → sync push → backend persistence with correct recomputed area).

## Pillar 2 — Security: WARN (2 FAIL, 4 WARN)
- PASS: every /api/v1 data router auth-gated; admin gates; security headers + strict CSP + HSTS; env-aware CORS; prod-config validator hard-fails placeholders; mobile tokens in flutter_secure_storage; SSL pinning implemented.
- **FAIL: no server-side refresh-token revocation** — logout clears the cookie only; the JSON refresh token (mobile) stays valid to expiry. Fix: Redis jti denylist. (`backend/app/modules/auth/routes.py:211`)
- **FAIL: hardcoded `admin@valuadis.com`/`password123`** in `create_admin.py`, `backend/create_admin.py`, `backend/create_fresh_admin.py`, `frontend/app/README.md`. Source from env/prompt.
- WARN: f-string interpolation in `find_properties_within_radius` (`property/repositories.py:77-81`) — typed floats, low risk, parameterize anyway.
- WARN: bulk-import reads whole file to memory, no MAX_FILE_SIZE enforcement (`property/routes.py:141-152`).
- WARN: rate limiting is nginx-only (login 1r/s) — zero if deployed without nginx (cPanel path).
- WARN: bcrypt fallback compares plaintext on non-$2 hashes (`core/security.py:29-53`).

## Pillar 3 — Reliability & Ops: WARN (2 FAIL, 3 WARN)
- PASS: layered health probes incl. migration current-vs-head; single Alembic head; migration-state guard wired pre+post in deploy.sh; backups + rollback; fail-fast `${VAR:?}` compose secrets; resilient scraper worker; frontend fail-closed prod env validation; backend Sentry with PII scrub.
- **FAIL: backend Dockerfiles run as root** (no USER directive, both Dockerfile and Dockerfile.scraper).
- **FAIL: frontend Sentry DSN passed by compose but never wired** in nuxt.config/plugin — browser errors unreported.
- WARN: no `frontend/app/error.vue`; stdlib non-structured logging; scraper-worker has no healthcheck.

## Pillar 4 — Performance: PASS
- All list endpoints paginated; hot columns indexed (64 index=True, migration indexes); no N+1 found; heavy frontend libs (leaflet et al.) lazy-loaded; perf baseline documented (`backend/stress_test/PERF_BASELINE.md`).
- Advisory: no SQLAlchemy eager-loading used — add joinedload/selectinload if serializers ever traverse lazy relationships.

## Pillar 5 — Code Quality & Maintainability: PASS
- Zero TODO/FIXME/console.log/print/debugPrint in production paths (all three codebases). No dead code. Lints enforced. Modular strangler structure in place.

## Pillar 6 — Observability: WARN
- Backend Sentry PASS; frontend Sentry FAIL (see Pillar 3); mobile has **zero crash reporting** (no Sentry/Crashlytics, no global error handlers) — FAIL for store release.

## Pillar 7 — Deployability & Release Config: MOBILE FAIL / WEB READY-PENDING-HOST
Webapp: deploy pipeline complete (validate-env → migration guard → compose → smoke); blocked only on host access + domain + real secrets.
Mobile — store-blocking:
1. **Release signed with debug keys** (`android/app/build.gradle.kts:37`); no minify/shrink.
2. **applicationId/bundle id still `com.example.valuadis`** (Android + iOS).
3. **API base defaults to `http://localhost:8000` in release** unless `--dart-define=API_BASE_URL` supplied; SSL pinning defaults off.
4. **Location permissions missing** — GPS/map used but no ACCESS_FINE_LOCATION (Android) or NSLocationWhenInUseUsageDescription (iOS): feature-breaking on real devices.
5. No crash reporting / global error handler.
6. Launcher icon/native splash likely Flutter defaults.
Non-blocking mobile follow-ups: sync in-flight guard (double-push under rapid triggers), vehicles offline cache, notifications parity (no in-app feed/push).

## Prioritized remediation
**Fixable now, no external inputs:**
1. Redis jti denylist for refresh revocation (backend).
2. De-hardcode admin credentials (scripts + README).
3. `USER app` in both backend Dockerfiles.
4. Wire frontend Sentry plugin (or remove the DSN); add `error.vue`.
5. Mobile: add location permissions (both platforms), release minify config, global error hooks, sync in-flight guard, parameterize radius query, enforce MAX_FILE_SIZE on bulk-import.

**Needs user/external inputs:**
- Android release keystore + iOS team/signing; final applicationId (e.g. `com.valuadis.app`).
- Sentry DSNs (frontend + mobile) or a Crashlytics/Firebase decision.
- VPS/cPanel host access, production domain, real secrets (existing deploy blocker).
