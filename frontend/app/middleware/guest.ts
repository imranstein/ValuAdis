import { getAccessToken } from '~/utils/authToken'

export default defineNuxtRouteMiddleware(async () => {
  if (process.client) {
    const token = getAccessToken()
    if (token) {
      // Phase E: send an already-logged-in visitor to their own persona
      // home (officer console, my-listings, my-applications) rather than
      // always /dashboard, which citizens can't reach.
      const authStore = useAuthStore()
      await authStore.initialize()
      const { homePath } = usePersona()
      return navigateTo(homePath.value)
    }
  }
})
