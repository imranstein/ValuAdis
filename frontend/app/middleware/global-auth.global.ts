import { getAccessToken } from '~/utils/authToken'

export default defineNuxtRouteMiddleware((to) => {
  if (process.server) return

  const publicPaths = ['/', '/login']
  if (publicPaths.some(p => to.path === p || to.path.startsWith(p + '/'))) return

  const authStore = useAuthStore()
  if (authStore.isAuthenticated) return

  const token = getAccessToken()
  if (!token) {
    return navigateTo('/login')
  }
})
