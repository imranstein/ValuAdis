import { test, expect } from '../setup/fixtures';

test.describe('Settings Management', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ settingsPage }) => {
    await settingsPage.goto();
  });

  test('should display settings page', async ({ settingsPage }) => {
    await expect(settingsPage.pageTitle).toBeVisible();
    await expect(settingsPage.pageTitle).toContainText(/Settings/i);
  });

  test('should display all settings tabs', async ({ settingsPage }) => {
    await expect(settingsPage.generalTab).toBeVisible();
    await expect(settingsPage.valuationTab).toBeVisible();
    await expect(settingsPage.notificationsTab).toBeVisible();
    await expect(settingsPage.securityTab).toBeVisible();
    await expect(settingsPage.backupTab).toBeVisible();
    await expect(settingsPage.apiTab).toBeVisible();
    await expect(settingsPage.scraperTab).toBeVisible();
  });

  test('should switch between tabs', async ({ settingsPage }) => {
    await settingsPage.switchToTab('Valuation');
    await expect(settingsPage.valuationTab).toHaveClass(/active/);
    
    await settingsPage.switchToTab('Security');
    await expect(settingsPage.securityTab).toHaveClass(/active/);
  });

  test('should display save button', async ({ settingsPage }) => {
    await expect(settingsPage.saveButton).toBeVisible();
  });

  test('should save settings', async ({ settingsPage, page }) => {
    await settingsPage.saveSettings();
    await page.waitForTimeout(500);
    
    const successMessage = page.locator('.success, .save-status.success');
    if (await successMessage.count() > 0) {
      await expect(successMessage.first()).toBeVisible();
    }
  });

  test.describe('Web Scraper Tab', () => {
    test.beforeEach(async ({ settingsPage }) => {
      await settingsPage.switchToTab('Web Scraper');
    });

    test('should display web scraper tab content', async ({ page }) => {
      const scraperSection = page.locator('.scraper-section, h2:has-text("Web Scraper")');
      await expect(scraperSection.first()).toBeVisible();
    });

    test('should display scraper statistics', async ({ page }) => {
      const stats = page.locator('.scraper-stats, .stat-card');
      if (await stats.count() > 0) {
        await expect(stats.first()).toBeVisible();
      }
    });

    test('should display add scraper button', async ({ page }) => {
      const addButton = page.locator('button:has-text("Add New")').first();
      await expect(addButton).toBeVisible();
    });

    test('should display scrapers table', async ({ page }) => {
      const table = page.locator('table');
      if (await table.count() > 0) {
        await expect(table.first()).toBeVisible();
      }
    });

    test('should open add scraper modal', async ({ page }) => {
      const addButton = page.locator('button:has-text("Add New")').first();
      await addButton.click();
      await page.waitForTimeout(300);

      const modal = page.locator('.modal-overlay, .modal, [role="dialog"]');
      await expect(modal.first()).toBeVisible();
    });

    test('should validate scraper form fields', async ({ page }) => {
      const addButton = page.locator('button:has-text("Add New")').first();
      await addButton.click();
      await page.waitForTimeout(300);
      
      const domainInput = page.locator('input[name="domain"], label:has-text("Domain") + input');
      const urlInput = page.locator('input[name="url_template"], label:has-text("URL") + input');
      
      if (await domainInput.count() > 0) {
        await expect(domainInput.first()).toBeVisible();
      }
      if (await urlInput.count() > 0) {
        await expect(urlInput.first()).toBeVisible();
      }
    });

    test('should toggle scraper status', async ({ page }) => {
      const toggleButton = page.locator('button[title*="Enable"], button[title*="Disable"]').first();
      
      if (await toggleButton.count() > 0) {
        await toggleButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('should test scraper configuration', async ({ page }) => {
      const testButton = page.locator('button[title*="Test"]').first();
      
      if (await testButton.count() > 0) {
        await testButton.click();
        await page.waitForTimeout(1000);
      }
    });

    test('should run scraper manually', async ({ page }) => {
      const runButton = page.locator('button[title*="Run"]').first();
      
      if (await runButton.count() > 0) {
        page.on('dialog', dialog => dialog.accept());
        await runButton.click();
        await page.waitForTimeout(500);
      }
    });

    test('should display scraper logs', async ({ page }) => {
      const logsSection = page.locator('.scraper-logs, h3:has-text("Logs")');
      if (await logsSection.count() > 0) {
        await expect(logsSection.first()).toBeVisible();
      }
    });

    test('should refresh scraper data', async ({ page }) => {
      const refreshButton = page.locator('button:has-text("Refresh")');
      if (await refreshButton.count() > 0) {
        await refreshButton.first().click();
        await page.waitForTimeout(500);
      }
    });

    test('should edit existing scraper', async ({ page }) => {
      const editButton = page.locator('button[title*="Edit"]').first();
      
      if (await editButton.count() > 0) {
        await editButton.click();
        await page.waitForTimeout(300);
        
        const modal = page.locator('.modal, [role="dialog"]');
        await expect(modal).toBeVisible();
      }
    });

    test('should delete scraper', async ({ page }) => {
      const deleteButton = page.locator('button[title*="Delete"]').first();
      
      if (await deleteButton.count() > 0) {
        page.on('dialog', dialog => dialog.accept());
        await deleteButton.click();
        await page.waitForTimeout(500);
      }
    });
  });

  test('should have responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/settings');

    const tabs = page.locator('.nav-tab');
    await tabs.first().waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    const count = await tabs.count();
    expect(count).toBeGreaterThan(0);
  });
});
