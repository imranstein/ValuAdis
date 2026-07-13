import { test, expect } from '../setup/fixtures';

test.describe('Settings Management', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ settingsPage }) => {
    await settingsPage.goto();
  });

  test('should display settings page', async ({ settingsPage }) => {
    await expect(settingsPage.pageTitle).toBeVisible();
    await expect(settingsPage.pageTitle).toContainText(/Settings/i);
  });

  test('should display the administrative profile panel', async ({ page }) => {
    await expect(page.locator('.panel-title', { hasText: 'Administrative profile' })).toBeVisible();
  });

  test('should display the workspace behavior panel', async ({ page }) => {
    await expect(page.locator('.panel-title', { hasText: 'Workspace behavior' })).toBeVisible();
  });

  test('should display email delivery and security panels', async ({ page }) => {
    await expect(page.locator('.panel-title', { hasText: 'Email delivery' })).toBeVisible();
    await expect(page.locator('.panel-title', { hasText: 'Security limits' })).toBeVisible();
  });

  test('should display save button', async ({ settingsPage }) => {
    await expect(settingsPage.saveButton).toBeVisible();
  });

  test('should change workspace data density', async ({ page }) => {
    const spacious = page.locator('.segmented-control button', { hasText: 'Spacious' });
    await spacious.click();
    await expect(spacious).toHaveClass(/active/);
  });

  test('should create an API key via the backend', async ({ settingsPage }) => {
    await expect(settingsPage.apiKeyRows).toHaveCount(0);
    await settingsPage.createApiKey('CI integration key');
    await expect(settingsPage.apiKeyRows).toHaveCount(1);
  });

  test('should save operational settings to the backend', async ({ settingsPage, page }) => {
    await settingsPage.saveSettings();
    await expect(page.locator('.table-panel .panel-subtitle')).toContainText(/Saved to backend/i);
  });

  test('should have responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/settings');
    await page.waitForLoadState('domcontentloaded');

    const panels = page.locator('.panel');
    await panels.first().waitFor({ state: 'visible', timeout: 10000 });
    expect(await panels.count()).toBeGreaterThan(0);
  });
});
