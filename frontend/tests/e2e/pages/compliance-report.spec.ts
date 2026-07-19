import { test, expect } from '../setup/fixtures';

const MOCK_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkB2YWx1YWRpcy5jb20iLCJleHAiOjk5OTk5OTk5OTl9.mock-e2e-signature';

function jsonResponse(body: unknown, status = 200) {
  return {
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  };
}

test.describe('Compliance report page', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem('valuadis_token', token);
    }, MOCK_TOKEN);

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill(
        jsonResponse({
          id: 1,
          email: 'admin@valuadis.com',
          full_name: 'Admin User',
          role: 'admin',
          is_admin: true,
          is_valuer: true,
        }),
      );
    });
  });

  test('renders compliance report with metrics, municipalities and exceptions', async ({ page }) => {
    await page.route('**/api/v1/audit/compliance', async (route) => {
      await route.fulfill(
        jsonResponse({
          success: true,
          compliance_report: {
            total_valuations_analyzed: 41,
            proclamation_1365_2025_compliance: {
              compliance_rate: 95.1,
              compliant_valuations: 39,
              non_compliant_valuations: 2,
              rule: '25% taxable value rule',
            },
            municipality_analysis: {
              'Addis Ababa': {
                total: 20,
                compliant: 19,
                compliance_rate: 95,
              },
              Dire: {
                total: 21,
                compliant: 20,
                compliance_rate: 95.2,
              },
            },
            property_type_analysis: {
              Residential: {
                total: 28,
                compliant: 27,
                compliance_rate: 96.4,
              },
              Commercial: {
                total: 13,
                compliant: 12,
                compliance_rate: 92.3,
              },
            },
            compliance_details: [
              {
                valuation_id: 1201,
                property_type: 'Residential',
                municipality: 'Dire',
                market_value: 1200000,
                taxable_value: 300000,
                expected_taxable: 300000,
                deviation: 0,
              },
            ],
          },
        }),
      );
    });

    await page.goto('/reports/compliance', { waitUntil: 'domcontentloaded' });

    await expect(page.getByRole('heading', { name: 'Compliance report.' })).toBeVisible();
    const metric = (label: string) => page.locator('.metric-card').filter({ hasText: label });
    await expect(metric('Compliance rate')).toContainText('95.1%');
    await expect(metric('Analyzed valuations')).toContainText('41');
    await expect(metric('Compliant')).toContainText('39');
    await expect(metric('Exceptions')).toContainText('2');
    await expect(page.getByRole('heading', { name: 'Municipality compliance' })).toBeVisible();
    await expect(page.getByText('Addis Ababa').first()).toBeVisible();
    await expect(page.getByText('Dire').first()).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Property-type compliance' })).toBeVisible();
    await expect(page.getByText('Residential').first()).toBeVisible();
    await expect(page.getByText('Commercial').first()).toBeVisible();
    await expect(page.getByText('No taxable-value exceptions are reported.')).toHaveCount(0);
    await expect(page.getByText('#1201')).toBeVisible();
  });

  test('shows an error state when compliance API returns 503', async ({ page }) => {
    await page.route('**/api/v1/audit/compliance', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'service unavailable' }),
      });
    });

    await page.goto('/reports/compliance', { waitUntil: 'domcontentloaded' });

    await expect(page.getByText('Compliance report unavailable')).toBeVisible();
    await expect(page.getByText('Compliance report request failed with 503')).toBeVisible();
  });

  test('renders deterministic fallback state when compliance payload is incomplete', async ({ page }) => {
    await page.route('**/api/v1/audit/compliance', async (route) => {
      await route.fulfill(
        jsonResponse({
          compliance_report: {
            proclamation_1365_2025_compliance: {
              rule: '25% taxable value rule',
            },
          },
        }),
      );
    });

    await page.goto('/reports/compliance', { waitUntil: 'domcontentloaded' });

    await expect(page.getByRole('heading', { name: 'Compliance report.' })).toBeVisible();
    await expect(page.getByText('0.0%')).toHaveCount(1);
    // Analyzed, Compliant, and Exceptions metrics all fall back to an exact "0".
    await expect(page.locator('.metric-value').filter({ hasText: /^0$/ })).toHaveCount(3);
    await expect(page.getByText('No municipality compliance records are available yet.')).toBeVisible();
    await expect(page.getByText('No property-type compliance records are available yet.')).toBeVisible();
    await expect(page.getByText('No taxable-value exceptions are reported.')).toBeVisible();
  });
});
