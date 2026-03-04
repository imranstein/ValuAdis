export default defineNuxtRouteMiddleware(() => {
  if (process.client) {
    const token = localStorage.getItem('valuadis_token')
    if (!token) {
      return navigateTo('/login')
    }
  }
})
