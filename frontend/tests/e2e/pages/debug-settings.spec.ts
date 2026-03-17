import { test } from '../setup/fixtures';
test.use({ storageState: 'tests/e2e/.auth/user.json' });
test('debug settings', async ({ page }) => {
  const apiCalls: string[] = [];
  page.on('request', r => { if (r.url().includes('8020')) apiCalls.push(`${r.method()} ${r.url().split('8020')[1]}`); });
  page.on('response', r => { if (r.url().includes('8020')) apiCalls.push(`  -> ${r.status()}`); });
  await page.goto('/settings', { waitUntil: 'networkidle' });
  const url = page.url();
  const h1 = await page.locator('h1').first().textContent().catch(() => 'none');
  console.log('URL:', url, 'H1:', h1, 'API:', JSON.stringify(apiCalls));
});
