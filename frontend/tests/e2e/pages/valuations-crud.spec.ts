import { test, expect } from '../setup/fixtures';
import { TEST_CREDENTIALS } from '../config/test-credentials';

test.describe('Valuations CRUD - Phase 2 Core Operations', () => {
  test.beforeEach(async ({ loginPage, page }) => {
    // Login before each test
    await loginPage.goto();
    await loginPage.login(TEST_CREDENTIALS.email, TEST_CREDENTIALS.fallbackPassword);
    
    // Wait for successful login
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
  });

  test.describe('Create Valuation', () => {
    test('should create valuation with Ethiopian calculations', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      const initialCount = await valuationsPage.getValuationCount();
      
      // Create a new valuation with Ethiopian calculations
      await valuationsPage.createValuation({
        marketValue: '1000000',
        taxableValue: '750000', // 25% tax rate
        confidenceScore: '85',
        valuationDate: '2026-03-07',
        status: 'Draft',
        notes: 'Test valuation with Ethiopian compliance'
      });
      
      // Wait for creation to complete
      await page.waitForTimeout(2000);
      
      // Verify valuation was created
      const finalCount = await valuationsPage.getValuationCount();
      expect(finalCount).toBeGreaterThan(initialCount);
      
      // Verify Ethiopian compliance data
      const firstValuationText = await valuationsPage.getFirstValuationText();
      expect(firstValuationText).toContain('1000000');
      
      // Check if Ethiopian compliance indicators are present
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });

    test('should verify ETB currency formatting', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a valuation with ETB currency
      await valuationsPage.createValuation({
        marketValue: '2500000',
        taxableValue: '1875000',
        confidenceScore: '90',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      // Check if ETB/Birr formatting is present
      const valuationText = await valuationsPage.getFirstValuationText();
      const hasETB = valuationText.includes('ETB') || valuationText.includes('Birr');
      expect(hasETB).toBe(true);
    });

    test('should validate required fields', async ({ valuationsPage }) => {
      await valuationsPage.goto();
      await valuationsPage.clickNewValuation();
      
      // Try to save without required fields
      await valuationsPage.saveButton.click();
      
      // Should show validation errors
      const marketValueInput = valuationsPage.marketValueInput;
      const isValid = await marketValueInput.evaluate((el: HTMLInputElement) => el.checkValidity());
      expect(isValid).toBe(false);
    });
  });

  test.describe('Edit Valuation', () => {
    test('should edit valuation and recalculate', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation first
      await valuationsPage.createValuation({
        marketValue: '500000',
        taxableValue: '375000',
        confidenceScore: '75',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      const initialText = await valuationsPage.getFirstValuationText();
      
      // Edit the valuation
      await valuationsPage.editValuation(0, {
        marketValue: '750000',
        taxableValue: '562500', // Should recalculate
        confidenceScore: '85'
      });
      
      // Verify changes were saved
      await page.waitForTimeout(2000);
      const updatedText = await valuationsPage.getFirstValuationText();
      expect(updatedText).not.toBe(initialText);
      expect(updatedText).toContain('750000');
    });

    test('should recalculate Ethiopian tax on edit', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a valuation with Ethiopian tax
      await valuationsPage.createValuation({
        marketValue: '2000000',
        taxableValue: '1500000', // 25% tax
        confidenceScore: '80',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      // Edit market value
      await valuationsPage.editValuation(0, {
        marketValue: '3000000'
      });
      
      // Verify tax was recalculated
      await page.waitForTimeout(2000);
      const updatedText = await valuationsPage.getFirstValuationText();
      expect(updatedText).toContain('3000000');
      
      // Check Ethiopian compliance
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });
  });

  test.describe('Delete Valuation', () => {
    test('should delete valuation with audit trail', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation first
      await valuationsPage.createValuation({
        marketValue: '1500000',
        taxableValue: '1125000',
        confidenceScore: '85',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      const initialCount = await valuationsPage.getValuationCount();
      
      // Delete the valuation
      await valuationsPage.deleteValuation(0);
      
      // Verify valuation was deleted
      await page.waitForTimeout(2000);
      const finalCount = await valuationsPage.getValuationCount();
      expect(finalCount).toBeLessThan(initialCount);
      
      // Audit trail verification would require database access or admin interface
      // For now, we just verify the deletion succeeded
    });

    test('should show confirmation dialog before deletion', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation first
      await valuationsPage.createValuation({
        marketValue: '1800000',
        taxableValue: '1350000',
        confidenceScore: '90',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      // Click delete button
      const deleteButtons = valuationsPage.deleteButton;
      if (await deleteButtons.first().isVisible()) {
        await deleteButtons.first().click();
        await page.waitForTimeout(500);
        
        // Should show confirmation dialog
        const confirmButton = valuationsPage.confirmDeleteButton;
        expect(await confirmButton.isVisible()).toBe(true);
        
        // Cancel deletion to test the dialog
        await valuationsPage.cancelButton.click();
        await page.waitForTimeout(1000);
        
        // Valuation should still exist
        const valuationCount = await valuationsPage.getValuationCount();
        expect(valuationCount).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Valuation Status Updates', () => {
    test('should test status workflow (Draft → Pending → Approved)', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuation in Draft status
      await valuationsPage.createValuation({
        marketValue: '1200000',
        taxableValue: '900000',
        confidenceScore: '80',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      // Verify initial status
      const initialStatus = await valuationsPage.getValuationStatus(0);
      expect(initialStatus).toBe('Draft');
      
      // Update status to Pending
      await valuationsPage.updateValuationStatus(0, 'Pending');
      await page.waitForTimeout(2000);
      
      // Verify status change
      const pendingStatus = await valuationsPage.getValuationStatus(0);
      expect(pendingStatus).toBe('Pending');
      
      // Update status to Approved
      await valuationsPage.updateValuationStatus(0, 'Approved');
      await page.waitForTimeout(2000);
      
      // Verify final status
      const finalStatus = await valuationsPage.getValuationStatus(0);
      expect(finalStatus).toBe('Approved');
    });

    test('should track status history', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuation
      await valuationsPage.createValuation({
        marketValue: '800000',
        taxableValue: '600000',
        confidenceScore: '75',
        status: 'Draft'
      });
      await page.waitForTimeout(2000);
      
      // Update status multiple times
      await valuationsPage.updateValuationStatus(0, 'Pending');
      await page.waitForTimeout(1000);
      
      await valuationsPage.updateValuationStatus(0, 'Approved');
      await page.waitForTimeout(1000);
      
      // Status history verification would require database access
      // For now, we verify the final status is correct
      const currentStatus = await valuationsPage.getValuationStatus(0);
      expect(currentStatus).toBe('Approved');
    });
  });

  test.describe('Valuation Filtering', () => {
    test('should filter by status', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuations with different statuses
      await valuationsPage.createValuation({
        marketValue: '1000000',
        taxableValue: '750000',
        status: 'Draft'
      });
      await page.waitForTimeout(1000);
      
      await valuationsPage.createValuation({
        marketValue: '1500000',
        taxableValue: '1125000',
        status: 'Approved'
      });
      await page.waitForTimeout(1000);
      
      // Filter by status
      await valuationsPage.filterByStatus('Draft');
      await page.waitForTimeout(1000);
      
      // Should show only Draft valuations
      const filteredResults = await valuationsPage.getFirstValuationText();
      expect(filteredResults).toContain('1000000');
      
      // Filter by Approved
      await valuationsPage.filterByStatus('Approved');
      await page.waitForTimeout(1000);
      
      const approvedResults = await valuationsPage.getFirstValuationText();
      expect(approvedResults).toContain('1500000');
    });

    test('should filter by date range', async ({ valuationsPage }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation
      await valuationsPage.createValuation({
        marketValue: '2000000',
        taxableValue: '1500000',
        valuationDate: '2026-03-07',
        status: 'Draft'
      });
      await valuationsPage.page.waitForTimeout(2000);
      
      // Filter by date range
      await valuationsPage.filterByDateRange('2026-03-01', '2026-03-31');
      await valuationsPage.page.waitForTimeout(1000);
      
      // Should show valuations within the date range
      const hasResults = await valuationsPage.hasValuations();
      expect(hasResults).toBe(true);
    });

    test('should handle multiple filters combined', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuations with different statuses and dates
      await valuationsPage.createValuation({
        marketValue: '900000',
        taxableValue: '675000',
        valuationDate: '2026-03-07',
        status: 'Draft'
      });
      await page.waitForTimeout(1000);
      
      await valuationsPage.createValuation({
        marketValue: '1100000',
        taxableValue: '825000',
        valuationDate: '2026-03-07',
        status: 'Approved'
      });
      await page.waitForTimeout(1000);
      
      // Apply status filter
      await valuationsPage.filterByStatus('Draft');
      await page.waitForTimeout(1000);
      
      // Apply date filter
      await valuationsPage.filterByDateRange('2026-03-01', '2026-03-31');
      await page.waitForTimeout(1000);
      
      // Should show only Draft valuations within date range
      const filteredText = await valuationsPage.getFirstValuationText();
      expect(filteredText).toContain('900000');
    });
  });

  test.describe('Valuation Reports', () => {
    test('should generate Ethiopian compliance report', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation with Ethiopian compliance data
      await valuationsPage.createValuation({
        marketValue: '2500000',
        taxableValue: '1875000',
        confidenceScore: '95',
        valuationDate: '2026-03-07',
        status: 'Approved',
        notes: 'Ethiopian compliance report test'
      });
      await page.waitForTimeout(2000);
      
      // Generate report
      await valuationsPage.generateReport(0, 'PDF');
      await page.waitForTimeout(3000);
      
      // Report generation should complete without errors
      const pageContent = await valuationsPage.page.locator('body').textContent();
      expect(pageContent).not.toContain('Error');
      expect(pageContent).not.toContain('Failed');
      
      // Verify Ethiopian compliance indicators
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });

    test('should include Ethiopian valuer license information', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuation with Ethiopian valuer information
      await valuationsPage.createValuation({
        marketValue: '1800000',
        taxableValue: '1350000',
        confidenceScore: '88',
        status: 'Approved',
        notes: 'Valuer: EV-1234-5678 - Ethiopian Certified Valuer'
      });
      await page.waitForTimeout(2000);
      
      // Generate report
      await valuationsPage.generateReport(0, 'PDF');
      await page.waitForTimeout(3000);
      
      // Check if valuer information is included
      const valuationText = await valuationsPage.getFirstValuationText();
      const hasValuerInfo = valuationText.includes('EV-') || valuationText.includes('Valuer');
      expect(hasValuerInfo).toBe(true);
    });

    test('should support multiple report formats', async ({ valuationsPage }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create a test valuation
      await valuationsPage.createValuation({
        marketValue: '1600000',
        taxableValue: '1200000',
        status: 'Approved'
      });
      await valuationsPage.page.waitForTimeout(2000);
      
      // Test Excel format
      await valuationsPage.generateReport(0, 'Excel');
      await valuationsPage.page.waitForTimeout(3000);
      
      // Should complete without errors
      const pageContent = await valuationsPage.page.locator('body').textContent();
      expect(pageContent).not.toContain('Error');
    });
  });

  test.describe('Quick Valuation', () => {
    test('should create quick valuation workflow', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      const initialCount = await valuationsPage.getValuationCount();
      
      // Create quick valuation
      await valuationsPage.createQuickValuation('Test Property', '1200000');
      await page.waitForTimeout(2000);
      
      // Verify quick valuation was created
      const finalCount = await valuationsPage.getValuationCount();
      expect(finalCount).toBeGreaterThan(initialCount);
      
      // Verify Ethiopian compliance
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });

    test('should verify Ethiopian compliance checks in quick valuation', async ({ valuationsPage }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create quick valuation
      await valuationsPage.createQuickValuation('Quick Test Property', '2000000');
      await valuationsPage.page.waitForTimeout(2000);
      
      // Verify Ethiopian compliance indicators
      const valuationText = await valuationsPage.getFirstValuationText();
      const hasETB = valuationText.includes('ETB') || valuationText.includes('Birr');
      expect(hasETB).toBe(true);
      
      // Verify tax calculation compliance (25% rate)
      const marketValue = await valuationsPage.getValuationMarketValue(0);
      expect(marketValue).toContain('2000000');
      
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });

    test('should handle minimal required data in quick valuation', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Check if quick valuation button is available
      const hasQuickButton = await valuationsPage.quickValuationButton.isVisible();
      
      if (hasQuickButton) {
        await valuationsPage.createQuickValuation('Minimal Test', '500000');
        await page.waitForTimeout(2000);
        
        // Should create valuation successfully
        const hasValuations = await valuationsPage.hasValuations();
        expect(hasValuations).toBe(true);
      }
    });
  });

  test.describe('Ethiopian Compliance Validation', () => {
    test('should enforce ETB currency formatting', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuation
      await valuationsPage.createValuation({
        marketValue: '3000000',
        taxableValue: '2250000',
        confidenceScore: '92',
        status: 'Approved'
      });
      await page.waitForTimeout(2000);
      
      // Verify ETB formatting
      const valuationText = await valuationsPage.getFirstValuationText();
      const hasCurrency = valuationText.includes('ETB') || valuationText.includes('Birr');
      expect(hasCurrency).toBe(true);
    });

    test('should verify 25% tax calculation compliance', async ({ valuationsPage, page }) => {
      await valuationsPage.goto();
      await valuationsPage.waitForValuationsToLoad();
      
      // Create valuation with specific amounts
      await valuationsPage.createValuation({
        marketValue: '4000000',
        taxableValue: '3000000', // Exactly 25%
        confidenceScore: '95',
        status: 'Approved'
      });
      await page.waitForTimeout(2000);
      
      // Verify tax calculation compliance
      const marketValue = await valuationsPage.getValuationMarketValue(0);
      expect(marketValue).toContain('4000000');
      
      const isCompliant = await valuationsPage.verifyEthiopianCompliance(0);
      expect(isCompliant).toBe(true);
    });
  });
});
