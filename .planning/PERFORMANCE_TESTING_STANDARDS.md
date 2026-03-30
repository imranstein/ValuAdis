# Performance Testing Standards

## Overview

This document defines performance testing standards for the ValuAdis platform. All performance tests must conform to these baselines and thresholds before merging to main.

## Tooling

| Layer | Tool | Location |
|-------|------|----------|
| E2E page load metrics | Playwright + custom helpers | `tests/e2e/performance.helpers.ts` |
| API load testing | k6 | `tests/performance/k6-load-test.js` |
| Baselines reference | JSON snapshot | `tests/performance/baseline.json` |

## Baseline Metrics

These baselines were established during subtask 01 (E2E) and subtask 03 (API) and must not be exceeded in CI.

### Frontend — Page Load (Playwright)

| Flow | Metric | Threshold |
|------|--------|-----------|
| Login page initial load | Time to Interactive | < 2000ms |
| Dashboard load (authenticated) | Time to Interactive | < 3000ms |
| Vehicle list page | Time to Interactive | < 2500ms |
| Map page | Time to Interactive | < 3500ms |
| Valuation wizard step render | Time to Interactive | < 2000ms |
| API response (frontend → backend) | Round-trip | < 500ms |

### Backend — API Endpoints (k6)

| Endpoint | p95 Response Time | Error Rate |
|----------|-------------------|------------|
| `POST /auth/login` | < 300ms | < 0.1% |
| `GET /vehicles` | < 500ms | < 0.1% |
| `GET /valuations` | < 500ms | < 0.1% |
| `POST /valuations` | < 800ms | < 0.1% |
| `GET /compliance/reports` | < 600ms | < 0.1% |

### Load Test Thresholds

- Concurrent users: 100
- Test duration: 5 minutes (steady state)
- Ramp-up: 30 seconds
- Degradation limit: 10% above baseline before threshold check fails
- Error rate limit: < 1% at full load

## Running Performance Tests

### E2E Performance Tests

```bash
# Run all E2E tests including performance metrics
npx playwright test tests/e2e/phase1-foundation.spec.ts --reporter=json

# Output captured to: tests/e2e/performance-report.json
```

### API Load Tests (k6)

```bash
# Install k6 (one-time)
brew install k6

# Run load test against local dev server
k6 run tests/performance/k6-load-test.js

# Run against staging
K6_BASE_URL=https://staging.valuadis.com k6 run tests/performance/k6-load-test.js
```

### Interpreting Results

See `TESTING_RUNBOOK.md` for step-by-step guidance on reading reports and triaging failures.

## Adding Performance Tests to New Features

When a new user-facing page or API endpoint is added:

1. **Frontend pages**: Add a timing assertion to the relevant E2E spec using `measurePageLoad()` from `tests/e2e/performance.helpers.ts`. Set the threshold at the value measured in development (round up to nearest 500ms).

2. **API endpoints**: Add the endpoint to `tests/performance/endpoints.yaml` with its expected p95 threshold. The k6 script reads this file dynamically.

3. **Update baselines**: After the feature is stable, run the k6 baseline capture:
   ```bash
   k6 run tests/performance/k6-load-test.js --env CAPTURE_BASELINE=true
   ```
   Commit the updated `tests/performance/baseline.json`.

4. **CI check**: The GitHub Actions `security-scan.yml` workflow also runs k6 on PRs. Ensure thresholds are realistic — do not set thresholds so tight that they fail on a slow CI runner.

## Regression Policy

- A PR that causes p95 to increase by > 10% on any endpoint will fail CI.
- A PR that causes page load to exceed any threshold will fail CI.
- Regressions must be investigated before merge — not suppressed by raising thresholds without justification.
- Threshold changes require a comment in the PR explaining why the new value is acceptable.
