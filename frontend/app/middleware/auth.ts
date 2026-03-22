/**
 * Check if JWT token is expired
 */
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true

    const payload = JSON.parse(
      Buffer.from(parts[1], 'base64').toString('utf-8')
    )

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
    const token = localStorage.getItem('valuadis_token')

    if (!token) {
      return navigateTo('/login')
    }

    // Check if token is expired
    if (isTokenExpired(token)) {
      localStorage.removeItem('valuadis_token')
      localStorage.removeItem('valuadis_user')
      const authStore = useAuthStore()
      authStore.logout()
      return navigateTo('/login?reason=token-expired')
    }

    // Ensure the Pinia store has the user populated
    const authStore = useAuthStore()
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
