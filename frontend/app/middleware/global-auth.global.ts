import { getAccessToken } from '~/utils/authToken'

export default defineNuxtRouteMiddleware(async (to) => {
  if (process.server) return

  const publicPaths = ['/', '/login']
  if (publicPaths.some(p => to.path === p || to.path.startsWith(p + '/'))) return

  const authStore = useAuthStore()

  // Wait for the boot session restore (httpOnly refresh cookie) before
  // deciding to redirect — otherwise every hard reload bounces to /login.
  await authStore.initialize()

  if (authStore.isAuthenticated) return

  const token = getAccessToken()
  if (!token) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  }
})
