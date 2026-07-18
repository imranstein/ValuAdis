import { test, expect, request as playwrightRequest, type APIRequestContext, type Browser, type Page } from '@playwright/test';

/**
 * Rentals Phase C — full registry chain E2E.
 *
 * owner lists property → officer verifies + publishes → renter applies inside
 * band (plus an outside-band 422 assertion) → owner accepts → officer creates
 * contract → deposit receipt recorded → contract active with PDF download.
 *
 * Requires a dedicated backend (E2E_API_BASE_URL, default 127.0.0.1:8010) with
 * an admin account (E2E_OFFICER_EMAIL/PASSWORD) whose is_admin flag satisfies
 * the rental-officer gate. Test data is namespaced per run via a timestamp so
 * the spec never collides with dev DB conventions.
 */

const API = process.env.E2E_API_BASE_URL || 'http://127.0.0.1:8010';
const OFFICER_EMAIL = process.env.E2E_OFFICER_EMAIL || 'officer.e2e@valuadis.com';
const OFFICER_PASSWORD = process.env.E2E_OFFICER_PASSWORD || 'OfficerE2e1!';

const runId = Date.now().toString().slice(-9);
const owner = {
  email: `owner-${runId}@e2e-valuadis.example.com`,
  full_name: 'Kebede E2E Owner',
  phone: `+2519${runId.slice(0, 8)}`,
  password: 'OwnerPass1!',
  municipality: 'Addis Ababa',
  fayda_id_number: `1${runId}00`,
  account_type: 'property_owner',
};
const renter = {
  email: `renter-${runId}@e2e-valuadis.example.com`,
  full_name: 'Meron E2E Renter',
  phone: `+2519${runId.slice(1, 9)}`,
  password: 'RenterPass1!',
  municipality: 'Addis Ababa',
  fayda_id_number: `2${runId}00`,
  account_type: 'renter',
};

test.describe('Rental registry full chain (Phase C)', () => {
  test.describe.configure({ mode: 'serial' });
  test.skip(({ browserName }) => browserName !== 'chromium', 'chain runs once, on chromium');

  let api: APIRequestContext;
  let ownerToken = '';
  let renterToken = '';
  let officerToken = '';
  let listingPublicId = '';
  let bandMin = 0;
  let bandMax = 0;
  let suggestedRent = 0;
  let applicationId = 0;
  let contractNo = '';
  let depositAmount = 0;

  test.beforeAll(async () => {
    api = await playwrightRequest.newContext({ baseURL: API });
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  async function login(page: Page, email: string, password: string) {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(email);
    await page.locator('input[type="password"]').fill(password);
    // The Sign In button is type="button" — Enter does not submit.
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL(/dashboard|properties|rentals/, { timeout: 20000 });
  }

  test('setup: accounts and property exist', async () => {
    const ownerRes = await api.post('/api/v1/rentals/signup', { data: owner });
    expect(ownerRes.status()).toBe(201);
    ownerToken = (await ownerRes.json()).data.access_token;

    const renterRes = await api.post('/api/v1/rentals/signup', { data: renter });
    expect(renterRes.status()).toBe(201);
    renterToken = (await renterRes.json()).data.access_token;

    const officerRes = await api.post('/api/v1/auth/login', {
      data: { email: OFFICER_EMAIL, password: OFFICER_PASSWORD },
    });
    expect(officerRes.status(), 'officer (admin) account must exist on the E2E backend').toBe(200);
    officerToken = (await officerRes.json()).data.access_token;

    const propertyRes = await api.post('/api/v1/properties', {
      headers: { Authorization: `Bearer ${ownerToken}` },
      data: {
        address: `Bole E2E ${runId}, Addis Ababa`,
        municipality: 'Addis Ababa',
        subcity: 'Bole',
        property_type: 'residential',
        property_subtype: 'apartment',
        area_sqm: 120,
        number_of_bedrooms: 2,
        owner_name: owner.full_name,
        owner_phone: owner.phone,
        coordinates: [
          [38.7578, 9.032],
          [38.758, 9.032],
          [38.758, 9.0318],
          [38.7578, 9.0318],
          [38.7578, 9.032],
        ],
      },
    });
    expect(propertyRes.status()).toBe(201);
  });

  test('owner registers the listing through the UI', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, owner.email, owner.password);
    await page.goto('/rentals/my-listings');

    const select = page.locator('select[aria-label="Select property"]');
    await expect(select).toBeVisible();
    await select.selectOption({ index: 1 });
    await page.getByRole('button', { name: /submit for review/i }).click();

    const notice = page.locator('.inline-notice');
    await expect(notice).toContainText('submitted for officer review', { timeout: 20000 });
    await expect(page.locator('tbody .record-id').first()).toContainText('AA-LST-');
    listingPublicId = (await page.locator('tbody .record-id').first().innerText()).trim();
    await page.close();
  });

  test('officer verifies the owner and publishes at the band', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, OFFICER_EMAIL, OFFICER_PASSWORD);
    await page.goto('/rentals');

    await expect(page.locator('tbody tr').first()).toContainText(listingPublicId, { timeout: 20000 });
    await page.locator('button[aria-label="Open listing"]').first().click();

    await page.getByRole('button', { name: /verify owner/i }).click();
    await expect(page.locator('.drawer-notice')).toContainText('Owner verified');

    await page.getByRole('button', { name: /publish at band/i }).click();
    // Publishing reloads the queue and closes the drawer; the listing leaves
    // pending_review.
    await expect(page.locator('.review-drawer')).toBeHidden({ timeout: 20000 });
    await page.close();

    const detail = await api.get(`/api/v1/rentals/listings/${listingPublicId}`);
    expect(detail.status(), 'listing must be publicly visible after publish').toBe(200);
    const body = (await detail.json()).data;
    bandMin = body.band_min;
    bandMax = body.band_max;
    suggestedRent = body.suggested_rent;
    expect(bandMin).toBeLessThan(bandMax);
  });

  test('outside-band offers are rejected with 422', async () => {
    const below = await api.post(`/api/v1/rentals/listings/${listingPublicId}/applications`, {
      headers: { Authorization: `Bearer ${renterToken}` },
      data: { offered_rent: bandMin - 1 },
    });
    expect(below.status()).toBe(422);

    const above = await api.post(`/api/v1/rentals/listings/${listingPublicId}/applications`, {
      headers: { Authorization: `Bearer ${renterToken}` },
      data: { offered_rent: bandMax + 1 },
    });
    expect(above.status()).toBe(422);
  });

  test('renter applies inside the band through the UI', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, renter.email, renter.password);
    await page.goto(`/rent/${listingPublicId}`);

    const offerInput = page.locator('.apply-form input[type="number"]');
    await expect(offerInput).toBeVisible({ timeout: 20000 });
    await offerInput.fill(String(Math.round(suggestedRent)));
    await page.getByRole('button', { name: /apply within band/i }).click();
    await expect(page.locator('.apply-success')).toContainText('Application submitted', { timeout: 20000 });
    await page.close();
  });

  test('owner accepts the application through the UI', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, owner.email, owner.password);
    await page.goto('/rentals/my-listings');

    await page.locator('button[aria-label="View applications"]').first().click();
    await expect(page.locator('.applications-panel tbody tr').first()).toContainText(renter.full_name, {
      timeout: 20000,
    });
    await page.getByRole('button', { name: /^accept$/i }).click();
    await expect(page.locator('.applications-panel .inline-notice')).toContainText('accepted', {
      timeout: 20000,
    });
    await page.close();

    const applications = await api.get(`/api/v1/rentals/listings/${listingPublicId}/applications`, {
      headers: { Authorization: `Bearer ${officerToken}` },
    });
    const accepted = (await applications.json()).data.find((a: any) => a.status === 'accepted');
    expect(accepted).toBeTruthy();
    applicationId = accepted.id;
  });

  test('officer registers the contract through the UI', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, OFFICER_EMAIL, OFFICER_PASSWORD);
    await page.goto('/rentals/contracts');

    await page.locator('input[aria-label="Listing public id"]').fill(listingPublicId);
    await page.getByRole('button', { name: /find accepted application/i }).click();
    await expect(page.locator('.accepted-summary')).toContainText(`#${applicationId}`, { timeout: 20000 });

    await page.locator('input[type="date"]').first().fill('2026-09-01');
    await page.locator('input[type="date"]').nth(1).fill('2027-09-01');
    await page.getByRole('button', { name: /register contract/i }).click();

    const notice = page.locator('.create-panel .inline-notice');
    await expect(notice).toContainText('registered as draft', { timeout: 20000 });
    const noticeText = await notice.innerText();
    contractNo = noticeText.match(/AA-RNT-\d{4}-\d{6}/)?.[0] ?? '';
    expect(contractNo).toMatch(/^AA-RNT-\d{4}-\d{6}$/);
    await page.close();

    const contracts = await api.get('/api/v1/rentals/contracts', {
      headers: { Authorization: `Bearer ${officerToken}` },
    });
    const record = (await contracts.json()).data.find((c: any) => c.contract_no === contractNo);
    expect(record.status).toBe('draft');
    depositAmount = record.deposit_amount;
  });

  test('deposit receipt activates the contract; PDF is downloadable', async ({ browser }) => {
    const page = await freshPage(browser);
    await login(page, OFFICER_EMAIL, OFFICER_PASSWORD);
    await page.goto('/rentals/contracts');

    await page.locator(`tr:has-text("${contractNo}")`).getByRole('button', { name: /record deposit/i }).click();
    await page.locator('.deposit-form input[type="text"]').fill(`TELE-E2E-${runId}`);
    // Amount is prefilled with the required deposit; submitting proves the
    // matching-amount activation path.
    await page.getByRole('button', { name: /record receipt/i }).click();
    await expect(page.locator('.deposit-panel .inline-notice')).toContainText('active', { timeout: 20000 });

    const downloadPromise = page.waitForEvent('download');
    await page.locator(`tr:has-text("${contractNo}") button[aria-label="Download contract PDF"]`).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain(contractNo);
    await page.close();
  });

  test('audit ledger records the chain', async () => {
    const audit = await api.get('/api/v1/audit/logs?limit=200', {
      headers: { Authorization: `Bearer ${officerToken}` },
    });
    expect(audit.status()).toBe(200);
    const text = JSON.stringify(await audit.json());
    for (const action of ['publish', 'apply', 'accept', 'create', 'deposit_recorded']) {
      expect(text, `audit ledger should contain a '${action}' action`).toContain(action);
    }
  });
});

async function freshPage(browser: Browser): Promise<Page> {
  const context = await browser.newContext({ storageState: undefined });
  return context.newPage();
}
