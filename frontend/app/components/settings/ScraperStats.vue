<template>
  <div class="scraper-stats">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-globe"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_scrapers }}</h3>
          <p>Total Scrapers</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon active">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.active_scrapers }}</h3>
          <p>Active Scrapers</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-database"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatNumber(stats.total_listings) }}</h3>
          <p>Total Listings</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.avg_success_rate }}%</h3>
          <p>Success Rate</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total_scrapers: 0,
      active_scrapers: 0,
      inactive_scrapers: 0,
      total_listings: 0,
      last_24h_listings: 0,
      avg_success_rate: 0
    })
  }
})

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}
</script>

<style scoped>
.scraper-stats {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.stat-icon.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}
</style>
