import { Page, Locator } from '@playwright/test';

export class AnalyticsPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly exportButton: Locator;
  readonly refreshButton: Locator;
  readonly dateRangeSelect: Locator;
  readonly customStartDate: Locator;
  readonly customEndDate: Locator;
  readonly metricCards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.exportButton = page.locator('button.action-button.secondary, button:has-text("Export")');
    this.refreshButton = page.locator('button.action-button.primary, button:has-text("Refresh")');
    this.dateRangeSelect = page.locator('select.date-select');
    this.customStartDate = page.locator('input[type="date"]').nth(0);
    this.customEndDate = page.locator('input[type="date"]').nth(1);
    this.metricCards = page.locator('.metric-card');
  }

  async goto() {
    await this.page.goto('/analytics', { waitUntil: 'domcontentloaded' });
  }

  async waitForAnalyticsToLoad() {
    await this.page.waitForTimeout(2000);
  }

  async selectDateRange(range: string) {
    await this.dateRangeSelect.selectOption(range);
    await this.page.waitForTimeout(500);
  }

  async setCustomDateRange(startDate: string, endDate: string) {
    await this.selectDateRange('custom');
    await this.customStartDate.fill(startDate);
    await this.customEndDate.fill(endDate);
    await this.page.waitForTimeout(500);
  }

  async getMetricCount(): Promise<number> {
    return await this.metricCards.count();
  }

  async hasMetrics(): Promise<boolean> {
    return (await this.metricCards.count()) > 0;
  }

  async refreshData() {
    await this.refreshButton.click();
    await this.page.waitForTimeout(1000);
  }

  async exportReport() {
    if (await this.exportButton.count() > 0) {
      await this.exportButton.click();
    }
  }
}
