import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

test.describe('Report generation UI', () => {
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

    await page.route('**/api/v1/analytics/dashboard**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          properties: { total: 42, active: 39 },
          valuations: { total: 18 },
          financials: { total_market_value: 126000000, total_taxable_value: 31500000 },
          compliance: { compliance_rate: 94, compliant_valuations: 17 },
        }),
      });
    });
  });

  test('selects report filters and downloads a PDF certificate', async ({ page }) => {
    let certificateRequested = false;
    await page.route('**/api/v1/valuations/1/certificate', async (route) => {
      certificateRequested = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        headers: { 'Content-Disposition': 'attachment; filename="ValuAdis_Certificate_1.pdf"' },
        body: Buffer.from('%PDF-1.4 mock certificate'),
      });
    });

    await page.goto('/reports', { waitUntil: 'domcontentloaded' });

    await page.getByTestId('report-type-select').selectOption('valuation_certificate');
    await page.getByTestId('report-start-date').fill('2026-01-01');
    await page.getByTestId('report-end-date').fill('2026-03-31');
    await page.getByTestId('report-municipality-select').selectOption('Addis Ababa');
    await page.getByTestId('report-valuation-id').fill('1');
    await page.getByTestId('report-download-button').click();

    await expect.poll(() => certificateRequested).toBe(true);
    await expect(page.getByTestId('report-download-status')).toContainText('ValuAdis_Certificate_1.pdf');
  });
});
