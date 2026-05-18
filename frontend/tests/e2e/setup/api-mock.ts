/**
 * API Mock - Intercepts backend API calls for E2E tests when backend is unavailable.
 * Allows full test suite to run without backend on port 8020.
 */

// Valid JWT format (header.payload.signature) with exp=9999999999 (year ~2286).
// The auth middleware calls isTokenExpired() which checks JWT structure and exp,
// so this must be a properly formatted JWT even though it's not cryptographically signed.
export const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';
export const MOCK_USER = {
  id: 1,
  email: 'admin@valuadis.com',
  full_name: 'Admin User',
  is_admin: true,
  is_valuer: false,
  is_active: true,
};

export async function setupApiMock(page: import('@playwright/test').Page) {
  // Intercept auth login - regex matches full URL
  await page.route(/\/api\/v1\/auth\/login\/?$/, async (route) => {
    let postData: { email?: string; password?: string } = {};
    try {
      postData = route.request().postDataJSON() || {};
    } catch {
      // ignore
    }
    if (postData?.email === 'admin@valuadis.com' && (postData?.password === 'admin123' || postData?.password === 'Admin123!')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: MOCK_TOKEN,
          refresh_token: MOCK_TOKEN,
          token_type: 'bearer',
          expires_in: 1800,
        }),
      });
    } else {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid email or password' }),
      });
    }
  });

  await page.route(/\/api\/v1\/auth\/me\/?$/, async (route) => {
    // Always return admin user in E2E test context
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 200 });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_USER),
    });
  });

  // Auth refresh - return valid tokens
  await page.route('**/api/v1/auth/refresh', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: MOCK_TOKEN,
        refresh_token: MOCK_TOKEN,
        token_type: 'bearer',
        expires_in: 1800,
      }),
    });
  });

  // Auth logout - no-op (frontend clears localStorage)
  await page.route('**/api/v1/auth/logout', async (route) => {
    await route.fulfill({ status: 200, body: '' });
  });

  // Mock common API endpoints with empty/minimal data
  const mockJson = (data: unknown) => ({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(data),
  });

  const emptyList = { items: [], total: 0, data: [] };
  const emptyObj = {};

  await page.route('**/api/v1/properties**', async (route) => {
    await route.fulfill(mockJson(route.request().method() === 'GET' ? { ...emptyList, data: [] } : emptyObj));
  });
  await page.route('**/api/v1/valuations**', async (route) => {
    await route.fulfill(mockJson(route.request().method() === 'GET' ? { ...emptyList, data: [] } : emptyObj));
  });
  await page.route('**/api/v1/users**', async (route) => {
    await route.fulfill(mockJson(route.request().method() === 'GET' ? emptyList : emptyObj));
  });
  await page.route('**/api/v1/vehicles**', async (route) => {
    const url = route.request().url();
    if (url.includes('statistics/summary')) {
      await route.fulfill(mockJson({ total_vehicles: 0, total_valuations: 0, total_market_value: 0, pending_valuations: 0 }));
    } else {
      await route.fulfill(mockJson(route.request().method() === 'GET' ? { ...emptyList, data: [], vehicles: [] } : emptyObj));
    }
  });
  await page.route('**/api/v1/analytics/**', async (route) => {
    await route.fulfill(mockJson({
      properties: { total: 0, growth_rate: 0 },
      valuations: { total: 0, growth_rate: 0 },
      financials: { total_market_value: 0, market_value_growth: 0 },
      compliance: { compliance_rate: 0 },
      property_types: {},
    }));
  });
  await page.route('**/api/v1/ethiopian/**', async (route) => {
    await route.fulfill(mockJson({ municipalities: [] }));
  });
  await page.route('**/api/v1/audit/**', async (route) => {
    await route.fulfill(mockJson({ logs: [], total: 0 }));
  });
  await page.route('**/api/v1/settings**', async (route) => {
    await route.fulfill(mockJson(emptyObj));
  });
  await page.route('**/api/v1/scrapers**', async (route) => {
    await route.fulfill(mockJson(emptyList));
  });
  await page.route('**/api/v1/valuation-feedback**', async (route) => {
    await route.fulfill(mockJson(emptyObj));
  });
  await page.route('**/api/v1/valuation-feedback/**', async (route) => {
    await route.fulfill(mockJson(emptyObj));
  });
}
