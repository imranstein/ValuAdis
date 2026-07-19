import { Page, Locator } from '@playwright/test';

/**
 * The rebranded Users surface is a read-only access registry: a search box,
 * role/status filters, metric cards, and a backend-backed table. There is no
 * in-app create/edit/deactivate UI, so this page object exposes registry
 * read/filter helpers plus pure Ethiopian format validators used by the specs.
 */
export class UsersPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly searchInput: Locator;
  readonly roleFilter: Locator;
  readonly statusFilter: Locator;
  readonly refreshButton: Locator;
  readonly resetFiltersButton: Locator;
  readonly usersTable: Locator;
  readonly userRows: Locator;
  readonly metricCards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.searchInput = page.locator('input[type="search"]');
    this.roleFilter = page.locator('select[aria-label="Filter by role"]');
    this.statusFilter = page.locator('select[aria-label="Filter by status"]');
    this.refreshButton = page.getByRole('button', { name: /refresh/i });
    this.resetFiltersButton = page.getByRole('button', { name: /reset filters/i });
    this.usersTable = page.locator('table.data-table');
    // Real data rows only (skip loading / empty placeholder rows which span all columns).
    this.userRows = page.locator('tbody tr:not(:has(td[colspan]))');
    this.metricCards = page.locator('.metric-card');
  }

  async goto() {
    // Single navigation so the storageState token stays available in memory for
    // the admin middleware (a second goto would drop the consumed token and force
    // a refresh round-trip that races under parallel workers).
    await this.page.goto('/users', { waitUntil: 'domcontentloaded' });
  }

  async waitForUsersToLoad() {
    await this.usersTable.waitFor({ state: 'visible', timeout: 20000 }).catch(() => {});
    // Seeded registry always has rows; wait generously so parallel-worker
    // hydration lag doesn't leave a test reading an empty table.
    await this.userRows.first().waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
  }

  async searchUser(query: string) {
    await this.searchInput.fill(query);
    // Registry filtering is reactive on input; no submit needed.
    await this.page.waitForTimeout(300);
  }

  async filterByRole(role: string) {
    await this.roleFilter.selectOption({ label: role });
    await this.page.waitForTimeout(300);
  }

  async filterByStatus(status: string) {
    await this.statusFilter.selectOption(status);
    await this.page.waitForTimeout(300);
  }

  async getUserCount() {
    return await this.userRows.count();
  }

  async hasUsers(): Promise<boolean> {
    return (await this.getUserCount()) > 0;
  }

  async getFirstUserText(): Promise<string> {
    return (await this.userRows.first().textContent()) || '';
  }

  async validateEthiopianPhone(phone: string): Promise<boolean> {
    const ethiopianPhoneRegex = /^(\+2519\d{8}|09\d{8})$/;
    return ethiopianPhoneRegex.test(phone);
  }

  async validateLicenseNumber(license: string): Promise<boolean> {
    const licenseRegex = /^[A-Z]{2}-\d{4}-\d{4}$/;
    return licenseRegex.test(license);
  }
}
