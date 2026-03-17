import { Page, Locator } from '@playwright/test';

export class UsersPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly addUserButton: Locator;
  readonly searchInput: Locator;
  readonly usersTable: Locator;
  readonly userRows: Locator;
  
  // CRUD form elements
  readonly userForm: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly roleSelect: Locator;
  readonly licenseNumberInput: Locator;
  readonly statusSelect: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;
  readonly deleteButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly editButton: Locator;
  readonly deactivateButton: Locator;
  readonly activateButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator('h1');
    this.addUserButton = page.locator('button:has-text("Add User"), button:has-text("Create User"), [data-testid="add-user"]');
    this.searchInput = page.locator('input[placeholder*="Search"], input[type="search"]');
    this.usersTable = page.locator('table, .data-table');
    this.userRows = page.locator('tbody tr, .table-row');
    
    // Form elements for CRUD operations
    this.userForm = page.locator('form, .user-form');
    this.firstNameInput = page.locator('input[name*="first_name"], input[placeholder*="first"]');
    this.lastNameInput = page.locator('input[name*="last_name"], input[placeholder*="last"]');
    this.emailInput = page.locator('input[name*="email"], input[type="email"]');
    this.phoneInput = page.locator('input[type="tel"]');
    this.roleSelect = page.locator('.modal-content select').first();
    this.licenseNumberInput = page.locator('input[placeholder*="license" i], input[placeholder*="EV-"]');
    this.statusSelect = page.locator('.modal-content select').nth(1);
    this.saveButton = page.locator('button:has-text("Save"), button:has-text("Submit"), button[type="submit"]');
    this.cancelButton = page.locator('button:has-text("Cancel"), button:has-text("Back")');
    this.deleteButton = page.locator('button.action-btn.delete, button[title="Delete"]');
    this.confirmDeleteButton = page.locator('button:has-text("Delete"), button:has-text("Confirm")').last();
    this.editButton = page.locator('button.action-btn.edit, button[title="Edit"]');
    this.deactivateButton = page.locator('button:has-text("Deactivate"), [data-testid="deactivate"]');
    this.activateButton = page.locator('button:has-text("Activate"), [data-testid="activate"]');
  }

  async goto() {
    await this.page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await this.page.goto('/users', { waitUntil: 'domcontentloaded' });
  }

  async searchUser(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(1000);
  }

  async getUserCount() {
    return await this.userRows.count();
  }

  async clickAddUser() {
    await this.addUserButton.click();
    await this.page.waitForTimeout(1000);
  }

  // CRUD Operations
  
  async createUser(userData: {
    firstName: string;
    lastName: string;
    email: string;
    phone?: string;
    role?: string;
    licenseNumber?: string;
    status?: string;
  }) {
    await this.clickAddUser();
    
    // Fill in user details
    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    
    if (userData.phone) {
      await this.phoneInput.fill(userData.phone);
    }
    
    if (userData.role && await this.roleSelect.isVisible()) {
      await this.roleSelect.selectOption({ label: userData.role });
    }
    
    if (userData.licenseNumber && await this.licenseNumberInput.isVisible()) {
      await this.licenseNumberInput.fill(userData.licenseNumber);
    }
    
    if (userData.status && await this.statusSelect.isVisible()) {
      await this.statusSelect.selectOption({ label: userData.status });
    }
    
    await this.saveButton.click();
    await this.page.waitForTimeout(2000);
  }

  async editUser(index: number, updatedData: {
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    role?: string;
    licenseNumber?: string;
    status?: string;
  }) {
    // Click edit button for the specified user
    const editButtons = this.editButton;
    if (await editButtons.nth(index).isVisible()) {
      await editButtons.nth(index).click();
      await this.page.waitForTimeout(1000);
      
      // Update the fields
      if (updatedData.firstName) {
        await this.firstNameInput.fill(updatedData.firstName);
      }
      
      if (updatedData.lastName) {
        await this.lastNameInput.fill(updatedData.lastName);
      }
      
      if (updatedData.email) {
        await this.emailInput.fill(updatedData.email);
      }
      
      if (updatedData.phone) {
        await this.phoneInput.fill(updatedData.phone);
      }
      
      if (updatedData.role && await this.roleSelect.isVisible()) {
        await this.roleSelect.selectOption({ label: updatedData.role });
      }
      
      if (updatedData.licenseNumber && await this.licenseNumberInput.isVisible()) {
        await this.licenseNumberInput.fill(updatedData.licenseNumber);
      }
      
      if (updatedData.status && await this.statusSelect.isVisible()) {
        await this.statusSelect.selectOption({ label: updatedData.status });
      }
      
      await this.saveButton.click();
      await this.page.waitForTimeout(2000);
    }
  }

  async deleteUser(index: number) {
    // Click delete button for the specified user
    const deleteButtons = this.deleteButton;
    if (await deleteButtons.nth(index).isVisible()) {
      await deleteButtons.nth(index).click();
      await this.page.waitForTimeout(1000);
      
      // Confirm deletion if confirmation dialog appears
      if (await this.confirmDeleteButton.isVisible()) {
        await this.confirmDeleteButton.click();
        await this.page.waitForTimeout(2000);
      }
    }
  }

  async deactivateUser(index: number) {
    // Click deactivate button for the specified user
    const deactivateButtons = this.deactivateButton;
    if (await deactivateButtons.nth(index).isVisible()) {
      await deactivateButtons.nth(index).click();
      await this.page.waitForTimeout(1000);
      
      // Confirm deactivation if confirmation dialog appears
      const confirmButton = this.page.locator('button:has-text("Confirm"), button:has-text("Yes")');
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
        await this.page.waitForTimeout(2000);
      }
    }
  }

  async activateUser(index: number) {
    // Click activate button for the specified user
    const activateButtons = this.activateButton;
    if (await activateButtons.nth(index).isVisible()) {
      await activateButtons.nth(index).click();
      await this.page.waitForTimeout(2000);
    }
  }

  async assignRole(index: number, role: string, licenseNumber?: string) {
    // Click edit button for the specified user
    const editButtons = this.editButton;
    if (await editButtons.nth(index).isVisible()) {
      await editButtons.nth(index).click();
      await this.page.waitForTimeout(1000);
      
      // Update role
      if (await this.roleSelect.isVisible()) {
        await this.roleSelect.selectOption({ label: role });
      }
      
      // Update license number if provided (for Ethiopian valuer role)
      if (licenseNumber && await this.licenseNumberInput.isVisible()) {
        await this.licenseNumberInput.fill(licenseNumber);
      }
      
      await this.saveButton.click();
      await this.page.waitForTimeout(2000);
    }
  }

  // Helper methods
  
  async waitForUsersToLoad() {
    await this.page.waitForTimeout(2000);
    await this.usersTable.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
  }

  async hasUsers(): Promise<boolean> {
    await this.waitForUsersToLoad();
    return await this.getUserCount() > 0;
  }

  async getFirstUserText(): Promise<string> {
    const firstRow = this.userRows.first();
    return await firstRow.textContent() || '';
  }

  async getUserEmail(index: number): Promise<string> {
    const userRow = this.userRows.nth(index);
    const emailCell = userRow.locator('td, .table-cell').filter({ hasText: /@/ }).first();
    return await emailCell.textContent() || '';
  }

  async getUserRole(index: number): Promise<string> {
    const userRow = this.userRows.nth(index);
    const roleCell = userRow.locator('td, .table-cell').filter({ 
      hasText: /^(Admin|Valuer|Manager|System Admin|User)$/ 
    }).first();
    return await roleCell.textContent() || '';
  }

  async getUserStatus(index: number): Promise<string> {
    const userRow = this.userRows.nth(index);
    const statusCell = userRow.locator('td, .table-cell').filter({ 
      hasText: /^(Active|Inactive|Deactivated)$/ 
    }).first();
    return await statusCell.textContent() || '';
  }

  async validateEthiopianPhone(phone: string): Promise<boolean> {
    // Ethiopian phone validation: +2519xxxxxxxx or 09xxxxxxxx
    const ethiopianPhoneRegex = /^(\+2519\d{8}|09\d{8})$/;
    return ethiopianPhoneRegex.test(phone);
  }

  async validateLicenseNumber(license: string): Promise<boolean> {
    // Ethiopian valuer license validation (basic format)
    const licenseRegex = /^[A-Z]{2}-\d{4}-\d{4}$/;
    return licenseRegex.test(license);
  }

  async verifyEthiopianCompliance(index: number): Promise<boolean> {
    // Check if user shows Ethiopian compliance data
    const userRow = this.userRows.nth(index);
    const rowText = await userRow.textContent();
    
    // Look for Ethiopian compliance indicators
    return rowText ? (
      rowText.includes('Ethiopian') || 
      rowText.includes('Valuer') ||
      rowText.includes('License')
    ) : false;
  }
}
