import { Page, Locator } from '@playwright/test';

export class PropertiesPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly addPropertyButton: Locator;
  readonly searchInput: Locator;
  readonly filterButton: Locator;
  readonly propertiesTable: Locator;
  readonly propertyRows: Locator;
  readonly municipalitySelect: Locator;
  readonly paginationControls: Locator;
  readonly nextPageButton: Locator;
  readonly previousPageButton: Locator;
  readonly exportButton: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly deleteButton: Locator;
  readonly addressInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.addPropertyButton = page.locator('button.action-button.primary').last();
    this.searchInput = page.locator('input[placeholder*="Search"]');
    this.filterButton = page.locator('button:has-text("Filter")');
    this.propertiesTable = page.locator('table');
    this.propertyRows = page.locator('tbody tr');
    this.municipalitySelect = page.locator('select').first();
    this.paginationControls = page.locator('.pagination, [aria-label*="pagination"]');
    this.nextPageButton = page.locator('button:has-text("Next"), .pagination button:last-child');
    this.previousPageButton = page.locator('button:has-text("Prev"), .pagination button:first-child');
    this.exportButton = page.locator('button:has-text("Export")');
    this.saveButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Add")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
    this.confirmDeleteButton = page.locator('button:has-text("Delete"), button:has-text("Confirm")');
    this.deleteButton = page.locator('button[title*="Delete"], button.delete-btn');
    this.addressInput = page.locator('input[name*="address"], input[placeholder*="address"]');
  }

  async goto() {
    await this.page.goto('/properties');
  }

  async waitForPropertiesToLoad() {
    await this.propertiesTable.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
    await this.page.waitForTimeout(500);
  }

  async searchProperty(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async getPropertyCount() {
    return await this.propertyRows.count();
  }

  async hasProperties() {
    return (await this.propertyRows.count()) > 0;
  }

  async clickAddProperty() {
    await this.addPropertyButton.click();
  }

  async createProperty(data: Record<string, string>) {
    await this.clickAddProperty();
    await this.page.waitForURL(/\/properties\/(create|new|add)/);
    for (const [name, value] of Object.entries(data)) {
      const input = this.page.locator(`input[name="${name}"], select[name="${name}"]`);
      if (await input.count() > 0) {
        const tag = await input.first().evaluate((el: HTMLElement) => el.tagName.toLowerCase());
        if (tag === 'select') {
          await input.first().selectOption(value);
        } else {
          await input.first().fill(value);
        }
      }
    }
  }

  async editProperty(index: number = 0) {
    const editBtn = this.page.locator('button[title*="Edit"], button.edit-btn').nth(index);
    if (await editBtn.count() > 0) {
      await editBtn.click();
    }
  }

  async deleteProperty(index: number = 0) {
    const delBtn = this.deleteButton.nth(index);
    if (await delBtn.count() > 0) {
      await delBtn.click();
    }
  }

  async viewPropertyDetails(index: number = 0) {
    const row = this.propertyRows.nth(index);
    if (await row.count() > 0) {
      await row.click();
    }
  }

  async getPropertyDetails() {
    return this.page.locator('.property-details, .detail-panel, .details');
  }

  async filterByPropertyType(type: string) {
    const select = this.page.locator('select.filter-dropdown, select[name*="type"]').first();
    if (await select.count() > 0) {
      await select.selectOption(type);
    }
  }

  async filterByStatus(status: string) {
    const select = this.page.locator('select.filter-dropdown, select[name*="status"]').first();
    if (await select.count() > 0) {
      await select.selectOption(status);
    }
  }

  async exportProperties(format: string = 'csv') {
    if (await this.exportButton.count() > 0) {
      await this.exportButton.first().click();
    }
  }

  async getCurrentPageNumber() {
    const activePage = this.page.locator('.pagination .active, .page-active');
    if (await activePage.count() > 0) {
      return parseInt((await activePage.first().textContent()) || '1');
    }
    return 1;
  }

  async getTotalPageCount() {
    const pages = this.page.locator('.pagination button, .pagination a');
    return await pages.count();
  }

  async getFirstPropertyText() {
    if (await this.propertyRows.count() > 0) {
      return await this.propertyRows.first().textContent();
    }
    return null;
  }

  async goToNextPage() {
    if (await this.nextPageButton.count() > 0) {
      await this.nextPageButton.first().click();
    }
  }

  async goToPreviousPage() {
    if (await this.previousPageButton.count() > 0) {
      await this.previousPageButton.first().click();
    }
  }
}
