# VALU Tasks Backup (from Jira SCRUM project)

Backup date: 2026-02-26  
Source: imransteina.atlassian.net, project SCRUM (Team AI)

---

## SCRUM-77 | Epic
**Summary:** VALU-EPIC-1: Documentation & Setup (20 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 1: Documentation & Setup (20 tasks)
Duration: Week 1 (Feb 25 - Mar 3, 2026)
This epic covers all documentation creation and project setup activities required to establish the foundation for the ValuAdis Ethiopian Property Valuation Platform.

Tasks Included:
- VALU-1: Create Master SRS document ✅
- VALU-2: Create Backend SRS and Guidelines ✅
- VALU-3: Create Frontend SRS and Guidelines ✅
- VALU-4: Create Mobile SRS and Guidelines ✅
- VALU-5: Create Database SRS ✅
- VALU-6: Create Testing Guidelines ✅
- VALU-7: Create System Architecture documentation ✅
- VALU-8: Create Project Timeline ✅
- VALU-9: Initialize Memory Bank ✅
- VALU-10: Update VA-source-of-truth skill ✅
- VALU-11: Create .gitignore and README ✅
- VALU-12: Create Docker configuration ✅
- VALU-13: Setup GitHub repository ✅
- VALU-14: Configure GitHub Actions CI/CD
- VALU-15: Setup JIRA project
- VALU-16: Create development environment
- VALU-17: Configure pre-commit hooks
- VALU-18: Setup Sentry error tracking
- VALU-19: Configure environment variables
- VALU-20: Create development workflow documentation

Status: 13/20 tasks completed (65%)
Remaining: 7 tasks for CI/CD and development environment setup

---

## SCRUM-78 | Epic
**Summary:** VALU-EPIC-2: Backend API Development (50 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 2: Backend API Development (50 tasks)
Duration: Week 2 (Mar 4 - Mar 10, 2026)
This epic covers the complete backend development using FastAPI, PostgreSQL + PostGIS, Redis, and various integrations for the ValuAdis platform.

Key Components: FastAPI REST API with JWT authentication, PostgreSQL database with PostGIS for geospatial data, Redis caching layer, M-Pesa payment integration, PDF certificate generation (ReportLab), Spatial calculations (Shapely).

Major Task Groups: Database Setup & Models (10 tasks), Core Services Development (15 tasks), API Endpoints Implementation (15 tasks), Testing & Quality Assurance (10 tasks).

Technology Stack: FastAPI (Python 3.11+), PostgreSQL 15 + PostGIS 3.3, Redis 7.x, SQLAlchemy 2.0, Shapely for spatial calculations, ReportLab for PDF generation, M-Pesa Ethiopia API.

Success Criteria: All API endpoints functional, 80% test coverage achieved, Spatial calculations working accurately, Payment integration tested in sandbox, PDF generation compliant with Proclamation 1365/2025.

---

## SCRUM-79 | Epic
**Summary:** VALU-EPIC-3: Frontend Web Dashboard (40 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 3: Frontend Web Dashboard (40 tasks)
Duration: Week 3 (Mar 11 - Mar 17, 2026)
This epic covers the complete frontend development using Vue.js 3, Nuxt.js 3, and PrimeVue components for the ValuAdis web dashboard.

Key Components: Vue.js 3 with Composition API, Nuxt.js 3 for SSR/SSG, PrimeVue UI component library, Pinia for state management, Leaflet.js for interactive maps, Axios for API communication.

Major Features: Authentication & User Management, Property Management (CRUD operations), Interactive GIS Mapping with boundary drawing, Valuation Calculator, Certificate Generation & Download, Payment Portal with M-Pesa integration, Admin Dashboard, Analytics & Reporting.

Technology Stack: Vue.js 3 (Composition API), Nuxt.js 3 (SSR/SSG), PrimeVue 7.x, Pinia, Leaflet.js + OpenStreetMap, Axios, Vuelidate (form validation), Playwright (E2E testing).

Success Criteria: 70% test coverage achieved, Responsive design (mobile-first), Lighthouse score >90, All user flows functional, Accessibility compliance (WCAG 2.1).

---

## SCRUM-80 | Epic
**Summary:** VALU-EPIC-4: Mobile App Development (30 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 4: Mobile App Development (30 tasks)
Duration: Week 4 (Mar 18 - Mar 24, 2026)
This epic covers the complete mobile app development using Flutter for the ValuAdis offline-first property valuation application.

Key Features: Offline-first architecture (7-day capability), GPS boundary mapping with 5m accuracy, Photo capture and management, Background synchronization, Field collection forms, Local data storage (SQLite + Hive).

Technology Stack: Flutter 3.x, SQLite, Hive, BLoC (state management), flutter_map (OpenStreetMap), geolocator (GPS), image_picker (camera), WorkManager (background sync).

Success Criteria: 75% test coverage achieved, 7-day offline capability verified, GPS accuracy <5m in field conditions, Background sync working reliably, Cross-platform compatibility (iOS + Android).

---

## SCRUM-81 | Epic
**Summary:** VALU-EPIC-5: Integration & Testing (15 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 5: Integration & Testing (15 tasks)
Duration: Week 5 (Mar 25 - Mar 30, 2026)
This epic covers comprehensive integration testing, quality assurance, and final validation of the ValuAdis platform before production launch.

Testing Scope: End-to-End Testing (Web + Mobile), API Integration Testing, Payment Gateway Testing, Offline Sync Testing, GPS Accuracy Testing, PDF Generation Testing, Load Testing & Performance, Security Audit & Penetration Testing, Compliance Verification, Bug Fixing & Optimization.

Testing Tools: Playwright (E2E web testing), Flutter Test (mobile testing), pytest (backend testing), JMeter (load testing), OWASP ZAP (security testing), Lighthouse (performance testing).

Success Criteria: All critical user flows tested, Zero critical security vulnerabilities, Performance benchmarks met, Compliance requirements satisfied.

---

## SCRUM-82 | Epic
**Summary:** VALU-EPIC-6: Deployment & Launch (15 tasks)  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Epic 6: Deployment & Launch (15 tasks)
Duration: Week 5 (Mar 25 - Mar 30, 2026)
This epic covers production deployment, beta tester onboarding, and the official launch of the ValuAdis Ethiopian Property Valuation Platform.

Deployment Infrastructure: cPanel hosting environment (MVP), PostgreSQL + PostGIS database, Redis caching layer, Docker container orchestration, SSL/TLS configuration, DNS and domain setup, Monitoring and logging.

Launch Date: March 30, 2026
Success Metrics: 99% uptime achieved, 5 beta firms onboarded, 50+ properties valued, 50+ certificates generated, Zero critical security issues.

---

## SCRUM-116 | Task
**Summary:** VALU-33: Create market value calculation algorithm  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Create market value calculation algorithm with multiple valuation methods and Ethiopian market factors.

Valuation Methods: Comparable sales approach, Cost approach (replacement cost), Income approach (for rental properties), Land residual method, Hybrid valuation methods.

Market Factors: Location premium/discount, Neighborhood quality scores, Accessibility factors, Market trends and inflation, Supply and demand dynamics, Economic indicators.

Algorithm Components: Base value calculation, Adjustment factors application, Weighted averaging of methods, Confidence scoring, Sensitivity analysis.

Status: ⏳ PENDING | Priority: High | Estimated Time: 3 days | Dependencies: VALU-30

---

## SCRUM-117 | Task
**Summary:** VALU-34: Implement 25% taxable value computation  
**Status:** To Do | **Priority:** Medium | **Created:** 2026-02-25

**Description:**
Implement 25% taxable value computation as per Proclamation 1365/2025 Ethiopian property tax law.

Taxable Value Calculation: 25% of market value (standard rate), Different rates for different property types, Exemptions and deductions, Minimum taxable thresholds, Maximum taxable limits.

Compliance Features: Proclamation 1365/2025 compliance, Audit trail for tax calculations, Documentation generation, Legal reference tracking, Regulation updates.

Status: ⏳ PENDING | Priority: High | Estimated Time: 1 day | Dependencies: VALU-33

---

## Sprint mapping (for re-creation)
| Sprint ID | Sprint name | Old keys (deleted) | New keys (re-created 2026-02-26) |
|-----------|-------------|--------------------|-----------------------------------|
| 9 | VALU S1: Doc & foundation | SCRUM-77 | SCRUM-254 |
| 8 | VALU Sprint 2: Backend & API | SCRUM-78, 116, 117 | SCRUM-255, 256, 257 |
| 10 | VALU S3: Frontend & dashboard | SCRUM-79 | SCRUM-258 |
| 12 | VALU S4: Integration & test | SCRUM-80, 81 | SCRUM-259, 260 |
| 11 | VALU S5: QA handoff Mar 31 | SCRUM-82 | SCRUM-261 |

**Re-creation:** All 8 issues were deleted and re-created with sprint assignment via `jira_create_issue` + `additional_fields: {"customfield_10020": <sprint_id>}`. Sprints were not re-created (existing IDs 8–12 used). Board shows issues in correct sprints.
