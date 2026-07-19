// Reports uncaught errors to Sentry when NUXT_PUBLIC_SENTRY_DSN is provided.
// No-op without a DSN so local development and tests are unaffected.
// ponytail: minimal envelope-API client (no @sentry/vue dependency — npm
// registry unreachable at build time); swap for the official SDK when
// breadcrumbs/tracing are needed.

interface SentryEndpoint {
  url: string
}

export function parseDsn(dsn: string): SentryEndpoint | null {
  try {
    const u = new URL(dsn)
    const projectId = u.pathname.replace(/\//g, '')
    if (!u.username || !projectId) return null
    return {
      url: `${u.protocol}//${u.host}/api/${projectId}/envelope/?sentry_key=${u.username}&sentry_version=7`
    }
  } catch {
    return null
  }
}

function buildEnvelope(error: unknown, environment: string): string {
  const err = error instanceof Error ? error : new Error(String(error))
  const eventId = crypto.randomUUID().replace(/-/g, '')
  const sentAt = new Date().toISOString()
  const event = {
    event_id: eventId,
    timestamp: sentAt,
    platform: 'javascript',
    level: 'error',
    environment,
    request: { url: window.location.href },
    exception: {
      values: [{ type: err.name, value: err.message }]
    },
    extra: { stack: err.stack || '' }
  }
  return [
    JSON.stringify({ event_id: eventId, sent_at: sentAt }),
    JSON.stringify({ type: 'event' }),
    JSON.stringify(event)
  ].join('\n')
}

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const endpoint = parseDsn(String(config.public.sentryDsn || ''))
  if (!endpoint) return

  const environment = import.meta.dev ? 'development' : 'production'
  const report = (error: unknown) => {
    try {
      fetch(endpoint.url, {
        method: 'POST',
        body: buildEnvelope(error, environment),
        keepalive: true
      }).catch(() => {})
    } catch {
      // reporting must never break the app
    }
  }

  nuxtApp.vueApp.config.errorHandler = (error) => {
    report(error)
    console.error(error)
  }
  window.addEventListener('error', (event) => report(event.error ?? event.message))
  window.addEventListener('unhandledrejection', (event) => report(event.reason))
})
