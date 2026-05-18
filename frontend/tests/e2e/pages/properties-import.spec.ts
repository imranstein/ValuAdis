import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

test.describe('Bulk property import', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem('valuadis_token', token);
    }, MOCK_TOKEN);

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'admin@valuadis.com',
          full_name: 'Admin User',
          role: 'admin',
          is_admin: true,
          is_valuer: true,
        }),
      });
    });
  });

  test('previews CSV rows and confirms valid import', async ({ page }) => {
    await page.route('**/api/v1/properties/bulk-import', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, imported_count: 1, data: [] }),
      });
    });

    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'properties.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,latitude,longitude,market_value,taxable_value',
          'Bole Atlas,Addis Ababa,residential,9.0320,38.7578,1000000,250000',
        ].join('\n')
      ),
    });

    await expect(page.getByTestId('property-import-mapping-table')).toContainText('address');
    await expect(page.getByTestId('property-import-validation-preview')).toContainText('All preview rows');
    await expect(page.getByTestId('property-import-preview-table')).toContainText('Bole Atlas');

    await page.getByTestId('property-import-confirm').click();
    await expect(page.getByText('1 properties imported')).toBeVisible();
  });

  test('blocks rows that violate the 25 percent taxable value rule', async ({ page }) => {
    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'invalid-properties.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,latitude,longitude,market_value,taxable_value',
          'Kazanchis Tower,Addis Ababa,commercial,9.0320,38.7578,1000000,300000',
        ].join('\n')
      ),
    });

    await expect(page.getByTestId('property-import-validation-preview')).toContainText('Taxable value must be exactly 25%');
    await expect(page.getByTestId('property-import-confirm')).toBeDisabled();
  });
});
