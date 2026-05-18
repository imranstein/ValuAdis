import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

test.describe('Analytics chart widgets', () => {
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
          properties: { total: 27, active: 24, growth_rate: 12.4 },
          valuations: { total: 18, growth_rate: 8.2 },
          financials: {
            total_market_value: 126000000,
            total_taxable_value: 31500000,
            avg_property_value: 7000000,
            market_value_growth: 14.2,
          },
          compliance: { compliance_rate: 94, compliant_valuations: 17 },
        }),
      });
    });

    await page.route('**/api/v1/analytics/trends**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          trends: {
            '2026-01': { count: 2, total_value: 8600000, total_taxable: 2150000, avg_value: 4300000 },
            '2026-02': { count: 3, total_value: 18300000, total_taxable: 4575000, avg_value: 6100000 },
            '2026-03': { count: 4, total_value: 28800000, total_taxable: 7200000, avg_value: 7200000 },
          },
        }),
      });
    });

    await page.route('**/api/v1/analytics/municipalities**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          municipalities: {
            'Addis Ababa': { properties: 12, total_value: 76000000, valuations: 9 },
            'Dire Dawa': { properties: 6, total_value: 28000000, valuations: 5 },
            Hawassa: { properties: 4, total_value: 22000000, valuations: 4 },
          },
        }),
      });
    });

    await page.route('**/api/v1/analytics/property-types**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          property_types: {
            residential: { count: 14, total_value: 52000000 },
            commercial: { count: 8, total_value: 61000000 },
            industrial: { count: 5, total_value: 13000000 },
          },
        }),
      });
    });
  });

  test('renders API-backed Chart.js analytics widgets', async ({ page }) => {
    await page.goto('/analytics', { waitUntil: 'domcontentloaded' });

    await expect(page.getByTestId('analytics-chart-valuation-volume')).toBeVisible();
    await expect(page.getByTestId('analytics-chart-municipality-breakdown')).toBeVisible();
    await expect(page.getByTestId('analytics-chart-property-types')).toBeVisible();
    await expect(page.getByTestId('analytics-chart-status-pipeline')).toBeVisible();

    await expect(page.locator('canvas')).toHaveCount(4);
    await expect(page.getByTestId('analytics-total-valuations')).toContainText('18');
    await expect(page.getByText('Addis Ababa')).toBeVisible();
    await expect(page.getByText('residential')).toBeVisible();
  });
});
