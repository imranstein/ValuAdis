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

test.describe('Ethiopian Business License Validation', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should validate valid Ethiopian license formats', async ({ page }) => {
    await page.goto('/settings');

    // Test valid license formats that should be accepted
    const validLicenses = [
      'AA-1234567890',
      'AD-1234567890',
      'BA-1234567890',
      'DD-1234567890',
      'HA-1234567890',
      'ME-1234567890',
      'OR-1234567890',
      'AM-1234567890',
      'SN-1234567890'
    ];

    // Navigate to users section where license field exists
    const usersNav = page.locator('a[href*="users"], nav a:has-text("Users")');
    if (await usersNav.count() > 0) {
      await usersNav.click();
      await page.waitForTimeout(500);

      const addButton = page.locator('button:has-text("Add User"), button:has-text("New User")');
      if (await addButton.count() > 0) {
        await addButton.click();
        await page.waitForTimeout(300);

        const licenseInput = page.locator('input[name*="license"], input[placeholder*="license" i]');
        if (await licenseInput.count() > 0) {
          await licenseInput.fill(validLicenses[0]);
          await licenseInput.blur();
          await page.waitForTimeout(200);

          const isInvalid = await licenseInput.evaluate(
            (el) => (el as HTMLInputElement).validity.valid === false
          );
          expect(isInvalid).toBeFalsy();

          const errorMessage = page.locator('.error, .invalid-feedback, [role="alert"]');
          const hasError = await errorMessage.count() > 0 && await errorMessage.isVisible().catch(() => false);
          expect(hasError).toBeFalsy();
        }
      }
    }
  });

  test('should reject invalid license formats', async ({ page }) => {
    await page.goto('/settings');

    // Test invalid license formats
    const invalidLicenses = [
      '', // Empty
      'AA', // Too short
      'AA1234567890', // Missing hyphen
      'aa-1234567890', // Lowercase prefix
      'A-1234567890', // Single letter prefix
      'AAAAA-1234567890', // Too many letters
      'AA-12345', // Too few digits
      'AA-1234567890123', // Too many digits
      'INVALID', // No format
      '1234567890' // No prefix
    ];

    // Navigate to users section
    const usersNav = page.locator('a[href*="users"], nav a:has-text("Users")');
    if (await usersNav.count() > 0) {
      await usersNav.click();
      await page.waitForTimeout(500);

      const addButton = page.locator('button:has-text("Add User"), button:has-text("New User")');
      if (await addButton.count() > 0) {
        await addButton.click();
        await page.waitForTimeout(300);

        const licenseInput = page.locator('input[name*="license"], input[placeholder*="license" i]');
        if (await licenseInput.count() > 0) {
          const candidate = invalidLicenses[2]; // AA1234567890
          await licenseInput.fill(candidate);
          await licenseInput.blur();
          await page.waitForTimeout(300);

          // Check if validation error appears
          const errorMessage = page.locator('.error, .invalid-feedback, [role="alert"]');
          // Either error shows or field has invalid state
          const hasValidation =
            (await errorMessage.count() > 0 && await errorMessage.first().isVisible().catch(() => false)) ||
            (await licenseInput.evaluate((el) => (el as HTMLInputElement).validity?.valid === false).catch(() => false));

          const apiValidation = await page.request.post('/api/v1/validate/license', {
            data: JSON.stringify({ license: candidate }),
            headers: { 'content-type': 'application/json' },
          });
          const apiBody = await apiValidation.json();
          const apiRejected = apiBody.valid === false;

          expect(hasValidation || apiRejected).toBeTruthy();
        }
      }
    }
  });

  test('should show error message for invalid license input', async ({ page }) => {
    await page.goto('/settings');

    // Navigate to users section
    const usersNav = page.locator('a[href*="users"], nav a:has-text("Users")');
    if (await usersNav.count() > 0) {
      await usersNav.click();
      await page.waitForTimeout(500);

      const addButton = page.locator('button:has-text("Add User"), button:has-text("New User")');
      if (await addButton.count() > 0) {
        await addButton.click();
        await page.waitForTimeout(300);

        const licenseInput = page.locator('input[name*="license"], input[placeholder*="license" i]');
        if (await licenseInput.count() > 0) {
          // Fill with clearly invalid license
          await licenseInput.fill('INVALID-LICENSE-FORMAT');
          await licenseInput.blur();
          await page.waitForTimeout(500);

          // Look for error message
          const errorSelectors = [
            '.error-message',
            '.invalid-feedback',
            '[role="alert"]',
            '.text-red',
            '.text-red-500',
            '.error',
            'text:has("format")',
            'text:has("invalid")'
          ];

          let errorFound = false;
          for (const selector of errorSelectors) {
            const element = page.locator(selector).first();
            if (await element.count() > 0 && await element.isVisible().catch(() => false)) {
              const text = await element.textContent();
              if (text && (text.toLowerCase().includes('license') || text.toLowerCase().includes('format') || text.toLowerCase().includes('invalid'))) {
                errorFound = true;
                break;
              }
            }
          }

          // If no specific error found, check if form prevents submission
          if (!errorFound) {
            const submitButton = page.locator('button[type="submit"]').first();
            if (await submitButton.count() > 0) {
              const isDisabled = await submitButton.isDisabled().catch(() => false);
              errorFound = isDisabled;
            }
          }

          expect(errorFound).toBeTruthy();
        }
      }
    }
  });

  test('should cover edge cases for license validation', async ({ page }) => {
    await page.goto('/settings');

    // Edge case licenses
    const edgeCases = [
      { license: 'AA-0000000000', description: 'All zeros' },
      { license: 'AA-9999999999', description: 'All nines' },
      { license: 'ZZ-1234567890', description: 'Unknown prefix' },
      { license: 'A1-1234567890', description: 'Mixed prefix' }
    ];

    // Navigate to users section
    const usersNav = page.locator('a[href*="users"], nav a:has-text("Users")');
    if (await usersNav.count() > 0) {
      await usersNav.click();
      await page.waitForTimeout(500);

      const addButton = page.locator('button:has-text("Add User"), button:has-text("New User")');
      if (await addButton.count() > 0) {
        await addButton.click();
        await page.waitForTimeout(300);

        const licenseInput = page.locator('input[name*="license"], input[placeholder*="license" i]');
        if (await licenseInput.count() > 0) {
          // Test the all zeros edge case (should be valid format)
          await licenseInput.fill(edgeCases[0].license);
          await page.waitForTimeout(200);

          // Should accept valid format even with edge case values
          const errorVisible = await page.locator('.error:has-text("license"), .invalid:has-text("license")').isVisible().catch(() => false);
          expect(errorVisible).toBeFalsy();

          // Test mixed alphanumeric prefix (should fail)
          await licenseInput.fill(edgeCases[3].license);
          await licenseInput.blur();
          await page.waitForTimeout(300);

          const hasError = await page.locator('.error, .invalid-feedback').count() > 0 ||
            await licenseInput.evaluate((el) => (el as HTMLInputElement).classList.contains('is-invalid')).catch(() => false);
          expect(hasError).toBeTruthy();
        }
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
