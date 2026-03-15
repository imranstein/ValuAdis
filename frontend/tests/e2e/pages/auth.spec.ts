import { test, expect } from '../setup/fixtures';

test.describe('Authentication', () => {
  test.beforeEach(async ({ loginPage }) => {
    await loginPage.goto();
  });

  test('should display login page', async ({ loginPage }) => {
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should login with valid credentials', async ({ loginPage, page }) => {
    await loginPage.login('admin@valuadis.com', 'Admin123!');
    await page.waitForURL(/\/(dashboard)?$/);
    await expect(page).toHaveURL(/\/(dashboard)?$/);
  });

  test('should show error with invalid credentials', async ({ loginPage }) => {
    await loginPage.login('invalid@email.com', 'wrongpassword');
    await expect(loginPage.errorMessage).toBeVisible();
  });

  test('should show error with empty email', async ({ loginPage }) => {
    await loginPage.login('', 'Admin123!');
    await expect(loginPage.emailInput).toHaveAttribute('required');
  });

  test('should show error with empty password', async ({ loginPage }) => {
    await loginPage.login('admin@valuadis.com', '');
    await expect(loginPage.passwordInput).toHaveAttribute('required');
  });

  test('should validate email format', async ({ loginPage, page }) => {
    await loginPage.emailInput.fill('invalid-email');
    await loginPage.passwordInput.fill('Admin123!');
    await loginPage.loginButton.click();
    
    const validationMessage = await loginPage.emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
    expect(validationMessage).toBeTruthy();
  });

  test('should logout successfully', async ({ loginPage, page }) => {
    await loginPage.login('admin@valuadis.com', 'Admin123!');
    await page.waitForURL(/\/(dashboard)?$/);
    
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout")');
    await logoutButton.click();
    
    await expect(page).toHaveURL('/');
  });

  test('should redirect to dashboard when already logged in', async ({ loginPage, page }) => {
    await loginPage.login('admin@valuadis.com', 'Admin123!');
    await page.waitForURL(/\/(dashboard)?$/);
    
    await page.goto('/');
    await expect(page).toHaveURL(/\/(dashboard)?$/);
  });
});
