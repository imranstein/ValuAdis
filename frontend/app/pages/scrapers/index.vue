<template>
  <div class="scrapers-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>🕷️ Web Scrapers</h1>
        <p>Manage Ethiopian property data collection and automated scraping</p>
      </div>
      <div class="header-actions">
        <button @click="refreshAll" class="btn-secondary">
          <i class="pi pi-refresh"></i>
          Refresh All
        </button>
      </div>
    </div>

    <!-- Scraper Management Component -->
    <ScraperManagement 
      :initial-scraper-type="'property'"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useNotifications } from '~/composables/useNotifications.js'
import ScraperManagement from '~/components/settings/ScraperManagement.vue'

// Page metadata
definePageMeta({
  title: 'Web Scrapers - ValuAdis',
  description: 'Manage Ethiopian property web scrapers and data collection'
})

// Notifications
const { success, error, warning, info } = useNotifications()

// Methods
const refreshAll = async () => {
  info('Refreshing all scraper data...')
  // The ScraperManagement component handles its own refresh
}

// Lifecycle
onMounted(() => {
  success('Web Scrapers page loaded')
})
</script>

<style scoped>
.scrapers-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
}

.header-content p {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
  max-width: 600px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
}
</style>
