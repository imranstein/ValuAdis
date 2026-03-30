import { Page } from '@playwright/test'

export interface SecurityTestResult {
  test: string
  passed: boolean
  details: string
}

/**
 * Generate a JWT token with a specific expiry (seconds from now, negative = expired)
 */
export function generateToken(expiryOffsetSeconds: number): string {
  const exp = Math.floor(Date.now() / 1000) + expiryOffsetSeconds
  const payload = Buffer.from(JSON.stringify({ exp, sub: 'test-user', role: 'viewer' })).toString(
    'base64url',
  )
  return `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${payload}.invalidsignature`
}

/**
 * Generate an expired JWT token (expired 1 hour ago)
 */
export function generateExpiredToken(): string {
  return generateToken(-3600)
}

/**
 * Generate a valid JWT token (expires in 1 hour)
 */
export function generateValidToken(): string {
  return generateToken(3600)
}

/**
 * Set a token in localStorage (simulates browser-side auth state)
 */
export async function setAuthToken(page: Page, token: string): Promise<void> {
  await page.evaluate((t) => {
    localStorage.setItem('valuadis_token', t)
  }, token)
}

/**
 * Clear all auth state from the browser context
 */
export async function clearAuthState(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('valuadis_token')
    localStorage.removeItem('valuadis_user')
  })
  await page.context().clearCookies()
}

/**
 * Attempt to access a protected route without credentials and return the resulting URL
 */
export async function attemptUnauthenticatedAccess(page: Page, route: string): Promise<string> {
  await clearAuthState(page)
  await page.goto(`http://localhost:3000${route}`)
  await page.waitForLoadState('networkidle')
  return page.url()
}

/**
 * Check if the current page URL indicates a redirect to login (access denied)
 */
export function isRedirectedToLogin(url: string): boolean {
  return url.includes('/login')
}

/**
 * Inject a SQL injection payload into a URL query parameter and navigate
 */
export async function injectSQLPayload(
  page: Page,
  baseRoute: string,
  param: string,
  payload: string,
): Promise<{ url: string; statusCode: number | null }> {
  const encodedPayload = encodeURIComponent(payload)
  const targetUrl = `http://localhost:3000${baseRoute}?${param}=${encodedPayload}`

  let statusCode: number | null = null
  page.on('response', (response) => {
    if (response.url().includes('/api/')) {
      statusCode = response.status()
    }
  })

  await page.goto(targetUrl)
  await page.waitForLoadState('networkidle')

  return { url: page.url(), statusCode }
}

/**
 * Check response headers for required security headers
 */
export async function getSecurityHeaders(
  page: Page,
  url: string,
): Promise<Record<string, string | null>> {
  const response = await page.goto(url)
  const headers: Record<string, string | null> = {}

  const requiredHeaders = [
    'x-content-type-options',
    'x-frame-options',
    'strict-transport-security',
    'content-security-policy',
  ]

  for (const header of requiredHeaders) {
    headers[header] = response?.headers()[header] ?? null
  }

  return headers
}

/**
 * Attempt to access API endpoints directly without auth token
 */
export async function probeApiEndpoint(
  page: Page,
  endpoint: string,
): Promise<{ status: number; body: string }> {
  const result = await page.evaluate(async (url) => {
    const res = await fetch(url, { credentials: 'omit' })
    const body = await res.text().catch(() => '')
    return { status: res.status, body }
  }, `http://localhost:8000${endpoint}`)

  return result
}

/**
 * Collect and return all security test results for reporting
 */
export class SecurityReporter {
  private results: SecurityTestResult[] = []

  record(test: string, passed: boolean, details: string): void {
    this.results.push({ test, passed, details })
  }

  logSummary(): void {
    const passed = this.results.filter((r) => r.passed).length
    const failed = this.results.filter((r) => !r.passed).length

    console.log('\nSECURITY TEST SUMMARY')
    console.log(`  Passed: ${passed}`)
    console.log(`  Failed: ${failed}`)
    console.log(`  Total:  ${this.results.length}\n`)

    this.results.forEach((r) => {
      const status = r.passed ? 'PASS' : 'FAIL'
      console.log(`  [${status}] ${r.test}: ${r.details}`)
    })
  }

  getFailures(): SecurityTestResult[] {
    return this.results.filter((r) => !r.passed)
  }
}

export const securityReporter = new SecurityReporter()
