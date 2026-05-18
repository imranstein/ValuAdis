<template>
  <div class="page-shell audit-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Compliance evidence</p>
        <h2 class="page-title">Audit log.</h2>
        <p class="page-subtitle">
          Review live system activity from the backend audit ledger with action, module, user, and source metadata.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadAuditLogs">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
      </div>
    </section>

    <section class="registry-toolbar panel">
      <div class="search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input v-model="searchQuery" type="search" placeholder="Search user, module, action, resource, IP" />
      </div>
      <select v-model="selectedAction" class="filter-select" aria-label="Filter by action">
        <option value="">All actions</option>
        <option v-for="action in actions" :key="action" :value="action">{{ action }}</option>
      </select>
      <select v-model="selectedModule" class="filter-select" aria-label="Filter by module">
        <option value="">All modules</option>
        <option v-for="module in modules" :key="module" :value="module">{{ module }}</option>
      </select>
      <button class="icon-button" type="button" aria-label="Reset filters" @click="resetFilters">
        <i class="pi pi-filter-slash" aria-hidden="true"></i>
      </button>
    </section>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Activity ledger</h3>
          <p class="panel-subtitle">Showing {{ filteredLogs.length }} of {{ totalRecords }} backend records</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>Audit ledger unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Action</th>
              <th>Module</th>
              <th>Resource</th>
              <th>IP address</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7">Loading audit records...</td>
            </tr>
            <tr v-else-if="filteredLogs.length === 0">
              <td colspan="7">No audit records match the current filters.</td>
            </tr>
            <tr v-for="log in filteredLogs" v-else :key="log.id">
              <td class="num">{{ log.timestamp }}</td>
              <td>
                <strong>{{ log.userName }}</strong>
                <span class="record-id">User {{ log.userId }}</span>
              </td>
              <td>
                <span class="status-pill" :class="log.actionClass">{{ log.action }}</span>
              </td>
              <td>{{ log.module }}</td>
              <td>
                <strong>{{ log.resourceType }}</strong>
                <span class="record-id">{{ log.resourceId }}</span>
              </td>
              <td class="num">{{ log.ipAddress }}</td>
              <td>
                <span class="status-pill good">{{ log.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: ['auth', 'admin'] })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const searchQuery = ref('')
const selectedAction = ref('')
const selectedModule = ref('')
const loading = ref(true)
const errorMessage = ref('')
const auditLogs = ref<any[]>([])
const totalRecords = ref(0)

const filteredLogs = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return auditLogs.value.filter((log) => {
    const matchesSearch = !q || [
      log.userName,
      log.action,
      log.module,
      log.resourceType,
      log.resourceId,
      log.ipAddress,
    ].some((value) => value.toLowerCase().includes(q))
    const matchesAction = !selectedAction.value || log.action === selectedAction.value
    const matchesModule = !selectedModule.value || log.module === selectedModule.value
    return matchesSearch && matchesAction && matchesModule
  })
})

const actions = computed(() => Array.from(new Set(auditLogs.value.map((log) => log.action))).filter(Boolean).sort())
const modules = computed(() => Array.from(new Set(auditLogs.value.map((log) => log.module))).filter(Boolean).sort())

const metrics = computed(() => [
  { label: 'Total events', value: String(totalRecords.value), note: 'Reported by audit API' },
  { label: 'Loaded window', value: String(auditLogs.value.length), note: 'Most recent records' },
  { label: 'Modules', value: String(modules.value.length), note: 'Distinct backend tables' },
  { label: 'Users', value: String(new Set(auditLogs.value.map((log) => log.userName)).size), note: 'Actors in current window' },
])

onMounted(loadAuditLogs)

async function loadAuditLogs() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(`${apiBase}/api/v1/audit/logs?limit=100`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })

    if (!response.ok) throw new Error(`Audit log request failed with ${response.status}`)

    const payload = await response.json()
    auditLogs.value = Array.isArray(payload.data) ? payload.data.map(normalizeAuditLog) : []
    totalRecords.value = Number(payload.total || auditLogs.value.length)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load audit records.'
    auditLogs.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

function normalizeAuditLog(log: any) {
  const action = String(log.action_type || 'view').toUpperCase()
  return {
    id: String(log.id),
    timestamp: formatTimestamp(log.timestamp),
    userName: log.user_name || 'System',
    userId: log.user_id ? String(log.user_id) : 'system',
    action,
    actionClass: actionClass(action),
    module: log.module || 'unknown',
    resourceType: log.resource_type || log.module || 'unknown',
    resourceId: log.resource_id ? `#${log.resource_id}` : 'Not recorded',
    ipAddress: log.ip_address || 'Not recorded',
    status: log.status || 'success',
  }
}

function formatTimestamp(value: string | null) {
  if (!value) return 'Not recorded'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-ET', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  }).format(date)
}

function actionClass(action: string) {
  if (action === 'DELETE') return 'bad'
  if (['CREATE', 'INSERT'].includes(action)) return 'good'
  if (['UPDATE', 'LOGIN'].includes(action)) return 'warn'
  return 'muted'
}

function resetFilters() {
  searchQuery.value = ''
  selectedAction.value = ''
  selectedModule.value = ''
}
</script>
