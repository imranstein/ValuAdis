<template>
  <div class="scraper-table">
    <table>
      <thead>
        <tr>
          <th>Domain</th>
          <th>Status</th>
          <th>Schedule</th>
          <th>Last Run</th>
          <th>Listings</th>
          <th>Success Rate</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="scraper in scrapers" :key="scraper.id">
          <td>
            <div class="domain-cell">
              <i class="pi pi-globe"></i>
              <span>{{ scraper.domain }}</span>
            </div>
          </td>
          <td>
            <span class="status-badge" :class="scraper.enabled ? 'active' : 'inactive'">
              {{ scraper.enabled ? 'Active' : 'Inactive' }}
            </span>
          </td>
          <td>{{ scraper.schedule }}</td>
          <td>{{ formatDate(scraper.last_run) }}</td>
          <td>{{ formatNumber(scraper.total_listings) }}</td>
          <td>
            <span class="status-badge" :class="getStatusClass(scraper.last_status)">
              {{ scraper.last_status || 'N/A' }}
            </span>
          </td>
          <td>
            <div class="action-buttons">
              <button 
                class="action-btn" 
                @click="$emit('toggle', scraper.id)"
                :title="scraper.enabled ? 'Disable' : 'Enable'"
              >
                <i :class="scraper.enabled ? 'pi pi-pause' : 'pi pi-play'"></i>
              </button>
              <button 
                class="action-btn" 
                @click="$emit('test', scraper.id)"
                title="Test Scraper"
              >
                <i class="pi pi-bolt"></i>
              </button>
              <button 
                class="action-btn" 
                @click="$emit('run', scraper.id)"
                title="Run Now"
              >
                <i class="pi pi-refresh"></i>
              </button>
              <button 
                class="action-btn" 
                @click="$emit('edit', scraper)"
                title="Edit"
              >
                <i class="pi pi-pencil"></i>
              </button>
              <button 
                class="action-btn delete" 
                @click="$emit('delete', scraper.id)"
                title="Delete"
              >
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!scrapers || scrapers.length === 0" class="empty-state">
      <i class="pi pi-inbox"></i>
      <h3>No scrapers configured</h3>
      <p>Add your first scraper to start collecting property listings</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  scrapers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['toggle', 'test', 'run', 'edit', 'delete'])

const formatDate = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num || 0)
}

const getStatusClass = (status) => {
  if (!status) return 'neutral'
  if (status === 'success') return 'success'
  if (status === 'running') return 'running'
  return 'error'
}
</script>

<style scoped>
.scraper-table {
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
  transition: background-color 0.2s;
}

tbody tr:hover {
  background-color: #f9fafb;
}

td {
  padding: 1rem;
  color: #1f2937;
}

.domain-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.domain-cell i {
  color: #059669;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.running {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.error {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.neutral {
  background: #f3f4f6;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #059669;
  color: white;
}

.action-btn.delete:hover {
  background: #dc2626;
  color: white;
}

.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  font-size: 4rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: #374151;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}
</style>
