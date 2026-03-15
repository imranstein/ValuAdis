import { Page, Locator } from '@playwright/test';

export class PropertiesPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly addPropertyButton: Locator;
  readonly searchInput: Locator;
  readonly filterButton: Locator;
  readonly propertiesTable: Locator;
  readonly propertyRows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.addPropertyButton = page.locator('button.action-button.primary').last();
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.filterButton = page.locator('button:has-text("Filter")');
    this.propertiesTable = page.locator('table');
    this.propertyRows = page.locator('tbody tr');
  }

  async goto() {
    await this.page.goto('/properties');
  }

  async searchProperty(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async getPropertyCount() {
    return await this.propertyRows.count();
  }

  async clickAddProperty() {
    await this.addPropertyButton.click();
  }
}
