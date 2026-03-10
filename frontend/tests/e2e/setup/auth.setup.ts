import { test as setup } from '@playwright/test';
import { TEST_CREDENTIALS } from '../config/test-credentials';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Check if already on dashboard (already logged in)
  const url = page.url();
  const isDashboard = url.includes('/dashboard') || url.endsWith(':3020/');

  if (!isDashboard) {
    // Perform login - admin@valuadis.com / admin123 (backend default)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.email);
    await page.fill('input[type="password"]', TEST_CREDENTIALS.fallbackPassword);
    await page.click('button[type="submit"]');

    // Wait for navigation - requires backend on port 8020
    await page.waitForURL(/\/(dashboard)?$/, { timeout: 15000 });
  }

  // Save authentication state
  await page.context().storageState({ path: authFile });
});
