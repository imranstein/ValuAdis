import { Page, Locator } from '@playwright/test';

export class ScrapersPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly refreshAllButton: Locator;
  readonly scraperCards: Locator;
  readonly scraperStatus: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.refreshAllButton = page.locator('button:has-text("Refresh"), button.btn-secondary');
    this.scraperCards = page.locator('.scraper-card, .scraper-item, [data-testid="scraper-card"]');
    this.scraperStatus = page.locator('.scraper-status, .status-badge, [data-testid="scraper-status"]');
  }

  async goto() {
    await this.page.goto('/scrapers', { waitUntil: 'domcontentloaded' });
  }

  async waitForScrapersToLoad() {
    await this.page.waitForTimeout(2000);
  }

  async refreshAll() {
    await this.refreshAllButton.click();
    await this.page.waitForTimeout(1000);
  }

  async getScraperCount(): Promise<number> {
    return await this.scraperCards.count();
  }

  async hasScrapers(): Promise<boolean> {
    return (await this.scraperCards.count()) > 0;
  }

  async getScraperStatus(index: number): Promise<string> {
    return (await this.scraperStatus.nth(index).textContent()) || '';
  }
}
