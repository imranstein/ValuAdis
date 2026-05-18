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

    await expect(page.getByTestId('email-settings-section')).toBeVisible();
    await expect(page.getByTestId('rate-limit-settings-section')).toBeVisible();
    await expect(page.getByTestId('api-key-settings-section')).toBeVisible();

    await page.getByTestId('smtp-host-input').fill('smtp.valuadis.et');
    await page.getByTestId('rate-limit-input').fill('1200');
    await page.getByTestId('generate-api-key-button').click();
    await page.getByTestId('settings-save-button').click();

    await expect(page.getByTestId('api-key-row')).toHaveCount(3);
    await expect(page.getByTestId('settings-save-status')).toContainText('Settings saved');
  });
});
