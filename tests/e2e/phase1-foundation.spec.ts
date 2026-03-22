import { test, expect } from '@playwright/test'

test.describe('Phase 1: Foundation - Token Expiry', () => {
  test('should logout user when token expires', async ({ page }) => {
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
    await page.goto('http://localhost:3000/dashboard')

    // Should redirect to login with expired message
    await expect(page).toHaveURL(/.*login.*token-expired.*/)

    // Token should be cleared from localStorage
    const token = await page.evaluate(() => localStorage.getItem('valuadis_token'))
    expect(token).toBeNull()
  })

  test('should allow access with valid token', async ({ page }) => {
    // Create valid token (expires in 1 hour)
    const futureTime = Math.floor(Date.now() / 1000) + 3600
    const validToken = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${Buffer.from(JSON.stringify({ exp: futureTime })).toString('base64')}.signature`

    await page.evaluate((token) => {
      localStorage.setItem('valuadis_token', token)
    }, validToken)

    // Navigate to protected route
    await page.goto('http://localhost:3000/dashboard')

    // Should NOT redirect to login
    expect(page.url()).not.toContain('login')
  })
})
