# 🚀 PARALLEL TASK ASSIGNMENTS — Critical Features Execution Plan

**Created:** 2026-03-22
**Total Tasks:** 19 subtasks across 3 waves
**Total Effort:** 24-33 hours (2-3 days with parallelization)
**Status:** Ready for agent assignment

---

## 📋 Quick Assignment Guide

This document breaks down all critical features into atomic, parallel-safe subtasks. Each task:
- ✅ Has clear acceptance criteria (binary pass/fail)
- ✅ Lists specific deliverables (files/endpoints)
- ✅ Shows dependencies (what must complete first)
- ✅ Indicates if it can run in parallel
- ✅ Suggests appropriate agent type

---

## 🌊 WAVE 1: Security Foundation (Token Expiry)
**Status:** ✅ DONE (2026-03-22) — Unblocks Wave 2
**Duration:** 2-4 hours (COMPLETED)
**Parallelization:** Sequential (dependencies)

### Task 01: Implement token validation in useAuth.ts
- **Agent:** CoderAgent
- **Depends on:** None (start first)
- **Parallel:** Yes
- **Files:**
  - `frontend/app/composables/useAuth.ts` (update)
- **Acceptance Criteria:**
  - ✓ Token validation check function exports from useAuth.ts
  - ✓ Function detects expired tokens based on JWT exp claim
  - ✓ Function handles missing or invalid tokens gracefully

### Task 02: Create auth middleware for token expiry
- **Agent:** CoderAgent
- **Depends on:** Task 01 (token validation function)
- **Parallel:** No
- **Files:**
  - `frontend/app/middleware/auth.ts` (update)
- **Acceptance Criteria:**
  - ✓ Middleware exports a default navigation guard
  - ✓ Middleware checks token expiry on every route navigation
  - ✓ Expired tokens trigger logout and redirect to login page
  - ✓ User sees clear message about token expiration

### Task 03: E2E test for token expiry scenario
- **Agent:** TestEngineer
- **Depends on:** Task 02 (middleware complete)
- **Parallel:** No
- **Files:**
  - `tests/e2e/phase1-foundation.spec.ts` (add test)
- **Acceptance Criteria:**
  - ✓ E2E test creates a valid token with short expiry
  - ✓ Test navigates to protected route and waits for expiry
  - ✓ Test verifies automatic logout occurs
  - ✓ Test confirms redirect to login page
  - ✓ Test passes consistently

**Unblocks:** Wave 2 (all following tasks depend on token expiry working)

---

## 🌊 WAVE 2: Core Features (Vehicle + Compliance Items)
**Status:** Ready to start after Wave 1
**Duration:** 13-16 hours (parallel execution)
**Parallelization:** YES — Group A, B, C can run simultaneously

### 🏎️ GROUP 2A: Vehicle Registration → Valuation Workflow

#### Task 04: Backend - Verify/complete vehicle API routes
- **Agent:** CoderAgent
- **Depends on:** Wave 1 complete (token expiry)
- **Parallel:** Yes (can run with 09, 10 simultaneously)
- **Files:**
  - `backend/src/routes/vehicles.ts` (verify/complete)
- **Acceptance Criteria:**
  - ✓ GET /vehicles endpoint returns all vehicles
  - ✓ POST /vehicles endpoint creates new vehicle with validation
  - ✓ Vehicle data persists to database
  - ✓ Routes return proper error responses for invalid input
  - ✓ All routes require authentication

#### Task 05: Frontend - Create VehicleForm component
- **Agent:** CoderAgent
- **Depends on:** Task 04 (API routes ready)
- **Parallel:** Yes (with Tasks 06, 07)
- **Files:**
  - `frontend/app/components/VehicleForm.vue` (NEW)
- **Acceptance Criteria:**
  - ✓ VehicleForm component accepts vehicle object as prop
  - ✓ Form includes: type, make, model, year, VIN, registration
  - ✓ Form validates required fields
  - ✓ Form emits 'submit' event with vehicle data
  - ✓ Styling matches dashboard design system (glassmorphism, green accent)

#### Task 06: Frontend - Create vehicle list page
- **Agent:** CoderAgent
- **Depends on:** Task 05 (VehicleForm complete)
- **Parallel:** Yes (with Task 07)
- **Files:**
  - `frontend/app/pages/vehicles/list.vue` (NEW)
- **Acceptance Criteria:**
  - ✓ Page fetches vehicles from API on mount
  - ✓ Vehicles display in table/card grid with type, make, model, year
  - ✓ Page includes 'Add Vehicle' button linking to register page
  - ✓ Each vehicle shows edit/delete actions
  - ✓ Styling matches dashboard design system

#### Task 07: Frontend - Create vehicle registration page
- **Agent:** CoderAgent
- **Depends on:** Task 06 (list page complete)
- **Parallel:** No
- **Files:**
  - `frontend/app/pages/vehicles/register.vue` (NEW)
- **Acceptance Criteria:**
  - ✓ Page displays VehicleForm component
  - ✓ Page accepts optional property_id as query param
  - ✓ Form submission calls POST /vehicles API
  - ✓ On success: links vehicle to property and redirects to list
  - ✓ On error: displays validation error message

#### Task 08: E2E test - Vehicle registration to valuation workflow
- **Agent:** TestEngineer
- **Depends on:** Task 07 (register page complete)
- **Parallel:** No
- **Files:**
  - `tests/e2e/phase4-workflows.spec.ts` (add test)
- **Acceptance Criteria:**
  - ✓ Test navigates to vehicle registration page
  - ✓ Test fills vehicle form with valid data
  - ✓ Test submits form and confirms API success
  - ✓ Test verifies vehicle appears in list
  - ✓ Test verifies vehicle linked to property
  - ✓ Test passes consistently

---

### 🕸️ GROUP 2B: Web Scraper E2E Tests

#### Task 09: E2E tests - Web scraper (8 scenarios)
- **Agent:** TestEngineer
- **Depends on:** Wave 1 complete (token expiry)
- **Parallel:** Yes (can run with Tasks 04-07, 10-11 simultaneously)
- **Files:**
  - `tests/e2e/phase3-compliance-scraper.spec.ts` (NEW)
- **Acceptance Criteria:**
  - ✓ Scenario 1: Successful market data scrape returns data
  - ✓ Scenario 2: Property attributes extracted correctly
  - ✓ Scenario 3: Scraper retries on timeout
  - ✓ Scenario 4: Error handling for invalid URL
  - ✓ Scenario 5: Data validation post-scrape
  - ✓ Scenario 6: Rate limiting compliance enforced
  - ✓ Scenario 7: Data cache updated correctly
  - ✓ Scenario 8: Fallback to cached data on failure
  - ✓ All 8 scenarios pass consistently

---

### ⚖️ GROUP 2C: License Validation (Ethiopian Format)

#### Task 10: Frontend - License validation utility
- **Agent:** CoderAgent
- **Depends on:** Wave 1 complete (token expiry)
- **Parallel:** Yes (can run with Tasks 04-09 simultaneously)
- **Files:**
  - `frontend/app/utils/ethiopianValidation.ts` (update)
- **Acceptance Criteria:**
  - ✓ Export validateEthiopianLicense() function
  - ✓ Function accepts license string parameter
  - ✓ Function validates Ethiopian business license format
  - ✓ Function returns boolean (valid/invalid)
  - ✓ Function rejects invalid formats with clear message
  - ✓ Function accepts valid formats

#### Task 11: Backend - License validation endpoint
- **Agent:** CoderAgent
- **Depends on:** Task 10 (validator utility ready)
- **Parallel:** Yes (with Task 12)
- **Files:**
  - `backend/src/validators/license.ts` (NEW)
  - Backend route registration for /validate/license
- **Acceptance Criteria:**
  - ✓ POST /validate/license endpoint accepts license string
  - ✓ Endpoint validates against Ethiopian business license format
  - ✓ Endpoint returns {valid: boolean, error?: string}
  - ✓ Rejects invalid licenses with error message
  - ✓ Accepts valid licenses
  - ✓ Requires authentication

#### Task 12: E2E test - License validation scenarios
- **Agent:** TestEngineer
- **Depends on:** Task 11 (endpoint complete)
- **Parallel:** No
- **Files:**
  - `tests/e2e/phase3-compliance.spec.ts` (add test)
- **Acceptance Criteria:**
  - ✓ Test validates valid Ethiopian license formats
  - ✓ Test rejects invalid license formats
  - ✓ Test shows error message for invalid input
  - ✓ Test passes consistently
  - ✓ Test covers edge cases

---

## 🌊 WAVE 3: Advanced Features (Reports + Status)
**Status:** Ready after Wave 2 complete
**Duration:** 9-11 hours (parallel execution)
**Parallelization:** YES — Group A, B can partially overlap

### 📄 GROUP 3A: Compliance Reports Generation

#### Task 13: Backend - Report generation service
- **Agent:** CoderAgent
- **Depends on:** Wave 2 complete (vehicle, scraper, license)
- **Parallel:** Yes (with Task 14, 17)
- **Files:**
  - `backend/src/services/reportGenerator.ts` (NEW)
- **Acceptance Criteria:**
  - ✓ Export generateComplianceReport() function
  - ✓ Function accepts valuation_id parameter
  - ✓ Function fetches valuation, vehicle, and property data
  - ✓ Function includes Ethiopian-specific compliance fields
  - ✓ Function generates PDF output
  - ✓ Function returns PDF buffer or file path

#### Task 14: Backend - Report API routes
- **Agent:** CoderAgent
- **Depends on:** Task 13 (service ready)
- **Parallel:** Yes (with Task 15)
- **Files:**
  - `backend/src/routes/reports.ts` (NEW)
- **Acceptance Criteria:**
  - ✓ POST /reports/compliance endpoint generates report
  - ✓ Endpoint accepts valuation_id in body
  - ✓ Endpoint calls reportGenerator service
  - ✓ Endpoint returns PDF file for download
  - ✓ Endpoint includes proper headers (Content-Type, Content-Disposition)
  - ✓ Requires authentication

#### Task 15: Frontend - Compliance report page
- **Agent:** CoderAgent
- **Depends on:** Task 14 (API routes ready)
- **Parallel:** Yes (with Task 16)
- **Files:**
  - `frontend/app/pages/reports/compliance.vue` (NEW)
- **Acceptance Criteria:**
  - ✓ Page displays list of valuations with 'Generate Report' button
  - ✓ Button calls POST /reports/compliance API
  - ✓ Page displays loading state during generation
  - ✓ On success: triggers PDF download
  - ✓ On error: displays error message
  - ✓ Styling matches dashboard design system

#### Task 16: E2E test - Compliance report generation
- **Agent:** TestEngineer
- **Depends on:** Task 15 (page complete)
- **Parallel:** No
- **Files:**
  - `tests/e2e/phase3-compliance-reports.spec.ts` (NEW)
- **Acceptance Criteria:**
  - ✓ Test navigates to compliance reports page
  - ✓ Test selects a valuation
  - ✓ Test clicks 'Generate Report' button
  - ✓ Test waits for PDF generation
  - ✓ Test verifies PDF download initiated
  - ✓ Test passes consistently

---

### 🔄 GROUP 3B: Valuation Status Workflow

#### Task 17: Backend - Valuation status enum and model updates
- **Agent:** CoderAgent
- **Depends on:** Wave 2 complete
- **Parallel:** Yes (can run with Tasks 13-14)
- **Files:**
  - `backend/src/models/Valuation.ts` (update)
- **Acceptance Criteria:**
  - ✓ Valuation model includes status field with enum
  - ✓ Status enum includes: Draft, Pending, Approved, Archived
  - ✓ Model exports status enum
  - ✓ Status defaults to Draft on creation
  - ✓ Status field persists to database

#### Task 18: Backend - Valuation status transitions service
- **Agent:** CoderAgent
- **Depends on:** Task 17 (model ready)
- **Parallel:** Yes (with Task 19)
- **Files:**
  - `backend/src/services/valuationService.ts` (update)
- **Acceptance Criteria:**
  - ✓ Export transitionStatus() function
  - ✓ Function validates status transitions (Draft→Pending→Approved→Archived)
  - ✓ Function prevents invalid transitions
  - ✓ Function updates database on valid transition
  - ✓ Function returns updated valuation
  - ✓ Function includes audit logging

#### Task 19: E2E test - Valuation status workflow
- **Agent:** TestEngineer
- **Depends on:** Task 18 (service ready)
- **Parallel:** No
- **Files:**
  - `tests/e2e/phase4-workflows.spec.ts` (update)
- **Acceptance Criteria:**
  - ✓ Test creates a new valuation in Draft status
  - ✓ Test transitions from Draft to Pending
  - ✓ Test transitions from Pending to Approved
  - ✓ Test transitions from Approved to Archived
  - ✓ Test prevents invalid transitions
  - ✓ Test verifies status persists after refresh
  - ✓ Test passes consistently

---

## 📊 EXECUTION TIMELINE

```
WAVE 1 (Sequential)
├─ Task 01: Token Validation (1-2h)
├─ Task 02: Auth Middleware (1-2h)
└─ Task 03: E2E Test (1-2h)
    ↓ (unblocks Wave 2)

WAVE 2 (Parallel)
├─ GROUP 2A: Vehicle Workflow
│  ├─ Task 04: Backend API (1-2h)
│  ├─ Task 05: VehicleForm (1-2h)
│  ├─ Task 06: List Page (1-2h)
│  ├─ Task 07: Register Page (1-2h)
│  └─ Task 08: E2E Test (1-2h)
│
├─ GROUP 2B: Web Scraper Tests (parallel to Group 2A)
│  └─ Task 09: 8 E2E Scenarios (4-6h)
│
└─ GROUP 2C: License Validation (parallel to Groups 2A & 2B)
   ├─ Task 10: Frontend Util (1-2h)
   ├─ Task 11: Backend Endpoint (1-2h)
   └─ Task 12: E2E Test (1-2h)
    ↓ (unblocks Wave 3)

WAVE 3 (Parallel)
├─ GROUP 3A: Compliance Reports
│  ├─ Task 13: Report Service (1-2h)
│  ├─ Task 14: API Routes (1-2h)
│  ├─ Task 15: Frontend Page (1-2h)
│  └─ Task 16: E2E Test (1-2h)
│
└─ GROUP 3B: Status Workflow (partial parallel to 3A)
   ├─ Task 17: Model Updates (1h)
   ├─ Task 18: Service Logic (1-2h)
   └─ Task 19: E2E Test (1-2h)
```

---

## 🎯 AGENT ASSIGNMENT RECOMMENDATIONS

### CoderAgent (Frontend/Backend Development)
- **Wave 1:** Tasks 01, 02
- **Wave 2:** Tasks 04, 05, 06, 07, 10, 11
- **Wave 3:** Tasks 13, 14, 15, 17, 18
- **Total:** ~13-14 hours

### TestEngineer (E2E Testing)
- **Wave 1:** Task 03
- **Wave 2:** Tasks 08, 09, 12
- **Wave 3:** Tasks 16, 19
- **Total:** ~12-14 hours

---

## ✅ Task Completion Checklist

### Wave 1
- [ ] Task 01: Token validation in useAuth.ts
- [ ] Task 02: Auth middleware created
- [ ] Task 03: E2E token expiry test passes

### Wave 2A (Vehicle Workflow)
- [ ] Task 04: Vehicle API routes verified
- [ ] Task 05: VehicleForm component created
- [ ] Task 06: Vehicle list page created
- [ ] Task 07: Vehicle register page created
- [ ] Task 08: Vehicle workflow E2E test passes

### Wave 2B (Web Scraper)
- [ ] Task 09: 8 web scraper E2E scenarios passing

### Wave 2C (License)
- [ ] Task 10: License validation utility created
- [ ] Task 11: License validation endpoint created
- [ ] Task 12: License validation E2E test passes

### Wave 3A (Reports)
- [ ] Task 13: Report generation service created
- [ ] Task 14: Report API routes created
- [ ] Task 15: Compliance report page created
- [ ] Task 16: Report generation E2E test passes

### Wave 3B (Status)
- [ ] Task 17: Valuation status model updated
- [ ] Task 18: Status transition service created
- [ ] Task 19: Status workflow E2E test passes

---

## 📝 Notes

- **All subtasks have JSON definitions** in `.tmp/tasks/critical-features/subtask_NN.json` for programmatic access
- **No dependencies between Groups 2A, 2B, 2C** — assign to different agents for maximum parallelization
- **Wave 3 can partially start** once Wave 2 is 50% complete (Tasks 13-14-17 don't depend on all Wave 2 tasks)
- **Total execution time with parallelization:** ~2-3 days vs 3-4 days sequential
- **Success metric:** All 19 subtasks complete with passing E2E tests


---

## 📊 EXECUTION STATUS

### ✅ Wave 1: COMPLETE
- Task 01: useAuth.ts ✅
- Task 02: auth.ts middleware ✅  
- Task 03: E2E test ✅
- **Status:** Pushed to GitHub (commit 87555f4)

### 🟡 Wave 2: READY TO START

**Group 2A (Vehicle Workflow) - Ready for assignment**
- Task 04: Backend API verification
- Task 05: VehicleForm component
- Task 06: Vehicle list page
- Task 07: Vehicle register page
- Task 08: E2E test

**Note:** Backend route structure needs to be confirmed (routes directory may not exist)
