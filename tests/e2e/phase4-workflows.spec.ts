import { test, expect } from '@playwright/test'

test('Vehicle registration to list workflow', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3000/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForNavigation()

  // Navigate to vehicle register
  await page.goto('http://localhost:3000/vehicles/register')

  // Fill vehicle form
  await page.fill('input[placeholder*="type"]', 'Sedan')
  await page.fill('input[placeholder*="make"]', 'Toyota')
  await page.fill('input[placeholder*="model"]', 'Camry')
  await page.fill('input[type="number"]', '2022')
  await page.fill('input[placeholder*="VIN"]', 'JT2BF28K5M0047429')
  await page.fill('input[placeholder*="Plate"]', 'AA-1234')

  // Submit form
  await page.click('button:has-text("Save Vehicle")')

  // Verify redirected to list
  await page.waitForURL('**/vehicles/list')
  expect(page.url()).toContain('/vehicles/list')

  // Verify vehicle appears in list
  const vehicleText = await page.textContent('body')
  expect(vehicleText).toContain('Toyota')
  expect(vehicleText).toContain('Camry')
  expect(vehicleText).toContain('2022')
})
