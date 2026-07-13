import { test, expect } from '../setup/fixtures';

/**
 * The rebranded Valuations surface is a read-only appraisal ledger with search,
 * compliance metrics, ETB currency formatting, and a CSV export, plus a Quick
 * Valuation entry point for authoring new estimates. These tests verify the
 * ledger and the quick-valuation workflow entry (valuation authoring/state
 * transitions are exercised by backend + flow tests).
 */
test.describe('Valuations ledger', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  const dataRows = (page: import('@playwright/test').Page) =>
    page.locator('tbody tr:not(:has(td[colspan]))');

  test.beforeEach(async ({ valuationsPage }) => {
    await valuationsPage.goto();
    await valuationsPage.waitForValuationsToLoad();
  });

  test('should render backend valuation records', async ({ page }) => {
    await expect(dataRows(page).first()).toBeVisible();
    expect(await dataRows(page).count()).toBeGreaterThan(0);
  });

  test('should display compliance metric cards', async ({ page }) => {
    await expect(page.locator('.metric-label', { hasText: 'Total market value' })).toBeVisible();
    await expect(page.locator('.metric-label', { hasText: 'Compliance rate' })).toBeVisible();
    await expect(page.locator('.metric-label', { hasText: 'Pending appraisals' })).toBeVisible();
  });

  test('should format valuation amounts in ETB', async ({ page }) => {
    await expect(dataRows(page).first()).toContainText('ETB');
  });

  test('should search valuations by asset type', async ({ valuationsPage, page }) => {
    await valuationsPage.searchInput.fill('residential');
    await expect(dataRows(page)).toHaveCount(1);
    await expect(dataRows(page).first()).toContainText('Residential');
  });

  test('should search valuations by municipality', async ({ valuationsPage, page }) => {
    await valuationsPage.searchInput.fill('Mekelle');
    await expect(dataRows(page)).toHaveCount(1);
    await expect(dataRows(page).first()).toContainText('Mekelle');
  });

  test('should search valuations by status', async ({ valuationsPage, page }) => {
    await valuationsPage.searchInput.fill('approved');
    await expect(dataRows(page)).toHaveCount(1);
    await expect(dataRows(page).first()).toContainText('Approved');
  });

  test('should export the ledger as CSV', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: /export csv/i }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/valuations.*\.csv/i);
  });

  test.describe('Quick valuation', () => {
    test('should open the quick valuation workflow', async ({ valuationsPage, page }) => {
      await valuationsPage.clickNewValuation();
      await page.waitForURL(/\/valuations\/quick/, { timeout: 8000 });
      await expect(page.getByRole('heading', { name: /quick valuation/i }).first()).toBeVisible();
    });

    test('should present the property details form', async ({ page }) => {
      await page.goto('/valuations/quick', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('form.valuation-form')).toBeVisible();
      await expect(page.locator('select').first()).toBeVisible();
    });
  });
});
