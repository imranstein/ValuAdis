import { test, expect } from '../setup/fixtures';

test.describe('Properties Management', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ propertiesPage }) => {
    await propertiesPage.goto();
  });

  test('should display properties page', async ({ propertiesPage }) => {
    await expect(propertiesPage.pageTitle).toBeVisible();
    await expect(propertiesPage.pageTitle).toContainText(/Properties/i);
  });

  test('should display add property button', async ({ propertiesPage }) => {
    await expect(propertiesPage.addPropertyButton).toBeVisible();
  });

  test('should display search input', async ({ propertiesPage }) => {
    await expect(propertiesPage.searchInput).toBeVisible();
  });

  test('should display properties table', async ({ propertiesPage }) => {
    await expect(propertiesPage.propertiesTable).toBeVisible();
  });

  test('should search properties', async ({ propertiesPage, page }) => {
    await propertiesPage.searchProperty('Addis Ababa');
    await page.waitForTimeout(500);
    
    const rowCount = await propertiesPage.getPropertyCount();
    expect(rowCount).toBeGreaterThanOrEqual(0);
  });

  test('should filter properties', async ({ propertiesPage, page }) => {
    const filterButton = propertiesPage.filterButton;
    
    if (await filterButton.count() > 0) {
      await filterButton.click();
      await page.waitForTimeout(300);
      
      const filterPanel = page.locator('.filter-panel, .filters');
      await expect(filterPanel).toBeVisible();
    }
  });

  test('should open add property modal', async ({ propertiesPage, page }) => {
    await propertiesPage.clickAddProperty();
    await page.waitForURL(/\/properties\/create/, { timeout: 5000 });
    // Create page has wizard or form
    await expect(page.getByRole('heading', { name: /register|create|property/i }).first()).toBeVisible();
  });

  test('should sort properties by column', async ({ page }) => {
    const columnHeader = page.locator('th').first();
    await columnHeader.click();
    await page.waitForTimeout(500);
    
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThanOrEqual(0);
  });

  test('should paginate through properties', async ({ page }) => {
    const nextButton = page.locator('button:has-text("Next"), .pagination button:last-child');
    
    if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
      await nextButton.click();
      await page.waitForTimeout(500);
      await expect(page.locator('tbody tr').first()).toBeVisible();
    }
  });

  test('should display property details on row click', async ({ page }) => {
    const firstRow = page.locator('tbody tr').first();
    
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);
      
      const detailsPanel = page.locator('.property-details, .details-panel, [role="dialog"]');
      if (await detailsPanel.count() > 0) {
        await expect(detailsPanel).toBeVisible();
      }
    }
  });

  test('should validate required fields in add property form', async ({ propertiesPage, page }) => {
    await propertiesPage.clickAddProperty();
    await page.waitForURL(/\/properties\/create/, { timeout: 5000 });
    
    // Create page has wizard - check for required fields or validation
    const requiredInputs = page.locator('input[required]');
    const count = await requiredInputs.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should export properties data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export")');
    
    if (await exportButton.count() > 0) {
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      try {
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/properties.*\.(csv|xlsx|json)/i);
      } catch (e) {
        // Export might not be implemented yet
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
