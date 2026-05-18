import { test as setup } from '@playwright/test';
import { MOCK_TOKEN, setupApiMock } from './api-mock';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Register API mocks before any navigation so all requests are intercepted
  await setupApiMock(page);

  // Inject token into localStorage before the page loads.
  // This way Nuxt's auth middleware finds a valid token on first render
  // and allows access to /dashboard without going through the login form.
  await page.addInitScript((token) => {
    localStorage.setItem('valuadis_token', token);
  }, MOCK_TOKEN);

  await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });

  await page.context().storageState({ path: authFile });
});

