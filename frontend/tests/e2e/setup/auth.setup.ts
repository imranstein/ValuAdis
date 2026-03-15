import { test as setup, expect } from '@playwright/test';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Check if already on dashboard (already logged in)
  const isDashboard = await page.url().includes('/dashboard') || page.url() === 'http://localhost:3020/';

  if (!isDashboard) {
    // Perform login
    await page.fill('input[type="email"]', 'admin@valuadis.com');
    await page.fill('input[type="password"]', 'Admin123!');
    await page.click('button[type="submit"]');

    // Wait for navigation to complete
    await page.waitForURL(/\/(dashboard)?$/, { timeout: 15000 });
  }
  
  // Save authentication state
  await page.context().storageState({ path: authFile });
});
