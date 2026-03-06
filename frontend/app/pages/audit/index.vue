<template>
  <div class="audit-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Audit Log</h1>
        <p>Track system activities, user actions, and security events</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportAuditLog">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button class="action-button primary" @click="refreshLogs">
          <i class="pi pi-refresh"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-row">
        <div class="form-field">
          <label>Date Range</label>
          <select v-model="filters.dateRange">
            <option value="today">Today</option>
            <option value="week">Last 7 Days</option>
            <option value="month">Last 30 Days</option>
            <option value="quarter">Last 90 Days</option>
            <option value="year">Last Year</option>
          </select>
        </div>
        
        <div class="form-field">
          <label>Action Type</label>
          <select v-model="filters.actionType">
            <option value="">All Actions</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="export">Export</option>
          </select>
        </div>
        
        <div class="form-field">
          <label>User</label>
          <input type="text" v-model="filters.user" placeholder="Search user..." />
        </div>
        
        <div class="form-field">
          <label>Module</label>
          <select v-model="filters.module">
            <option value="">All Modules</option>
            <option value="users">Users</option>
            <option value="properties">Properties</option>
            <option value="valuations">Valuations</option>
            <option value="settings">Settings</option>
            <option value="reports">Reports</option>
          </select>
        </div>
        
        <button class="reset-button" @click="resetFilters">
          <i class="pi pi-refresh"></i>
          Reset
        </button>
      </div>
    </div>

    <!-- Statistics -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-list"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalLogs }}</h3>
          <p>Total Activities</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ userActivities }}</h3>
          <p>User Actions</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-shield"></i>
        </div>
        <div class="stat-content">
          <h3>{{ securityEvents }}</h3>
          <p>Security Events</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ criticalEvents }}</h3>
          <p>Critical Events</p>
        </div>
      </div>
    </div>

    <!-- Audit Table -->
    <div class="audit-table-container">
      <div class="table-header">
        <h2>Audit Trail</h2>
        <div class="table-info">
          <span>{{ filteredLogs.length }} records</span>
        </div>
      </div>

      <div class="table-container">
        <table class="audit-table">
          <thead>
            <tr>
              <th @click="sortBy('timestamp')">
                Timestamp
                <i class="pi" :class="getSortIcon('timestamp')"></i>
              </th>
              <th @click="sortBy('user')">
                User
                <i class="pi" :class="getSortIcon('user')"></i>
              </th>
              <th @click="sortBy('action')">
                Action
                <i class="pi" :class="getSortIcon('action')"></i>
              </th>
              <th @click="sortBy('module')">
                Module
                <i class="pi" :class="getSortIcon('module')"></i>
              </th>
              <th @click="sortBy('resource')">
                Resource
                <i class="pi" :class="getSortIcon('resource')"></i>
              </th>
              <th @click="sortBy('ip_address')">
                IP Address
                <i class="pi" :class="getSortIcon('ip_address')"></i>
              </th>
              <th @click="sortBy('status')">
                Status
                <i class="pi" :class="getSortIcon('status')"></i>
              </th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in paginatedLogs" :key="log.id">
              <td>
                <span class="timestamp">{{ formatDateTime(log.timestamp) }}</span>
              </td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">{{ getInitials(log.user_name) }}</div>
                  <span>{{ log.user_name }}</span>
                </div>
              </td>
              <td>
                <span class="action-badge" :class="log.action_type">{{ getActionLabel(log.action_type) }}</span>
              </td>
              <td>
                <span class="module-badge">{{ getModuleLabel(log.module) }}</span>
              </td>
              <td>
                <span class="resource-info">{{ log.resource_type }}: {{ log.resource_id }}</span>
              </td>
              <td>
                <span class="ip-address">{{ log.ip_address }}</span>
              </td>
              <td>
                <span class="status-badge" :class="log.status">{{ getStatusLabel(log.status) }}</span>
              </td>
              <td>
                <button class="detail-btn" @click="showLogDetails(log)">
                  <i class="pi pi-eye"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="filteredLogs.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="pi pi-list"></i>
        </div>
        <h3>No audit records found</h3>
        <p>Try adjusting your filters or check back later</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredLogs.length > itemsPerPage" class="pagination">
      <div class="pagination-info">
        <span>Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredLogs.length) }} of {{ filteredLogs.length }} records</span>
      </div>
      <div class="pagination-controls">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <i class="pi pi-chevron-left"></i>
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <i class="pi pi-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Log Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Audit Log Details</h3>
          <button class="modal-close" @click="closeModal">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>Timestamp:</label>
              <span>{{ formatDateTime(selectedLog.timestamp) }}</span>
            </div>
            <div class="detail-item">
              <label>User:</label>
              <span>{{ selectedLog.user_name }}</span>
            </div>
            <div class="detail-item">
              <label>Action:</label>
              <span class="action-badge" :class="selectedLog.action_type">{{ getActionLabel(selectedLog.action_type) }}</span>
            </div>
            <div class="detail-item">
              <label>Module:</label>
              <span>{{ getModuleLabel(selectedLog.module) }}</span>
            </div>
            <div class="detail-item">
              <label>Resource:</label>
              <span>{{ selectedLog.resource_type }}: {{ selectedLog.resource_id }}</span>
            </div>
            <div class="detail-item">
              <label>IP Address:</label>
              <span>{{ selectedLog.ip_address }}</span>
            </div>
            <div class="detail-item">
              <label>User Agent:</label>
              <span>{{ selectedLog.user_agent }}</span>
            </div>
            <div class="detail-item">
              <label>Status:</label>
              <span class="status-badge" :class="selectedLog.status">{{ getStatusLabel(selectedLog.status) }}</span>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>Description</h4>
            <p>{{ selectedLog.description }}</p>
          </div>
          
          <div class="detail-section" v-if="selectedLog.changes">
            <h4>Changes Made</h4>
            <pre class="changes-json">{{ JSON.stringify(selectedLog.changes, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive data
const filters = ref({
  dateRange: 'week',
  actionType: '',
  user: '',
  module: ''
})

const sortField = ref('timestamp')
const sortDirection = ref('desc')
const currentPage = ref(1)
const itemsPerPage = ref(20)
const showModal = ref(false)
const selectedLog = ref(null)

// Real audit logs from API
const auditLogs = ref([])

// Computed properties
const filteredLogs = computed(() => {
  let filtered = auditLogs.value

  // Apply date range filter
  if (filters.value.dateRange) {
    const now = new Date()
    let startDate
    
    switch (filters.value.dateRange) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        break
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case 'quarter':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
      case 'year':
        startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
        break
    }
    
    filtered = filtered.filter(log => new Date(log.timestamp) >= startDate)
  }

  // Apply other filters
  if (filters.value.actionType) {
    filtered = filtered.filter(log => log.action_type === filters.value.actionType)
  }

  if (filters.value.user) {
    const query = filters.value.user.toLowerCase()
    filtered = filtered.filter(log => 
      log.user_name.toLowerCase().includes(query)
    )
  }

  if (filters.value.module) {
    filtered = filtered.filter(log => log.module === filters.value.module)
  }

  // Sort
  filtered.sort((a, b) => {
    let aVal = a[sortField.value]
    let bVal = b[sortField.value]
    
    if (sortField.value === 'timestamp') {
      aVal = new Date(aVal)
      bVal = new Date(bVal)
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return filtered
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredLogs.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredLogs.value.length / itemsPerPage.value)
})

const totalLogs = computed(() => auditLogs.value.length)
const userActivities = computed(() => auditLogs.value.filter(log => log.user_id > 0).length)
const securityEvents = computed(() => auditLogs.value.filter(log => log.module === 'auth' || log.action_type === 'delete').length)
const criticalEvents = computed(() => auditLogs.value.filter(log => log.status === 'failed' || log.action_type === 'delete').length)

// Methods
function sortBy(field) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

function getSortIcon(field) {
  if (sortField.value !== field) return 'pi-sort'
  return sortDirection.value === 'asc' ? 'pi-sort-up' : 'pi-sort-down'
}

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function getActionLabel(action) {
  const labels = {
    create: 'Create',
    update: 'Update',
    delete: 'Delete',
    login: 'Login',
    logout: 'Logout',
    export: 'Export',
    view: 'View',
    download: 'Download'
  }
  return labels[action] || action
}

function getModuleLabel(module) {
  const labels = {
    users: 'Users',
    properties: 'Properties',
    valuations: 'Valuations',
    settings: 'Settings',
    reports: 'Reports',
    auth: 'Authentication'
  }
  return labels[module] || module
}

function getStatusLabel(status) {
  const labels = {
    success: 'Success',
    failed: 'Failed',
    pending: 'Pending',
    warning: 'Warning'
  }
  return labels[status] || status
}

function formatDateTime(timestamp) {
  return new Date(timestamp).toLocaleString('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function resetFilters() {
  filters.value = {
    dateRange: 'week',
    actionType: '',
    user: '',
    module: ''
  }
  currentPage.value = 1
}

function showLogDetails(log) {
  selectedLog.value = log
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedLog.value = null
}

async function refreshLogs() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch('http://localhost:8020/api/v1/audit/logs', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      auditLogs.value = data.data || []
    } else {
      console.error('Failed to load audit logs from API')
      auditLogs.value = []
    }
  } catch (error) {
    console.error('Error loading audit logs:', error)
    auditLogs.value = []
  }
}

function exportAuditLog() {
  const dataStr = JSON.stringify(filteredLogs.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `audit-log-${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

onMounted(() => {
  refreshLogs()
})
</script>

<style scoped>
/* Audit Container */
.audit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.header-content p {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button.primary {
  background: white;
  color: #059669;
}

.action-button.primary:hover {
  background: #f8fafc;
  transform: translateY(-2px);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Filters */
.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: end;
  flex-wrap: wrap;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.form-field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-field input,
.form-field select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
}

.reset-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  height: fit-content;
}

.reset-button:hover {
  background: #f8fafc;
  border-color: #059669;
  color: #059669;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.stat-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* Audit Table */
.audit-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #f1f5f9;
}

.table-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.table-info span {
  color: #64748b;
  font-size: 0.875rem;
}

.table-container {
  overflow-x: auto;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
}

.audit-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  user-select: none;
}

.audit-table th:hover {
  background: #f1f5f9;
}

.audit-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.timestamp {
  font-family: 'Courier New', monospace;
  color: #64748b;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #059669;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.action-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.action-badge.create {
  background: #dcfce7;
  color: #059669;
}

.action-badge.update {
  background: #dbeafe;
  color: #1e40af;
}

.action-badge.delete {
  background: #fecaca;
  color: #dc2626;
}

.action-badge.login {
  background: #e0f2fe;
  color: #0369a1;
}

.action-badge.export {
  background: #fef3c7;
  color: #d97706;
}

.module-badge {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.resource-info {
  color: #374151;
}

.ip-address {
  font-family: 'Courier New', monospace;
  color: #64748b;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.success {
  background: #bbf7d0;
  color: #059669;
}

.status-badge.failed {
  background: #fecaca;
  color: #dc2626;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.detail-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.detail-btn:hover {
  background: #6b7280;
  color: white;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 2rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: white;
  border-top: 1px solid #f1f5f9;
}

.pagination-info {
  color: #64748b;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e5e7eb;
}

.modal-body {
  padding: 2rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.detail-item span {
  font-size: 0.875rem;
  color: #1e293b;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.75rem 0;
}

.detail-section p {
  color: #64748b;
  line-height: 1.5;
  margin: 0;
}

.changes-json {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 1rem;
  font-size: 0.75rem;
  color: #374151;
  overflow-x: auto;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .filter-row {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
