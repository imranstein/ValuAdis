import { Page, Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly statsCards: Locator;
  readonly recentActivities: Locator;
  readonly quickActions: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.statsCards = page.locator('.stat-card');
    this.recentActivities = page.locator('.recent-activities');
    this.quickActions = page.locator('.quick-actions');
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async getStatsCount() {
    return await this.statsCards.count();
  }
}
