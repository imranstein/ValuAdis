<template>
  <div class="scraper-logs">
    <div class="logs-header">
      <h3>Scraping Logs</h3>
      <button class="refresh-btn" @click="$emit('refresh')">
        <i class="pi pi-refresh"></i>
        Refresh
      </button>
    </div>

    <div class="logs-table">
      <table>
        <thead>
          <tr>
            <th>Scraper</th>
            <th>Started</th>
            <th>Duration</th>
            <th>Status</th>
            <th>Found</th>
            <th>Saved</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ getScraperDomain(log.scraper_id) }}</td>
            <td>{{ formatDate(log.started_at) }}</td>
            <td>{{ calculateDuration(log.started_at, log.completed_at) }}</td>
            <td>
              <span class="status-badge" :class="log.status">
                {{ log.status || 'Unknown' }}
              </span>
            </td>
            <td>{{ log.listings_found }}</td>
            <td>{{ log.listings_saved }}</td>
            <td>
              <span v-if="log.error_message" class="error-text" :title="log.error_message">
                {{ truncateError(log.error_message) }}
              </span>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!logs || logs.length === 0" class="empty-state">
        <i class="pi pi-inbox"></i>
        <p>No scraping logs available</p>
      </div>
    </div>

    <div v-if="logs && logs.length > 0" class="pagination">
      <button @click="$emit('prev-page')" :disabled="currentPage === 1">
        <i class="pi pi-chevron-left"></i>
      </button>
      <span>Page {{ currentPage }}</span>
      <button @click="$emit('next-page')">
        <i class="pi pi-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  logs: {
    type: Array,
    default: () => []
  },
  scrapers: {
    type: Array,
    default: () => []
  },
  currentPage: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['refresh', 'prev-page', 'next-page'])

const getScraperDomain = (scraperId) => {
  const scraper = props.scrapers.find(s => s.id === scraperId)
  return scraper ? scraper.domain : `ID: ${scraperId}`
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

const calculateDuration = (start, end) => {
  if (!start || !end) return '-'
  const duration = new Date(end) - new Date(start)
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

const truncateError = (error) => {
  if (!error) return ''
  return error.length > 50 ? error.substring(0, 50) + '...' : error
}
</script>

<style scoped>
.scraper-logs {
  margin-top: 2rem;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.logs-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.logs-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

tbody tr:hover {
  background-color: #f9fafb;
}

td {
  padding: 1rem;
  color: #1f2937;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.running {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.failed {
  background: #fee2e2;
  color: #991b1b;
}

.error-text {
  color: #dc2626;
  font-size: 0.75rem;
  cursor: help;
}

.empty-state {
  padding: 3rem 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.pagination button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-weight: 500;
  color: #374151;
}
</style>
