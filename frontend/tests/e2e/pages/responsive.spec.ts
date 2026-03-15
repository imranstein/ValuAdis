import { test, expect } from '../setup/fixtures';
import { LoginPage } from '../page-objects/LoginPage';

const VALID_EMAIL = 'admin@valuadis.com';
const VALID_PASSWORD = 'Admin123!';

test.describe('Responsive Design', () => {
  test('should display login page correctly on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should display login page correctly on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should display login page correctly on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
  });

  test('should login and display dashboard on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(VALID_EMAIL, VALID_PASSWORD);
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
    await page.waitForTimeout(2000);
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should handle viewport resizing', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(VALID_EMAIL, VALID_PASSWORD);
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
    const viewports = [{ width: 1024, height: 768 }, { width: 375, height: 667 }];
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500);
      const pageContent = await page.locator('body').textContent();
      expect(pageContent?.length).toBeGreaterThan(0);
    }
  });

  test('should display properties page on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(VALID_EMAIL, VALID_PASSWORD);
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
    await page.goto('/properties');
    await page.waitForTimeout(2000);
    const formElements = page.locator('input, select, textarea');
    const formCount = await formElements.count();
    if (formCount > 0) {
      const firstFormElement = formElements.first();
      await expect(firstFormElement).toBeVisible();
    }
  });
});
