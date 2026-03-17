import { test } from '../setup/fixtures';
test.use({ storageState: 'tests/e2e/.auth/user.json' });
test('debug localStorage', async ({ page }) => {
  // Check localStorage BEFORE goto
  const preToken = await page.evaluate(() => localStorage.getItem('valuadis_token')).catch(() => 'error');
  console.log('PRE-NAV token:', preToken);
  await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
  const token = await page.evaluate(() => localStorage.getItem('valuadis_token')).catch(() => 'error');
  console.log('POST-DASH token:', token);
  await page.goto('/settings', { waitUntil: 'domcontentloaded' });
  console.log('FINAL URL:', page.url());
});
