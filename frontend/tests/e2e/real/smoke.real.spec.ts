import { test, expect, type APIRequestContext, type Page } from '@playwright/test';

/**
 * Real-backend smoke suite — no API mocking.
 *
 * Exercises the genuine auth boundary and the certificate happy path against
 * the live FastAPI backend, covering exactly what the mock suite cannot:
 * real login/logout, a real 401 redirect, and real persisted data rendering.
 */

const API = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8020';
const EMAIL = 'admin@valuadis.com';
const PASSWORD = 'password123';

const POLYGON = [
  [38.7578, 9.032],
  [38.758, 9.032],
  [38.758, 9.0318],
  [38.7578, 9.0318],
  [38.7578, 9.032],
];

let apiToken = '';
let approvedValuationId: number | null = null;
let approvedMarketValue = 0;

async function apiLogin(request: APIRequestContext): Promise<string> {
  const res = await request.post(`${API}/api/v1/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
  });
  expect(res.status(), 'backend must be reachable and seeded with the admin').toBe(200);
  return (await res.json()).data.access_token;
}

/** Create a property + valuation and approve it, so the UI has real data. */
async function seedApprovedValuation(request: APIRequestContext, token: string) {
  const auth = { Authorization: `Bearer ${token}` };
  const prop = await request.post(`${API}/api/v1/properties`, {
    headers: auth,
    data: {
      address: 'Real E2E Parcel, Bole',
      municipality: 'Addis Ababa',
      property_type: 'residential',
      area_sqm: 200.0,
      coordinates: POLYGON,
    },
  });
  expect(prop.status(), 'create property').toBeLessThan(300);
  const propertyId = (await prop.json()).data.id;

  const val = await request.post(`${API}/api/v1/valuations/`, {
    headers: auth,
    data: {
      property_id: propertyId,
      property_type: 'residential',
      municipality: 'Addis Ababa',
      area_sqm: 200.0,
      coordinates: POLYGON,
    },
  });
  expect(val.status(), 'create valuation').toBeLessThan(300);
  const valBody = (await val.json()).data;
  const valuationId = valBody.id;
  approvedMarketValue = Number(valBody.market_value || 0);

  for (const status of ['pending', 'approved']) {
    const t = await request.patch(`${API}/api/v1/valuations/${valuationId}/status`, {
      headers: auth,
      data: { status },
    });
    expect(t.status(), `transition to ${status}`).toBe(200);
  }
  return valuationId;
}

/** UI login using the real form; Enter submits (the a11y fix). */
async function uiLogin(page: Page) {
  await page.goto('/login');
  await page.locator('input[type="email"]').fill(EMAIL);
  const pw = page.locator('input[type="password"]');
  await pw.fill(PASSWORD);
  await pw.press('Enter');
  await page.waitForURL('**/dashboard', { timeout: 15000 });
}

test.beforeAll(async ({ request }) => {
  apiToken = await apiLogin(request);
  approvedValuationId = await seedApprovedValuation(request, apiToken);
});

test.beforeEach(async ({ page }) => {
  // Start each test signed out: clear any restored session.
  await page.goto('/');
  await page.evaluate(async (api) => {
    localStorage.clear();
    sessionStorage.clear();
    try {
      await fetch(`${api}/api/v1/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch (_) {
      /* ignore */
    }
  }, API);
});

test('unauthenticated deep-link redirects to /login', async ({ page }) => {
  await page.goto('/valuations');
  await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
});

test('wrong password is rejected and stays on /login', async ({ page }) => {
  await page.goto('/login');
  await page.locator('input[type="email"]').fill(EMAIL);
  const pw = page.locator('input[type="password"]');
  await pw.fill('definitely-wrong');
  await pw.press('Enter');
  // Must NOT reach the dashboard.
  await page.waitForTimeout(3000);
  await expect(page).toHaveURL(/\/login/);
});

test('real login lands on the dashboard with backend data', async ({ page }) => {
  await uiLogin(page);
  await expect(page).toHaveURL(/\/dashboard/);
  // Dashboard renders backend-derived content (not a blank shell).
  await expect(page.getByText(/valuation operations/i)).toBeVisible({ timeout: 15000 });
});

test('approved valuation renders with correct 25% taxable value', async ({ page }) => {
  await uiLogin(page);
  await page.goto('/valuations');
  // The seeded valuation must appear as APPROVED.
  await expect(page.getByText(/approved/i).first()).toBeVisible({ timeout: 15000 });
  // Taxable value is exactly 25% of market value (Ethiopian rule).
  const expectedTaxable = Math.round(approvedMarketValue * 0.25);
  const body = await page.locator('main').innerText();
  const digits = (n: number) => n.toLocaleString('en-US');
  expect(
    body.includes(digits(expectedTaxable)) || body.includes(String(expectedTaxable)),
    `taxable ${expectedTaxable} should be shown for market ${approvedMarketValue}`,
  ).toBeTruthy();
});

test('logout clears the session and protected routes bounce to /login', async ({ page }) => {
  await uiLogin(page);
  await page.getByRole('button', { name: /logout/i }).click();
  await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
  // Deep-linking after logout must not restore the session.
  await page.goto('/properties');
  await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
});

test('approved valuation certificate downloads as a real PDF (API)', async ({ request }) => {
  const res = await request.get(
    `${API}/api/v1/valuations/${approvedValuationId}/certificate`,
    { headers: { Authorization: `Bearer ${apiToken}` } },
  );
  expect(res.status()).toBe(200);
  expect(res.headers()['content-type']).toContain('application/pdf');
  const buf = await res.body();
  expect(buf.slice(0, 5).toString()).toBe('%PDF-');
  expect(buf.length).toBeGreaterThan(1000);
});
