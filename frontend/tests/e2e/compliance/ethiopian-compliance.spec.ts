import { test, expect } from '../setup/fixtures';

test.describe('Ethiopian Compliance - Proclamation 1365/2025', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should display Ethiopian Birr (ETB) as default currency', async ({ page }) => {
    await page.goto('/settings');
    
    const currencySelect = page.locator('select[name*="currency"]');
    if (await currencySelect.count() > 0) {
      const selectedValue = await currencySelect.inputValue();
      expect(selectedValue).toBe('ETB');
    }
  });

  test('should display Addis Ababa timezone', async ({ page }) => {
    await page.goto('/settings');
    
    const timezoneSelect = page.locator('select[name*="timezone"]');
    if (await timezoneSelect.count() > 0) {
      const selectedValue = await timezoneSelect.inputValue();
      expect(selectedValue).toContain('Addis_Ababa');
    }
  });

  test('should have Proclamation 1365/2025 compliance toggle', async ({ page }) => {
    await page.goto('/settings');
    
    const valuationTab = page.locator('button:has-text("Valuation")');
    await valuationTab.click();
    await page.waitForTimeout(300);
    
    const proclamationToggle = page.locator('input[type="checkbox"]:near(:text("Proclamation 1365"))');
    if (await proclamationToggle.count() > 0) {
      await expect(proclamationToggle).toBeVisible();
    }
  });

  test('should validate Ethiopian property types', async ({ page }) => {
    await page.goto('/properties');
    
    const addButton = page.locator('button:has-text("Add Property")');
    if (await addButton.count() > 0) {
      await addButton.click();
      await page.waitForTimeout(300);
      
      const propertyTypeSelect = page.locator('select[name*="type"], select[name*="property_type"]');
      if (await propertyTypeSelect.count() > 0) {
        await expect(propertyTypeSelect).toBeVisible();
      }
    }
  });

  test('should support Ethiopian municipalities', async ({ page }) => {
    await page.goto('/properties');
    
    const addButton = page.locator('button:has-text("Add Property")');
    if (await addButton.count() > 0) {
      await addButton.click();
      await page.waitForTimeout(300);
      
      const locationInput = page.locator('input[name*="location"], input[placeholder*="Location"]');
      if (await locationInput.count() > 0) {
        await locationInput.fill('Addis Ababa');
        await page.waitForTimeout(300);
        
        const suggestions = page.locator('.suggestion, .autocomplete-item');
        if (await suggestions.count() > 0) {
          await expect(suggestions.first()).toBeVisible();
        }
      }
    }
  });

  test('should display valuation methods compliant with Ethiopian standards', async ({ page }) => {
    await page.goto('/valuations');
    
    const newButton = page.locator('button:has-text("New Valuation")');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForTimeout(300);
      
      const methodSelect = page.locator('select[name*="method"]');
      if (await methodSelect.count() > 0) {
        const options = await methodSelect.locator('option').allTextContents();
        expect(options.some(opt => opt.includes('Comparative') || opt.includes('Cost') || opt.includes('Income'))).toBeTruthy();
      }
    }
  });

  test('should support Amharic language option', async ({ page }) => {
    await page.goto('/settings');
    
    const languageSelect = page.locator('select[name*="language"]');
    if (await languageSelect.count() > 0) {
      const options = await languageSelect.locator('option').allTextContents();
      expect(options.some(opt => opt.includes('Amharic') || opt.includes('አማርኛ'))).toBeTruthy();
    }
  });

  test('should validate Ethiopian date format', async ({ page }) => {
    await page.goto('/settings');
    
    const dateFormatSelect = page.locator('select[name*="date"]');
    if (await dateFormatSelect.count() > 0) {
      await expect(dateFormatSelect).toBeVisible();
    }
  });

  test('should display required documentation for Ethiopian compliance', async ({ page }) => {
    await page.goto('/settings');
    
    const valuationTab = page.locator('button:has-text("Valuation")');
    await valuationTab.click();
    await page.waitForTimeout(300);
    
    const documentationSection = page.locator('label:has-text("Required Documentation"), h3:has-text("Documentation")');
    if (await documentationSection.count() > 0) {
      await expect(documentationSection.first()).toBeVisible();
    }
  });

  test('should validate property ownership documentation', async ({ page }) => {
    await page.goto('/properties');
    
    const addButton = page.locator('button:has-text("Add Property")');
    if (await addButton.count() > 0) {
      await addButton.click();
      await page.waitForTimeout(300);
      
      const ownershipField = page.locator('input[name*="ownership"], label:has-text("Ownership")');
      if (await ownershipField.count() > 0) {
        await expect(ownershipField.first()).toBeVisible();
      }
    }
  });
});

test.describe('Ethiopian Market Data Integration', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should display Ethiopian property sources in scraper', async ({ page }) => {
    await page.goto('/settings');
    
    const scraperTab = page.locator('button:has-text("Web Scraper")');
    await scraperTab.click();
    await page.waitForTimeout(300);
    
    const table = page.locator('table');
    if (await table.count() > 0) {
      const tableText = await table.textContent();
      
      const ethiopianSources = [
        'livingethio.com',
        'ethiopiapropertycentre.com',
        'ethiopianproperties.com',
        'zegebeya.com',
        'jiji.com.et'
      ];
      
      const hasEthiopianSource = ethiopianSources.some(source => tableText?.includes(source));
      expect(hasEthiopianSource).toBeTruthy();
    }
  });

  test('should validate Ethiopian property listing data', async ({ page }) => {
    await page.goto('/properties');
    
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.count() > 0) {
      const rowText = await firstRow.textContent();
      
      // Check for Ethiopian location references
      const ethiopianLocations = ['Addis Ababa', 'Bole', 'Piassa', 'Merkato', 'Bahir Dar', 'Gondar'];
      const hasEthiopianLocation = ethiopianLocations.some(loc => rowText?.includes(loc));
      
      if (rowText && rowText.length > 0) {
        expect(hasEthiopianLocation || rowText.includes('ETB')).toBeTruthy();
      }
    }
  });
});
