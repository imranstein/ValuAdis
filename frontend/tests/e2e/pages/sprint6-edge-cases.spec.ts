import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

test.describe('Sprint 6 edge cases', () => {
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

  test('blocks bulk import when required CSV columns are missing', async ({ page }) => {
    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'missing-columns.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,market_value,taxable_value',
          'Bole Atlas,Addis Ababa,residential,1000000,250000',
        ].join('\n')
      ),
    });

    await expect(page.getByTestId('property-import-mapping-table')).toContainText('latitude');
    await expect(page.getByTestId('property-import-mapping-table')).toContainText('Missing');
    await expect(page.getByTestId('property-import-validation-preview')).toContainText('latitude is required');
    await expect(page.getByTestId('property-import-validation-preview')).toContainText('longitude is required');
    await expect(page.getByTestId('property-import-confirm')).toBeDisabled();
  });

  test('shows backend bulk import validation errors without losing preview rows', async ({ page }) => {
    await page.route('**/api/v1/properties/bulk-import', async (route) => {
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [{ row: 2, message: 'Duplicate parcel number' }],
        }),
      });
    });

    await page.goto('/properties/import', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('property-import-file-input').setInputFiles({
      name: 'duplicate-parcel.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(
        [
          'address,municipality,property_type,latitude,longitude,market_value,taxable_value',
          'Bole Atlas,Addis Ababa,residential,9.0320,38.7578,1000000,250000',
        ].join('\n')
      ),
    });

    await page.getByTestId('property-import-confirm').click();

    await expect(page.getByText('Duplicate parcel number')).toBeVisible();
    await expect(page.getByTestId('property-import-preview-table')).toContainText('Bole Atlas');
  });

  test('requires valuation ID before downloading a certificate', async ({ page }) => {
    await page.route('**/api/v1/analytics/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          properties: { total: 1 },
          valuations: { total: 1 },
          financials: { total_taxable_value: 250000 },
          compliance: { compliance_rate: 100 },
        }),
      });
    });

    await page.goto('/reports', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('report-type-select').selectOption('valuation_certificate');
    await page.getByTestId('report-valuation-id').fill('');

    await expect(page.getByTestId('report-download-button')).toBeDisabled();
    await expect(page.getByTestId('report-download-status')).toContainText('Ready to generate');
  });

  test('reports failed downloads and allows a corrected retry', async ({ page }) => {
    let requestCount = 0;

    await page.route('**/api/v1/analytics/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          properties: { total: 2 },
          valuations: { total: 2 },
          financials: { total_taxable_value: 500000 },
          compliance: { compliance_rate: 88 },
        }),
      });
    });

    await page.route('**/api/v1/valuations/99/certificate', async (route) => {
      requestCount += 1;
      await route.fulfill({
        status: requestCount === 1 ? 404 : 200,
        contentType: requestCount === 1 ? 'application/json' : 'application/pdf',
        headers: requestCount === 1 ? {} : { 'Content-Disposition': 'attachment; filename="ValuAdis_Certificate_99.pdf"' },
        body: requestCount === 1 ? JSON.stringify({ detail: 'Valuation not found' }) : Buffer.from('%PDF-1.4 retry certificate'),
      });
    });

    await page.goto('/reports', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('report-type-select').selectOption('valuation_certificate');
    await page.getByTestId('report-valuation-id').fill('99');
    await page.getByTestId('report-download-button').click();

    await expect(page.getByTestId('report-download-status')).toContainText('Report generation failed');

    await page.getByTestId('report-download-button').click();
    await expect(page.getByTestId('report-download-status')).toContainText('ValuAdis_Certificate_99.pdf downloaded');
  });

  test('removes generated API keys before saving settings', async ({ page }) => {
    await page.goto('/settings', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('generate-api-key-button').click();
    await expect(page.getByTestId('api-key-row')).toHaveCount(3);

    await page.getByTestId('api-key-row').last().getByRole('button').click();
    await page.getByTestId('settings-save-button').click();

    await expect(page.getByTestId('api-key-row')).toHaveCount(2);
    await expect(page.getByTestId('settings-save-status')).toContainText('Settings saved');
  });
});
