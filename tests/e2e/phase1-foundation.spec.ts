import { test, expect } from '@playwright/test'
import { performanceTracker } from './performance.helpers'

test.describe('Phase 1: Foundation - Token Expiry', () => {
  test('should logout user when token expires', async ({ page }) => {
    performanceTracker.startTest()

    // Set expired token in localStorage
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NDAwMDAwMDB9.invalid'
    await page.context().addCookies([
      {
        name: 'valuadis_token',
        value: expiredToken,
        url: 'http://localhost:3000',
      },
    ])
    await page.evaluate((token) => {
      localStorage.setItem('valuadis_token', token)
    }, expiredToken)

    // Navigate to protected route
    const pageLoadTime = await (async () => {
      const start = Date.now()
      await page.goto('http://localhost:3000/dashboard')
      return Date.now() - start
    })()

    // Should redirect to login with expired message
    await expect(page).toHaveURL(/.*login.*token-expired.*/)

    // Token should be cleared from localStorage
    const token = await page.evaluate(() => localStorage.getItem('valuadis_token'))
    expect(token).toBeNull()

    // Record metrics
    performanceTracker.recordMetric('Token Expiry Logout', pageLoadTime, 0)
  })

  test('should allow access with valid token', async ({ page }) => {
    performanceTracker.startTest()

    // Create valid token (expires in 1 hour)
    const futureTime = Math.floor(Date.now() / 1000) + 3600
    const validToken = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${Buffer.from(JSON.stringify({ exp: futureTime })).toString('base64')}.signature`

    await page.evaluate((token) => {
      localStorage.setItem('valuadis_token', token)
    }, validToken)

    // Navigate to protected route
    const pageLoadTime = await (async () => {
      const start = Date.now()
      await page.goto('http://localhost:3000/dashboard')
      return Date.now() - start
    })()

    // Should NOT redirect to login
    expect(page.url()).not.toContain('login')

    // Record metrics
    performanceTracker.recordMetric('Valid Token Access', pageLoadTime, 0)
  })

  test.afterAll(() => {
    // Log all collected metrics and generate report
    performanceTracker.logMetrics()

    // Check for regressions
    const regressions = performanceTracker.checkRegressions()
    if (regressions.length > 0) {
      console.warn('\n⚠️  PERFORMANCE REGRESSIONS DETECTED:')
      regressions.forEach((r) => console.warn(`  - ${r}`))
    }
  })
})
