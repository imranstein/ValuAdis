import { test, expect } from '@playwright/test'

test('Compliance report generation workflow', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3000/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForNavigation()

  // Navigate to reports
  await page.goto('http://localhost:3000/reports/compliance')
  await page.waitForLoadState('networkidle')

  // Verify page loaded
  expect(page.url()).toContain('/reports/compliance')
  const heading = await page.textContent('h1')
  expect(heading).toContain('Compliance Reports')

  // Click generate report button
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('button:has-text("Generate Report")')
  ])

  // Verify PDF download
  expect(download.suggestedFilename()).toMatch(/compliance_report_\d+\.pdf/)
})
