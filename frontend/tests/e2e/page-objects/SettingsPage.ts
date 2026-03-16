import { Page, Locator } from '@playwright/test';

export class SettingsPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly generalTab: Locator;
  readonly valuationTab: Locator;
  readonly notificationsTab: Locator;
  readonly securityTab: Locator;
  readonly backupTab: Locator;
  readonly apiTab: Locator;
  readonly scraperTab: Locator;
  readonly saveButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.generalTab = page.locator('button:has-text("General")');
    this.valuationTab = page.locator('button:has-text("Valuation")');
    this.notificationsTab = page.locator('button:has-text("Notifications")');
    this.securityTab = page.locator('button:has-text("Security")');
    this.backupTab = page.locator('button:has-text("Backup")');
    this.apiTab = page.locator('button:has-text("API")');
    this.scraperTab = page.locator('button:has-text("Web Scraper")');
    this.saveButton = page.locator('button:has-text("Save Changes")');
  }

  async goto() {
    // Navigate to dashboard first (full load) so auth.client.ts plugin fully populates
    // the user store before admin middleware checks is_admin on /settings
    await this.page.goto('/dashboard');
    await this.page.goto('/settings');
    await this.page.locator('.nav-tab').first().waitFor({ state: 'visible', timeout: 10000 });
  }

  async switchToTab(tabName: string) {
    const tab = this.page.locator(`button:has-text("${tabName}")`);
    await tab.waitFor({ state: 'visible', timeout: 10000 });
    await tab.click();
  }

  async saveSettings() {
    await this.saveButton.click();
  }
}
