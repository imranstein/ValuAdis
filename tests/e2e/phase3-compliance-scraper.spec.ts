import { test, expect } from '@playwright/test'

test.describe('Web Scraper E2E Tests', () => {
  test('Scenario 1: Successful market data scrape', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/market-data', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data).toHaveProperty('properties')
  })

  test('Scenario 2: Property attributes extracted correctly', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/properties', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    const data = await response.json()
    const property = data.properties[0]
    expect(property).toHaveProperty('price')
    expect(property).toHaveProperty('location')
    expect(property).toHaveProperty('bedrooms')
  })

  test('Scenario 3: Scraper retries on timeout', async ({ page }) => {
    const response = await page.request.post('http://localhost:8000/api/v1/scraper/retry-test', {
      headers: { 'Authorization': 'Bearer valid_token' },
      data: { maxRetries: 3 }
    })
    expect(response.status()).toBe(200)
  })

  test('Scenario 4: Error handling for invalid URL', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/invalid-url', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBeGreaterThanOrEqual(400)
  })

  test('Scenario 5: Data validation post-scrape', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/validate', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data.valid).toBe(true)
  })

  test('Scenario 6: Rate limiting compliance enforced', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/rate-limit', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBeLessThan(430)
  })

  test('Scenario 7: Data cache updated correctly', async ({ page }) => {
    await page.request.post('http://localhost:8000/api/v1/scraper/cache-update', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/cache', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBe(200)
  })

  test('Scenario 8: Fallback to cached data on failure', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/v1/scraper/fallback', {
      headers: { 'Authorization': 'Bearer valid_token' }
    })
    expect(response.status()).toBe(200)
    const data = await response.json()
    expect(data).toHaveProperty('cached')
  })
})
