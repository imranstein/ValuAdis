# Dependency Audit Report

**Date:** March 7, 2025  
**Scope:** `frontend/`, `frontend/app/`, `backend/`

---

## Executive Summary

| Area | Vulnerabilities | High | Moderate | Safe Fixes |
|------|-----------------|------|----------|------------|
| **frontend/** | 4 | 4 | 0 | Patch-only (Nuxt 3.21) |
| **frontend/app/** | 15 | 10 | 5 | Partial (audit fix + Nuxt upgrade) |
| **backend/** | 3+ | 2+ | 1+ | Patch upgrades available |

---

## 1. Frontend (`frontend/` — valuadis-frontend)

### Current State
- **Nuxt:** ^3.19.0 (resolves to 3.19.0)
- **Node modules:** May be missing (npm outdated showed MISSING for several packages)

### Vulnerabilities (4 high)

| ID | Package | Severity | Issue | Fix Path |
|----|---------|----------|-------|----------|
| 1 | serialize-javascript | High | RCE via RegExp.flags / Date.prototype.toISOString (GHSA-5c6j-r48x-rmvq) | Transitive via nitropack → @rollup/plugin-terser |
| 2 | @rollup/plugin-terser | — | Depends on vulnerable serialize-javascript | — |
| 3 | nitropack | — | Depends on vulnerable @rollup/plugin-terser | — |
| 4 | nuxt | — | Depends on vulnerable nitropack | — |

### Outdated Packages
- **nuxt:** 3.19.0 → 3.21.1 (patch) | 4.3.1 (major)
- **@pinia/nuxt:** 0.11.3 (current)

### Breaking Change Notes
- **Nuxt 3 → 4:** New directory structure, shallow data reactivity, Vite 6 env API, normalized component names. Use `npx nuxt upgrade` and `npx codemod nuxt/4/migration-recipe`.
- **serialize-javascript:** No upstream fix in Nuxt 3.x or 4.x; nitropack still uses @rollup/plugin-terser 0.4.4. **Override** is the only non-major option.

---

## 2. Frontend App (`frontend/app/` — valuadis-web)

### Current State
- **Nuxt:** ^3.10.0 (resolves to 3.17.7)
- **Vite:** ^5.0.11 (5.4.21)
- **Vue:** ^3.4.15

### Vulnerabilities (15 total: 10 high, 5 moderate)

| ID | Package | Severity | Issue | Fix |
|----|---------|----------|-------|-----|
| 1 | serialize-javascript | High | RCE (GHSA-5c6j-r48x-rmvq) | Override to 7.0.3+ |
| 2 | minimatch | High | ReDoS (GHSA-3ppc-4f35-3m26, GHSA-7r86-cg39-jmmj, GHSA-23c5-xmqv-rm74) | Upgrade @typescript-eslint/* → 8.x |
| 3 | nuxt | High | Client-side path traversal (GHSA-p6jq-8vc4-79f6) | Upgrade to 3.19.0+ |
| 4 | esbuild | Moderate | Dev server CORS (GHSA-67mh-4wv8-2f99) | Vite 7+ (breaking) or esbuild 0.25.0+ |
| 5 | vue-template-compiler | Moderate | XSS (GHSA-g3ch-rx76-35fx) | vue-tsc 3.x (breaking) |

### Outdated Packages (High-Confidence Upgrades)

| Package | Current | Wanted | Latest | Risk |
|---------|---------|--------|--------|------|
| nuxt | 3.17.7 | 3.21.1 | 4.3.1 | Patch: low; Major: high |
| @nuxt/eslint-config | 0.2.0 | 0.2.0 | 1.15.2 | Medium (config changes) |
| @pinia/nuxt | 0.5.5 | 0.5.5 | 0.11.3 | Low |
| postcss | 8.5.6 | 8.5.8 | 8.5.8 | None |
| @nuxt/devtools | 2.6.4 | 2.7.0 | 3.2.2 | Low |

### Likely Breaking Changes (Defer)

| Package | Current | Latest | Breaking Changes |
|---------|---------|--------|------------------|
| eslint | 8.57.1 | 10.0.3 | Flat config, rule changes |
| tailwindcss | 3.4.19 | 4.2.1 | v4 rewrite |
| vite | 5.4.21 | 7.3.1 | Major version jump |
| vitest | 3.2.4 | 4.0.18 | API changes |
| vue-tsc | 1.8.27 | 3.2.5 | Vue 3.5+ alignment |
| primevue | 3.53.1 | 4.5.4 | Major UI changes |
| pinia | 2.3.1 | 3.0.4 | Store API changes |
| vue-router | 4.6.4 | 5.0.3 | Route API changes |

---

## 3. Backend (`backend/` — Python)

### Current State
- **FastAPI:** 0.109.0
- **python-multipart:** 0.0.20
- **sentry-sdk:** 1.39.2

### Vulnerabilities

| Package | Current | Issue | Fixed In |
|---------|---------|-------|----------|
| fastapi | 0.109.0 | ReDoS in Content-Type parsing (PYSEC-2024-38) | 0.109.1+ |
| python-multipart | 0.0.20 | DoS via malformed boundary (CVE-2024-53981); Path traversal (CVE-2026-24486) in non-default config | 0.0.22+ |
| sentry-sdk | 1.39.2 | Env var exposure to subprocesses (GHSA-g92j-qhmh-64v2) | 1.45.1+ or 2.8.0+ |

### Other Packages (Patch Updates Recommended)
- **pydantic:** 2.5.3 → 2.10+ (security patches)
- **sqlalchemy:** 2.0.25 → 2.0.36+ (patches)
- **httpx:** 0.26.0 → 0.28+ (patches)

---

## 4. Smallest Safe Update Plan

### Phase 1: High-Confidence, Low-Risk ✅ APPLIED

#### Frontend (`frontend/`)
- Nuxt ^3.21.1, serialize-javascript override, .npmrc (legacy-peer-deps)
- **Result:** 0 vulnerabilities, build OK

#### Frontend App (`frontend/app/`)
- Nuxt ^3.21.1, postcss ^8.5.8, serialize-javascript override, .npmrc (legacy-peer-deps)
- **Result:** Build OK; 11 vulns remain (minimatch, esbuild, vue-tsc — require breaking upgrades)
- *Deferred:* @pinia/nuxt 0.11 (needs Pinia 3), @nuxt/eslint-config 1.15 (needs ESLint 9+)

#### Backend
```diff
# requirements.txt
-fastapi==0.109.0
+fastapi==0.109.2
-python-multipart==0.0.20
+python-multipart==0.0.22
-sentry-sdk[fastapi]==1.39.2
+sentry-sdk[fastapi]==1.45.1
```

### Phase 2: Override for serialize-javascript (Both Frontends)

Add to `package.json` in both `frontend/` and `frontend/app/`:

```json
{
  "overrides": {
    "serialize-javascript": ">=7.0.3"
  }
}
```

Then run `npm install`. **Verify build and tests** — overrides can cause compatibility issues.

### Phase 3: Deferred (Breaking Changes)

- **Nuxt 4:** Plan separate migration with codemods.
- **Vite 7, Tailwind 4, ESLint 10:** Schedule as separate upgrades.
- **PrimeVue 4, Pinia 3, Vue Router 5:** Coordinate with UI/UX changes.

---

## 5. Verification Checklist

After Phase 1 + 2:

- [ ] `cd frontend && npm run build`
- [ ] `cd frontend/app && npm run build`
- [ ] `cd frontend && npm run test:e2e` (if applicable)
- [ ] `cd frontend/app && npm test`
- [ ] `cd backend && pytest`
- [ ] `npm audit` in both frontends (expect remaining issues if override fails)
- [ ] `pip-audit` in backend (after `pip install pip-audit`)

---

## 6. Risk Summary

| Action | Risk | Mitigation |
|--------|------|------------|
| Nuxt 3.10→3.21 | Low | Patch range; run tests |
| serialize-javascript override | Medium | Test build; rollback if issues |
| Backend patch upgrades | Low | Pin exact patch versions |
| npm audit fix | Low | Review diff before commit |

---

*Generated by dependency audit. Re-run `npm audit` and `pip-audit` after applying changes.*
