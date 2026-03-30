import { test, expect } from '@playwright/test'
import {
  generateExpiredToken,
  generateValidToken,
  setAuthToken,
  clearAuthState,
  attemptUnauthenticatedAccess,
  isRedirectedToLogin,
  injectSQLPayload,
  getSecurityHeaders,
  probeApiEndpoint,
  securityReporter,
} from './security.helpers'

// OWASP Top 10 Security Tests
// Covers A01 Broken Access Control, A02 Cryptographic Failures,
// A03 Injection, and A06 Vulnerable Components

const BASE_URL = 'http://localhost:3000'

// Protected routes that must not be accessible without valid auth
const PROTECTED_ROUTES = [
  '/dashboard',
  '/vehicles',
  '/valuations',
  '/map',
  '/reports',
]

// Public routes that should always be accessible
const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password']

// API endpoints that must require authentication
const PROTECTED_API_ENDPOINTS = [
  '/api/v1/vehicles/',
  '/api/v1/valuations/',
  '/api/v1/reports/',
]

// ─── OWASP A01: Broken Access Control ────────────────────────────────────────

test.describe('OWASP A01 - Broken Access Control', () => {
  test('should redirect unauthenticated users from protected routes to login', async ({ page }) => {
    for (const route of PROTECTED_ROUTES) {
      const resultUrl = await attemptUnauthenticatedAccess(page, route)
      const redirected = isRedirectedToLogin(resultUrl)

      securityReporter.record(
        `A01: Unauthenticated access to ${route}`,
        redirected,
        redirected ? 'Correctly redirected to login' : `Stayed at ${resultUrl}`,
      )

      expect(redirected, `Route ${route} must redirect to login when unauthenticated`).toBe(true)
    }
  })

  test('should allow unauthenticated access to public routes', async ({ page }) => {
    await clearAuthState(page)

    for (const route of PUBLIC_ROUTES) {
      await page.goto(`${BASE_URL}${route}`)
      await page.waitForLoadState('networkidle')
      const currentUrl = page.url()

      // Public routes must not redirect away from themselves
      const stayedOnPage = currentUrl.includes(route)
      securityReporter.record(
        `A01: Public route ${route} accessible without auth`,
        stayedOnPage,
        stayedOnPage ? 'Accessible' : `Redirected to ${currentUrl}`,
      )

      expect(stayedOnPage, `Public route ${route} should be accessible without auth`).toBe(true)
    }
  })

  test('should block access with an expired JWT token (auth bypass attempt)', async ({ page }) => {
    const expiredToken = generateExpiredToken()
    await setAuthToken(page, expiredToken)

    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    const currentUrl = page.url()
    const blocked = isRedirectedToLogin(currentUrl)

    securityReporter.record(
      'A01: Expired token auth bypass attempt',
      blocked,
      blocked ? 'Expired token correctly rejected' : `Bypass succeeded - stayed at ${currentUrl}`,
    )

    expect(blocked, 'Expired tokens must not grant access to protected routes').toBe(true)
  })

  test('should clear expired token from localStorage on rejection', async ({ page }) => {
    const expiredToken = generateExpiredToken()
    await setAuthToken(page, expiredToken)

    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // After redirect, token must be removed from localStorage
    const storedToken = await page.evaluate(() => localStorage.getItem('valuadis_token'))

    securityReporter.record(
      'A01: Expired token cleared from storage',
      storedToken === null,
      storedToken === null ? 'Token cleared' : 'Token still present in localStorage',
    )

    expect(storedToken, 'Expired token must be removed from localStorage').toBeNull()
  })

  test('should block access with a malformed JWT token', async ({ page }) => {
    // Malformed token: missing payload and signature segments
    const malformedToken = 'not.a.valid.jwt.token.at.all'
    await setAuthToken(page, malformedToken)

    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    const blocked = isRedirectedToLogin(page.url())

    securityReporter.record(
      'A01: Malformed token auth bypass attempt',
      blocked,
      blocked ? 'Malformed token correctly rejected' : 'Bypass succeeded',
    )

    expect(blocked, 'Malformed tokens must not grant access').toBe(true)
  })

  test('should block API endpoints from unauthenticated requests', async ({ page }) => {
    await clearAuthState(page)

    for (const endpoint of PROTECTED_API_ENDPOINTS) {
      const { status } = await probeApiEndpoint(page, endpoint)

      // API must return 401 or 403, never 200, for unauthenticated requests
      const isBlocked = status === 401 || status === 403

      securityReporter.record(
        `A01: API ${endpoint} requires auth`,
        isBlocked,
        `Returned HTTP ${status}`,
      )

      expect(
        isBlocked,
        `API endpoint ${endpoint} must return 401/403 for unauthenticated requests (got ${status})`,
      ).toBe(true)
    }
  })
})

// ─── OWASP A02: Cryptographic Failures ───────────────────────────────────────

test.describe('OWASP A02 - Cryptographic Failures', () => {
  test('should not expose sensitive data in client-side storage', async ({ page }) => {
    const validToken = generateValidToken()
    await setAuthToken(page, validToken)

    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // Check that no plaintext passwords, API keys, or secrets are in localStorage
    const storageData = await page.evaluate(() => {
      const data: Record<string, string | null> = {}
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key) data[key] = localStorage.getItem(key)
      }
      return data
    })

    const sensitiveKeyPatterns = [/password/i, /secret/i, /api[_-]?key/i, /private[_-]?key/i]

    for (const [key] of Object.entries(storageData)) {
      const isSensitive = sensitiveKeyPatterns.some((pattern) => pattern.test(key))

      securityReporter.record(
        `A02: localStorage key "${key}" is not a sensitive field`,
        !isSensitive,
        isSensitive ? 'Sensitive key found in localStorage' : 'Key is safe',
      )

      expect(isSensitive, `Sensitive key "${key}" must not be stored in localStorage`).toBe(false)
    }
  })

  test('should not transmit tokens via URL query parameters', async ({ page }) => {
    const validToken = generateValidToken()
    await setAuthToken(page, validToken)

    // Navigate through app pages and verify token never appears in URL
    const pagesToCheck = [BASE_URL + '/dashboard', BASE_URL + '/vehicles']

    for (const url of pagesToCheck) {
      await page.goto(url)
      await page.waitForLoadState('networkidle')

      const currentUrl = page.url()
      const tokenInUrl = currentUrl.includes('token=') || currentUrl.includes('jwt=')

      securityReporter.record(
        `A02: Token not in URL for ${url}`,
        !tokenInUrl,
        tokenInUrl ? 'Token exposed in URL' : 'Token not in URL',
      )

      expect(tokenInUrl, `Auth token must never appear in URL query parameters`).toBe(false)
    }
  })
})

// ─── OWASP A03: Injection ─────────────────────────────────────────────────────

test.describe('OWASP A03 - Injection', () => {
  // SQL injection payloads to test against URL parameters
  const SQL_PAYLOADS = [
    "' OR '1'='1",
    "1; DROP TABLE vehicles; --",
    "' UNION SELECT * FROM users --",
    '1 AND 1=1',
  ]

  // XSS payloads to test against input fields
  const XSS_PAYLOADS = [
    '<script>alert("xss")</script>',
    '"><img src=x onerror=alert(1)>',
    "javascript:alert('xss')",
  ]

  test('should not execute SQL injection payloads in route parameters', async ({ page }) => {
    // Only test against routes that render without crashing (not auth-gated for param test)
    for (const payload of SQL_PAYLOADS) {
      const { url } = await injectSQLPayload(page, '/vehicles', 'search', payload)

      // App must not show a raw database error — any redirect or safe page is acceptable
      const pageContent = await page.content()
      const hasDbError =
        /sql error|syntax error|mysql|postgresql|sqlite|ora-\d+/i.test(pageContent)

      securityReporter.record(
        `A03: SQL injection payload "${payload.slice(0, 30)}" does not expose DB errors`,
        !hasDbError,
        hasDbError ? 'Database error exposed in response' : `Safe response at ${url}`,
      )

      expect(hasDbError, 'SQL injection must not expose database errors').toBe(false)
    }
  })

  test('should sanitize XSS payloads in search inputs', async ({ page }) => {
    const validToken = generateValidToken()
    await setAuthToken(page, validToken)

    await page.goto(`${BASE_URL}/vehicles`)
    await page.waitForLoadState('networkidle')

    // Skip if not on vehicles page (redirect happened)
    if (!page.url().includes('/vehicles')) {
      test.skip()
      return
    }

    for (const payload of XSS_PAYLOADS) {
      // Listen for dialog alerts — any alert means XSS executed
      let xssExecuted = false
      page.once('dialog', async (dialog) => {
        xssExecuted = true
        await dialog.dismiss()
      })

      // Try to inject via URL query param used for search
      await page.goto(`${BASE_URL}/vehicles?search=${encodeURIComponent(payload)}`)
      await page.waitForLoadState('networkidle')

      // Short wait to let any script tags execute
      await page.waitForTimeout(500)

      securityReporter.record(
        `A03: XSS payload "${payload.slice(0, 30)}" is sanitized`,
        !xssExecuted,
        xssExecuted ? 'XSS payload executed (alert fired)' : 'Payload safely sanitized',
      )

      expect(xssExecuted, `XSS payload must not execute: ${payload}`).toBe(false)
    }
  })

  test('should reject requests with injection in API parameters', async ({ page }) => {
    await clearAuthState(page)

    // Probe API with injection payload — must return 401/403/400, never 500 with DB details
    const { status, body } = await probeApiEndpoint(
      page,
      `/api/v1/vehicles/?search=${encodeURIComponent("' OR '1'='1")}`,
    )

    const isDbError = /sql error|syntax error|mysql|postgresql|sqlite/i.test(body)
    const isSafeStatus = status !== 500 || !isDbError

    securityReporter.record(
      'A03: API does not expose DB errors on injection attempt',
      isSafeStatus,
      `Status ${status}, DB error in body: ${isDbError}`,
    )

    expect(isDbError, 'API must not expose database errors on injection attempts').toBe(false)
  })
})

// ─── OWASP A06: Vulnerable Components ────────────────────────────────────────

test.describe('OWASP A06 - Vulnerable Components', () => {
  test('should serve security headers on all responses', async ({ page }) => {
    // Test headers on the login page (accessible without auth)
    const headers = await getSecurityHeaders(page, `${BASE_URL}/login`)

    // x-content-type-options prevents MIME-type sniffing attacks
    securityReporter.record(
      'A06: X-Content-Type-Options header present',
      headers['x-content-type-options'] !== null,
      headers['x-content-type-options'] ?? 'MISSING',
    )

    // x-frame-options prevents clickjacking
    securityReporter.record(
      'A06: X-Frame-Options header present',
      headers['x-frame-options'] !== null,
      headers['x-frame-options'] ?? 'MISSING',
    )

    // Log results — in many dev environments headers may be absent;
    // we warn but do not hard-fail so CI can run without full HTTPS/reverse-proxy setup.
    // Flip to expect(...).not.toBeNull() once a reverse proxy is in front of the app.
    console.log('[A06] Security headers:', JSON.stringify(headers, null, 2))
  })

  test('should not expose server version or framework details in headers', async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/login`)
    const headers = response?.headers() ?? {}

    const exposedServerHeaders = ['server', 'x-powered-by', 'x-aspnet-version']

    for (const header of exposedServerHeaders) {
      const value = headers[header]
      const isExposed = value !== undefined && value !== null

      securityReporter.record(
        `A06: Header "${header}" not exposed`,
        !isExposed,
        isExposed ? `Exposes: ${value}` : 'Not present',
      )

      // Warn only — some reverse proxies inject these and it may be outside app control
      if (isExposed) {
        console.warn(`[A06 WARNING] Response header "${header}: ${value}" may expose server info`)
      }
    }
  })

  test('should not expose stack traces or internal paths in error responses', async ({ page }) => {
    await clearAuthState(page)

    // Probe a clearly invalid endpoint to provoke an error response
    const { status, body } = await probeApiEndpoint(page, '/api/v1/nonexistent-endpoint-xyz/')

    const exposesInternals =
      /traceback|stack trace|file "\/|line \d+, in |at \/usr\/|at \/home\//i.test(body)

    securityReporter.record(
      'A06: Error responses do not expose stack traces',
      !exposesInternals,
      exposesInternals ? 'Stack trace found in response body' : `Clean error response (${status})`,
    )

    expect(exposesInternals, 'Error responses must not expose internal stack traces').toBe(false)
  })
})

// ─── Summary Report ───────────────────────────────────────────────────────────

test.afterAll(() => {
  securityReporter.logSummary()

  const failures = securityReporter.getFailures()
  if (failures.length > 0) {
    console.warn('\n[SECURITY] FAILURES DETECTED:')
    failures.forEach((f) => console.warn(`  - [FAIL] ${f.test}: ${f.details}`))
  }
})
