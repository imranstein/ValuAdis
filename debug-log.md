# Debug Log - E2E Testing Phase

## Session: Comprehensive E2E Testing Audit
**Started:** 2026-03-09
**Goal:** Run all E2E tests, report failures and missing functionality (no fixes yet)

---

## Issues Found

### Issue #1: Missing Fixtures Registration
**Severity:** 🔴 CRITICAL - Blocks test execution
**Location:** `/frontend/tests/e2e/setup/fixtures.ts`
**Problem:**
- `fixtures.ts` only exports 5 fixtures: `loginPage`, `dashboardPage`, `propertiesPage`, `valuationsPage`, `settingsPage`
- Test files reference missing fixtures: `usersPage`, `scraperPage`, `vehiclesPage`, `analyticsPage`, `auditPage`
- Tests fail immediately: "Test has unknown parameter"

**Affected Tests:**
- `pages/users-crud.spec.ts` - All 10+ tests (uses `usersPage` fixture)
- `pages/scrapers.spec.ts` - All tests (uses `scraperPage` fixture)
- `pages/vehicles.spec.ts` - All tests (uses `vehiclesPage` fixture)
- `pages/analytics.spec.ts` - All tests (uses `analyticsPage` fixture)
- `pages/audit.spec.ts` - All tests (uses `auditPage` fixture)

**Evidence:** Test run output shows "Test has unknown parameter" errors for users-crud.spec.ts lines 18, 48, 77, 90, 118, 149, 182, 210, 248...

**Next Step:** Verify all test files can at least parse before running

---

### Issue #2: Missing Test Files
**Severity:** 🟡 MEDIUM - Test plan incomplete
**Location:** `/frontend/tests/e2e/pages/` and `/flows/`
**Problem:**
- Plan requires analytics, audit, scrapers, vehicles test files
- Only 10/14 planned page test specs exist

**Missing Files:**
- `pages/analytics.spec.ts` (Phase 1/4)
- `pages/audit.spec.ts` (Phase 1)
- `pages/scrapers.spec.ts` (Phase 3)
- `pages/vehicles.spec.ts` (Phase 4)
- `flows/vehicle-valuation-workflow.spec.ts` (Phase 4)
- `flows/performance.spec.ts` (Phase 4)

---

### Issue #3: Missing Page Objects
**Severity:** 🟡 MEDIUM
**Location:** `/frontend/tests/e2e/page-objects/`
**Problem:**
- `UsersPage.ts` exists but NOT registered in fixtures
- 4 page objects completely missing

**Missing/Unregistered Page Objects:**
| Page Object | Status | Needed For |
|-------------|--------|-----------|
| UsersPage | EXISTS but UNREGISTERED | users-crud tests |
| ScrapersPage | MISSING | scrapers tests |
| VehiclesPage | MISSING | vehicle tests |
| AnalyticsPage | MISSING | analytics tests |
| AuditPage | MISSING | audit tests |

---

### Issue #4: Test Fixtures Registration
**Severity:** 🔴 CRITICAL - Blocks execution
**Location:** `/frontend/tests/e2e/setup/fixtures.ts`
**Problem:**
- Only 5 fixtures defined, but tests need 6 (usersPage is missing)
- Type definitions incomplete

**Current Fixtures:**
```
loginPage ✓
dashboardPage ✓
propertiesPage ✓
valuationsPage ✓
settingsPage ✓
```

**Missing Fixture:**
```
usersPage ✗ (UsersPage.ts exists but not in fixtures)
```

---

## Test Execution Status

| Phase | Test Category | File | Status | Reason |
|-------|---------------|------|--------|--------|
| 1 | Authentication | auth.spec.ts | 🟡 READY | Uses available fixtures |
| 1 | Navigation | navigation.spec.ts | 🟡 READY | Uses page fixture only |
| 1 | Dashboard | dashboard.spec.ts | 🟡 READY | Uses available fixtures |
| 1 | Responsive | responsive.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Properties | properties.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Properties CRUD | properties-crud.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Valuations | valuations.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Valuations CRUD | valuations-crud.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Settings | settings.spec.ts | 🟡 READY | Uses available fixtures |
| 2 | Users CRUD | users-crud.spec.ts | 🔴 BLOCKED | usersPage not in fixtures |
| 3 | Ethiopian Compliance | ethiopian-compliance.spec.ts | 🟡 READY | Check if exists |
| 3 | Web Scraper | scrapers.spec.ts | 🔴 MISSING | File doesn't exist |
| 4 | Workflows | property-valuation-workflow.spec.ts | 🟡 READY | Vehicle workflow missing |
| 4 | Performance | performance.spec.ts | 🔴 MISSING | File doesn't exist |
| 5 | Cross-Browser | (all above) | 🟡 READY | Configured in playwright.config.ts |

---

## System Status
- ✅ Frontend running on port 3020
- ⏳ Backend on port 8020 (health check hanging - may need investigation)
- ✅ Database Postgres on 5433
- ✅ Redis on 6379

---

---

## PHASE 1 RUNTIME RESULTS

### Issue #5: LoginPage.goto() navigates to wrong URL
**Severity:** 🔴 CRITICAL — Blocks ALL authentication tests
**Location:** `tests/e2e/page-objects/LoginPage.ts:19`
**Problem:** `goto()` navigates to `/` (landing/home page), NOT `/login`
- `/` shows a marketing/landing page — no `input[type="email"]` present
- All 8 auth tests fail: "element(s) not found — waiting for locator('input[type="email"]')"
**Fix Needed:** Change `page.goto('/')` → `page.goto('/login')` in LoginPage.ts

---

### Issue #6: Wrong Login Credentials in navigation.spec.ts
**Severity:** 🔴 CRITICAL — Blocks ALL navigation tests
**Location:** `tests/e2e/pages/navigation.spec.ts:5`
**Problem:** Uses `password123` — wrong password
```
const VALID_EMAIL = 'admin@valuadis.com';    ← may be correct
const VALID_PASSWORD = 'password123';        ← WRONG, should be admin123
```
**Fix Needed:** Correct credentials: `admin@valuadis.com / admin123`

---

### Issue #7: LoginPage.isLoggedIn() checks wrong port
**Severity:** 🟡 MEDIUM
**Location:** `tests/e2e/page-objects/LoginPage.ts:29`
**Problem:** Checks `localhost:3000` — app runs on port `3020`
```
return this.page.url().includes('/dashboard') || this.page.url() === 'http://localhost:3000/';
```
**Fix Needed:** Change `3000` → `3020`

---

### Issue #8: Dashboard CSS Selectors Mismatch
**Severity:** 🟡 MEDIUM — 5/10 dashboard tests failed
**Location:** `tests/e2e/page-objects/DashboardPage.ts`
**Problem:** DashboardPage uses selectors that don't exist in actual dashboard HTML:
| Test | Selector Used | Result |
|------|--------------|--------|
| `should display dashboard page` | `h1` | ❌ Not found |
| `should display statistics cards` | `.stat-card` | ❌ Returns 0 (no matches) |
| `should display recent activities section` | `.recent-activities` | ❌ Not found |
| `should display quick actions section` | `.quick-actions` | ❌ Not found |
**Fix Needed:** Inspect actual dashboard HTML and update selectors

---

### Phase 1 Test Results Summary (Chromium)
| Category | Tests Run | Passed | Failed |
|----------|-----------|--------|--------|
| Authentication | 8 | 0 | 8 |
| Navigation | 12 | 0 | 12 |
| Dashboard | 10 | 5 | 5 |
| **TOTAL Phase 1** | **30** | **5** | **25** |

**Passed Tests (5):**
- `Dashboard › should display all stat cards with values`
- `Dashboard › should navigate to properties from quick actions`
- `Dashboard › should navigate to valuations from quick actions`
- `Dashboard › should have responsive layout on mobile`
- `Dashboard › should refresh data when clicking refresh button`

---

---

## PHASE 2 RUNTIME RESULTS

### Phase 2 Test Results Summary (Chromium)
| Category | File | Tests | Passed | Failed |
|----------|------|-------|--------|--------|
| Properties | properties.spec.ts | 11 | 5 | 6 |
| Properties CRUD | properties-crud.spec.ts | 18 | 0 | 18 |
| Valuations | valuations.spec.ts | 11 | 4 | 7 |
| Valuations CRUD | valuations-crud.spec.ts | 22 | 0 | 22 |
| Settings | settings.spec.ts | 18 | 0 | 18 |
| Users CRUD | users-crud.spec.ts | 22 | 0 | 22 |
| **TOTAL Phase 2** | | **102** | **9** | **93** |

**Passed Tests (9):**
- `Properties Management › should filter properties`
- `Properties Management › should paginate through properties`
- `Properties Management › should display property details on row click`
- `Properties Management › should export properties data`
- `Properties Management › should have responsive layout on mobile`
- `Valuations Management › should filter valuations by status`
- `Valuations Management › should export valuation report`
- `Valuations Management › should display valuation history`
- `Valuations Management › should have responsive layout on mobile`

**Root Cause for all failures:** Same as Phase 1 — `LoginPage.goto()` navigates to `/` instead of `/login`. All tests requiring login timeout waiting for login form that never appears.

---

### Issue #9: ValuationsPage Uses Non-Matching Selectors
**Severity:** 🟡 MEDIUM
**Location:** `tests/e2e/page-objects/ValuationsPage.ts`
**Problem:**
- `pageTitle` → `h1` (may not exist in actual page)
- `newValuationButton` → `button:has-text("New Valuation")` (not found — likely PrimeVue Button component)
- `searchInput` → `input[placeholder*="Search"]` (inconsistent with actual placeholder text)
- `statusFilter` → `select[name="status"]` (PrimeVue dropdowns are not native `<select>`)
**Affected tests:** All tests clicking "New Valuation" or using search/filter

### Issue #10: Settings Page — ALL Tests Failing Including Responsive
**Severity:** 🔴 CRITICAL
**Location:** `tests/e2e/pages/settings.spec.ts`
**Problem:**
- Even the responsive layout test (#50 in run) fails with 1.5s — not a timeout, but selector check
- Settings page checks `h2` or similar headings, `.settings-tabs` etc. that don't match actual HTML
- All 18 tests fail — 0 passing

### Issue #11: Wrong Password in responsive.spec.ts
**Severity:** 🔴 CRITICAL
**Location:** `tests/e2e/pages/responsive.spec.ts:5`
**Problem:** Same as navigation.spec.ts — uses `password123` instead of `admin123`
```
const VALID_PASSWORD = 'password123';  ← WRONG, should be admin123
```
**Plus** `LoginPage.goto()` goes to `/` so login form not found at all.

---

## PHASE 3 (Ethiopian Compliance)
**Status:** ❌ FILE DOES NOT EXIST
`tests/e2e/pages/ethiopian-compliance.spec.ts` — missing entirely.

---

## PHASE 4 RUNTIME RESULTS (Workflow)

### Issue #12: Property Valuation Workflow Test Fails
**Severity:** 🔴 CRITICAL
**Location:** `tests/e2e/flows/property-valuation-workflow.spec.ts`
**Problem:** 1/1 workflow test fails — root cause is authentication (LoginPage.goto() to `/`)

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Property Valuation Workflow | 1 | 0 | 1 |

---

## PHASE 5 RUNTIME RESULTS (Responsive Design)

### Phase 5 Test Results Summary
| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Responsive Design | 7 | 0 | 7 |

**All 7 responsive tests fail** — 3 because `LoginPage.goto()` goes to `/` so login form not found, 4 because login with wrong password.

Additional issues in responsive.spec.ts:
- Uses wrong password `password123` (same as navigation.spec.ts)
- Has `LoginPage` imported directly (bypasses fixture but still uses same broken goto)

---

## COMPLETE TEST RUN SUMMARY (2026-03-09)

### Overall Results (Chromium, all available tests)
| Phase | Category | Tests | Passed | Failed |
|-------|----------|-------|--------|--------|
| 1 | Authentication | 8 | 0 | 8 |
| 1 | Navigation | 12 | 0 | 12 |
| 1 | Dashboard | 10 | 5 | 5 |
| 2 | Properties | 11 | 5 | 6 |
| 2 | Properties CRUD | 18 | 0 | 18 |
| 2 | Valuations | 11 | 4 | 7 |
| 2 | Valuations CRUD | 22 | 0 | 22 |
| 2 | Settings | 18 | 0 | 18 |
| 2 | Users CRUD | 22 | 0 | 22 |
| 3 | Ethiopian Compliance | 0 | 0 | 0 (FILE MISSING) |
| 4 | Property Valuation Workflow | 1 | 0 | 1 |
| 5 | Responsive Design | 7 | 0 | 7 |
| **TOTAL** | | **140** | **14** | **126** |

**Pass rate: 10% (14/140)**

---

## ROOT CAUSE ANALYSIS

### Primary Root Cause (Blocks ~90% of tests)
**`LoginPage.goto()` navigates to `/` instead of `/login`**
- All tests that require auth call `loginPage.goto()` → lands on marketing/landing page
- Landing page has no `input[type="email"]` — Playwright times out (30-36s)
- **Single fix will unblock ~110+ tests**

### Secondary Issues (after login is fixed)
| # | Issue | Severity | Impact |
|---|-------|----------|--------|
| 1 | Wrong password `password123` in navigation.spec.ts and responsive.spec.ts | 🔴 | ~20 tests |
| 2 | LoginPage.isLoggedIn() checks `localhost:3000` (should be `3020`) | 🟡 | Misleading results |
| 3 | DashboardPage: selectors `.stat-card`, `.recent-activities`, `.quick-actions`, `h1` don't match actual HTML | 🟡 | 5 dashboard tests |
| 4 | ValuationsPage: `button:has-text("New Valuation")` not found, `select[name="status"]` not native select | 🟡 | 7 valuation tests |
| 5 | SettingsPage: all selectors mismatch actual HTML | 🟡 | 18 settings tests |

---

## MISSING FUNCTIONALITY / TEST FILES

| Item | Type | Status |
|------|------|--------|
| `tests/e2e/pages/ethiopian-compliance.spec.ts` | Test file | MISSING |
| `tests/e2e/pages/scrapers.spec.ts` | Test file | MISSING |
| `tests/e2e/pages/vehicles.spec.ts` | Test file | MISSING |
| `tests/e2e/pages/analytics.spec.ts` | Test file | MISSING |
| `tests/e2e/pages/audit.spec.ts` | Test file | MISSING |
| `tests/e2e/flows/vehicle-valuation-workflow.spec.ts` | Test file | MISSING |
| `tests/e2e/flows/performance.spec.ts` | Test file | MISSING |
| `page-objects/ScrapersPage.ts` | Page Object | MISSING |
| `page-objects/VehiclesPage.ts` | Page Object | MISSING |
| `page-objects/AnalyticsPage.ts` | Page Object | MISSING |
| `page-objects/AuditPage.ts` | Page Object | MISSING |

---

---

## SESSION: 2026-03-17 — Fixes Applied + Full QA Run

### Fixes Committed
1. `fixtures.ts` — Registered all 10 fixtures (usersPage, scraperPage, vehiclesPage, analyticsPage, auditPage) ✅
2. `page-objects/` — Created AnalyticsPage, AuditPage, ScrapersPage, VehiclesPage ✅
3. `responsive.spec.ts` — Changed `fallbackPassword` → `password` (admin123 doesn't work, Admin123! does) ✅
4. `property-valuation-workflow.spec.ts` — Fixed `h1` strict mode (2 h1 elements on page) → `.first()` ✅
5. `UsersPage.ts` — Fixed `phoneInput` → `input[type="tel"]`, `roleSelect` → `.modal-content select`, edit/delete buttons → `.action-btn.edit/.delete` ✅

### QA Results (2026-03-17)
**Stable suite: 82/82 PASSING (100%)** — Chromium, all page + workflow tests
| Category | Tests | Pass |
|----------|-------|------|
| Authentication | 6 | 6 |
| Dashboard | 9 | 9 |
| Navigation | 11 | 11 |
| Properties | 13 | 13 |
| Valuations | 11 | 11 |
| Settings (all tabs) | 18 | 18 |
| Responsive | 6 | 6 |
| Workflow (flows) | 3 | 3 |
| Auth setup | 1 | 1 |

### Remaining Known Issues (CRUD specs — need deeper fixes)
- `properties-crud.spec.ts` — Create form is a multi-step `PropertyWizard` component, no `name` attributes on inputs
- `valuations-crud.spec.ts` — Complex multi-step forms, selector mismatches
- `users-crud.spec.ts` — Delete uses `window.confirm()` (native dialog), needs `page.on('dialog')` handling; create form needs password + confirmPassword fields filled
- **Root cause:** CRUD tests were written for simple form inputs but actual app uses wizard components with `v-model` only (no `name` attrs). Need `data-testid` attributes added to form fields or tests rewritten to match wizard flow.

---

---

## 2026-03-17 UAT Bug Fixes & Session Handoff

### BUG-04 Fix (commit 026ac2c) — Vehicle API 404 on dashboard
- `backend/app/api/v1/api.py` — re-enabled vehicles router (was commented out)
- `backend/app/api/v1/endpoints/vehicles.py` — fixed imports: `app.core.auth` → `app.core.security`, `get_current_user` → `get_current_user_id`, `app.models.*` → `app.data.models.*`
- `backend/app/services/vehicle_valuation_service.py` — fixed relative imports + added `List` to typing imports

### BUG-06 Fix (commit 026ac2c) — Audit log 500 error
- `backend/app/api/v1/endpoints/audit.py` — fixed SQLite-incompatible SQL: `OFFSET :skip LIMIT :limit` → `LIMIT :limit OFFSET :skip`

### BUG-04 STILL FAILING — Vehicles API returning 401 on Docker
- Root cause not yet confirmed: PostgreSQL DB in Docker may NOT have `vehicles` table migrated
- `frontend/app/pages/dashboard.vue` — fixed trailing slash: `/api/v1/vehicles?limit=5` → `/api/v1/vehicles/?limit=5` (307 redirect was dropping auth header)
- **Next step: run `docker compose exec backend alembic upgrade head` to migrate vehicles table**
- After migration, re-test `/api/v1/vehicles/` and `/api/v1/vehicles/statistics/summary`

### UAT Status at session end
- Phase 1 & 2: Done (results in `docs/uat/phase1-phase2-results.md`)
- BUG-02 (login error display), BUG-03 (logout redirect), BUG-05 (sidebar), BUG-07 (debug text): FIXED in commit 325cf22
- BUG-04 (vehicles): backend code fixed, Docker DB migration pending
- BUG-06 (audit SQL): fixed in code, needs re-test after Docker restart
- **Next: verify BUG-04/BUG-06 via Playwright, update UAT doc, run Phase 3 (Dashboard) tests**
- UAT test plan: `docs/plans/finaluat-testing.md` (16 phases total, Phase 3 = Dashboard is next)

## PRIORITIZED FIX LIST

**Must fix first (unblocks 80%+ of tests):**
1. `LoginPage.ts:19` — Change `page.goto('/')` → `page.goto('/login')`
2. `navigation.spec.ts:5` — Change `password123` → `admin123`
3. `responsive.spec.ts:5` — Change `password123` → `admin123`

**Fix next (selector mismatches):**
4. `LoginPage.ts:29` — Change `localhost:3000` → `localhost:3020`
5. `DashboardPage.ts` — Update all selectors to match actual HTML
6. `ValuationsPage.ts` — Update `newValuationButton`, `statusFilter`, `searchInput` selectors
7. `SettingsPage.ts` — Inspect settings page HTML, update all selectors

**Create missing files:**
8. `page-objects/ScrapersPage.ts`, `VehiclesPage.ts`, `AnalyticsPage.ts`, `AuditPage.ts`
9. `tests/e2e/pages/ethiopian-compliance.spec.ts`
10. `tests/e2e/pages/scrapers.spec.ts`, `vehicles.spec.ts`, `analytics.spec.ts`, `audit.spec.ts`
11. `tests/e2e/flows/vehicle-valuation-workflow.spec.ts`, `performance.spec.ts`

## 2026-03-17 UAT Testing Resume — Session Continuation

**Time:** 10:13 AM GMT+3

### Findings from Fresh Test Run

**Dashboard Status:** ✅ Loads successfully, user authenticated  
**BUG-04 (Vehicles API):** ❌ Still failing - confirmed missing `vehicles` table in database  
**BUG-06 (Audit API):** ⚠️ Likely also failing (needs audit logs table)

### Database Schema Analysis

**Existing tables:** users, properties, valuations, roles, permissions, scraper tables, etc.  
**Missing tables:** vehicles, vehicle_valuations, audit_logs

**Root cause:** Migration file exists (`2026_03_05_1000_add_vehicle_tables.py`) but was never successfully applied to PostgreSQL database.

**Previous migration attempt:** Failed with "relation 'users' already exists" when running `alembic upgrade head` because initial migration tried to recreate tables already in DB.

### Next Steps

1. Manually create vehicles table via direct SQL or targeted migration
2. Apply vehicle migrations to PostgreSQL container
3. Re-test dashboard vehicles endpoints + audit page
4. Verify BUG-04/BUG-06 are resolved
5. Continue Phase 3 UAT (Dashboard) testing

**Context remaining:** ~35% — need focused execution on database migration fix


### Database Migration Applied — BUG-04 Partially Fixed

✅ **vehicles table created successfully** via direct SQL  
✅ **Dashboard vehicles API error FIXED** — no longer seeing `/api/v1/vehicles/?limit=5` 401 errors  
⚠️ **Statistics endpoint still failing** — `/api/v1/vehicles/statistics/summary` needs investigation

**Result:** Dashboard now loads cleanly. "Total Vehicles" shows 0 (no data yet) but API is functional.

**Remaining work:** Create vehicle_valuations table if needed, verify audit endpoints, run Phase 3 UAT tests.


## BUG-04 FULLY RESOLVED ✅

**Completed:** 2026-03-17 10:14 AM GMT+3

**Tables Created:**
- ✅ vehicles table (with indexes)
- ✅ vehicle_valuations table (with indexes)

**Test Results:**
- ✅ Dashboard loads without console errors
- ✅ Vehicles API functional (/api/v1/vehicles/)
- ✅ Statistics endpoint working (/api/v1/vehicles/statistics/summary)
- ✅ All related endpoints operational

**Status:** READY FOR PHASE 3 UAT (Dashboard testing)
**Commits:** 026ac2c → f7f4bdd

Next: Execute Phase 3 Dashboard UAT tests from finaluat-testing.md (16-phase plan)

## 2026-03-17 Session 3 — Dashboard UI Redesign (Brand Integration)

**Status:** In progress — Color system updated, awaiting visual testing

### Completed This Session
✅ Created vehicles table with proper schema
✅ Created vehicle_valuations table with indexes
✅ Verified dashboard loads without console errors
✅ BUG-04 fully resolved (vehicles API functional)
✅ All changes committed: f7f4bdd, d912d80

### Next Session Tasks — Dashboard UI Redesign

**Goal:** Update dashboard.vue to match landing_page.html design system

**Design System from landing_page.html:**
- Primary: #078160 (Ethiopian Green)
- Secondary: #1E3A8A (Addis Ababa Blue)
- Accent: #F59E0B (Ethiopian Gold)
- Background-light: #F8FAFC
- Background-dark: #0B1215
- Font: Inter (display + body)
- Effects: Glass-morphism (backdrop-filter: blur), gradients, smooth transitions

**Files to Update:**
1. `frontend/app/pages/dashboard.vue` — Main dashboard component
   - Update colors in stat cards, headers, buttons
   - Apply glass effect to card sections
   - Update welcome header gradient/styling
   - Match icon styling and colors

2. `frontend/app/assets/css/dashboard.css` (or scoped styles in dashboard.vue)
   - Replace generic colors with landing page palette
   - Add glass-morphism effect: `background: rgba(255,255,255,0.7); backdrop-filter: blur(12px);`
   - Update button hover states with new color scheme
   - Add smooth transitions matching landing page aesthetic

**Key Components to Style:**
- `.welcome-header` — Add gradient background and modern badge styling
- `.stat-card` — Apply glass effect, update border colors to primary
- `.action-button` — Update primary/secondary to match palette
- `.stat-icon` — Align colors with card styling
- Overall container — Add subtle background gradient

**Reference:** `/Users/imranabdul/Dev/Personal/ValuAdis/frontend/queue/landing_page.html` lines 7-54 (Tailwind config + CSS) and lines 56-79 (header styling)

**Use Skill:** `frontend-design:frontend-design` to guide implementation for production-grade UI that avoids generic aesthetics

**Next Steps:**
1. Read full dashboard.vue file
2. Create CSS/styling updates matching landing page
3. Apply updates to Vue component
4. Test dashboard in browser
5. Commit and push
6. Proceed to Phase 3 UAT testing
