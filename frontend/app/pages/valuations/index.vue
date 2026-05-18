<template>
  <div class="page-shell valuations-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Valuation ledger</p>
        <h2 class="page-title">Appraisal history.</h2>
        <p class="page-subtitle">
          Review backend valuation records, compliance posture, and exportable appraisal evidence.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" :disabled="exporting" @click="exportValuations">
          <i class="pi pi-download" aria-hidden="true"></i>
          {{ exporting ? 'Exporting' : 'Export CSV' }}
        </button>
        <NuxtLink to="/valuations/quick" class="btn-primary">
          <i class="pi pi-bolt" aria-hidden="true"></i>
          Quick valuation
        </NuxtLink>
      </div>
    </section>

    <section class="metric-grid" aria-label="Valuation metrics">
      <article class="metric-card">
        <p class="metric-label">Total market value</p>
        <p class="metric-value">{{ formatCompactCurrency(totalMarketValue) }}</p>
        <p class="metric-note">{{ valuations.length }} records loaded from API</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Compliance rate</p>
        <p class="metric-value">{{ complianceRate }}%</p>
        <p class="metric-note">Approved valuation share</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Pending appraisals</p>
        <p class="metric-value">{{ pendingCount }}</p>
        <p class="metric-note">Pending or draft records</p>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Appraisal ledger</h3>
          <p class="panel-subtitle">{{ ledgerStatus }}</p>
        </div>
        <label class="search-field">
          <i class="pi pi-search" aria-hidden="true"></i>
          <input v-model="searchQuery" type="search" placeholder="Search valuation, type, municipality, or status" />
        </label>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Valuation</th>
              <th>Asset type</th>
              <th>Municipality</th>
              <th>Status</th>
              <th class="text-right">Market value</th>
              <th class="text-right">Taxable value</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="empty-cell">Loading valuation records...</td>
            </tr>
            <tr v-else-if="loadError">
              <td colspan="6" class="empty-cell">{{ loadError }}</td>
            </tr>
            <tr v-else-if="filteredValuations.length === 0">
              <td colspan="6" class="empty-cell">No valuations match the current search.</td>
            </tr>
            <tr v-for="valuation in filteredValuations" v-else :key="valuation.id">
              <td class="record-id">#{{ valuation.id }}</td>
              <td>{{ valuation.type }}</td>
              <td>{{ valuation.location }}</td>
              <td>
                <span class="status-pill" :class="valuation.statusClass">{{ valuation.status }}</span>
              </td>
              <td class="text-right num">{{ valuation.value }}</td>
              <td class="text-right num">{{ valuation.taxableValue }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-footer">
        <span>Showing {{ filteredValuations.length }} of {{ valuations.length }} backend appraisals</span>
        <span>{{ exportStatus }}</span>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

interface ValuationRow {
  id: string
  type: string
  location: string
  value: string
  taxableValue: string
  rawMarketValue: number
  rawStatus: string
  status: string
  statusClass: string
}

const searchQuery = ref('')
const loading = ref(true)
const exporting = ref(false)
const loadError = ref('')
const exportStatus = ref('Ready')
const valuations = ref<ValuationRow[]>([])
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const filteredValuations = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return valuations.value
  return valuations.value.filter((valuation) =>
    [valuation.id, valuation.type, valuation.location, valuation.status]
      .some((value) => String(value).toLowerCase().includes(query))
  )
})

const totalMarketValue = computed(() => valuations.value.reduce((sum, valuation) => sum + valuation.rawMarketValue, 0))
const approvedCount = computed(() => valuations.value.filter((valuation) => valuation.rawStatus === 'approved').length)
const pendingCount = computed(() => valuations.value.filter((valuation) => ['pending', 'draft'].includes(valuation.rawStatus)).length)
const complianceRate = computed(() => {
  if (valuations.value.length === 0) return 0
  return Math.round((approvedCount.value / valuations.value.length) * 100)
})
const ledgerStatus = computed(() => {
  if (loading.value) return 'Loading backend valuation records'
  if (loadError.value) return 'Backend valuation records unavailable'
  return 'Backend valuation records'
})

onMounted(loadValuations)

async function loadValuations() {
  loading.value = true
  loadError.value = ''
  try {
    const response = await fetch(`${apiBase}/api/v1/valuations/`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) {
      loadError.value = 'Valuation records could not be loaded from the backend.'
      return
    }
    const json = await response.json()
    const rows = Array.isArray(json.data) ? json.data : []
    valuations.value = rows.map(normalizeValuation)
  } catch {
    loadError.value = 'Valuation records could not be loaded from the backend.'
  } finally {
    loading.value = false
  }
}

function normalizeValuation(valuation: Record<string, any>): ValuationRow {
  const status = String(valuation.status || 'draft').toLowerCase()
  return {
    id: String(valuation.id),
    type: labelize(valuation.property_type || valuation.property?.property_type || 'property'),
    location: valuation.municipality || valuation.property?.municipality || 'Unassigned municipality',
    value: formatCurrency(Number(valuation.market_value || 0)),
    taxableValue: formatCurrency(Number(valuation.taxable_value || 0)),
    rawMarketValue: Number(valuation.market_value || 0),
    rawStatus: status,
    status: labelize(status),
    statusClass: status === 'approved' ? 'good' : status === 'rejected' ? 'error' : 'warn',
  }
}

async function exportValuations() {
  exporting.value = true
  exportStatus.value = 'Exporting CSV'
  try {
    const response = await fetch(`${apiBase}/api/v1/valuations/export?format=csv`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) throw new Error('Valuation export failed')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'valuations_export.csv'
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
    exportStatus.value = 'CSV exported'
  } catch {
    exportStatus.value = 'CSV export failed'
  } finally {
    exporting.value = false
  }
}

function labelize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}

function formatCompactCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(Number(value || 0))
}

useHead({
  title: 'Valuations - ValuAdis',
  meta: [{ name: 'description', content: 'Backend-backed property valuation ledger.' }],
})
</script>

<style scoped>
.table-head {
  align-items: center;
  margin: 0;
  padding: 20px 22px;
  border-bottom: 1px solid var(--line);
}

.search-field {
  position: relative;
  width: min(360px, 100%);
}

.search-field i {
  position: absolute;
  top: 50%;
  left: 12px;
  color: var(--muted);
  transform: translateY(-50%);
}

.search-field input {
  min-height: 40px;
  width: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink);
  padding: 0 12px 0 38px;
}

.empty-cell {
  color: var(--muted);
  padding: 24px;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
  padding: 14px 22px;
}

@media (max-width: 720px) {
  .table-head,
  .table-footer {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
