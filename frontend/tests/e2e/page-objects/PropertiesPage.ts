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
    this.pageTitle = page.getByRole('heading', { name: /properties/i }).first();
    this.addPropertyButton = page.getByRole('button', { name: /create property/i }).first();
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.filterButton = page.locator('button:has-text("Reset")');
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

  async waitForPropertiesToLoad() {
    await this.page.waitForSelector('table.modern-table, .empty-state, .properties-table', { timeout: 10000 });
  }

  async hasProperties() {
    return (await this.propertyRows.count()) > 0;
  }

  async getFirstPropertyText() {
    const first = this.propertyRows.first();
    return first.isVisible() ? first.textContent() : '';
  }

  get saveButton() {
    return this.page.locator('button[type="submit"], button:has-text("Save")');
  }

  get addressInput() {
    return this.page.locator('input[name="address"], input[placeholder*="address" i]').first();
  }

  get municipalitySelect() {
    return this.page.locator('select').filter({ hasText: /municipality|addis/i }).first();
  }

  get deleteButton() {
    return this.page.locator('button[title*="Delete" i], .action-btn.delete');
  }

  get confirmDeleteButton() {
    return this.page.locator('button:has-text("Confirm"), button:has-text("Delete")');
  }

  get cancelButton() {
    return this.page.locator('button:has-text("Cancel")');
  }

  async createProperty(_data: { address?: string; municipality?: string; propertyType?: string; area?: string; condition?: string }) {
    await this.clickAddProperty();
    await this.page.waitForURL(/\/properties\/create/, { timeout: 5000 });
  }

  async editProperty(_index: number, _changes: Record<string, string>) {
    await this.deleteButton.nth(_index).click();
  }

  async deleteProperty(_index: number) {
    await this.deleteButton.nth(_index).click();
    await this.page.waitForTimeout(300);
    await this.confirmDeleteButton.click();
  }
}
