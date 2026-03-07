# VA-60: Sprint 3 QA & Deployment Checklist

## Pre-Deployment Verification

### Frontend
- [ ] Run `npm run build` in `frontend/app` - verify no errors
- [ ] Run `npm run test` (Vitest) - verify unit tests pass
- [ ] Run `npm run test:e2e` (Playwright) - verify E2E tests pass
- [ ] Verify all pages load: `/`, `/login`, `/dashboard`, `/properties`, `/valuations`, `/map`, `/users`, `/analytics`, `/settings`
- [ ] Test responsive design on tablet (768px) and mobile (480px)
- [ ] Verify map property markers with clustering work
- [ ] Verify user management CRUD operations

### Backend
- [ ] Run `pytest` - verify all tests pass
- [ ] Verify API health at `/api/v1/health` (if exists)
- [ ] Verify property API returns `latitude`/`longitude` for map

### Integration
- [ ] Login flow: landing → login → dashboard
- [ ] Auth redirect: unauthenticated → `/login`
- [ ] API base URL from `NUXT_PUBLIC_API_BASE_URL` env

## Staging Environment

```bash
# Frontend
cd frontend/app
NUXT_PUBLIC_API_BASE_URL=https://api.staging.valuadis.gov.et npm run build
# Deploy dist/ to CDN or static host

# Backend
# Deploy FastAPI with uvicorn, set CORS origins for staging frontend URL
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NUXT_PUBLIC_API_BASE_URL` | Backend API URL |
| `NUXT_PUBLIC_MAP_DEFAULT_LAT` | Default map center lat |
| `NUXT_PUBLIC_MAP_DEFAULT_LNG` | Default map center lng |

## Sprint 3 Completed Tasks

- VA-53: Map property markers with clustering ✅
- VA-54: User management page ✅
- VA-55: Responsive design ✅
- VA-56: Frontend unit tests (Vitest) ✅
- VA-57: E2E tests (Playwright) ✅
- VA-58: Accessibility (ARIA, landmarks) ✅
- VA-59: Performance (code splitting) ✅
- VA-60: QA & Deployment prep ✅
