/**
 * API Mock - Intercepts backend API calls for E2E tests when backend is unavailable.
 * Allows the full test suite to run without a live backend on port 8020.
 *
 * Auth state is stateful per page: the mock defaults to an authenticated admin
 * session (so the bulk of protected-route tests work), but a spec can call
 * `setUnauthenticated(page)` before navigating to exercise logged-out / expired /
 * unauthenticated-redirect flows. A successful login flips the session back on,
 * and logout flips it off — mirroring the real refresh-cookie behaviour that the
 * frontend relies on for session restore across reloads.
 */
import type { Page } from '@playwright/test';

// Valid JWT format (header.payload.signature) with exp=9999999999 (year ~2286).
// The auth middleware calls isJwtExpired() which checks JWT structure and exp,
// so this must be a properly formatted JWT even though it's not cryptographically signed.
export const MOCK_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

export const MOCK_USER = {
  id: 1,
  email: 'admin@valuadis.com',
  full_name: 'Admin User',
  is_admin: true,
  is_valuer: false,
  is_active: true,
};

type AuthState = { loggedIn: boolean };

// Per-page auth state so specs can toggle logged-out flows independently.
const authStates = new WeakMap<Page, AuthState>();

/**
 * Switch a page's mocked session to logged-out: /auth/me and /auth/refresh will
 * return 401 so the frontend's session-restore boot fails and the router
 * redirects to /login. Call before navigating to a protected route.
 */
export function setUnauthenticated(page: Page): void {
  const state = authStates.get(page);
  if (state) state.loggedIn = false;
}

// Seed records so read-only registry, search, filter, and metric surfaces render
// real rows instead of empty states.
const SEED_PROPERTIES = [
  {
    id: 101,
    address: 'Bole Road, Addis Ababa',
    property_type: 'residential',
    municipality: 'Addis Ababa',
    market_value: 2500000,
    taxable_value: 1875000,
    status: 'active',
    neighborhood: 'Bole',
    subcity: 'Bole',
    region: 'Addis Ababa',
    area_sqm: 120,
  },
  {
    id: 102,
    address: 'Kirkos Avenue, Addis Ababa',
    property_type: 'commercial',
    municipality: 'Addis Ababa',
    market_value: 5400000,
    taxable_value: 4050000,
    status: 'pending',
    neighborhood: 'Kirkos',
    subcity: 'Kirkos',
    region: 'Addis Ababa',
    area_sqm: 300,
  },
  {
    id: 103,
    address: 'Hawelti Street, Mekelle',
    property_type: 'commercial',
    municipality: 'Mekelle',
    market_value: 3100000,
    taxable_value: 2325000,
    status: 'active',
    neighborhood: 'Hawelti',
    subcity: 'Hawelti',
    region: 'Tigray',
    area_sqm: 210,
  },
];

const SEED_VALUATIONS = [
  {
    id: 201,
    property_type: 'commercial',
    municipality: 'Addis Ababa',
    status: 'approved',
    market_value: 5400000,
    taxable_value: 4050000,
  },
  {
    id: 202,
    property_type: 'residential',
    municipality: 'Addis Ababa',
    status: 'pending',
    market_value: 2500000,
    taxable_value: 1875000,
  },
  {
    id: 203,
    property_type: 'commercial',
    municipality: 'Mekelle',
    status: 'draft',
    market_value: 3100000,
    taxable_value: 2325000,
  },
];

const SEED_USERS = [
  {
    id: 1,
    full_name: 'Admin User',
    email: 'admin@valuadis.com',
    municipality: 'Addis Ababa',
    license_number: 'EV-1000-2000',
    is_active: true,
    is_verified: true,
    is_admin: true,
    is_valuer: false,
    roles: [{ name: 'system_admin', display_name: 'System Admin' }],
  },
  {
    id: 2,
    full_name: 'Selam Bekele',
    email: 'selam.bekele@valuadis.com',
    municipality: 'Addis Ababa',
    license_number: 'EV-3344-5566',
    is_active: true,
    is_verified: true,
    is_admin: false,
    is_valuer: true,
    roles: [{ name: 'valuer', display_name: 'Valuer' }],
  },
  {
    id: 3,
    full_name: 'Dawit Tesfaye',
    email: 'dawit.tesfaye@valuadis.com',
    municipality: 'Mekelle',
    license_number: 'EV-7788-9900',
    is_active: false,
    is_verified: false,
    is_admin: false,
    is_valuer: true,
    roles: [{ name: 'valuer', display_name: 'Valuer' }],
  },
];

const SEED_VEHICLES = [
  {
    id: 301,
    make: 'Toyota',
    model: 'Corolla',
    year: 2019,
    vin: '1HGCM82633A004352',
    registration_number: 'AA-3-12345',
    status: 'active',
    market_value: 1800000,
  },
];

export async function setupApiMock(page: Page) {
  const state: AuthState = { loggedIn: true };
  authStates.set(page, state);

  const mockJson = (data: unknown) => ({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(data),
  });
  const unauthorized = {
    status: 401,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Not authenticated' }),
  };
  const tokenBody = {
    access_token: MOCK_TOKEN,
    refresh_token: MOCK_TOKEN,
    token_type: 'bearer',
    expires_in: 1800,
  };

  // Auth login - regex matches full URL. A valid login re-establishes the session.
  await page.route(/\/api\/v1\/auth\/login\/?$/, async (route) => {
    let postData: { email?: string; password?: string } = {};
    try {
      postData = route.request().postDataJSON() || {};
    } catch {
      // ignore malformed body
    }
    const validPassword = postData?.password === 'admin123' || postData?.password === 'Admin123!';
    if (postData?.email === 'admin@valuadis.com' && validPassword) {
      state.loggedIn = true;
      await route.fulfill(mockJson(tokenBody));
    } else {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid email or password' }),
      });
    }
  });

  await page.route(/\/api\/v1\/auth\/me\/?$/, async (route) => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 200 });
      return;
    }
    await route.fulfill(state.loggedIn ? mockJson(MOCK_USER) : unauthorized);
  });

  // Refresh mirrors the httpOnly cookie: succeeds only while the session is live.
  await page.route('**/api/v1/auth/refresh', async (route) => {
    await route.fulfill(state.loggedIn ? mockJson(tokenBody) : unauthorized);
  });

  // Logout is a no-op for the mock's restorable-session flag. The frontend
  // calls logout not only on an intentional sign-out but also when a session
  // request (e.g. /auth/me) is aborted mid-navigation, which would otherwise
  // wrongly tear the session down for the rest of a multi-navigation test.
  // Intentional sign-out still lands on /login because the frontend clears its
  // local tokens; genuinely logged-out flows opt in via setUnauthenticated().
  await page.route('**/api/v1/auth/logout', async (route) => {
    await route.fulfill({ status: 200, body: '' });
  });

  const listResponse = (rows: unknown[]) => ({ items: rows, total: rows.length, data: rows });

  await page.route('**/api/v1/properties**', async (route) => {
    const url = route.request().url();
    const method = route.request().method();
    if (method !== 'GET') {
      await route.fulfill(mockJson({ id: 999 }));
      return;
    }
    const match = url.match(/\/properties\/(\d+)/);
    if (match) {
      const found = SEED_PROPERTIES.find((p) => String(p.id) === match[1]) || SEED_PROPERTIES[0];
      await route.fulfill(mockJson(found));
      return;
    }
    await route.fulfill(mockJson(listResponse(SEED_PROPERTIES)));
  });

  await page.route('**/api/v1/valuations**', async (route) => {
    const method = route.request().method();
    if (method !== 'GET') {
      await route.fulfill(mockJson({ id: 999 }));
      return;
    }
    await route.fulfill(mockJson(listResponse(SEED_VALUATIONS)));
  });

  await page.route('**/api/v1/users**', async (route) => {
    await route.fulfill(mockJson(route.request().method() === 'GET' ? SEED_USERS : {}));
  });

  await page.route('**/api/v1/vehicles**', async (route) => {
    const url = route.request().url();
    if (url.includes('statistics/summary')) {
      await route.fulfill(
        mockJson({
          total_vehicles: SEED_VEHICLES.length,
          total_valuations: 1,
          total_market_value: 1800000,
          pending_valuations: 0,
        })
      );
      return;
    }
    if (route.request().method() !== 'GET') {
      await route.fulfill(mockJson({ id: 999 }));
      return;
    }
    await route.fulfill(mockJson({ ...listResponse(SEED_VEHICLES), vehicles: SEED_VEHICLES }));
  });

  await page.route('**/api/v1/vehicle-data/**', async (route) => {
    await route.fulfill(mockJson({ makes: [], models: [], data: [] }));
  });

  await page.route('**/api/v1/analytics/**', async (route) => {
    await route.fulfill(
      mockJson({
        properties: { total: SEED_PROPERTIES.length, growth_rate: 4.2 },
        valuations: { total: SEED_VALUATIONS.length, growth_rate: 3.1 },
        financials: { total_market_value: 11000000, market_value_growth: 5.4, total_taxable_value: 8250000 },
        compliance: { compliance_rate: 92 },
        property_types: { residential: 1, commercial: 2 },
      })
    );
  });

  await page.route('**/api/v1/ethiopian/**', async (route) => {
    await route.fulfill(mockJson({ municipalities: ['Addis Ababa', 'Mekelle', 'Bahir Dar', 'Dire Dawa'] }));
  });

  await page.route('**/api/v1/audit/**', async (route) => {
    await route.fulfill(mockJson({ logs: [], total: 0, items: [], data: [] }));
  });

  // Stateful settings mock mirroring the real backend (preferences + api keys).
  const settingsState: {
    preferences: Record<string, unknown>;
    apiKeys: Array<Record<string, unknown>>;
    nextId: number;
  } = { preferences: {}, apiKeys: [], nextId: 1 };

  await page.route('**/api/v1/settings**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    // /api/v1/settings/api-keys/{id}
    const keyIdMatch = path.match(/\/settings\/api-keys\/(\d+)\/?$/);
    if (keyIdMatch) {
      const id = Number(keyIdMatch[1]);
      if (method === 'DELETE') {
        settingsState.apiKeys = settingsState.apiKeys.map((k) =>
          k.id === id ? { ...k, revoked: true } : k,
        );
        await route.fulfill(mockJson({ success: true }));
        return;
      }
      await route.fulfill(mockJson({}));
      return;
    }

    // /api/v1/settings/api-keys
    if (/\/settings\/api-keys\/?$/.test(path)) {
      if (method === 'POST') {
        let body: { name?: string } = {};
        try { body = route.request().postDataJSON() || {}; } catch { /* ignore */ }
        const id = settingsState.nextId++;
        const stored = {
          id, name: body.name || `Key ${id}`, key_prefix: `vk_${id}abc`,
          revoked: false, created_at: new Date().toISOString(), last_used_at: null,
        };
        settingsState.apiKeys.push(stored);
        // The create response carries the one-time plaintext key.
        await route.fulfill({ status: 201, contentType: 'application/json',
          body: JSON.stringify({ ...stored, key: `vk_${id}abc_secretplaintext` }) });
        return;
      }
      await route.fulfill(mockJson(settingsState.apiKeys));
      return;
    }

    // /api/v1/settings
    if (method === 'PUT') {
      let body: { preferences?: Record<string, unknown> } = {};
      try { body = route.request().postDataJSON() || {}; } catch { /* ignore */ }
      settingsState.preferences = { ...settingsState.preferences, ...(body.preferences || {}) };
      await route.fulfill(mockJson({ preferences: settingsState.preferences }));
      return;
    }
    await route.fulfill(mockJson({ preferences: settingsState.preferences }));
  });

  await page.route('**/api/v1/scrapers**', async (route) => {
    await route.fulfill(mockJson(listResponse([])));
  });

  await page.route('**/api/v1/notifications**', async (route) => {
    await route.fulfill(mockJson({ count: 0, notifications: [] }));
  });

  await page.route('**/api/v1/valuation-feedback**', async (route) => {
    await route.fulfill(mockJson({}));
  });
  await page.route('**/api/v1/valuation-feedback/**', async (route) => {
    await route.fulfill(mockJson({}));
  });
}
