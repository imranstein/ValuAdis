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
    this.pageTitle = page.locator('h1');
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
    await this.page.goto('/settings');
  }

  async switchToTab(tabName: string) {
    const tab = this.page.locator(`button:has-text("${tabName}")`);
    await tab.click();
  }

  async saveSettings() {
    await this.saveButton.click();
  }
}
