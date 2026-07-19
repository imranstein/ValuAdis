import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

test.describe('System settings completion', () => {
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

  test('updates email, rate-limit, and API key settings', async ({ page }) => {
    await page.goto('/settings', { waitUntil: 'domcontentloaded' });

    await expect(page.locator('.panel-title', { hasText: 'Email delivery' })).toBeVisible();
    await expect(page.locator('.panel-title', { hasText: 'Security limits' })).toBeVisible();
    await expect(page.locator('.panel-title', { hasText: 'API keys' })).toBeVisible();

    await page.locator('.field', { hasText: 'SMTP host' }).locator('input').fill('smtp.valuadis.et');
    await page.locator('.field', { hasText: 'Requests per window' }).locator('input').fill('1200');

    const keyRows = page.locator('.table-panel tbody tr:not(:has(.empty-cell))');
    page.once('dialog', (dialog) => dialog.accept('Config key'));
    await page.getByRole('button', { name: /create api key/i }).click();
    await expect(keyRows).toHaveCount(1);

    await page.getByRole('button', { name: /save settings/i }).click();
    await expect(page.locator('.table-panel .panel-subtitle')).toContainText(/Saved to backend/i);
  });
});
