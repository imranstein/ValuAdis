import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

const pushMock = vi.fn()
const tokenState = ref<string | null>(null)
const userState = ref<any>(null)

vi.mock('#app', () => ({
  useRouter: () => ({
    push: pushMock,
  }),
  useState: (key: string, initializer: () => unknown) => {
    if (key === 'auth.token') return tokenState
    if (key === 'auth.user') return userState
    return ref(initializer())
  },
}))

const { useAuth } = await import('./useAuth')

describe('useAuth', () => {
  beforeEach(() => {
    tokenState.value = null
    userState.value = null
    pushMock.mockReset()
  })

  const makeToken = (expiryOffsetSeconds: number): string => {
    const payload = {
      exp: Math.floor(Date.now() / 1000) + expiryOffsetSeconds,
      sub: 'test-user',
    }
    return `a.${Buffer.from(JSON.stringify(payload)).toString('base64')}.b`
  }

  it('accepts a valid token in JWT payload', () => {
    const { isTokenValid } = useAuth()
    expect(isTokenValid(makeToken(60))).toBe(true)
  })

  it('rejects an expired token', () => {
    const { isTokenValid } = useAuth()
    expect(isTokenValid(makeToken(-60))).toBe(false)
  })

  it('rejects invalid jwt format', () => {
    const { isTokenValid } = useAuth()
    expect(isTokenValid('bad-token')).toBe(false)
  })

  it('returns decoded token payload', () => {
    const { getTokenPayload } = useAuth()
    const token = makeToken(120)
    expect(getTokenPayload(token)).toMatchObject({
      sub: 'test-user',
      exp: expect.any(Number),
    })
  })

  it('clears auth state and redirects when token is invalid', async () => {
    const { setAuth, validateAndRefresh, token, user } = useAuth()
    setAuth(makeToken(-120), { id: 3, full_name: 'Tester' })

    await expect(validateAndRefresh()).resolves.toBe(false)
    expect(token.value).toBeNull()
    expect(user.value).toBeNull()
    expect(pushMock).toHaveBeenCalledWith('/login?reason=token-expired')
  })

  it('clears token and user with clearAuth', () => {
    const { setAuth, clearAuth, token, user } = useAuth()
    setAuth('token-value', { id: 7 })

    clearAuth()
    expect(token.value).toBeNull()
    expect(user.value).toBeNull()
  })
})
