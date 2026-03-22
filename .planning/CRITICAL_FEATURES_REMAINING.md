# 🔴 CRITICAL FEATURES REMAINING — Must Complete

**Last Updated:** 2026-03-22
**Priority:** BLOCKING RELEASE
**Status:** Not Started → In Progress

---

## 1. 🔐 **Token Expiry Handling** (Phase 1 - Security)

**Category:** Authentication / Security
**Severity:** HIGH — Security vulnerability
**Effort:** 2-4 hours

### Requirements
- Implement token expiry detection in frontend
- Auto-logout when token expires
- Graceful error handling with redirect to login
- E2E test for token expiry scenario

### Acceptance Criteria
- [ ] Token validation on app initialization
- [ ] Automatic logout on expiry
- [ ] User redirect to login with clear message
- [ ] E2E test passing: Token Expiry scenario

### Files to Modify
- `frontend/app/composables/useAuth.ts` — Add token expiry check
- `frontend/app/middleware/auth.ts` — Add expiry middleware
- `tests/e2e/phase1-foundation.spec.ts` — Add token expiry test

### Dependencies
- None (core auth system)

---

## 2. 🚗 **Vehicle Registration → Valuation Workflow** (Phase 4 - Core Business)

**Category:** Business Workflow
**Severity:** HIGH — Core feature
**Effort:** 6-8 hours

### Requirements
- Create vehicle registration form
- Link vehicle to property valuation
- Display vehicle data in valuation context
- Complete end-to-end workflow test

### Acceptance Criteria
- [ ] Vehicle registration UI complete
- [ ] Vehicle data persisted to database
- [ ] Vehicle linked to property record
- [ ] Valuation references vehicle details
- [ ] E2E test: Full vehicle→valuation workflow

### Files to Create/Modify
- `frontend/app/pages/vehicles/register.vue` — NEW
- `frontend/app/pages/vehicles/list.vue` — NEW
- `frontend/app/components/VehicleForm.vue` — NEW
- `backend/src/routes/vehicles.ts` — Existing, verify completeness
- `tests/e2e/phase4-workflows.spec.ts` — Add vehicle workflow test

### Dependencies
- Database schema (vehicles table) — ✅ Already exists
- API endpoints — ✅ Already exists

---

## 3. 📋 **Web Scraper E2E Tests** (Phase 3 - Integration)

**Category:** Data Integration / Testing
**Severity:** HIGH — Compliance & market data
**Effort:** 4-6 hours

### Requirements
- Implement 8 E2E test scenarios for web scraper
- Test market data retrieval
- Test property attribute mapping
- Test error handling for scraper failures

### Test Scenarios
1. [ ] Successful market data scrape
2. [ ] Property attribute extraction
3. [ ] Scraper retry on timeout
4. [ ] Error handling for invalid URL
5. [ ] Data validation post-scrape
6. [ ] Rate limiting compliance
7. [ ] Data cache update
8. [ ] Fallback to cached data

### Files to Create
- `tests/e2e/phase3-compliance-scraper.spec.ts` — NEW

### Dependencies
- Web scraper API — Verify endpoint availability
- Test data sources — Define reliable test URLs

---

## 4. 📜 **License Validation (Ethiopian Format)** (Phase 3 - Compliance)

**Category:** Ethiopian Compliance
**Severity:** HIGH — Legal/compliance
**Effort:** 3-4 hours

### Requirements
- Validate Ethiopian business license format
- Implement license format checking
- Add E2E test for license validation

### Acceptance Criteria
- [ ] License format validation implemented
- [ ] Rejects invalid formats
- [ ] Accepts valid formats
- [ ] E2E test: License validation scenarios

### Files to Modify
- `frontend/app/utils/ethiopianValidation.ts` — Add license validator
- `backend/src/validators/license.ts` — Add backend validation
- `tests/e2e/phase3-compliance.spec.ts` — Add license test

### Dependencies
- None (validation-only)

---

## 5. 📊 **Compliance Reports Generation** (Phase 3 - Reporting)

**Category:** Reporting / Compliance
**Severity:** HIGH — Business requirement
**Effort:** 5-6 hours

### Requirements
- Generate compliance report from valuation data
- Include Ethiopian-specific compliance fields
- Export as PDF
- Add E2E test for report generation

### Acceptance Criteria
- [ ] Report generation API working
- [ ] PDF output includes all required fields
- [ ] Report accessible from UI
- [ ] E2E test: Generate and verify compliance report

### Files to Create/Modify
- `backend/src/services/reportGenerator.ts` — NEW
- `backend/src/routes/reports.ts` — NEW
- `frontend/app/pages/reports/compliance.vue` — NEW
- `tests/e2e/phase3-compliance-reports.spec.ts` — NEW

### Dependencies
- PDF library (likely pdfkit or similar)
- Valuation data schema — ✅ Exists

---

## 6. 🔄 **Valuation Status Workflow** (Phase 4 - Business Logic)

**Category:** Business Workflow
**Severity:** MEDIUM — Core feature
**Effort:** 4-5 hours

### Requirements
- Implement valuation status states: Draft → Pending → Approved → Archived
- Add status transitions with validation
- Restrict actions based on status
- Add E2E test for workflow

### Acceptance Criteria
- [ ] Status transitions implemented
- [ ] Validation prevents invalid transitions
- [ ] UI reflects current status
- [ ] E2E test: Full status workflow

### Files to Modify
- `backend/src/models/Valuation.ts` — Add status enum
- `backend/src/services/valuationService.ts` — Add status logic
- `frontend/app/pages/valuations/detail.vue` — Add status UI
- `tests/e2e/phase4-workflows.spec.ts` — Add status test

### Dependencies
- Valuation data schema — ✅ Exists

---

## 📊 Summary Table

| Feature | Phase | Status | Effort | Priority | Owner |
|---------|-------|--------|--------|----------|-------|
| Token Expiry | 1 | Not Started | 2-4h | 🔴 CRITICAL | TBD |
| Vehicle Workflow | 4 | Not Started | 6-8h | 🔴 CRITICAL | TBD |
| Web Scraper Tests | 3 | Not Started | 4-6h | 🔴 CRITICAL | TBD |
| License Validation | 3 | Not Started | 3-4h | 🔴 CRITICAL | TBD |
| Compliance Reports | 3 | Not Started | 5-6h | 🔴 CRITICAL | TBD |
| Status Workflow | 4 | Not Started | 4-5h | 🟡 MEDIUM | TBD |

**Total Effort:** 24-33 hours
**Estimated Timeline:** 3-4 days (with parallel work)

---

## 🚀 Next Steps

1. ✅ Review and approve critical features list
2. Create Jira tickets for each feature
3. Assign owners
4. Prioritize by blockers (Token Expiry, Vehicle Workflow should be first)
5. Update sprint planning with these items

---

## Notes

- All features have existing schema/API support
- Token expiry is pure security blocker
- Vehicle workflow and Web Scraper tests are core business logic
- Compliance items (license, reports) are regulatory requirements
- Status workflow enables proper business process

