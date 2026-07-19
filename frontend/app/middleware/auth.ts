import { clearAuthTokens, getAccessToken } from '~/utils/authToken'
import { isJwtExpired } from '~/utils/jwt'

function buildLoginRedirect(path: string, reason?: string) {
  const query: Record<string, string> = { redirect: path }
  if (reason) {
    query.reason = reason
  }

  return {
    path: '/login',
    query,
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
      return navigateTo(buildLoginRedirect(to.fullPath))
    }

    if (isJwtExpired(token)) {
      clearAuthTokens()
      authStore.logout()
      return navigateTo(buildLoginRedirect(to.fullPath, 'token-expired'))
    }

    if (!authStore.user) {
      try {
        await authStore.fetchCurrentUser()
      } catch {
        authStore.logout()
        return navigateTo(buildLoginRedirect(to.fullPath))
      }
    }
  }
})
