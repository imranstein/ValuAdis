<template>
  <div class="page-shell dashboard-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Command ledger</p>
        <h2 class="page-title">Valuation operations at a glance.</h2>
        <p class="page-subtitle">
          Monitor record readiness, valuation throughput, asset coverage, and compliance posture from one desk view.
        </p>
      </div>
      <div class="page-actions">
        <NuxtLink to="/properties/create" class="btn-secondary">
          <i class="pi pi-plus" aria-hidden="true"></i>
          New property
        </NuxtLink>
        <NuxtLink to="/valuations/quick" class="btn-primary">
          <i class="pi pi-bolt" aria-hidden="true"></i>
          Quick valuation
        </NuxtLink>
      </div>
    </section>

    <section class="metric-grid" aria-label="Dashboard metrics">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="automation-panel panel" aria-label="AI automation status">
      <div class="panel-head">
        <div>
          <h3 class="panel-title">AI automation desk</h3>
          <p class="panel-subtitle">Prediction, review learning, and compliance signals</p>
        </div>
        <NuxtLink to="/properties/create" class="btn-ghost">Run assessment</NuxtLink>
      </div>
      <div class="automation-grid">
        <article v-for="item in aiAutomation" :key="item.label" class="automation-item">
          <p>{{ item.label }}</p>
          <strong>{{ item.value }}</strong>
          <span>{{ item.note }}</span>
        </article>
      </div>
    </section>

    <section class="dashboard-grid">
      <article class="panel trend-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Valuation trend</h3>
            <p class="panel-subtitle">Last six operating periods</p>
          </div>
          <select v-model="timeRange" class="period-select" aria-label="Select trend range">
            <option>Last 6 Months</option>
            <option>Last Year</option>
          </select>
        </div>
        <div class="bar-chart" aria-label="Valuation trend chart">
          <div v-for="(height, index) in chartData" :key="months[index]" class="bar-column">
            <div class="bar-track">
              <span class="bar-fill" :style="{ height: `${height}%` }"></span>
            </div>
            <span>{{ months[index] }}</span>
          </div>
        </div>
      </article>

      <article class="panel distribution-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Asset distribution</h3>
            <p class="panel-subtitle">Current registry mix</p>
          </div>
        </div>
        <div class="distribution-ring" aria-hidden="true">
          <svg viewBox="0 0 42 42">
            <circle class="ring-track" cx="21" cy="21" r="15.9" fill="none" stroke-width="6"></circle>
            <circle class="ring-seg-a" cx="21" cy="21" r="15.9" fill="none" stroke-width="6" stroke-dasharray="42 100"></circle>
            <circle class="ring-seg-b" cx="21" cy="21" r="15.9" fill="none" stroke-width="6" stroke-dasharray="31 100" stroke-dashoffset="-42"></circle>
            <circle class="ring-seg-c" cx="21" cy="21" r="15.9" fill="none" stroke-width="6" stroke-dasharray="27 100" stroke-dashoffset="-73"></circle>
          </svg>
          <div>
            <strong>{{ formatCount(totalAssets) }}</strong>
            <span>Total assets</span>
          </div>
        </div>
        <div class="distribution-list">
          <div v-for="item in distribution" :key="item.label" class="distribution-item">
            <span :style="{ background: item.color }"></span>
            <p>{{ item.label }}</p>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Recent valuations</h3>
          <p class="panel-subtitle">Latest records that need operational attention</p>
        </div>
        <NuxtLink to="/valuations" class="btn-ghost">View all</NuxtLink>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Asset</th>
              <th>Type</th>
              <th>Status</th>
              <th class="text-right">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="recentValuationsLoading">
              <td colspan="5" class="empty-cell">Loading recent valuation records...</td>
            </tr>
            <tr v-else-if="recentValuations.length === 0">
              <td colspan="5" class="empty-cell">
                {{ recentValuationsError || 'No valuation records are available from the backend yet.' }}
              </td>
            </tr>
            <tr v-for="valuation in recentValuations" v-else :key="valuation.id">
              <td class="record-id">#{{ valuation.id }}</td>
              <td>
                <strong>{{ valuation.name }}</strong>
                <span>{{ valuation.location }}</span>
              </td>
              <td>{{ valuation.type }}</td>
              <td>
                <span class="status-pill" :class="statusClass(valuation.status)">
                  {{ valuation.status }}
                </span>
              </td>
              <td class="text-right num">{{ formatCurrency(valuation.value) }}</td>
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

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const stats = ref({
  totalProperties: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  propertyTrend: 0,
  valuationTrend: 0
})

const vehicleStats = ref({
  totalVehicles: 0,
  totalValuations: 0,
  totalMarketValue: 0
})

const aiTrustMetrics = ref({
  trustScore: 75,
  totalReviews: 0
})

const marketInsight = ref({
  forecast: 'Loading',
  opportunities: 0
})

const complianceRate = ref('98.2%')
const timeRange = ref('Last 6 Months')
const chartData = ref([38, 52, 44, 68, 83, 64])
const months = ref(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN'])
const recentValuations = ref<RecentValuation[]>([])
const recentValuationsLoading = ref(true)
const recentValuationsError = ref('')

interface RecentValuation {
  id: string
  name: string
  location: string
  type: string
  status: string
  value: number
}

const totalAssets = computed(() => stats.value.totalProperties + vehicleStats.value.totalVehicles)

const metrics = computed(() => [
  {
    label: 'Total properties',
    value: formatCount(stats.value.totalProperties),
    note: `${formatSigned(stats.value.propertyTrend)}% month over month`
  },
  {
    label: 'Fleet assets',
    value: formatCount(vehicleStats.value.totalVehicles),
    note: 'Vehicle registry coverage'
  },
  {
    label: 'Valuations',
    value: formatCount(stats.value.totalValuations),
    note: `${formatSigned(stats.value.valuationTrend)}% active period`
  },
  {
    label: 'Compliance',
    value: complianceRate.value,
    note: 'Audit package completeness'
  }
])

const distribution = [
  { label: 'Residential', value: '42%', color: 'var(--green)' },
  { label: 'Commercial', value: '31%', color: 'var(--blue)' },
  { label: 'Industrial', value: '27%', color: 'var(--gold-bright)' }
]

const aiAutomation = computed(() => [
  {
    label: 'AI trust score',
    value: `${Math.round(aiTrustMetrics.value.trustScore)}%`,
    note: `${formatCount(aiTrustMetrics.value.totalReviews)} reviewer decisions learned`
  },
  {
    label: 'Market forecast',
    value: marketInsight.value.forecast,
    note: `${formatCount(marketInsight.value.opportunities)} monitored opportunities`
  },
  {
    label: 'Automation mode',
    value: 'Human-in-loop',
    note: 'AI estimates require reviewer confirmation'
  }
])

onMounted(async () => {
  await Promise.all([loadDashboardStats(), loadVehicleStats(), loadAiAutomation(), loadRecentValuations()])
})

async function loadDashboardStats() {
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/analytics/dashboard?period=month`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) return

    const data = await response.json()
    stats.value = {
      totalProperties: data.properties?.total ?? 0,
      totalValuations: data.valuations?.total ?? 0,
      totalMarketValue: data.financials?.total_market_value ?? 0,
      propertyTrend: Math.round(data.properties?.growth_rate ?? 0),
      valuationTrend: Math.round(data.valuations?.growth_rate ?? 0)
    }
    if (data.compliance) {
      complianceRate.value = `${Math.round(data.compliance.compliance_rate ?? 98.2)}%`
    }
  } catch {
  }
}

async function loadVehicleStats() {
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/vehicles/statistics/summary`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) return

    const data = await response.json()
    vehicleStats.value = {
      totalVehicles: data.total_vehicles ?? 0,
      totalValuations: data.total_valuations ?? 0,
      totalMarketValue: data.total_market_value ?? 0
    }
  } catch {
  }
}

async function loadAiAutomation() {
  await Promise.all([loadTrustMetrics(), loadMarketInsights()])
}

async function loadRecentValuations() {
  recentValuationsLoading.value = true
  recentValuationsError.value = ''
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/valuations/?skip=0&limit=5`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) {
      recentValuationsError.value = 'Recent valuations could not be loaded from the backend.'
      return
    }

    const payload = await response.json()
    const records = Array.isArray(payload.data) ? payload.data : []
    recentValuations.value = records.map(mapRecentValuation)
  } catch {
    recentValuationsError.value = 'Recent valuations could not be loaded from the backend.'
  } finally {
    recentValuationsLoading.value = false
  }
}

function mapRecentValuation(record: Record<string, any>): RecentValuation {
  return {
    id: String(record.id),
    name: record.property?.address || `Property ${record.property_id}`,
    location: record.property?.municipality || record.municipality || 'Municipality unavailable',
    type: formatPropertyType(record.property?.property_type || record.property_type),
    status: formatStatus(record.status),
    value: Number(record.market_value || 0)
  }
}

async function loadTrustMetrics() {
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/valuation-feedback/metrics`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!response.ok) return

    const data = await response.json()
    aiTrustMetrics.value = {
      trustScore: data.trust_score ?? 75,
      totalReviews: data.total_reviews ?? 0
    }
  } catch {
  }
}

async function loadMarketInsights() {
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/analytics/market-insights`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) return

    const data = await response.json()
    marketInsight.value = {
      forecast: data.forecast?.medium_term_outlook ?? 'Available',
      opportunities: data.ethiopian_context?.market_opportunities?.length ?? 0
    }
  } catch {
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value || 0)
}

function formatCount(value: number) {
  return new Intl.NumberFormat('en-US').format(value || 0)
}

function formatSigned(value: number) {
  return value > 0 ? `+${value}` : `${value}`
}

function formatPropertyType(value?: string) {
  if (!value) return 'Unclassified'
  return value
    .split('_')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function formatStatus(value?: string) {
  return formatPropertyType(value || 'draft')
}

function statusClass(status: string) {
  const normalized = status.toLowerCase()
  if (normalized === 'completed' || normalized === 'approved') return 'good'
  if (normalized === 'pending' || normalized === 'in progress' || normalized === 'draft') return 'warn'
  return ''
}
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.85fr);
  gap: var(--space-4);
}

/* AI automation desk — dark ledger panel */
.automation-panel {
  margin-bottom: var(--space-4);
  border-color: var(--shell-line);
  background:
    linear-gradient(rgba(241, 238, 224, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(241, 238, 224, 0.018) 1px, transparent 1px),
    var(--shell-bg);
  background-size: 44px 44px, 44px 44px, auto;
  color: var(--shell-ink);
}

.automation-panel .panel-title {
  color: var(--shell-ink);
}

.automation-panel .panel-subtitle {
  color: var(--shell-muted);
}

.automation-panel .btn-ghost {
  border: 1px solid var(--shell-line);
  color: var(--shell-ink);
}

.automation-panel .btn-ghost:hover {
  background: var(--shell-bg-raised);
}

.automation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  border-top: 1px solid var(--shell-line);
  background: var(--shell-line);
}

.automation-item {
  min-height: 124px;
  padding: var(--space-4);
  background: var(--shell-bg-raised);
}

.automation-item p {
  margin: 0 0 var(--space-3);
  color: var(--shell-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.automation-item strong {
  display: block;
  color: var(--shell-gold);
  font-family: var(--mono);
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.1;
}

.automation-item span {
  display: block;
  margin-top: var(--space-3);
  color: var(--shell-ink);
  font-size: 13px;
}

.period-select {
  min-height: 40px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink-soft);
  padding: 0 var(--space-3);
}

.bar-chart {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  align-items: end;
  gap: 16px;
  height: 280px;
  padding-top: 8px;
}

.bar-column {
  height: 100%;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 10px;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 800;
  text-align: center;
}

.bar-track {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-2);
}

.bar-fill {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  border-top: 2px solid var(--gold-bright);
  background: var(--green);
}

.distribution-panel {
  display: flex;
  flex-direction: column;
}

.distribution-ring {
  position: relative;
  width: 220px;
  margin: 4px auto 20px;
}

.distribution-ring svg {
  width: 220px;
  height: 220px;
  transform: rotate(-90deg);
}

.ring-track {
  stroke: var(--surface-3);
}

.ring-seg-a {
  stroke: var(--green);
}

.ring-seg-b {
  stroke: var(--blue);
}

.ring-seg-c {
  stroke: var(--gold-bright);
}

.distribution-ring div {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
}

.distribution-ring strong {
  font-family: var(--mono);
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.distribution-ring span {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.distribution-list {
  display: grid;
  gap: 10px;
  margin-top: auto;
}

.distribution-item {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 10px;
  color: var(--ink-soft);
  font-size: 14px;
}

.distribution-item span {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.distribution-item p {
  margin: 0;
}

.distribution-item strong {
  font-family: var(--mono);
  font-size: 12px;
}

.table-panel {
  overflow: hidden;
}

.table-head {
  margin: 0;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--line);
}

.record-id {
  color: var(--green);
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
}

.data-table td strong,
.data-table td span {
  display: block;
}

.data-table td span:not(.status-pill) {
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
}

.empty-cell {
  padding: var(--space-6);
  color: var(--muted);
  text-align: center;
}

@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .automation-grid {
    grid-template-columns: 1fr;
  }

  .bar-chart {
    gap: 8px;
    height: 220px;
  }
}
</style>
