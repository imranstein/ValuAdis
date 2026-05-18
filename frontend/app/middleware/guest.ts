import { getAccessToken } from '~/utils/authToken'

export default defineNuxtRouteMiddleware(() => {
  if (process.client) {
    const token = getAccessToken()
    if (token) {
      return navigateTo('/dashboard')
    }
  }
})
