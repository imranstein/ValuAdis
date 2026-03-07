export default defineNuxtRouteMiddleware((to) => {
  if (process.server) return

  const publicPaths = ['/', '/login']
  if (publicPaths.some(p => to.path === p || to.path.startsWith(p + '/'))) return

  const token = localStorage.getItem('valuadis_token')
  if (!token) {
    return navigateTo('/login')
  }
})
