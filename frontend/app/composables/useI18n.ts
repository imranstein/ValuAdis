import { ref, computed } from 'vue'
import en from '~/locales/en.json'
import am from '~/locales/am.json'

/**
 * Lightweight i18n (U9). English is the default; Amharic content lives in
 * locales/am.json. A single reactive locale is shared app-wide and persisted
 * per device. t('nav.dashboard') resolves a dot path in the active locale,
 * falling back to English and finally the key itself, so a missing Amharic
 * string degrades to English rather than blank.
 */
type Dict = Record<string, unknown>
const messages: Record<string, Dict> = { en, am }
const AVAILABLE = ['en', 'am'] as const
export type Locale = (typeof AVAILABLE)[number]
const STORAGE_KEY = 'valuadis_locale'

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

export function useI18n() {
  if (!restored && process.client) {
    restored = true
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && (AVAILABLE as readonly string[]).includes(saved)) {
      locale.value = saved as Locale
    }
  }

  function t(key: string): string {
    return resolve(messages[locale.value], key) ?? resolve(messages.en, key) ?? key
  }

  function setLocale(next: Locale) {
    if (!(AVAILABLE as readonly string[]).includes(next)) return
    locale.value = next
    if (process.client) localStorage.setItem(STORAGE_KEY, next)
  }

  return { t, locale: computed(() => locale.value), setLocale, available: AVAILABLE }
}
