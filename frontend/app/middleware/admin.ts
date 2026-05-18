export default defineNuxtRouteMiddleware(async () => {
  if (process.server) return

  const authStore = useAuthStore()
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }

  const u = authStore.user as any
  const isAdmin = u?.is_admin || ['system_admin', 'firm_admin', 'municipal_admin'].includes(u?.role || '')

  if (!isAdmin) {
    return navigateTo('/dashboard')
  }
})
