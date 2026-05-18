<template>
  <div class="page-shell scrapers-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Data operations</p>
        <h1 class="page-title">Web scrapers.</h1>
        <p class="page-subtitle">Monitor public-data collection targets, source health, and imported listing records.</p>
      </div>
      <button type="button" class="btn-secondary" @click="refreshAll">
        <i class="pi pi-refresh" aria-hidden="true"></i>
        Refresh
      </button>
    </section>

    <ScraperManagement 
      :initial-scraper-type="'property'"
    />
  </div>
</template>

<script setup>
import { useNotifications } from '~/composables/useNotifications.js'
import ScraperManagement from '~/components/settings/ScraperManagement.vue'

definePageMeta({
  middleware: ['auth', 'admin'],
  title: 'Web Scrapers - ValuAdis',
  description: 'Manage Ethiopian property web scrapers and data collection'
})

const { info } = useNotifications()

const refreshAll = async () => {
  info('Use the scraper controls below to refresh the current backend view.')
}
</script>

<style scoped>
.scrapers-page {
  max-width: 1400px;
  margin: 0 auto;
  gap: 24px;
}

@media (max-width: 768px) {
  .scrapers-page .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
