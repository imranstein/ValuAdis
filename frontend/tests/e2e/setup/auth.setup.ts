import { test as setup } from '@playwright/test';
import { TEST_CREDENTIALS } from '../config/test-credentials';
import { setupApiMock } from './api-mock';

const authFile = 'tests/e2e/.auth/user.json';

const MOCK_TOKEN = 'mock-jwt-e2e-' + Date.now();

setup('authenticate', async ({ page }) => {
  // Mock API when backend unavailable
  await setupApiMock(page);

  // Navigate to login page
  await page.goto('/login', { waitUntil: 'domcontentloaded' });

  const url = page.url();
  const isDashboard = url.includes('/dashboard') || url.endsWith(':3020/');

  if (!isDashboard) {
    // Try real login first (works if backend is running)
    await page.fill('input[type="email"]', TEST_CREDENTIALS.email);
    await page.fill('input[type="password"]', TEST_CREDENTIALS.fallbackPassword);
    await page.click('button[type="submit"]');

    try {
      await page.waitForURL(/\/(dashboard)?$/, { timeout: 8000 });
    } catch {
      // Login failed (no backend) - inject mock auth directly
      await page.goto('/login');
      await page.evaluate((token) => {
        localStorage.setItem('valuadis_token', token);
        localStorage.setItem('valuadis_refresh_token', token);
      }, MOCK_TOKEN);
      await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    }
  }

  // Save authentication state
  await page.context().storageState({ path: authFile });
});
