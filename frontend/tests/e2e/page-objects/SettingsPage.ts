import { Page, Locator } from '@playwright/test';

/**
 * The rebranded Settings surface is a set of restrained panels (no tab bar):
 * Administrative profile, Workspace behavior, Email delivery, Security limits,
 * and an API keys table. Actions are "Create API key" (backend-backed, prompts
 * for a name) and "Save settings" (PUT to the backend settings service).
 */
export class SettingsPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly panels: Locator;
  readonly panelTitles: Locator;
  readonly saveButton: Locator;
  readonly createKeyButton: Locator;
  readonly apiKeysTable: Locator;
  readonly apiKeyRows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1').first();
    this.panels = page.locator('.panel');
    this.panelTitles = page.locator('.panel-title');
    this.saveButton = page.getByRole('button', { name: /save settings/i });
    this.createKeyButton = page.getByRole('button', { name: /create api key/i });
    this.apiKeysTable = page.locator('.table-panel table.data-table');
    this.apiKeyRows = page.locator('.table-panel tbody tr:not(:has(.empty-cell))');
  }

  async goto() {
    // Single navigation: the storageState token is consumed into memory on this
    // load and the global auth boot populates the user store before the admin
    // middleware runs. A second goto would drop the consumed token and force a
    // refresh round-trip that races under parallel workers.
    await this.page.goto('/settings', { waitUntil: 'domcontentloaded' });
    // Hydration can be slow under parallel workers; wait generously for panels.
    await this.panelTitles.first().waitFor({ state: 'visible', timeout: 20000 });
  }

  async saveSettings() {
    await this.saveButton.click();
  }

  async createApiKey(name = 'Integration key') {
    // Creating a key prompts for a name; accept the dialog before clicking.
    this.page.once('dialog', (dialog) => dialog.accept(name));
    await this.createKeyButton.click();
  }

  // Back-compat alias for specs that referenced the old draft flow.
  async createDraftKey() {
    await this.createApiKey();
  }
}
