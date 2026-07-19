import { getAccessToken } from '~/utils/authToken'

export default defineNuxtRouteMiddleware(async (to) => {
  if (process.server) return

  // /rent is the public rental registry browse surface (no auth by design)
  const publicPaths = ['/', '/login', '/rent']
  const isPublicPath = publicPaths.some(p => to.path === p || to.path.startsWith(p + '/'))

  // Phase E: /rent/signup is citizen self-registration. A staff account
  // already has credentials, so bounce it to its own shell instead of
  // showing the citizen signup form — but only pay the initialize() cost
  // (a possible refresh-cookie round trip) when a token is already present;
  // a genuinely anonymous visitor must never be blocked from signing up.
  if (to.path === '/rent/signup' && getAccessToken()) {
    const authStore = useAuthStore()
    await authStore.initialize()
    if (authStore.isAuthenticated) {
      const { persona, homePath } = usePersona()
      if (persona.value === 'staff') {
        return navigateTo(homePath.value)
      }
    }
  }

  if (isPublicPath) return

  const authStore = useAuthStore()

  // Wait for the boot session restore (httpOnly refresh cookie) before
  // deciding to redirect — otherwise every hard reload bounces to /login.
  await authStore.initialize()

  if (!authStore.isAuthenticated) {
    const token = getAccessToken()
    if (!token) {
      return navigateTo({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    }
    return
  }

  // Phase E: role-scoped routing. Citizens must never land on the staff
  // shell (and vice versa for citizen-only surfaces) — redirect to the
  // caller's own persona home instead of rendering a mismatched shell.
  const { homePath, isRouteAllowed } = usePersona()
  if (!isRouteAllowed(to.path)) {
    return navigateTo(homePath.value)
  }
})
