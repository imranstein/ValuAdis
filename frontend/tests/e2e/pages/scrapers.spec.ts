import { test, expect } from '../setup/fixtures'

const MOCK_USER = {
  id: 1,
  email: 'admin@valuadis.com',
  full_name: 'Admin User',
  role: 'admin',
  is_admin: true,
  is_valuer: true
}

function jsonResponse (body: unknown, status = 200) {
  return {
    status,
    contentType: 'application/json',
    body: JSON.stringify(body)
  }
}

function fillScraperForm (page: any, domain: string, urlTemplate: string, selectors = {
  title: '.title',
  price: '.price',
  location: '.location',
  listingUrl: '.url'
}, maxPages = '40') {
  return page
    .locator('input[placeholder="e.g., mekelleproperty.com"]')
    .fill(domain)
    .then(() =>
      page.locator('input[placeholder="https://mekelleproperty.com/properties?page={page}"]').fill(urlTemplate)
    )
    .then(() => page.locator('select').selectOption('daily'))
    .then(() => page.locator('input[type="number"]').fill(maxPages))
    .then(() => page.locator('input[placeholder=".property-title, .listing-title"]').fill(selectors.title))
    .then(() => page.locator('input[placeholder=".property-price, .price"]').fill(selectors.price))
    .then(() => page.locator('input[placeholder=".location, .address"]').fill(selectors.location))
    .then(() => page.locator('input[placeholder=".property-link a, .listing-link"]').fill(selectors.listingUrl))
}

test.describe('Scrapers', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' })

  test.beforeEach(async ({ page }) => {
    const baseScrapers = [
      {
        id: 101,
        domain: 'ethproperty.com',
        url_template: 'https://ethproperty.com/listings?page={page}',
        schedule: 'daily',
        enabled: true,
        max_pages: 12,
        total_listings: 40,
        last_status: 'success',
        last_run: new Date().toISOString(),
        selectors: {
          title: '.property-title',
          price: '.property-price',
          location: '.property-location',
          listing_url: '.property-link',
          area: '.property-area',
          property_type: '.property-type',
          bedrooms: '.bedrooms',
          bathrooms: '.bathrooms'
        }
      }
    ]

    let scrapers = [...baseScrapers]
    const stats = {
      total_scrapers: 1,
      active_scrapers: 1,
      inactive_scrapers: 0,
      total_listings: 40,
      last_24h_listings: 7,
      avg_success_rate: 97,
      error_count: 0
    }

    const getScraperIdFromUrl = (url: string) => {
      const match = url.match(/\/api\/v1\/scrapers\/(\d+)(?:\/|[?#]|$)/)
      return match ? Number(match[1]) : null
    }

    await page.route('**/api/v1/auth/me', async (route) => {
      // The frontend reads /auth/me as the user object directly (no success/data wrapper),
      // so returning it unwrapped keeps is_admin visible to the admin middleware.
      await route.fulfill(jsonResponse(MOCK_USER))
    })

    await page.route('**/api/v1/scrapers/stats', async (route) => {
      await route.fulfill(
        jsonResponse({
          success: true,
          data: stats
        })
      )
    })

    await page.route('**/api/v1/scrapers/*/toggle', async (route) => {
      const id = getScraperIdFromUrl(route.request().url())
      if (id == null) {
        await route.fulfill(jsonResponse({ success: false, error: 'not found' }, 404))
        return
      }

      const target = scrapers.find((item) => item.id === id)
      if (!target) {
        await route.fulfill(jsonResponse({ success: false, error: 'not found' }, 404))
        return
      }

      target.enabled = !target.enabled
      await route.fulfill(
        jsonResponse({
          success: true,
          data: target
        })
      )
    })

    await page.route('**/api/v1/scrapers/*/test', async (route) => {
      const id = getScraperIdFromUrl(route.request().url())
      if (id == null) {
        await route.fulfill(jsonResponse({ success: false, error: 'bad request' }, 400))
        return
      }

      await route.fulfill(
        jsonResponse({
          success: true,
          data: {
            success: true,
            items_found: 11
          }
        })
      )
    })

    await page.route('**/api/v1/scrapers/*/run', async (route) => {
      const id = getScraperIdFromUrl(route.request().url())
      if (id == null) {
        await route.fulfill(jsonResponse({ success: false, error: 'bad request' }, 400))
        return
      }

      await route.fulfill(
        jsonResponse({
          success: true,
          data: {
            message: 'Scraper started',
            items_found: 9,
            job_id: 9912
          }
        })
      )
    })

    // Match the base collection endpoint only (list GET + create POST), including the
    // trailing slash and query string the service uses, without shadowing the specific
    // /scrapers/{id}/... routes registered above.
    await page.route(/\/api\/v1\/scrapers\/?(\?.*)?$/, async (route) => {
      const method = route.request().method()
      if (method === 'GET') {
        // The axios service returns the response body as-is and the component's
        // handleApiCall wraps it, so the list endpoint must return the raw array.
        await route.fulfill(jsonResponse(scrapers))
        return
      }

      if (method === 'POST') {
        const data = JSON.parse(route.request().postData() || '{}')
        const nextId = scrapers.length ? Math.max(...scrapers.map((item) => item.id)) + 1 : 1
        const scraper = {
          ...data,
          id: nextId,
          total_listings: 0,
          last_status: 'success',
          last_run: null,
          selectors: {
            ...data.selectors
          }
        }

        scrapers = [...scrapers, scraper]
        stats.total_scrapers = scrapers.length
        stats.active_scrapers = scrapers.filter((item) => item.enabled).length

        await route.fulfill(
          jsonResponse({
            success: true,
            data: scraper
          })
        )
        return
      }

      await route.fallback()
    })

    await page.route('**/api/v1/scrapers/*', async (route) => {
      const url = route.request().url()
      const id = getScraperIdFromUrl(url)
      if (id == null) {
        await route.fallback()
        return
      }

      if (route.request().method() === 'DELETE') {
        scrapers = scrapers.filter((item) => item.id !== id)
        stats.total_scrapers = scrapers.length
        stats.active_scrapers = scrapers.filter((item) => item.enabled).length
        await route.fulfill(
          jsonResponse({
            success: true,
            data: { id }
          })
        )
        return
      }

      await route.fulfill(jsonResponse({ success: false, error: 'unsupported' }, 400))
    })

    await page.route('**/api/v1/properties*', async (route) => {
      await route.fulfill(jsonResponse({ data: [] }))
    })

    await page.route('**/api/v1/vehicles*', async (route) => {
      await route.fulfill(jsonResponse({ data: [] }))
    })
  })

  test('should validate scraper URL placeholder before create', async ({ page }) => {
    await page.goto('/scrapers', { waitUntil: 'domcontentloaded' })

    await page.getByRole('button', { name: /Add New Property Scraper/ }).click()
    await expect(page.locator('.modal-content')).toBeVisible()

    const rowsBefore = await page.locator('.scraper-table table tbody tr').count()
    await fillScraperForm(
      page,
      'example-scraper.com',
      'https://example-scraper.com/properties?page=1'
    )

    await page.getByRole('button', { name: 'Add Scraper' }).click()

    await expect(page.getByText('URL template must contain the {page} placeholder.')).toBeVisible()
    await expect(page.locator('.scraper-table table tbody tr')).toHaveCount(rowsBefore)
  })

  test('should create, exercise lifecycle, and delete a scraper', async ({ page }) => {
    await page.goto('/scrapers', { waitUntil: 'domcontentloaded' })

    const scraperRows = page.locator('.scraper-table table tbody tr')
    // Wait for the seeded scraper to load before measuring the baseline.
    await expect(scraperRows.filter({ hasText: 'ethproperty.com' })).toBeVisible()
    const rowsBefore = await scraperRows.count()

    await page.getByRole('button', { name: /Add New Property Scraper/ }).click()
    await fillScraperForm(page, 'new-scraper.com', 'https://new-scraper.com/properties?page={page}')

    const createRequest = page.waitForResponse((response) =>
      response.url().includes('/api/v1/scrapers') &&
      response.request().method() === 'POST' &&
      response.status() === 200
    )

    await page.getByRole('button', { name: 'Add Scraper' }).click()
    await createRequest

    await expect(scraperRows.filter({ hasText: 'new-scraper.com' }).first()).toBeVisible()
    expect(await scraperRows.count()).toBeGreaterThan(rowsBefore)

    const createdRow = page
      .locator('.scraper-table table tbody tr')
      .filter({ hasText: 'new-scraper.com' })
      .first()
    await expect(createdRow).toBeVisible()

    const toggleRequest = page.waitForResponse((response) =>
      response.url().includes('/api/v1/scrapers/') &&
      response.url().includes('/toggle') &&
      response.request().method() === 'PATCH'
    )
    await createdRow.locator('button[title="Disable"]').click()
    await toggleRequest

    const testRequest = page.waitForResponse((response) =>
      response.url().includes('/api/v1/scrapers/') &&
      response.url().includes('/test') &&
      response.request().method() === 'POST'
    )
    await createdRow.locator('button[title="Test Scraper"]').click()
    await testRequest

    const runRequest = page.waitForResponse((response) =>
      response.url().includes('/api/v1/scrapers/') &&
      response.url().includes('/run') &&
      response.request().method() === 'POST'
    )
    await createdRow.locator('button[title="Run Now"]').click()
    await runRequest

    const rowIsDeleted = page
      .locator('.scraper-table table tbody tr')
      .filter({ hasText: 'new-scraper.com' })

    const deleteRequest = page.waitForResponse((response) =>
      /\/api\/v1\/scrapers\/\d+$/.test(response.url()) &&
      response.request().method() === 'DELETE'
    )

    page.once('dialog', (dialog) => dialog.accept())
    await rowIsDeleted.locator('button[title="Delete"]').click()
    await deleteRequest

    await expect(rowIsDeleted).toHaveCount(0)

    await page.getByRole('button', { name: /Vehicle scrapers/ }).click()
    await expect(page.getByRole('button', { name: /Vehicle scrapers/ })).toHaveClass(/active/)
    await expect(page.getByText('Scraped vehicles')).toBeVisible()
  })
})
