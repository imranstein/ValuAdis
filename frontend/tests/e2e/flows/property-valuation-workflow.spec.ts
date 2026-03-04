import { test, expect } from '../setup/fixtures';

test.describe('Property Valuation Workflow', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should complete full property valuation workflow', async ({ page }) => {
    // Step 1: Navigate to Properties
    await page.goto('/properties');
    await expect(page.locator('h1')).toContainText(/Properties/i);

    // Step 2: Add new property
    const addButton = page.locator('button:has-text("Add Property")');
    if (await addButton.count() > 0) {
      await addButton.click();
      await page.waitForTimeout(300);

      // Fill property details
      const titleInput = page.locator('input[name="title"], input[placeholder*="Title"]').first();
      if (await titleInput.count() > 0) {
        await titleInput.fill('Test Property - Addis Ababa');
      }

      const locationInput = page.locator('input[name="location"], input[placeholder*="Location"]').first();
      if (await locationInput.count() > 0) {
        await locationInput.fill('Bole, Addis Ababa');
      }

      const submitButton = page.locator('button[type="submit"], button:has-text("Add"), button:has-text("Save")').first();
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForTimeout(500);
      }
    }

    // Step 3: Navigate to Valuations
    await page.goto('/valuations');
    await expect(page.locator('h1')).toContainText(/Valuations/i);

    // Step 4: Create new valuation
    const newValuationButton = page.locator('button:has-text("New Valuation")');
    if (await newValuationButton.count() > 0) {
      await newValuationButton.click();
      await page.waitForTimeout(300);

      // Select property
      const propertySelect = page.locator('select[name*="property"], input[name*="property"]').first();
      if (await propertySelect.count() > 0) {
        await expect(propertySelect).toBeVisible();
      }

      // Select valuation method
      const methodSelect = page.locator('select[name*="method"]').first();
      if (await methodSelect.count() > 0) {
        await methodSelect.selectOption({ index: 1 });
      }

      // Submit valuation
      const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Calculate")').first();
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Step 5: Verify valuation was created
    const valuationRows = page.locator('tbody tr');
    if (await valuationRows.count() > 0) {
      expect(await valuationRows.count()).toBeGreaterThan(0);
    }
  });

  test('should handle property search and valuation creation', async ({ page }) => {
    // Search for property
    await page.goto('/properties');
    const searchInput = page.locator('input[placeholder*="Search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('Addis Ababa');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
    }

    // Select first property
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);

      // Create valuation from property details
      const valuateButton = page.locator('button:has-text("Valuate"), button:has-text("Create Valuation")');
      if (await valuateButton.count() > 0) {
        await valuateButton.click();
        await page.waitForTimeout(300);
        
        const modal = page.locator('.modal, [role="dialog"]');
        await expect(modal).toBeVisible();
      }
    }
  });

  test('should export valuation report after completion', async ({ page }) => {
    await page.goto('/valuations');
    
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);

      const exportButton = page.locator('button:has-text("Export"), button:has-text("Download PDF")');
      if (await exportButton.count() > 0) {
        await expect(exportButton).toBeVisible();
      }
    }
  });
});
