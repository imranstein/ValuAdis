import { Page, Locator } from '@playwright/test';

export class ValuationsPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly newValuationButton: Locator;
  readonly searchInput: Locator;
  readonly valuationsTable: Locator;
  readonly valuationRows: Locator;
  readonly statusFilter: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.newValuationButton = page.locator('button:has-text("New Valuation")');
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.valuationsTable = page.locator('table');
    this.valuationRows = page.locator('tbody tr');
    this.statusFilter = page.locator('select[name="status"]');
  }

  async goto() {
    await this.page.goto('/valuations');
  }

  async searchValuation(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async filterByStatus(status: string) {
    await this.statusFilter.selectOption(status);
  }

  async getValuationCount() {
    return await this.valuationRows.count();
  }

  async clickNewValuation() {
    await this.newValuationButton.click();
  }
}
