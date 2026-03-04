import { test as setup, expect } from '@playwright/test';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto('/');
  
  // Check if already on dashboard (already logged in)
  const isDashboard = await page.url().includes('/dashboard') || page.url() === 'http://localhost:3000/';
  
  if (!isDashboard) {
    // Perform login
    await page.fill('input[type="email"]', 'admin@valuadis.gov.et');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to complete
    await page.waitForURL(/\/(dashboard)?$/);
  }
  
  // Save authentication state
  await page.context().storageState({ path: authFile });
});
