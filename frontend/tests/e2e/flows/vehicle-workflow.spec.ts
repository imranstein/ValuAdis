import { test, expect } from '../setup/fixtures';

const MOCK_USER = {
  id: 1,
  email: 'admin@valuadis.com',
  full_name: 'Admin User',
  role: 'admin',
  is_admin: true,
  is_valuer: true,
};

function jsonResponse(body: unknown, status = 200) {
  return {
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  };
}

test.describe('Vehicle workflow', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should block VIN validation errors before API submission', async ({ page }) => {
    let createCallCount = 0;

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill(jsonResponse(MOCK_USER));
    });

    await page.route('**/api/v1/vehicles**', async (route) => {
      if (route.request().method() === 'POST') {
        createCallCount += 1;
        await route.fulfill(
          jsonResponse({ detail: 'vehicle VIN already exists' }, 400),
        );
        return;
      }

      await route.fulfill(jsonResponse({ data: [], total: 0, items: [], vehicles: [] }));
    });

    await page.goto('/vehicles/create', { waitUntil: 'domcontentloaded' });

    await page.locator('input[placeholder*="e.g., Toyota"]').fill('Toyota');
    await page.locator('input[placeholder*="e.g., Corolla"]').fill('Corolla');
    // Two fields share this placeholder (vehicle year + import year); the first is the vehicle year.
    await page.locator('input[placeholder*="e.g., 2020"]').first().fill('2022');
    // Deliberately 16 characters so client-side validation blocks the submit before any API call.
    await page.getByPlaceholder('17-character VIN', { exact: true }).fill('1HGCM82633A00435');
    await page.locator('input[placeholder*="e.g., AA-123-BC"]').fill('AA-123-BC');

    await page.evaluate(() => {
      const regionSelect = Array.from(document.querySelectorAll('select')).find(
        (node) =>
          Array.from(node.querySelectorAll('option')).some((option) =>
            option.value === 'Addis Ababa',
          ),
      );
      if (regionSelect) {
        regionSelect.value = 'Addis Ababa';
        regionSelect.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });

    await page.getByRole('button', { name: 'Save Vehicle' }).click();

    // The specific VIN error renders inline; the submit status shows a summary.
    await expect(page.getByText('VIN must be 17 characters')).toBeVisible();
    await expect(page.getByTestId('vehicle-create-status')).toContainText(
      'Review the highlighted fields before saving',
    );
    expect(createCallCount).toBe(0);
  });

  test('should create a vehicle and generate a valuation', async ({ page }) => {
    const vehicle = {
      id: 901,
      user_id: 1,
      make: 'Toyota',
      model: 'Corolla',
      year: 2022,
      vin: '1HGCM82633A0043527',
      plate_number: 'AA-777-BC',
      body_type: 'sedan',
      fuel_type: 'gasoline',
      transmission: 'automatic',
      engine_capacity: 1800,
      mileage: 52000,
      region: 'Addis Ababa',
      city: 'Bole',
      import_year: 2022,
      custom_duty_paid: true,
      customs_declaration_number: 'CD-991122',
      description: 'Flow test vehicle',
      status: 'active',
    };

    const valuation = {
      id: 7001,
      vehicle_id: vehicle.id,
      user_id: 1,
      market_value: 1125000,
      taxable_value: 281250,
      confidence_score: 87,
      status: 'draft',
      created_date: '2026-05-31T00:00:00Z',
      regional_multiplier: 1.15,
      customs_multiplier: 1.05,
      make_reliability_multiplier: 0.95,
      condition_multiplier: 0.9,
      vehicle_make: vehicle.make,
      vehicle_model: vehicle.model,
      vehicle_year: vehicle.year,
      vehicle_vin: vehicle.vin,
    };

    let valuationCreated = false;

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill(jsonResponse(MOCK_USER));
    });

    // Double-star so sub-paths (/vehicles/{id}, /{id}/valuations, /{id}/valuation) are intercepted.
    await page.route('**/api/v1/vehicles**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (url.includes('/statistics/summary')) {
        await route.fulfill(
          jsonResponse({
            total_vehicles: 1,
            total_valuations: 1,
            total_market_value: valuation.market_value,
            recent_valuations: 1,
          }),
        );
        return;
      }

      const singleVehicleMatch = url.match(/\/api\/v1\/vehicles\/(\d+)$/);
      if (singleVehicleMatch) {
        await route.fulfill(jsonResponse(vehicle));
        return;
      }

      const valuationsMatch = url.match(
        /\/api\/v1\/vehicles\/(\d+)\/valuations$/,
      );
      if (valuationsMatch) {
        await route.fulfill(jsonResponse(valuationCreated ? [valuation] : []));
        return;
      }

      const valuationMatch = url.match(/\/api\/v1\/vehicles\/(\d+)\/valuation$/);
      if (valuationMatch && method === 'POST') {
        valuationCreated = true;
        await route.fulfill(jsonResponse(valuation));
        return;
      }

      if (method === 'POST') {
        await route.fulfill(jsonResponse(vehicle, 200));
        return;
      }

      await route.fulfill(jsonResponse([vehicle]));
    });

    await page.goto('/vehicles/create', { waitUntil: 'domcontentloaded' });

    await page.locator('input[placeholder*="e.g., Toyota"]').fill('Toyota');
    await page.locator('input[placeholder*="e.g., Corolla"]').fill('Corolla');
    // Two fields share this placeholder (vehicle year + import year); the first is the vehicle year.
    await page.locator('input[placeholder*="e.g., 2020"]').first().fill('2022');
    await page.getByPlaceholder('17-character VIN', { exact: true }).fill(vehicle.vin);
    await page.locator('input[placeholder*="e.g., AA-123-BC"]').fill(vehicle.plate_number);

    await page.evaluate(() => {
      const regionSelect = Array.from(document.querySelectorAll('select')).find(
        (node) =>
          Array.from(node.querySelectorAll('option')).some((option) =>
            option.value === 'Addis Ababa',
          ),
      );
      if (regionSelect) {
        regionSelect.value = 'Addis Ababa';
        regionSelect.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });

    await page.getByRole('button', { name: 'Save Vehicle' }).click();
    await expect(page.getByTestId('vehicle-create-status')).toContainText('Vehicle saved');

    await page.goto('/vehicles', { waitUntil: 'domcontentloaded' });
    const row = page.getByRole('row', { name: vehicle.vin }).first();
    // Generous timeout: list fetch + hydration can lag under parallel-worker load.
    await expect(row).toBeVisible({ timeout: 15000 });

    await row.locator('button[aria-label="View vehicle"]').click();
    await expect(page).toHaveURL(new RegExp(`/vehicles/${vehicle.id}`));

    const newValuationButton = page.getByRole('button', { name: 'New Valuation' }).first();
    await expect(newValuationButton).toBeVisible({ timeout: 15000 });
    await newValuationButton.click();
    await expect.poll(() => valuationCreated).toBeTruthy();
    await expect(page.getByText('Latest Valuation')).toBeVisible();
    await expect(page.getByText('Market Value').first()).toBeVisible();
  });
});
