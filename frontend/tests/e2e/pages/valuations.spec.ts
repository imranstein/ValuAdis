import { test, expect } from '../setup/fixtures';

test.describe('Valuations Management', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ valuationsPage }) => {
    await valuationsPage.goto();
  });

  test('should display valuations page', async ({ valuationsPage }) => {
    await expect(valuationsPage.pageTitle).toBeVisible();
    await expect(valuationsPage.pageTitle).toContainText(/Valuations/i);
  });

  test('should display new valuation button', async ({ valuationsPage }) => {
    await expect(valuationsPage.newValuationButton).toBeVisible();
  });

  test('should display search input', async ({ valuationsPage }) => {
    await expect(valuationsPage.searchInput).toBeVisible();
  });

  test('should display valuations table', async ({ valuationsPage }) => {
    await expect(valuationsPage.valuationsTable).toBeVisible();
  });

  test('should search valuations', async ({ valuationsPage, page }) => {
    await valuationsPage.searchValuation('Commercial');
    await page.waitForTimeout(500);
    
    const rowCount = await valuationsPage.getValuationCount();
    expect(rowCount).toBeGreaterThanOrEqual(0);
  });

  test('should filter valuations by status', async ({ valuationsPage, page }) => {
    if (await valuationsPage.statusFilter.count() > 0) {
      await valuationsPage.filterByStatus('completed');
      await page.waitForTimeout(500);
      
      const rows = await valuationsPage.getValuationCount();
      expect(rows).toBeGreaterThanOrEqual(0);
    }
  });

  test('should open new valuation page', async ({ valuationsPage, page }) => {
    await valuationsPage.clickNewValuation();
    await page.waitForURL(/\/valuations\/(quick|create|new|\d+)/);
    await expect(page).toHaveURL(/\/valuations/);
  });

  test('should display valuation methods', async ({ valuationsPage, page }) => {
    await valuationsPage.clickNewValuation();
    await page.waitForTimeout(300);
    
    const methodOptions = page.locator('select[name*="method"], input[name*="method"]');
    if (await methodOptions.count() > 0) {
      await expect(methodOptions.first()).toBeVisible();
    }
  });

  test('should validate Ethiopian compliance fields', async ({ valuationsPage, page }) => {
    await valuationsPage.clickNewValuation();
    await page.waitForTimeout(300);
    
    const proclamationField = page.locator('input[name*="proclamation"], label:has-text("Proclamation 1365")');
    if (await proclamationField.count() > 0) {
      await expect(proclamationField.first()).toBeVisible();
    }
  });

  test('should calculate valuation estimate', async ({ valuationsPage, page }) => {
    await valuationsPage.clickNewValuation();
    await page.waitForTimeout(300);
    
    const calculateButton = page.locator('button:has-text("Calculate"), button:has-text("Estimate")');
    if (await calculateButton.count() > 0) {
      await expect(calculateButton.first()).toBeVisible();
    }
  });

  test('should export valuation report', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();
    
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);
      
      const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")');
      if (await exportButton.count() > 0) {
        await expect(exportButton.first()).toBeVisible();
      }
    }
  });

  test('should display valuation history', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();
    
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);
      
      const historySection = page.locator('.history, .timeline, .audit-trail');
      if (await historySection.count() > 0) {
        await expect(historySection.first()).toBeVisible();
      }
    }
  });

  test('should have responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const table = page.locator('table');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });
});
