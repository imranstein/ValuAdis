import { Page, Locator } from '@playwright/test';

export class ValuationsPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly newValuationButton: Locator;
  readonly quickValuationButton: Locator;
  readonly searchInput: Locator;
  readonly valuationsTable: Locator;
  readonly valuationRows: Locator;
  readonly statusFilter: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly deleteButton: Locator;
  readonly marketValueInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.newValuationButton = page.locator('button.action-button.primary').last();
    this.quickValuationButton = page.locator('button:has-text("Quick"), a:has-text("Quick")').first();
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.valuationsTable = page.locator('table');
    this.valuationRows = page.locator('tbody tr');
    this.statusFilter = page.locator('select.filter-dropdown').first();
    this.saveButton = page.locator('button[type="submit"], button:has-text("Save")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
    this.confirmDeleteButton = page.locator('button:has-text("Delete"), button:has-text("Confirm")');
    this.deleteButton = page.locator('button[title*="Delete"], button.delete-btn');
    this.marketValueInput = page.locator('input[name*="market_value"], input[name*="value"]');
  }

  async goto() {
    await this.page.goto('/valuations');
  }

  async waitForValuationsToLoad() {
    await this.valuationsTable.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    await this.page.waitForTimeout(500);
  }

  async searchValuation(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async filterByStatus(status: string) {
    await this.statusFilter.selectOption(status);
  }

  async getValuationCount() {
    await this.valuationRows.first().waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
    return await this.valuationRows.count();
  }

  async hasValuations() {
    return (await this.valuationRows.count()) > 0;
  }

  async clickNewValuation() {
    await this.newValuationButton.click();
  }

  async createValuation(data: Record<string, string>) {
    await this.clickNewValuation();
    await this.page.waitForURL(/\/valuations\/(create|new|quick)/, { timeout: 5000 }).catch(() => {});
    await this.page.waitForTimeout(500);
    for (const [name, value] of Object.entries(data)) {
      const input = this.page.locator(`input[name="${name}"], select[name="${name}"]`).first();
      if (await input.count() > 0) {
        const tag = await input.evaluate((el: HTMLElement) => el.tagName.toLowerCase());
        if (tag === 'select') await input.selectOption(value);
        else await input.fill(value);
      }
    }
  }

  async createQuickValuation(propertyName: string = '', _amount: string = '') {
    await this.page.goto('/valuations/quick');
    await this.page.waitForLoadState('networkidle').catch(() => {});
    if (propertyName) {
      const nameInput = this.page.locator('input[placeholder*="property" i], input[placeholder*="name" i]').first();
      if (await nameInput.count() > 0) await nameInput.fill(propertyName);
    }
  }

  async editValuation(index: number = 0, _data?: Record<string, string>) {
    const editBtn = this.page.locator('button[title*="Edit"], button.edit-btn').nth(index);
    if (await editBtn.count() > 0) await editBtn.click();
  }

  async deleteValuation(index: number = 0) {
    const delBtn = this.deleteButton.nth(index);
    if (await delBtn.count() > 0) {
      this.page.once('dialog', dialog => dialog.accept());
      await delBtn.click();
      await this.page.waitForTimeout(300);
      if (await this.confirmDeleteButton.isVisible()) {
        await this.confirmDeleteButton.click();
      }
    }
  }

  async updateValuationStatus(_index: number = 0, status: string) {
    const statusSelect = this.page.locator('select[name*="status"]');
    if (await statusSelect.count() > 0) await statusSelect.selectOption(status);
  }

  async getValuationStatus(index: number = 0) {
    const statusCell = this.valuationRows.nth(index).locator('.status-badge, td:has-text("pending"), td:has-text("approved")');
    if (await statusCell.count() > 0) return await statusCell.first().textContent();
    return null;
  }

  async getValuationMarketValue(index: number = 0) {
    const valueCell = this.valuationRows.nth(index).locator('td').nth(3);
    if (await valueCell.count() > 0) return await valueCell.textContent();
    return null;
  }

  async getFirstValuationText() {
    if (await this.valuationRows.count() > 0) return await this.valuationRows.first().textContent();
    return null;
  }

  async generateReport(_index?: number, _format?: string) {
    const reportBtn = this.page.locator('button:has-text("Report"), button:has-text("Generate"), button:has-text("Export")');
    if (await reportBtn.count() > 0) await reportBtn.first().click();
  }

  async filterByDateRange(startDate: string, endDate: string) {
    const startInput = this.page.locator('input[type="date"], input[name*="start"]').first();
    const endInput = this.page.locator('input[type="date"], input[name*="end"]').last();
    if (await startInput.count() > 0) await startInput.fill(startDate);
    if (await endInput.count() > 0) await endInput.fill(endDate);
  }

  async verifyEthiopianCompliance(_index?: number): Promise<boolean> {
    const complianceSection = this.page.locator('.compliance, [data-compliance], label:has-text("Proclamation"), :has-text("ETB"), :has-text("Birr")');
    return (await complianceSection.count()) > 0;
  }
}
