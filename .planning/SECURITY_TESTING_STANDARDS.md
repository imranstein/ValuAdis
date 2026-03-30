# Security Testing Standards

## Overview

This document defines security testing standards for the ValuAdis platform. Security tests cover OWASP Top 10 (2021), dependency scanning, and auth/session integrity.

## Tooling

| Layer | Tool | Location |
|-------|------|----------|
| OWASP E2E tests | Playwright | `tests/e2e/security-owasp.spec.ts` |
| Security helpers | TypeScript | `tests/e2e/security.helpers.ts` |
| Auth unit tests | Vitest/Jest | `tests/unit/auth.security.test.ts` |
| Input validation tests | Vitest/Jest | `tests/unit/validation.security.test.ts` |
| Session security tests | Vitest/Jest | `tests/unit/session.security.test.ts` |
| Dependency scanning | npm audit + bandit | `.github/workflows/security-scan.yml` |
| Pre-commit hook | Husky | `.husky/pre-commit` |

## OWASP Top 10 (2021) Coverage

### A01 — Broken Access Control
- Tests: `tests/e2e/security-owasp.spec.ts`
- What is verified:
  - Unauthenticated users cannot access protected routes (`/dashboard`, `/vehicles`, `/valuations`)
  - Users cannot access resources belonging to other users
  - Role-based access is enforced (e.g., admin-only endpoints reject non-admin tokens)
- Pass criteria: All protected route requests redirect to `/login` or return HTTP 401/403

### A02 — Cryptographic Failures
- Tests: `tests/e2e/security-owasp.spec.ts`, `tests/unit/auth.security.test.ts`
- What is verified:
  - JWT tokens use RS256 or HS256 (not `none` algorithm)
  - Tampered token payloads are rejected
  - Expired tokens return 401 and trigger re-login
  - Passwords are never stored or logged in plaintext
- Pass criteria: All tamper/expiry scenarios result in auth rejection

### A03 — Injection
- Tests: `tests/unit/validation.security.test.ts`
- What is verified:
  - SQL injection payloads in input fields are rejected by backend validation
  - XSS payloads (`<script>`, `javascript:`, `onerror=`) are sanitised before render
  - Command injection characters (`; | && ||`) are stripped from API inputs
- Pass criteria: Payloads do not execute or return raw SQL errors

### A04 — Insecure Design
- Manual review required (no automated test)
- Checklist items:
  - Auth flows include rate limiting on login attempts
  - Password reset tokens are single-use and expire in 15 minutes
  - Valuation data is scoped to authenticated user's organisation

### A05 — Security Misconfiguration
- Tests: `.github/workflows/security-scan.yml` (headers check)
- What is verified:
  - HTTP security headers present: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security`
  - Debug endpoints (`/docs`, `/redoc`) are disabled in production
- Pass criteria: All headers present in production response

### A06 — Vulnerable and Outdated Components
- Tests: `scripts/scan-dependencies.sh`, pre-commit hook
- What is verified:
  - `npm audit` reports zero critical vulnerabilities on commit
  - Python `bandit` scan reports no high-severity findings
  - Safety DB scan of `requirements.txt` reports zero known CVEs
- Pass criteria: CI blocks merge on any critical/high finding

### A07 — Identification and Authentication Failures
- Tests: `tests/unit/auth.security.test.ts`, `tests/unit/session.security.test.ts`
- What is verified:
  - JWT signature validation rejects tokens signed with incorrect key
  - Session tokens are regenerated after login (session fixation prevention)
  - CSRF token validation on state-mutating requests
  - Password complexity requirements enforced
- Pass criteria: All invalid/replayed session attempts rejected

### A08 — Software and Data Integrity Failures
- Manual review required
- Checklist items:
  - CI pipeline uses pinned action versions (not `@latest`)
  - NPM packages use lock files committed to repo
  - No unsigned packages accepted in build

### A09 — Security Logging and Monitoring Failures
- Manual review required
- Checklist items:
  - Failed login attempts logged with IP and timestamp
  - Auth token rejections logged at WARN level
  - Logs do not contain PII or credentials

### A10 — Server-Side Request Forgery (SSRF)
- Tests: `tests/unit/validation.security.test.ts`
- What is verified:
  - URL inputs that resolve to internal addresses (`169.254.x.x`, `10.x.x.x`, `localhost`) are rejected
- Pass criteria: Internal URL requests blocked before network call

## Dependency Scanning Policy

- `npm audit` runs on every `git commit` via Husky pre-commit hook
- Full scan (npm + Python) runs in CI on every PR via `.github/workflows/security-scan.yml`
- Critical vulnerabilities block merge — no exceptions without security team approval
- High vulnerabilities must be resolved within 7 days of detection
- Medium vulnerabilities tracked in the backlog — not merge-blocking

## Adding Security Tests to New Features

When adding a new feature:

1. **New auth mechanism**: Add unit tests to `tests/unit/auth.security.test.ts` covering token lifecycle (issue, expiry, rejection).

2. **New user input field**: Add sanitisation tests to `tests/unit/validation.security.test.ts` with at least: XSS payload, SQL injection payload, and boundary-length input.

3. **New protected route**: Add an E2E test to `tests/e2e/security-owasp.spec.ts` confirming unauthenticated access is denied and redirected.

4. **New API endpoint**: Verify the endpoint is listed in the route-level auth middleware. Add a test asserting a request with no token returns 401.

5. **New external dependency**: Run `npm audit` and `bandit` locally before committing. Document the package's purpose in the PR description.

## Security Test Run Commands

```bash
# Unit security tests
npx vitest run tests/unit/auth.security.test.ts
npx vitest run tests/unit/validation.security.test.ts
npx vitest run tests/unit/session.security.test.ts

# OWASP E2E tests
npx playwright test tests/e2e/security-owasp.spec.ts

# Dependency scan (manual)
bash scripts/scan-dependencies.sh

# npm audit only
npm audit --audit-level=critical
```
