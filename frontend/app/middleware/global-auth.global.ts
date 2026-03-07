export default defineNuxtRouteMiddleware((to) => {
  if (process.server) return

  const publicPaths = ['/', '/login']
  if (publicPaths.includes(to.path)) return

  const token = localStorage.getItem('valuadis_token')
  if (!token) {
    return navigateTo('/login')
  }
})
