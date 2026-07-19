# Zero-runtime-error console sweep — dev completion (web/backend)

Date: 2026-07-19
Branch: `fix/dev-completion-web`

## Environment

- Backend: `backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8030`,
  `DATABASE_URL=sqlite:///./valuadis_devcheck.db` (fresh sibling SQLite DB, dev-only
  schema sync via `Base.metadata.create_all()` — never one of the dirty local DBs).
- Frontend: `npm run build` with `NUXT_PUBLIC_API_BASE_URL=http://localhost:8030`,
  then `PORT=3000 node .output/server/index.mjs` (build+preview per the runbook —
  `nuxt dev` is broken on this stack).
- Browser: Playwright MCP (`mcp__playwright__browser_*`), navigated on
  `http://localhost:3000` (never `127.0.0.1`, per the runbook).
- Seed data: 3 accounts (staff/admin, property_owner, renter — `*@devcheck.dev`,
  password `DevcheckPass1!`), 2 properties, 2 photos, 1 published listing
  (`AA-LST-2026-251114`), 1 rented listing with an accepted application and a
  draft tenancy contract (`AA-LST-2026-575855` / `AA-RNT-2026-000001`) — seeded
  via direct API calls so every persona's pages have real content instead of
  all-empty states.

## Bug found and fixed during the sweep

`backend/app/main.py`'s `SecurityHeadersMiddleware` sets
`Cross-Origin-Resource-Policy: same-origin` on every response. That's correct
for the JSON API, but it also blocked the new photo-file endpoint
(`GET /api/v1/properties/{id}/photos/{id}/file`) from loading as an `<img src>`
on the frontend's origin (a different port by design) —
`net::ERR_BLOCKED_BY_RESPONSE.NotSameOrigin` in the console on both the public
listing gallery and the owner/officer photo panels. Fixed by special-casing
that one path pattern to `cross-origin`; every other response keeps the strict
`same-origin` default. See commit for `backend/app/main.py`.

## Routes visited (persona → route → result)

### Public (anonymous)
| Route | Result |
|---|---|
| `/` | clean |
| `/rent` | clean |
| `/rent/AA-LST-2026-251114` (published listing, has a photo) | clean after the CORP fix above (was 1 error before) |
| `/rent/AA-LST-2026-575855` (rented, no longer public) | app-level 404 + one browser-native "Failed to load resource: 404" console line — expected: `get_public_listing` correctly serves only `published` listings; a rented listing is honestly not public anymore. Not a bug. |
| `/rent/index` (district rent index — a distinct page from the `[publicId]` dynamic route) | clean, honest "Insufficient data yet" empty state |
| `/rent/signup` | clean |
| `/login` | clean once genuinely anonymous (see note below) |

**Note on `/auth/refresh` 401s:** the app's boot-time `authStore.initialize()`
silently probes for a refresh cookie on every route. For a truly anonymous
visitor this legitimately 401s and is logged by the browser as a resource-load
error — this is pre-existing architecture (httpOnly refresh-cookie flow, see
CLAUDE.md's 2026-07-12 session learnings), not something touched by tasks 1–3,
and it does not appear once a session exists. Out of scope for this sweep's
"fix what our code caused" mandate; noted here so it isn't mistaken for a new
regression.

### Renter shell (`devrenter@devcheck.dev`)
| Route | Result |
|---|---|
| Browse (`/rent`) | clean (covered above) |
| `/rentals/my-applications` | clean |
| `/rentals/my-contracts` | clean |
| `/profile` | clean |

### Owner shell (`devowner@devcheck.dev`)
| Route | Result |
|---|---|
| `/rentals/my-listings` | clean; "Manage photos" panel opened, shows the uploaded photo, upload control, delete button — see `owner-photo-manager.png` |
| `/rentals/my-contracts` | clean |
| `/properties/create` | clean |

### Officer (`staffadmin@devcheck.dev`, `is_admin=True` — honors the officer gate per `app/core/rbac.py`)
| Route | Result |
|---|---|
| `/rentals` (review queue, both `pending_review` and `published` filters) | clean; opened the review drawer for the published listing — photos render inline, see `officer-drawer-photos.png` |
| `/rentals/contracts` | clean; "Export CSV" download clean, "Download contract PDF" download clean |

### Staff (same admin account — a plain registered account is already "staff" per `is_staff()`; this account additionally has `is_admin=True`)
| Route | Result |
|---|---|
| `/dashboard` | clean |
| `/valuations` | clean |
| `/properties`, `/properties/2` | clean |
| `/reports` | clean |
| `/audit` | clean |
| `/analytics` | clean |
| `/settings` | clean |
| `/vehicles` | clean |
| `/scrapers` | clean |
| `/map` | clean |

## Network requests

Spot-checked non-static requests on `/rentals/contracts` and `/properties/2` via
`browser_network_requests`: all 200s except one expected FastAPI trailing-slash
`307` (`/api/v1/valuations?property_id=2` → `/api/v1/valuations/?property_id=2`,
pre-existing behavior, resolves to `200`), and the intentional `/rent/AA-LST-2026-575855`
404 noted above.

## Errors found → fixed

1. `Cross-Origin-Resource-Policy: same-origin` blocking cross-origin `<img>` loads
   of property photos — fixed in `backend/app/main.py` (scoped exception for the
   photo-file path only).

No other error-level console messages or failed requests attributable to this
branch's code were found across the routes above.
