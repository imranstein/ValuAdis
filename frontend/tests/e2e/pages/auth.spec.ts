import { test, expect } from '../setup/fixtures';
import { TEST_CREDENTIALS, INVALID_CREDENTIALS } from '../config/test-credentials';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ loginPage }) => {
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should login with valid credentials', async ({ loginPage, page }) => {
    await loginPage.login(TEST_CREDENTIALS.email, TEST_CREDENTIALS.fallbackPassword);
    await page.waitForURL(/\/(dashboard)?$/);
    await expect(page).toHaveURL(/\/(dashboard)?$/);
  });

  test('should show error with invalid credentials', async ({ loginPage }) => {
    await loginPage.login(INVALID_CREDENTIALS.invalidEmail, INVALID_CREDENTIALS.invalidPassword);
    await expect(loginPage.errorMessage).toBeVisible({ timeout: 5000 });
  });

  test('should show error with empty email', async ({ loginPage }) => {
    await loginPage.login('', 'password123');
    await expect(loginPage.emailInput).toHaveAttribute('required');
  });

  test('should show error with empty password', async ({ loginPage }) => {
    await loginPage.login(TEST_CREDENTIALS.email, '');
    await expect(loginPage.passwordInput).toHaveAttribute('required');
  });

  test('should validate email format', async ({ loginPage }) => {
    await loginPage.emailInput.fill(INVALID_CREDENTIALS.malformedEmail);
    await loginPage.passwordInput.fill('password123');
    await loginPage.loginButton.click();
    
    const validationMessage = await loginPage.emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
    expect(validationMessage).toBeTruthy();
  });

  test('should logout successfully', async ({ loginPage, page }) => {
    await loginPage.login(TEST_CREDENTIALS.email, TEST_CREDENTIALS.fallbackPassword);
    await page.waitForURL(/\/(dashboard)?$/);
    
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout")');
    await logoutButton.click();
    
    await expect(page).toHaveURL('/');
  });

  test('should redirect to dashboard when already logged in', async ({ loginPage, page }) => {
    await loginPage.login(TEST_CREDENTIALS.email, TEST_CREDENTIALS.fallbackPassword);
    await page.waitForURL(/\/(dashboard)?$/);
    
    await page.goto('/login');
    await expect(page).toHaveURL(/\/(dashboard)?$/);
  });

  test('should persist session across page refresh', async ({ loginPage, page }) => {
    await loginPage.login(TEST_CREDENTIALS.email, TEST_CREDENTIALS.fallbackPassword);
    await page.waitForURL(/\/(dashboard)?$/);
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/(dashboard)?$/);
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.removeItem('valuadis_token');
      sessionStorage.clear();
    });
    await page.context().clearCookies();
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });
});
