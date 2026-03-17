import { Page, Locator } from '@playwright/test';

export class AuditPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly exportButton: Locator;
  readonly refreshButton: Locator;
  readonly dateRangeFilter: Locator;
  readonly actionTypeFilter: Locator;
  readonly userSearchInput: Locator;
  readonly moduleFilter: Locator;
  readonly resetButton: Locator;
  readonly auditTable: Locator;
  readonly auditRows: Locator;
  readonly recordCount: Locator;
  readonly detailButtons: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.exportButton = page.locator('button.action-button.secondary, button:has-text("Export")');
    this.refreshButton = page.locator('button.action-button.primary, button:has-text("Refresh")');
    this.dateRangeFilter = page.locator('.filters-section select').nth(0);
    this.actionTypeFilter = page.locator('.filters-section select').nth(1);
    this.userSearchInput = page.locator('input[placeholder="Search user..."]');
    this.moduleFilter = page.locator('.filters-section select').nth(2);
    this.resetButton = page.locator('button.reset-button');
    this.auditTable = page.locator('table.audit-table, table');
    this.auditRows = page.locator('table.audit-table tbody tr, .audit-table tbody tr');
    this.recordCount = page.locator('.table-info span');
    this.detailButtons = page.locator('button.detail-btn');
  }

  async goto() {
    await this.page.goto('/audit', { waitUntil: 'domcontentloaded' });
  }

  async waitForLogsToLoad() {
    await this.auditTable.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    await this.page.waitForTimeout(500);
  }

  async getLogCount(): Promise<number> {
    return await this.auditRows.count();
  }

  async hasLogs(): Promise<boolean> {
    return (await this.auditRows.count()) > 0;
  }

  async filterByActionType(actionType: string) {
    await this.actionTypeFilter.selectOption(actionType);
    await this.page.waitForTimeout(500);
  }

  async filterByModule(module: string) {
    await this.moduleFilter.selectOption(module);
    await this.page.waitForTimeout(500);
  }

  async searchByUser(query: string) {
    await this.userSearchInput.fill(query);
    await this.page.waitForTimeout(500);
  }

  async resetFilters() {
    await this.resetButton.click();
    await this.page.waitForTimeout(500);
  }

  async exportAuditLog() {
    if (await this.exportButton.count() > 0) {
      await this.exportButton.click();
    }
  }

  async viewLogDetails(index: number = 0) {
    if (await this.detailButtons.nth(index).isVisible()) {
      await this.detailButtons.nth(index).click();
    }
  }

  async getRecordCountText(): Promise<string> {
    return (await this.recordCount.first().textContent()) || '';
  }
}
