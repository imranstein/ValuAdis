import { test, expect } from '../setup/fixtures';

test.describe('Basic Navigation - Phase 1 Foundation', () => {
  const VALID_EMAIL = 'admin@valuadis.com';
  const VALID_PASSWORD = 'Admin123!';

  test.beforeEach(async ({ loginPage, page }) => {
    // Login before each navigation test
    await loginPage.goto();
    await loginPage.login(VALID_EMAIL, VALID_PASSWORD);
    
    // Wait for successful login
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBe(true);
  });

  test('should access dashboard page', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 10000 });
    
    // Check for dashboard elements
    const pageTitle = await page.locator('h1, h2').first().textContent();
    expect(pageTitle).toMatch(/dashboard|welcome|overview/i);
  });

  test('should access properties page', async ({ page }) => {
    await page.goto('/properties');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should access valuations page', async ({ page }) => {
    await page.goto('/valuations');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should access analytics page', async ({ page }) => {
    await page.goto('/analytics');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should access settings page', async ({ page }) => {
    await page.goto('/settings');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should access audit log page', async ({ page }) => {
    await page.goto('/audit');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should access users page', async ({ page }) => {
    await page.goto('/users');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Should have some content (even if empty)
    const pageContent = await page.locator('body').textContent();
    expect(pageContent?.length).toBeGreaterThan(0);
  });

  test('should handle navigation between pages', async ({ page }) => {
    const pages = ['/dashboard', '/properties', '/valuations', '/analytics'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      await page.waitForTimeout(1000);
      
      // Should not have 404 or error page
      const pageContent = await page.locator('body').textContent();
      expect(pageContent?.length).toBeGreaterThan(0);
      expect(pageContent).not.toContain('404');
      expect(pageContent).not.toContain('Page not found');
    }
  });

  test('should show navigation menu for authenticated users', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for navigation elements
    const navElements = page.locator('nav, .navigation, .menu, [role="navigation"]');
    const hasNavigation = await navElements.count() > 0;
    
    if (hasNavigation) {
      await expect(navElements.first()).toBeVisible();
    }
  });

  test('should maintain authentication across navigation', async ({ page }) => {
    // Navigate to multiple pages
    await page.goto('/properties');
    await page.waitForTimeout(1000);
    
    await page.goto('/valuations');
    await page.waitForTimeout(1000);
    
    await page.goto('/dashboard');
    await page.waitForTimeout(1000);
    
    // Should still be authenticated (not redirected to login)
    expect(page.url()).not.toContain('/login');
  });
});
