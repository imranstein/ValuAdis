import { test, expect } from '../setup/fixtures';

/**
 * The rebranded Properties surface is a backend-backed registry: search box,
 * municipality/type filters, metric cards, and a read-only table whose row
 * actions navigate to dedicated create/import/detail/edit pages. These tests
 * verify the registry behaviour and that the create/import/detail entry points
 * route correctly (record mutation is exercised by backend tests).
 */
test.describe('Properties registry', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  const dataRows = (page: import('@playwright/test').Page) =>
    page.locator('tbody tr:not(:has(td[colspan]))');

  test.beforeEach(async ({ propertiesPage }) => {
    await propertiesPage.goto();
    await propertiesPage.waitForPropertiesToLoad();
  });

  test('should render backend property records', async ({ page }) => {
    await expect(dataRows(page).first()).toBeVisible();
    expect(await dataRows(page).count()).toBeGreaterThan(0);
  });

  test('should display property metric cards', async ({ page }) => {
    await expect(page.locator('.metric-card', { hasText: 'Total properties' })).toBeVisible();
  });

  test('should search properties by address', async ({ propertiesPage, page }) => {
    await propertiesPage.searchInput.fill('Bole');
    await expect(dataRows(page)).toHaveCount(1);
    await expect(dataRows(page).first()).toContainText('Bole');
  });

  test('should handle no search results', async ({ propertiesPage, page }) => {
    await propertiesPage.searchInput.fill('NonExistentProperty12345');
    await expect(dataRows(page)).toHaveCount(0);
  });

  test('should filter properties by municipality', async ({ page }) => {
    await page.locator('select[aria-label="Filter by municipality"]').selectOption('Mekelle');
    await expect(dataRows(page)).toHaveCount(1);
    await expect(dataRows(page).first()).toContainText('Mekelle');
  });

  test('should filter properties by type', async ({ page }) => {
    await page.locator('select[aria-label="Filter by property type"]').selectOption('commercial');
    await expect(dataRows(page).first()).toContainText('Commercial');
    for (const cell of await dataRows(page).allTextContents()) {
      expect(cell).toContain('Commercial');
    }
  });

  test('should reset filters', async ({ propertiesPage, page }) => {
    await propertiesPage.searchInput.fill('Bole');
    await expect(dataRows(page)).toHaveCount(1);
    await propertiesPage.filterButton.click();
    expect(await dataRows(page).count()).toBeGreaterThan(1);
  });

  test('should open the create property page', async ({ propertiesPage, page }) => {
    await propertiesPage.clickAddProperty();
    await page.waitForURL(/\/properties\/create/, { timeout: 8000 });
    await expect(page.locator('input, select, textarea').first()).toBeVisible();
  });

  test('should open the property import page', async ({ page }) => {
    await page.getByRole('link', { name: /import/i }).click();
    await page.waitForURL(/\/properties\/import/, { timeout: 8000 });
    await expect(page).toHaveURL(/\/properties\/import/);
  });

  test('should navigate to property details from a row', async ({ page }) => {
    await dataRows(page).first().getByRole('button', { name: /view property/i }).click();
    await page.waitForURL(/\/properties\/\d+/, { timeout: 8000 });
    await expect(page).toHaveURL(/\/properties\/\d+/);
  });

  test('should export the property registry as CSV', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: /export/i }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/properties.*\.csv/i);
  });
});
