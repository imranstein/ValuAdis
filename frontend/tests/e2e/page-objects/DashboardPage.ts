import { Page, Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly statsCards: Locator;
  readonly recentActivities: Locator;
  readonly quickActions: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.statsCards = page.locator('.metric-card');
    this.recentActivities = page.locator('.table-panel').filter({ hasText: 'Recent valuations' });
    this.quickActions = page.locator('.page-actions');
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async getStatsCount() {
    await this.statsCards.first().waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    return await this.statsCards.count();
  }
}
