import { test, expect } from '../setup/fixtures';

test.describe('Dashboard', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ dashboardPage }) => {
    await dashboardPage.goto();
  });

  test('should display dashboard page', async ({ dashboardPage }) => {
    await expect(dashboardPage.pageTitle).toBeVisible();
    await expect(dashboardPage.pageTitle).toContainText(/Dashboard|Overview|Welcome/i);
  });

  test('should display statistics cards', async ({ dashboardPage }) => {
    const statsCount = await dashboardPage.getStatsCount();
    expect(statsCount).toBeGreaterThan(0);
  });

  test('should display all stat cards with values', async ({ page }) => {
    const statCards = page.locator('.metric-card');
    await expect(statCards.first()).toBeVisible();
    const count = await statCards.count();

    for (let i = 0; i < count; i++) {
      const card = statCards.nth(i);
      await expect(card).toBeVisible();

      const value = card.locator('.metric-value');
      await expect(value).toBeVisible();
    }
  });

  test('should display recent activities section', async ({ dashboardPage }) => {
    await expect(dashboardPage.recentActivities).toBeVisible();
  });

  test('should display quick actions section', async ({ dashboardPage }) => {
    await expect(dashboardPage.quickActions).toBeVisible();
  });

  test('should navigate to properties from quick actions', async ({ page }) => {
    const propertiesLink = page.locator('a[href="/properties"], button:has-text("Properties")');
    if (await propertiesLink.count() > 0) {
      await propertiesLink.first().click();
      await expect(page).toHaveURL(/\/properties/);
    }
  });

  test('should navigate to valuations from quick actions', async ({ page }) => {
    const valuationsLink = page.locator('a[href="/valuations"], button:has-text("Valuations")');
    if (await valuationsLink.count() > 0) {
      await valuationsLink.first().click();
      await expect(page).toHaveURL(/\/valuations/);
    }
  });

  test('should have responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    const statsCards = page.locator('.metric-card');
    const count = await statsCards.count();

    for (let i = 0; i < count; i++) {
      await expect(statsCards.nth(i)).toBeVisible();
    }
  });

  test('should refresh data when clicking refresh button', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Refresh"), button[title*="Refresh"]');

    if (await refreshButton.count() > 0) {
      await refreshButton.first().click();
      await page.waitForTimeout(500);
      await expect(page.locator('.metric-card').first()).toBeVisible();
    }
  });
});
