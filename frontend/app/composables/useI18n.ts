import { ref, computed } from 'vue'
import en from '~/locales/en.json'
import am from '~/locales/am.json'

/**
 * Lightweight i18n (U9, extended in Phase G for rentals). English is the
 * default; Amharic content lives in locales/am.json. A single reactive
 * locale is shared app-wide and persisted per device via a cookie (so it
 * survives reload the same way on every page, public or authenticated).
 * t('nav.dashboard') resolves a dot path in the active locale, falling back
 * to English and finally the key itself, so a missing Amharic string
 * degrades to English rather than blank. Amharic (Ge'ez script) is
 * left-to-right, so `dir` stays 'ltr' for both locales.
 */
type Dict = Record<string, unknown>
const messages: Record<string, Dict> = { en, am }
const AVAILABLE = ['en', 'am'] as const
export type Locale = (typeof AVAILABLE)[number]
const STORAGE_KEY = 'valuadis_locale'
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365 // 1 year

// Module-scoped so every component shares one reactive locale.
const locale = ref<Locale>('en')
let restored = false

function resolve(dict: Dict | undefined, path: string): string | undefined {
  if (!dict) return undefined
  const value = path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object') return (acc as Dict)[key]
    return undefined
  }, dict)
  return typeof value === 'string' ? value : undefined
}

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

function writeCookie(name: string, value: string) {
  document.cookie = `${name}=${encodeURIComponent(value)}; max-age=${COOKIE_MAX_AGE}; path=/; samesite=lax`
}

function applyDocumentLocale(next: Locale) {
  document.documentElement.lang = next
  document.documentElement.dir = 'ltr'
}

export function useI18n() {
  if (!restored && process.client) {
    restored = true
    const saved = readCookie(STORAGE_KEY) || localStorage.getItem(STORAGE_KEY)
    if (saved && (AVAILABLE as readonly string[]).includes(saved)) {
      locale.value = saved as Locale
    }
    applyDocumentLocale(locale.value)
  }

  function t(key: string, replacements?: Record<string, string | number>): string {
    const template = resolve(messages[locale.value], key) ?? resolve(messages.en, key) ?? key
    if (!replacements) return template
    return Object.entries(replacements).reduce(
      (result, [name, value]) => result.replaceAll(`{${name}}`, String(value)),
      template,
    )
  }

  function setLocale(next: Locale) {
    if (!(AVAILABLE as readonly string[]).includes(next)) return
    locale.value = next
    if (process.client) {
      writeCookie(STORAGE_KEY, next)
      localStorage.setItem(STORAGE_KEY, next)
      applyDocumentLocale(next)
    }
  }

  return { t, locale: computed(() => locale.value), setLocale, available: AVAILABLE }
}
