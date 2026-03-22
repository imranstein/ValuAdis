import { test, expect } from '@playwright/test'

test('Valuation status workflow transitions', async ({ page }) => {
  // Login and create valuation in draft
  await page.goto('http://localhost:3000/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')

  // Create new valuation
  const response = await page.request.post('http://localhost:8000/api/v1/vehicles/1/valuation', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
  })
  const valuation = await response.json()

  // Verify status is draft
  expect(valuation.status).toBe('draft')

  // Transition to pending
  const pending = await page.request.post(
    `http://localhost:8000/api/v1/valuations/${valuation.id}/transition`,
    {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      data: { new_status: 'pending' }
    }
  )
  const pendingData = await pending.json()
  expect(pendingData.status).toBe('pending')

  // Transition to approved
  const approved = await page.request.post(
    `http://localhost:8000/api/v1/valuations/${valuation.id}/transition`,
    {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      data: { new_status: 'approved' }
    }
  )
  const approvedData = await approved.json()
  expect(approvedData.status).toBe('approved')

  // Transition to archived
  const archived = await page.request.post(
    `http://localhost:8000/api/v1/valuations/${valuation.id}/transition`,
    {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      data: { new_status: 'archived' }
    }
  )
  const archivedData = await archived.json()
  expect(archivedData.status).toBe('archived')
})
