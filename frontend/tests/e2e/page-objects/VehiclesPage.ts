import { Page, Locator } from '@playwright/test';

export class VehiclesPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly addVehicleButton: Locator;
  readonly exportButton: Locator;
  readonly searchInput: Locator;
  readonly makeFilter: Locator;
  readonly yearFilter: Locator;
  readonly regionFilter: Locator;
  readonly statusFilter: Locator;
  readonly resetButton: Locator;
  readonly vehiclesTable: Locator;
  readonly vehicleRows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.addVehicleButton = page.locator('button.action-button.primary, button:has-text("Add Vehicle"), button:has-text("Create Vehicle")');
    this.exportButton = page.locator('button.action-button.secondary, button:has-text("Export")');
    this.searchInput = page.locator('input[placeholder*="Search vehicles"]');
    this.makeFilter = page.locator('select.filter-dropdown').nth(0);
    this.yearFilter = page.locator('select.filter-dropdown').nth(1);
    this.regionFilter = page.locator('select.filter-dropdown').nth(2);
    this.statusFilter = page.locator('select.filter-dropdown').nth(3);
    this.resetButton = page.locator('button.reset-button');
    this.vehiclesTable = page.locator('table.vehicles-table, table');
    this.vehicleRows = page.locator('table.vehicles-table tbody tr, tbody tr');
  }

  async goto() {
    await this.page.goto('/vehicles', { waitUntil: 'domcontentloaded' });
  }

  async waitForVehiclesToLoad() {
    await this.vehiclesTable.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    await this.page.waitForTimeout(500);
  }

  async searchVehicle(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500);
  }

  async getVehicleCount(): Promise<number> {
    return await this.vehicleRows.count();
  }

  async hasVehicles(): Promise<boolean> {
    return (await this.vehicleRows.count()) > 0;
  }

  async resetFilters() {
    await this.resetButton.click();
    await this.page.waitForTimeout(500);
  }

  async exportVehicles() {
    if (await this.exportButton.count() > 0) {
      await this.exportButton.click();
    }
  }

  async clickAddVehicle() {
    await this.addVehicleButton.click();
    await this.page.waitForURL(/\/vehicles\/(create|new)/, { timeout: 5000 });
  }
}
