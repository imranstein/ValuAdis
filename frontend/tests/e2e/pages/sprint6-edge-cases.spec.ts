import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

function generateExpiredToken(): string {
  const exp = Math.floor(Date.now() / 1000) - 3600
  const payload = Buffer.from(
    JSON.stringify({ exp, sub: '1', role: 'admin', email: 'admin@valuadis.com' }),
  ).toString('base64url')
  return `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${payload}.invalidsignature`
}

test.describe('Sprint 6 edge cases', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem('valuadis_token', token);
    }, MOCK_TOKEN);

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'admin@valuadis.com',
          full_name: 'Admin User',
          role: 'admin',
          is_admin: true,
          is_valuer: true,
        }),
      });
    });
  });

  test('blocks bulk import when required CSV columns are missing', async ({ page }) => {
    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'missing-columns.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,market_value,taxable_value',
          'Bole Atlas,Addis Ababa,residential,1000000,250000',
        ].join('\n')
      ),
    });

    await expect(page.getByTestId('property-import-mapping-table')).toContainText('latitude');
    await expect(page.getByTestId('property-import-mapping-table')).toContainText('Missing');
    await expect(page.getByTestId('property-import-validation-preview')).toContainText('latitude is required');
    await expect(page.getByTestId('property-import-validation-preview')).toContainText('longitude is required');
    await expect(page.getByTestId('property-import-confirm')).toBeDisabled();
  });

  test('shows backend bulk import validation errors without losing preview rows', async ({ page }) => {
    await page.route('**/api/v1/properties/bulk-import', async (route) => {
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [{ row: 2, message: 'Duplicate parcel number' }],
        }),
      });
    });

    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'duplicate-parcel.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,latitude,longitude,market_value,taxable_value',
          'Bole Atlas,Addis Ababa,residential,9.0320,38.7578,1000000,250000',
        ].join('\n')
      ),
    });

    await page.getByTestId('property-import-confirm').click();

    await expect(page.getByText('Duplicate parcel number')).toBeVisible();
    await expect(page.getByTestId('property-import-preview-table')).toContainText('Bole Atlas');
  });

  test('requires valuation ID before downloading a certificate', async ({ page }) => {
    await page.route('**/api/v1/analytics/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          properties: { total: 1 },
          valuations: { total: 1 },
          financials: { total_taxable_value: 250000 },
          compliance: { compliance_rate: 100 },
        }),
      });
    });

    await page.goto('/reports', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('report-type-select').selectOption('valuation_certificate');
    await page.getByTestId('report-valuation-id').fill('');

    await expect(page.getByRole('button', { name: /download|generating/i })).toBeDisabled();
    await expect(page.getByTestId('report-download-status')).toContainText('Ready to generate');
  });

  test('reports failed downloads and allows a corrected retry', async ({ page }) => {
    let requestCount = 0;

    await page.route('**/api/v1/analytics/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          properties: { total: 2 },
          valuations: { total: 2 },
          financials: { total_taxable_value: 500000 },
          compliance: { compliance_rate: 88 },
        }),
      });
    });

    await page.route('**/api/v1/valuations/99/certificate', async (route) => {
      requestCount += 1;
      await route.fulfill({
        status: requestCount === 1 ? 404 : 200,
        contentType: requestCount === 1 ? 'application/json' : 'application/pdf',
        headers: requestCount === 1 ? {} : { 'Content-Disposition': 'attachment; filename="ValuAdis_Certificate_99.pdf"' },
        body: requestCount === 1 ? JSON.stringify({ detail: 'Valuation not found' }) : Buffer.from('%PDF-1.4 retry certificate'),
      });
    });

    await page.goto('/reports', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('report-type-select').selectOption('valuation_certificate');
    await page.getByTestId('report-valuation-id').fill('99');
    const downloadButton = page.getByRole('button', { name: /download|generating/i });
    await downloadButton.click();

    await expect(page.getByTestId('report-download-status')).toContainText('Report generation failed');

    await downloadButton.click();
    await expect(page.getByTestId('report-download-status')).toContainText('ValuAdis_Certificate_99.pdf downloaded');
  });

  test('revokes an API key and saves settings to the backend', async ({ page }) => {
    await page.goto('/settings', { waitUntil: 'domcontentloaded' });

    const createKeyButton = page.getByRole('button', { name: /create api key/i });
    const keyRows = page.locator('.table-panel tbody tr:not(:has(.empty-cell))');
    // Each create prompts for a name; auto-accept every dialog for this test.
    page.on('dialog', (dialog) => dialog.accept('Key ' + Date.now()));

    await createKeyButton.click();
    await expect(keyRows).toHaveCount(1);
    await createKeyButton.click();
    await expect(keyRows).toHaveCount(2);

    // Revoke is a soft-delete: the row stays but its revoke control disappears.
    const revokeButtons = page.locator('.table-panel tbody tr button[aria-label="Revoke API key"]');
    await expect(revokeButtons).toHaveCount(2);
    await revokeButtons.last().click();
    await expect(revokeButtons).toHaveCount(1);

    await page.getByRole('button', { name: /save settings/i }).click();
    await expect(page.locator('.table-panel .panel-subtitle')).toContainText(/Saved to backend/i);
  });

  test('replays protected deep link after re-authentication', async ({ page }) => {
    let loginRequests = 0
    let loggedIn = false
    const tokens = {
      access_token: MOCK_TOKEN,
      refresh_token: MOCK_TOKEN,
      token_type: 'bearer',
      expires_in: 1800,
    }
    const adminUser = { id: 1, email: 'admin@valuadis.com', full_name: 'Admin User', role: 'admin', is_admin: true, is_valuer: true }

    // Session-restore endpoints reflect the logged-out state until a login lands.
    await page.route('**/api/v1/auth/refresh', async (route) => {
      await route.fulfill(loggedIn
        ? { status: 200, contentType: 'application/json', body: JSON.stringify(tokens) }
        : { status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Not authenticated' }) })
    })
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill(loggedIn
        ? { status: 200, contentType: 'application/json', body: JSON.stringify(adminUser) }
        : { status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Not authenticated' }) })
    })
    await page.route('**/api/v1/auth/login', async (route) => {
      loginRequests += 1
      loggedIn = true
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(tokens) })
    })

    // Start logged out (clear the token the describe's beforeEach seeds).
    await page.addInitScript(() => localStorage.removeItem('valuadis_token'))

    await page.goto('/users', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/login/)
    expect(new URL(page.url()).searchParams.get('redirect')).toBe('/users')

    await page.locator('input[type="email"]').fill('admin@valuadis.com')
    await page.locator('input[type="password"]').fill('Admin123!')
    await page.getByRole('button', { name: 'Sign In' }).click()

    await expect(page).toHaveURL(/\/users/, { timeout: 10000 })
    expect(loginRequests).toBe(1)
  });

  test('prevents duplicate login submit while request is in flight', async ({ page }) => {
    let loginRequests = 0
    let loggedIn = false
    const tokens = {
      access_token: MOCK_TOKEN,
      refresh_token: MOCK_TOKEN,
      token_type: 'bearer',
      expires_in: 1800,
    }
    const adminUser = { id: 1, email: 'admin@valuadis.com', full_name: 'Admin User', role: 'admin', is_admin: true, is_valuer: true }

    await page.route('**/api/v1/auth/refresh', async (route) => {
      await route.fulfill(loggedIn
        ? { status: 200, contentType: 'application/json', body: JSON.stringify(tokens) }
        : { status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Not authenticated' }) })
    })
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill(loggedIn
        ? { status: 200, contentType: 'application/json', body: JSON.stringify(adminUser) }
        : { status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Not authenticated' }) })
    })
    await page.route('**/api/v1/auth/login', async (route) => {
      loginRequests += 1
      loggedIn = true
      // Hold the request in flight so the submit button is provably disabled
      // while the duplicate submit is attempted (deterministic across load).
      await new Promise((resolve) => setTimeout(resolve, 800))
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(tokens) })
    })

    // Start logged out so the login form is reachable.
    await page.addInitScript(() => localStorage.removeItem('valuadis_token'))

    await page.goto('/login')
    // Use the class (not the accessible name): the label changes to "Signing in…"
    // once the request is in flight.
    const submitButton = page.locator('.login-btn')
    await expect(submitButton).toBeVisible()
    await page.locator('input[type="email"]').fill('admin@valuadis.com')
    await page.locator('input[type="password"]').fill('Admin123!')
    await submitButton.click()

    // The button disables while the login request is in flight; a forced second
    // click on the disabled button must not fire a second request.
    await expect(submitButton).toBeDisabled()
    await page.locator('.login-btn').evaluate((node) => {
      (node as HTMLButtonElement).click()
    })

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 })
    expect(loginRequests).toBe(1)
  });

  test('blocks non-admin users from admin-only routes', async ({ page }) => {
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 7,
          email: 'valuer@valuadis.com',
          full_name: 'Valuer User',
          role: 'valuer',
          is_admin: false,
          is_valuer: true,
          is_active: true,
        }),
      })
    })

    await page.goto('/users', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
  });
});
