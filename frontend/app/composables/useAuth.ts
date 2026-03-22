import { useRouter } from '#app'

/**
 * Composable for authentication utilities
 */
export const useAuth = () => {
  const router = useRouter()
  const token = useState('auth.token', () => null as string | null)
  const user = useState('auth.user', () => null as any)

  /**
   * Validates if JWT token has expired
   * @param jwtToken - JWT token string
   * @returns true if token is valid, false if expired or invalid
   */
  const isTokenValid = (jwtToken?: string): boolean => {
    const tokenToCheck = jwtToken || token.value

    if (!tokenToCheck) return false

    try {
      // Parse JWT payload (no verification here, just checking expiry)
      const parts = tokenToCheck.split('.')
      if (parts.length !== 3) return false

      // Decode payload
      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64').toString('utf-8')
      )

      // Check if exp claim exists
      if (!payload.exp) return false

      // Check if token expired (exp is in seconds, Date.now() is in milliseconds)
      const expiryTime = payload.exp * 1000
      const currentTime = Date.now()

      return expiryTime > currentTime
    } catch (error) {
      console.error('Token validation error:', error)
      return false
    }
  }

  /**
   * Get decoded token payload without verification
   * @param jwtToken - JWT token string
   * @returns Decoded payload object or null if invalid
   */
  const getTokenPayload = (jwtToken?: string): any => {
    const tokenToCheck = jwtToken || token.value

    if (!tokenToCheck) return null

    try {
      const parts = tokenToCheck.split('.')
      if (parts.length !== 3) return null

      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64').toString('utf-8')
      )
      return payload
    } catch (error) {
      console.error('Token decode error:', error)
      return null
    }
  }

  /**
   * Check token validity and logout if expired
   * @returns true if token is valid, false if expired
   */
  const validateAndRefresh = async (): Promise<boolean> => {
    if (!isTokenValid()) {
      // Token expired - clear auth state and redirect
      token.value = null
      user.value = null
      await router.push('/login?reason=token-expired')
      return false
    }
    return true
  }

  /**
   * Set auth token and user
   */
  const setAuth = (newToken: string, newUser?: any) => {
    token.value = newToken
    if (newUser) user.value = newUser
  }

  /**
   * Clear auth state
   */
  const clearAuth = () => {
    token.value = null
    user.value = null
  }

  return {
    token: readonly(token),
    user: readonly(user),
    isTokenValid,
    getTokenPayload,
    validateAndRefresh,
    setAuth,
    clearAuth,
  }
}
