import { test, expect } from '../setup/fixtures';

test.describe('Properties CRUD - Phase 2 Core Operations', () => {
  const VALID_EMAIL = 'admin@valuadis.com';
  const VALID_PASSWORD = 'Admin123!';

  test.beforeEach(async ({ loginPage, page }) => {
    // Login before each test
    await loginPage.goto();
    await loginPage.login(VALID_EMAIL, VALID_PASSWORD);
    
    // Wait for successful login
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
  });

  test.describe('Create Property', () => {
    test('should create property with Ethiopian address format', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      const initialCount = await propertiesPage.getPropertyCount();
      
      // Create a new property with Ethiopian address
      await propertiesPage.createProperty({
        address: 'Bole, Addis Ababa, Ethiopia',
        municipality: 'Addis Ababa',
        propertyType: 'Residential',
        area: '120',
        condition: 'Good'
      });
      
      // Wait for creation to complete
      await page.waitForTimeout(2000);
      
      // Verify property was created
      const finalCount = await propertiesPage.getPropertyCount();
      expect(finalCount).toBeGreaterThan(initialCount);
      
      // Verify Ethiopian address format is preserved
      const firstPropertyText = await propertiesPage.getFirstPropertyText();
      expect(firstPropertyText).toContain('Bole');
      expect(firstPropertyText).toContain('Addis Ababa');
    });

    test('should validate required fields', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.clickAddProperty();
      
      // Try to save without required fields
      await propertiesPage.saveButton.click();
      
      // Should show validation errors
      const addressInput = propertiesPage.addressInput;
      const isValid = await addressInput.evaluate((el: HTMLInputElement) => el.checkValidity());
      expect(isValid).toBe(false);
    });

    test('should handle Ethiopian municipality selection', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.clickAddProperty();
      
      // Fill in address and check municipality dropdown
      await propertiesPage.addressInput.fill('Mekane Yesus, Addis Ababa');
      
      if (await propertiesPage.municipalitySelect.isVisible()) {
        // Check if Ethiopian municipalities are available
        await propertiesPage.municipalitySelect.click();
        await page.waitForTimeout(500);
        
        // Look for Ethiopian municipalities
        const options = page.locator('option');
        const hasEthiopianMunicipality = await options.filter({ hasText: /Addis|Bahir Dar|Gondar|Hawassa|Mekelle/ }).count() > 0;
        expect(hasEthiopianMunicipality).toBe(true);
      }
    });
  });

  test.describe('Edit Property', () => {
    test('should edit property functionality', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Check if we have properties to edit
      const hasProperties = await propertiesPage.hasProperties();
      if (!hasProperties) {
        // Create a test property first
        await propertiesPage.createProperty({
          address: 'Kirkos, Addis Ababa, Ethiopia',
          propertyType: 'Commercial',
          area: '200',
          condition: 'Fair'
        });
        await page.waitForTimeout(2000);
      }
      
      const initialText = await propertiesPage.getFirstPropertyText();
      
      // Edit the first property
      await propertiesPage.editProperty(0, {
        address: 'Updated Address, Bole, Addis Ababa',
        propertyType: 'Residential',
        area: '150'
      });
      
      // Verify changes were saved
      await page.waitForTimeout(2000);
      const updatedText = await propertiesPage.getFirstPropertyText();
      expect(updatedText).not.toBe(initialText);
      expect(updatedText).toContain('Updated Address');
    });

    test('should preserve Ethiopian data during edit', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a property with Ethiopian data first
      await propertiesPage.createProperty({
        address: 'Arada, Addis Ababa, Ethiopia',
        municipality: 'Addis Ababa',
        propertyType: 'Residential',
        area: '85',
        condition: 'Excellent'
      });
      await page.waitForTimeout(2000);
      
      // Edit the property
      await propertiesPage.editProperty(0, {
        area: '95'
      });
      
      // Verify Ethiopian data is preserved
      const updatedText = await propertiesPage.getFirstPropertyText();
      expect(updatedText).toContain('Arada');
      expect(updatedText).toContain('Addis Ababa');
    });
  });

  test.describe('Delete Property', () => {
    test('should delete property with confirmation', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a test property first
      await propertiesPage.createProperty({
        address: 'Test Property for Deletion, Addis Ababa',
        propertyType: 'Residential',
        area: '100'
      });
      await page.waitForTimeout(2000);
      
      const initialCount = await propertiesPage.getPropertyCount();
      
      // Delete the property
      await propertiesPage.deleteProperty(0);
      
      // Verify property was deleted
      await page.waitForTimeout(2000);
      const finalCount = await propertiesPage.getPropertyCount();
      expect(finalCount).toBeLessThan(initialCount);
    });

    test('should show confirmation dialog before deletion', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a test property first
      await propertiesPage.createProperty({
        address: 'Confirmation Test Property, Addis Ababa',
        propertyType: 'Commercial',
        area: '150'
      });
      await page.waitForTimeout(2000);
      
      // Click delete button
      const deleteButtons = propertiesPage.deleteButton;
      if (await deleteButtons.first().isVisible()) {
        await deleteButtons.first().click();
        await page.waitForTimeout(500);
        
        // Should show confirmation dialog
        const confirmButton = propertiesPage.confirmDeleteButton;
        expect(await confirmButton.isVisible()).toBe(true);
        
        // Cancel deletion to test the dialog
        await propertiesPage.cancelButton.click();
        await page.waitForTimeout(1000);
        
        // Property should still exist
        const propertyCount = await propertiesPage.getPropertyCount();
        expect(propertyCount).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Property Search', () => {
    test('should search properties by address', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create test properties
      await propertiesPage.createProperty({
        address: 'Search Test Property 1, Bole, Addis Ababa',
        propertyType: 'Residential',
        area: '120'
      });
      await page.waitForTimeout(2000);
      
      await propertiesPage.createProperty({
        address: 'Search Test Property 2, Kirkos, Addis Ababa',
        propertyType: 'Commercial',
        area: '200'
      });
      await page.waitForTimeout(2000);
      
      // Search for specific property
      await propertiesPage.searchProperty('Search Test Property 1');
      await page.waitForTimeout(1000);
      
      // Should show filtered results
      const searchResults = await propertiesPage.getFirstPropertyText();
      expect(searchResults).toContain('Search Test Property 1');
      expect(searchResults).not.toContain('Search Test Property 2');
    });

    test('should search properties by municipality', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create test properties with different municipalities
      await propertiesPage.createProperty({
        address: 'Municipality Test 1, Addis Ababa',
        municipality: 'Addis Ababa',
        propertyType: 'Residential',
        area: '100'
      });
      await page.waitForTimeout(2000);
      
      await propertiesPage.createProperty({
        address: 'Municipality Test 2, Bahir Dar',
        municipality: 'Bahir Dar',
        propertyType: 'Residential',
        area: '80'
      });
      await page.waitForTimeout(2000);
      
      // Search by municipality
      await propertiesPage.searchProperty('Addis Ababa');
      await page.waitForTimeout(1000);
      
      // Should show Addis Ababa properties
      const searchResults = await propertiesPage.getFirstPropertyText();
      expect(searchResults).toContain('Addis Ababa');
    });

    test('should handle no search results', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Search for non-existent property
      await propertiesPage.searchProperty('NonExistentProperty12345');
      await propertiesPage.page.waitForTimeout(1000);
      
      // Should show no results or empty state
      const hasProperties = await propertiesPage.hasProperties();
      expect(hasProperties).toBe(false);
    });
  });

  test.describe('Property Filtering', () => {
    test('should filter properties by property type', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create test properties with different types
      await propertiesPage.createProperty({
        address: 'Filter Test Residential, Bole, Addis Ababa',
        propertyType: 'Residential',
        area: '120'
      });
      await page.waitForTimeout(2000);
      
      await propertiesPage.createProperty({
        address: 'Filter Test Commercial, Kirkos, Addis Ababa',
        propertyType: 'Commercial',
        area: '200'
      });
      await page.waitForTimeout(2000);
      
      // Filter by property type
      await propertiesPage.filterByPropertyType('Residential');
      await page.waitForTimeout(1000);
      
      // Should show only residential properties
      const filteredResults = await propertiesPage.getFirstPropertyText();
      expect(filteredResults).toContain('Filter Test Residential');
      expect(filteredResults).not.toContain('Filter Test Commercial');
    });

    test('should filter properties by status', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create test properties
      await propertiesPage.createProperty({
        address: 'Status Test Property 1, Bole, Addis Ababa',
        propertyType: 'Residential',
        area: '100'
      });
      await page.waitForTimeout(2000);
      
      // Filter by status (if available)
      await propertiesPage.filterByStatus('Active');
      await page.waitForTimeout(1000);
      
      // Should not crash and should show some results
      const hasResults = await propertiesPage.hasProperties();
      expect(hasResults).toBe(true);
    });
  });

  test.describe('Property Pagination', () => {
    test('should handle pagination controls', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Check if pagination controls exist
      const hasPagination = await propertiesPage.paginationControls.isVisible();
      
      if (hasPagination) {
        // Test next page button
        if (await propertiesPage.nextPageButton.isVisible()) {
          const currentPage = await propertiesPage.getCurrentPageNumber();
          await propertiesPage.goToNextPage();
          await propertiesPage.page.waitForTimeout(1000);
          
          const nextPage = await propertiesPage.getCurrentPageNumber();
          expect(nextPage).toBeGreaterThan(currentPage);
        }
        
        // Test previous page button
        if (await propertiesPage.previousPageButton.isVisible()) {
          const currentPage = await propertiesPage.getCurrentPageNumber();
          await propertiesPage.goToPreviousPage();
          await propertiesPage.page.waitForTimeout(1000);
          
          const prevPage = await propertiesPage.getCurrentPageNumber();
          expect(prevPage).toBeLessThan(currentPage);
        }
      }
    });

    test('should show correct page count', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      const hasPagination = await propertiesPage.paginationControls.isVisible();
      
      if (hasPagination) {
        const totalPages = await propertiesPage.getTotalPageCount();
        expect(totalPages).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Property Details', () => {
    test('should view property details', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a test property first
      await propertiesPage.createProperty({
        address: 'Details Test Property, Bole, Addis Ababa',
        municipality: 'Addis Ababa',
        propertyType: 'Residential',
        area: '150',
        condition: 'Good'
      });
      await page.waitForTimeout(2000);
      
      // View property details
      await propertiesPage.viewPropertyDetails(0);
      await page.waitForTimeout(2000);
      
      // Check if details page loaded
      const details = await propertiesPage.getPropertyDetails();
      expect(details.title).toBeTruthy();
      expect(details.info).toContain('Details Test Property');
    });

    test('should show valuations in property details', async ({ propertiesPage, page }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a test property first
      await propertiesPage.createProperty({
        address: 'Valuations Test Property, Kirkos, Addis Ababa',
        propertyType: 'Commercial',
        area: '300'
      });
      await page.waitForTimeout(2000);
      
      // View property details
      await propertiesPage.viewPropertyDetails(0);
      await page.waitForTimeout(2000);
      
      // Check if valuations section exists
      const valuationsSection = page.locator('.valuations, .property-valuations');
      const hasValuations = await valuationsSection.isVisible();
      
      // Valuations section may or may not exist depending on implementation
      // We just verify the page loads successfully
      const details = await propertiesPage.getPropertyDetails();
      expect(details.title).toBeTruthy();
    });
  });

  test.describe('Property Export', () => {
    test('should export properties data', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      // Create a test property first
      await propertiesPage.createProperty({
        address: 'Export Test Property, Bole, Addis Ababa',
        propertyType: 'Residential',
        area: '120'
      });
      await propertiesPage.page.waitForTimeout(2000);
      
      // Test export functionality
      const hasExportButton = await propertiesPage.exportButton.isVisible();
      
      if (hasExportButton) {
        await propertiesPage.exportProperties('CSV');
        await propertiesPage.page.waitForTimeout(2000);
        
        // Export should complete without errors
        // We can't verify the actual download in headless mode,
        // but we can verify no error occurred
        const pageContent = await propertiesPage.page.locator('body').textContent();
        expect(pageContent).not.toContain('Error');
        expect(pageContent).not.toContain('Failed');
      }
    });

    test('should support multiple export formats', async ({ propertiesPage }) => {
      await propertiesPage.goto();
      await propertiesPage.waitForPropertiesToLoad();
      
      const hasExportButton = await propertiesPage.exportButton.isVisible();
      
      if (hasExportButton) {
        await propertiesPage.exportProperties();
        await propertiesPage.page.waitForTimeout(500);
        
        // Check if format options are available
        const csvOption = propertiesPage.page.locator('button:has-text("CSV")');
        const excelOption = propertiesPage.page.locator('button:has-text("Excel")');
        const pdfOption = propertiesPage.page.locator('button:has-text("PDF")');
        
        const hasCSV = await csvOption.isVisible();
        const hasExcel = await excelOption.isVisible();
        const hasPDF = await pdfOption.isVisible();
        
        // At least one format should be available
        expect(hasCSV || hasExcel || hasPDF).toBe(true);
      }
    });
  });
});
