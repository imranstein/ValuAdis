export default defineNuxtRouteMiddleware(async () => {
  if (process.client) {
    const token = localStorage.getItem('valuadis_token')
    if (!token) {
      return navigateTo('/login')
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
