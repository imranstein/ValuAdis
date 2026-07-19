<template>
  <div class="lang-switcher" role="group" :aria-label="t('rentals.switcher.label')">
    <button
      v-for="option in available"
      :key="option"
      type="button"
      class="lang-option"
      :class="{ active: locale === option }"
      :aria-pressed="locale === option"
      @click="setLocale(option)"
    >
      {{ option === 'am' ? t('rentals.switcher.am') : t('rentals.switcher.en') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '~/composables/useI18n'

const { t, locale, setLocale, available } = useI18n()
</script>

<style scoped>
.lang-switcher {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 2px;
}

.lang-option {
  min-height: 30px;
  border: 0;
  border-radius: calc(var(--radius) - 2px);
  background: transparent;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0 10px;
  cursor: pointer;
  transition: background-color var(--duration-fast) var(--ease), color var(--duration-fast) var(--ease);
}

.lang-option:hover {
  color: var(--ink);
}

.lang-option.active {
  background: var(--green);
  color: var(--surface);
}
</style>
