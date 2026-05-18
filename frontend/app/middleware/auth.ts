import { clearAuthTokens, getAccessToken } from '~/utils/authToken'

/**
 * Check if JWT token is expired
 */
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true

    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(decodeURIComponent(
      atob(base64)
        .split('')
        .map(char => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    ))

    if (!payload.exp) return true

    const expiryTime = payload.exp * 1000
    const currentTime = Date.now()

    return expiryTime <= currentTime
  } catch {
    return true
  }
}

export default defineNuxtRouteMiddleware(async (to) => {
  // Skip auth check for public routes
  const publicRoutes = ['/login', '/register', '/forgot-password']
  if (publicRoutes.includes(to.path)) {
    return
  }

  if (process.client) {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) return

    const token = getAccessToken()

    if (!token) {
      return navigateTo('/login')
    }

    // Check if token is expired
    if (isTokenExpired(token)) {
      clearAuthTokens()
      authStore.logout()
      return navigateTo('/login?reason=token-expired')
    }

    // Ensure the Pinia store has the user populated
    if (!authStore.user) {
      try {
        await authStore.fetchCurrentUser()
      } catch {
        authStore.logout()
        return navigateTo('/login')
      }
    }
  }
})
