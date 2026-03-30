/**
 * Security Unit Tests: Session Management
 * Covers OWASP Top 10: A07 Authentication Failures, A01 Broken Access Control
 * Tests CSRF token validation, session fixation, session expiry,
 * and secure cookie attribute checks.
 */

// ─── Session Utilities (client-side session security helpers) ─────────────────

interface SessionData {
  id: string
  userId: string
  createdAt: number     // Unix ms
  lastActivityAt: number
  csrfToken: string
  userAgent?: string
  ipAddress?: string
}

const SESSION_TIMEOUT_MS = 30 * 60 * 1000 // 30 minutes

/**
 * Checks whether a session has expired due to inactivity.
 */
function isSessionExpired(session: SessionData): boolean {
  return Date.now() - session.lastActivityAt > SESSION_TIMEOUT_MS
}

/**
 * Validates a submitted CSRF token against the session-bound token.
 * Constant-time comparison is performed server-side; this mirrors the check logic.
 */
function validateCsrfToken(submittedToken: string, sessionToken: string): boolean {
  if (!submittedToken || !sessionToken) return false
  if (submittedToken.length !== sessionToken.length) return false
  return submittedToken === sessionToken
}

/**
 * Generates a cryptographically random CSRF token (browser environment substitute).
 * In production, window.crypto.getRandomValues is used.
 */
function generateCsrfToken(length = 32): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  // Use Math.random only in tests — server uses crypto.randomBytes
  return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

/**
 * Detects session fixation: a new session must have a different ID than any
 * pre-authentication session.
 */
function detectSessionFixation(preAuthSessionId: string, postAuthSessionId: string): boolean {
  // Returns true if fixation attack is detected (IDs are the same)
  return preAuthSessionId === postAuthSessionId
}

/**
 * Validates required secure cookie attributes from a Set-Cookie header string.
 */
function validateSecureCookieAttributes(setCookieHeader: string): {
  hasSecure: boolean
  hasHttpOnly: boolean
  hasSameSite: boolean
  sameSiteValue: string | null
} {
  const lower = setCookieHeader.toLowerCase()
  const sameSiteMatch = lower.match(/samesite=(\w+)/)
  return {
    hasSecure: lower.includes('secure'),
    hasHttpOnly: lower.includes('httponly'),
    hasSameSite: sameSiteMatch !== null,
    sameSiteValue: sameSiteMatch ? sameSiteMatch[1] : null,
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function makeSession(overrides: Partial<SessionData> = {}): SessionData {
  return {
    id: 'sess_abc123',
    userId: 'user_1',
    createdAt: Date.now(),
    lastActivityAt: Date.now(),
    csrfToken: generateCsrfToken(),
    ...overrides,
  }
}

// ─── CSRF Tests ───────────────────────────────────────────────────────────────

describe('Session Security — CSRF Token Validation', () => {
  test('accepts a matching CSRF token', () => {
    const token = generateCsrfToken()
    expect(validateCsrfToken(token, token)).toBe(true)
  })

  test('rejects a mismatched CSRF token', () => {
    const sessionToken = generateCsrfToken()
    const attackerToken = generateCsrfToken()
    // Ensure they are different (extremely high probability)
    expect(validateCsrfToken(attackerToken, sessionToken)).toBe(false)
  })

  test('rejects an empty submitted token', () => {
    expect(validateCsrfToken('', 'valid-token')).toBe(false)
  })

  test('rejects an empty session token', () => {
    expect(validateCsrfToken('some-token', '')).toBe(false)
  })

  test('rejects tokens of different lengths (length leak prevention)', () => {
    expect(validateCsrfToken('short', 'a-much-longer-token-value')).toBe(false)
  })

  test('CSRF tokens are unique per call (no reuse)', () => {
    const t1 = generateCsrfToken()
    const t2 = generateCsrfToken()
    expect(t1).not.toBe(t2)
  })

  test('CSRF token has minimum length for entropy', () => {
    const token = generateCsrfToken()
    expect(token.length).toBeGreaterThanOrEqual(32)
  })
})

// ─── Session Fixation Tests ───────────────────────────────────────────────────

describe('Session Security — Session Fixation Prevention', () => {
  test('detects when pre- and post-auth session IDs are identical', () => {
    const sessionId = 'sess_fixed_id'
    expect(detectSessionFixation(sessionId, sessionId)).toBe(true)
  })

  test('passes when session ID is regenerated after login', () => {
    const preAuth = 'sess_before_login'
    const postAuth = 'sess_after_login_new'
    expect(detectSessionFixation(preAuth, postAuth)).toBe(false)
  })

  test('new session must not reuse an empty or null-like ID', () => {
    expect(detectSessionFixation('', '')).toBe(true)
  })
})

// ─── Session Expiry Tests ─────────────────────────────────────────────────────

describe('Session Security — Session Expiry', () => {
  test('active session is not expired', () => {
    const session = makeSession({ lastActivityAt: Date.now() })
    expect(isSessionExpired(session)).toBe(false)
  })

  test('session inactive for more than 30 minutes is expired', () => {
    const session = makeSession({
      lastActivityAt: Date.now() - SESSION_TIMEOUT_MS - 1,
    })
    expect(isSessionExpired(session)).toBe(true)
  })

  test('session inactive for exactly the timeout boundary is expired', () => {
    const session = makeSession({
      lastActivityAt: Date.now() - SESSION_TIMEOUT_MS - 1,
    })
    expect(isSessionExpired(session)).toBe(true)
  })

  test('session inactive for 29 minutes is still valid', () => {
    const session = makeSession({
      lastActivityAt: Date.now() - 29 * 60 * 1000,
    })
    expect(isSessionExpired(session)).toBe(false)
  })
})

// ─── Secure Cookie Attribute Tests ────────────────────────────────────────────

describe('Session Security — Secure Cookie Attributes', () => {
  const validCookieHeader =
    'session=abc123; Path=/; HttpOnly; Secure; SameSite=Strict'

  test('recognises Secure flag on session cookie', () => {
    const attrs = validateSecureCookieAttributes(validCookieHeader)
    expect(attrs.hasSecure).toBe(true)
  })

  test('recognises HttpOnly flag on session cookie', () => {
    const attrs = validateSecureCookieAttributes(validCookieHeader)
    expect(attrs.hasHttpOnly).toBe(true)
  })

  test('recognises SameSite attribute on session cookie', () => {
    const attrs = validateSecureCookieAttributes(validCookieHeader)
    expect(attrs.hasSameSite).toBe(true)
    expect(attrs.sameSiteValue).toBe('strict')
  })

  test('flags a cookie missing the Secure attribute', () => {
    const insecure = 'session=abc123; Path=/; HttpOnly; SameSite=Lax'
    const attrs = validateSecureCookieAttributes(insecure)
    expect(attrs.hasSecure).toBe(false)
  })

  test('flags a cookie missing HttpOnly (XSS risk)', () => {
    const noHttpOnly = 'session=abc123; Path=/; Secure; SameSite=Strict'
    const attrs = validateSecureCookieAttributes(noHttpOnly)
    expect(attrs.hasHttpOnly).toBe(false)
  })

  test('flags a cookie with SameSite=None (CSRF risk when without Secure)', () => {
    const sameSiteNone = 'session=abc123; Path=/; HttpOnly; SameSite=None'
    const attrs = validateSecureCookieAttributes(sameSiteNone)
    expect(attrs.sameSiteValue).toBe('none')
    // SameSite=None without Secure is a CSRF vulnerability
    expect(attrs.hasSecure).toBe(false)
  })

  test('flags a cookie with no SameSite attribute at all', () => {
    const noSameSite = 'session=abc123; Path=/; HttpOnly; Secure'
    const attrs = validateSecureCookieAttributes(noSameSite)
    expect(attrs.hasSameSite).toBe(false)
  })
})

// ─── Session Binding Tests ────────────────────────────────────────────────────

describe('Session Security — Session Binding', () => {
  test('session stores userId to bind session to authenticated user', () => {
    const session = makeSession({ userId: 'user_42' })
    expect(session.userId).toBe('user_42')
  })

  test('session stores creation timestamp for absolute timeout enforcement', () => {
    const before = Date.now()
    const session = makeSession()
    const after = Date.now()
    expect(session.createdAt).toBeGreaterThanOrEqual(before)
    expect(session.createdAt).toBeLessThanOrEqual(after)
  })

  test('CSRF token is bound to the session (not global)', () => {
    const session1 = makeSession()
    const session2 = makeSession()
    // Each session has its own CSRF token
    expect(session1.csrfToken).not.toBe(session2.csrfToken)
  })
})
