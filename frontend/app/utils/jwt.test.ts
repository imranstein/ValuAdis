import { describe, expect, it } from 'vitest'
import { decodeJwtPayload, isJwtExpired, isJwtValid } from './jwt'

const makeToken = (payload: Record<string, unknown>): string => {
  const encode = (value: string) => btoa(value)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '')

  return `a.${encode(JSON.stringify(payload))}.b`
}

describe('jwt utils', () => {
  it('decodes payload from a jwt token', () => {
    const payload = { exp: 123, sub: 'test' }
    const token = makeToken(payload)

    expect(decodeJwtPayload(token)).toMatchObject(payload)
  })

  it('marks expired token as invalid', () => {
    const token = makeToken({ exp: Math.floor(Date.now() / 1000) - 30 })
    expect(isJwtValid(token)).toBe(false)
    expect(isJwtExpired(token)).toBe(true)
  })

  it('marks valid token as valid', () => {
    const token = makeToken({ exp: Math.floor(Date.now() / 1000) + 30 })
    expect(isJwtValid(token)).toBe(true)
    expect(isJwtExpired(token)).toBe(false)
  })

  it('returns null payload for malformed token', () => {
    expect(decodeJwtPayload('bad-token')).toBeNull()
  })
})
