import { test as setup } from '@playwright/test';
import { TEST_CREDENTIALS } from '../config/test-credentials';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });

  const url = page.url();
  const isDashboard = url.includes('/dashboard') || url.endsWith(':3020/');

  if (!isDashboard) {
    await page.fill('input[type="email"]', TEST_CREDENTIALS.email);
    await page.fill('input[type="password"]', TEST_CREDENTIALS.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard)?$/, { timeout: 15000 });
  }

  await page.context().storageState({ path: authFile });
});
