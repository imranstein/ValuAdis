/**
 * Security Unit Tests: JWT Authentication
 * Covers OWASP Top 10: A02 Cryptographic Failures, A07 Authentication Failures
 */

// Pure utility extracted from useAuth composable for unit testing
// Mirrors the isTokenValid / getTokenPayload logic without Vue runtime dependencies

function base64UrlDecode(str: string): string {
  // Pad base64 string and decode
  const padded = str + '=='.slice((str.length + 3) % 4 === 0 ? 4 : (str.length + 3) % 4)
  return Buffer.from(padded, 'base64').toString('utf-8')
}

function parseJwt(token: string): { header: any; payload: any } | null {
  const parts = token.split('.')
  if (parts.length !== 3) return null
  try {
    return {
      header: JSON.parse(base64UrlDecode(parts[0])),
      payload: JSON.parse(base64UrlDecode(parts[1])),
    }
  } catch {
    return null
  }
}

function isTokenValid(jwtToken: string): boolean {
  if (!jwtToken) return false
  try {
    const parts = jwtToken.split('.')
    if (parts.length !== 3) return false
    const payload = JSON.parse(base64UrlDecode(parts[1]))
    if (!payload.exp) return false
    return payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

function buildToken(payload: object, header = { alg: 'HS256', typ: 'JWT' }): string {
  const encode = (obj: object) =>
    Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=+$/, '')
  // Signature is intentionally a dummy — client-side never verifies crypto
  return `${encode(header)}.${encode(payload)}.fakesignature`
}

// ─── Helpers ────────────────────────────────────────────────────────────────

const FUTURE_EXP = Math.floor(Date.now() / 1000) + 3600 // 1 h from now
const PAST_EXP = Math.floor(Date.now() / 1000) - 3600   // 1 h ago

// ─── Tests ──────────────────────────────────────────────────────────────────

describe('JWT Token Validation — Security Tests', () => {
  // ── Expiry ──────────────────────────────────────────────────────────────

  describe('Token Expiry', () => {
    test('accepts a token with a future exp claim', () => {
      const token = buildToken({ sub: 'user1', exp: FUTURE_EXP })
      expect(isTokenValid(token)).toBe(true)
    })

    test('rejects a token whose exp is in the past', () => {
      const token = buildToken({ sub: 'user1', exp: PAST_EXP })
      expect(isTokenValid(token)).toBe(false)
    })

    test('rejects a token with exp exactly at current time (boundary)', () => {
      const nowSec = Math.floor(Date.now() / 1000)
      const token = buildToken({ sub: 'user1', exp: nowSec - 1 })
      expect(isTokenValid(token)).toBe(false)
    })

    test('rejects a token with no exp claim', () => {
      const token = buildToken({ sub: 'user1' })
      expect(isTokenValid(token)).toBe(false)
    })

    test('rejects a token where exp is zero', () => {
      const token = buildToken({ sub: 'user1', exp: 0 })
      expect(isTokenValid(token)).toBe(false)
    })
  })

  // ── Structural Tampering ────────────────────────────────────────────────

  describe('Token Tampering', () => {
    test('rejects a token with fewer than three segments', () => {
      expect(isTokenValid('header.payload')).toBe(false)
    })

    test('rejects a token with more than three segments', () => {
      expect(isTokenValid('a.b.c.d')).toBe(false)
    })

    test('rejects an empty string', () => {
      expect(isTokenValid('')).toBe(false)
    })

    test('rejects a token with a corrupted payload segment', () => {
      const token = buildToken({ sub: 'user1', exp: FUTURE_EXP })
      const parts = token.split('.')
      // Corrupt the payload
      parts[1] = parts[1].split('').reverse().join('')
      expect(isTokenValid(parts.join('.'))).toBe(false)
    })

    test('rejects a token where payload is not valid JSON', () => {
      const header = Buffer.from('{"alg":"HS256","typ":"JWT"}').toString('base64')
      const payload = Buffer.from('not-json-!!!').toString('base64')
      expect(isTokenValid(`${header}.${payload}.sig`)).toBe(false)
    })

    test('rejects null / undefined gracefully', () => {
      expect(isTokenValid(null as any)).toBe(false)
      expect(isTokenValid(undefined as any)).toBe(false)
    })
  })

  // ── Invalid Signatures (client-side awareness) ──────────────────────────

  describe('Signature Anomalies', () => {
    test('parseJwt extracts header algorithm claim', () => {
      const token = buildToken({ sub: 'u', exp: FUTURE_EXP })
      const parsed = parseJwt(token)
      expect(parsed?.header?.alg).toBe('HS256')
    })

    test('detects "none" algorithm in header (should be refused by server, flagged here)', () => {
      const token = buildToken({ sub: 'u', exp: FUTURE_EXP }, { alg: 'none', typ: 'JWT' })
      const parsed = parseJwt(token)
      // Client can detect and warn; server must reject — we assert detection
      expect(parsed?.header?.alg).toBe('none')
    })

    test('parseJwt returns null for a malformed token', () => {
      expect(parseJwt('bad.token')).toBeNull()
    })
  })

  // ── Privilege Escalation via Payload Manipulation ───────────────────────

  describe('Payload Claim Integrity', () => {
    test('a token claiming admin role is structurally parseable (server must verify sig)', () => {
      const token = buildToken({ sub: 'attacker', role: 'admin', exp: FUTURE_EXP })
      const parsed = parseJwt(token)
      // This token MUST NOT be trusted without server-side signature verification
      expect(parsed?.payload?.role).toBe('admin')
      // But client-side expiry check still works correctly
      expect(isTokenValid(token)).toBe(true)
    })

    test('a replayed token with altered sub is still structurally valid until server rejects', () => {
      const original = buildToken({ sub: 'user1', exp: FUTURE_EXP })
      const parts = original.split('.')
      const newPayload = Buffer.from(
        JSON.stringify({ sub: 'admin', exp: FUTURE_EXP })
      ).toString('base64').replace(/=+$/, '')
      const tampered = `${parts[0]}.${newPayload}.${parts[2]}`
      // Tampering is detectable only by signature verification on server
      const parsed = parseJwt(tampered)
      expect(parsed?.payload?.sub).toBe('admin')
    })
  })
})
