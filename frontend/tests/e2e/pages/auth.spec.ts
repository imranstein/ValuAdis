import { test, expect } from '../setup/fixtures';
import { setUnauthenticated } from '../setup/api-mock';
import { TEST_CREDENTIALS, INVALID_CREDENTIALS } from '../config/test-credentials';

function generateExpiredToken(): string {
  const exp = Math.floor(Date.now() / 1000) - 3600
  const payload = Buffer.from(JSON.stringify({ exp, sub: 'test-user', role: 'viewer' })).toString('base64url')
  return `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${payload}.invalidsignature`
}

test.describe('Authentication', () => {
  // Tests that need a pre-authenticated session (storageState + default logged-in mock)
  test.describe('with auth', () => {
    test.use({ storageState: 'tests/e2e/.auth/user.json' });

    test('should logout successfully', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('domcontentloaded');
      await page.locator('.sidebar-account').getByRole('button', { name: /logout/i }).click();
      await page.waitForURL(/\/(login)?\/?$/, { timeout: 5000 }).catch(() => {});
      expect(page.url()).not.toContain('/dashboard');
    });

    test('should redirect to dashboard when already logged in', async ({ page }) => {
      await page.goto('/login');
      await expect(page).toHaveURL(/\/(dashboard)?$/);
    });

    test('should persist session across page refresh', async ({ page }) => {
      await page.goto('/dashboard');
      await page.reload();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/\/(dashboard)?$/);
    });
  });

  // Logged-out flows: the mock must report an unauthenticated session so the
  // login form is reachable and protected routes redirect to /login.
  test.describe('logged out', () => {
    test.beforeEach(async ({ page }) => {
      setUnauthenticated(page);
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
      await expect(loginPage.errorMessage).toBeVisible({ timeout: 8000 });
    });

    test('should show error with empty email', async ({ loginPage }) => {
      await loginPage.login('', 'Admin123!');
      await expect(loginPage.emailInput).toHaveAttribute('required', '');
    });

    test('should show error with empty password', async ({ loginPage }) => {
      await loginPage.login(TEST_CREDENTIALS.email, '');
      await expect(loginPage.passwordInput).toHaveAttribute('required', '');
    });

    test('should validate email format', async ({ loginPage }) => {
      await loginPage.emailInput.fill(INVALID_CREDENTIALS.malformedEmail);
      await loginPage.passwordInput.fill('password123');
      await loginPage.loginButton.click();

      const validationMessage = await loginPage.emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
      expect(validationMessage).toBeTruthy();
    });

    test('should redirect unauthenticated users to login', async ({ page }) => {
      await page.evaluate(() => {
        localStorage.removeItem('valuadis_token');
        sessionStorage.clear();
      });
      await page.context().clearCookies();
      await page.goto('/dashboard');
      await expect(page).toHaveURL(/\/login/);
    });

    test('should reject expired tokens and return to login', async ({ page }) => {
      const expiredToken = generateExpiredToken()

      await page.evaluate((token) => {
        localStorage.setItem('valuadis_token', token)
      }, expiredToken)

      await page.goto('/dashboard')
      await expect(page).toHaveURL(/\/login/)

      const tokenAfterNav = await page.evaluate(() => localStorage.getItem('valuadis_token'))
      expect(tokenAfterNav).toBeNull()
    });
  });
});
