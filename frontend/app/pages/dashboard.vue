<template>
  <div class="dashboard-container">

    <!-- Welcome Header -->
    <div class="welcome-header">
      <div class="welcome-content">
        <div class="system-live-badge">
          <span class="pulse-dot"></span>
          <span class="live-text">System Live</span>
        </div>
        <h1>Welcome back, {{ userName || 'Admin' }}</h1>
        <p>Here's what's happening with your property and vehicle valuations today.</p>
      </div>
      <div class="welcome-actions">
        <button class="action-button primary" @click="router.push('/properties/create')">
          <i class="pi pi-plus"></i>
          New Property
        </button>
        <button class="action-button secondary" @click="router.push('/vehicles/create')">
          <i class="pi pi-plus"></i>
          Add Vehicle
        </button>
        <button class="action-button secondary" @click="router.push('/valuations/quick')">
          <i class="pi pi-bolt"></i>
          Quick Valuation
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-building"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalProperties }}</h3>
          <p>Total Properties</p>
          <span class="stat-trend positive" v-if="stats.propertyTrend > 0">
            ↑ {{ stats.propertyTrend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-car"></i>
        </div>
        <div class="stat-content">
          <h3>{{ vehicleStats.totalVehicles }}</h3>
          <p>Total Vehicles</p>
          <span class="stat-trend positive" v-if="vehicleStats.trend > 0">
            ↑ {{ vehicleStats.trend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-calculator"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalValuations }}</h3>
          <p>Total Valuations</p>
          <span class="stat-trend positive" v-if="stats.valuationTrend > 0">
            ↑ {{ stats.valuationTrend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatCurrency(stats.totalMarketValue + vehicleStats.totalMarketValue) }}</h3>
          <p>Total Market Value</p>
          <span class="stat-trend positive" v-if="stats.marketValueTrend > 0">
            ↑ {{ stats.marketValueTrend }}% growth
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ complianceRate }}%</h3>
          <p>Compliance Rate</p>
          <span class="stat-trend neutral">—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-top-border"></div>
        <div class="stat-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.pendingValuations + vehicleStats.pendingValuations }}</h3>
          <p>Pending Review</p>
          <span class="stat-trend neutral">—</span>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Recent Properties -->
      <div class="content-card">
        <div class="card-header">
          <h2><span class="card-accent-bar"></span>Recent Properties</h2>
          <button class="view-all-btn" @click="router.push('/properties')">
            View All
            <i class="pi pi-arrow-right"></i>
          </button>
        </div>
        <div class="recent-properties">
          <div v-for="prop in recentProperties" :key="prop.id" class="property-item">
            <div class="property-icon">
              <i class="pi pi-home"></i>
            </div>
            <div class="property-info">
              <h4>{{ prop.address || prop.property_ref || 'Property' }}</h4>
              <p>{{ prop.municipality || '—' }} • {{ formatPropertyType(prop.property_type) }}</p>
              <span class="property-value">{{ formatCurrency(prop.market_value) }}</span>
            </div>
            <div class="property-status">
              <span class="status-badge" :class="getStatusClass(prop.status)">{{ prop.status || '—' }}</span>
            </div>
          </div>
          <div v-if="recentProperties.length === 0" class="empty-state">
            <i class="pi pi-inbox empty-icon"></i>
            <p>No properties yet. <NuxtLink to="/properties/create">Add your first property</NuxtLink></p>
          </div>
        </div>
      </div>

      <!-- Recent Vehicles -->
      <div class="content-card">
        <div class="card-header">
          <h2><span class="card-accent-bar"></span>Recent Vehicles</h2>
          <button class="view-all-btn" @click="router.push('/vehicles')">
            View All
            <i class="pi pi-arrow-right"></i>
          </button>
        </div>
        <div class="recent-vehicles">
          <div v-for="vehicle in recentVehicles" :key="vehicle.id" class="vehicle-item">
            <div class="vehicle-icon">
              <i class="pi pi-car"></i>
            </div>
            <div class="vehicle-info">
              <h4>{{ vehicle.make }} {{ vehicle.model }} {{ vehicle.year }}</h4>
              <p>{{ vehicle.region || '—' }} • {{ vehicle.body_type || '—' }} • {{ vehicle.plate_number || '—' }}</p>
              <span class="vehicle-value">{{ formatCurrency(vehicle.market_value) }}</span>
            </div>
            <div class="vehicle-status">
              <span class="status-badge" :class="getStatusClass(vehicle.valuation_status)">{{ vehicle.valuation_status || '—' }}</span>
            </div>
          </div>
          <div v-if="recentVehicles.length === 0" class="empty-state">
            <i class="pi pi-inbox empty-icon"></i>
            <p>No vehicles yet. <NuxtLink to="/vehicles/create">Add your first vehicle</NuxtLink></p>
          </div>
        </div>
      </div>

      <!-- Valuation Activity -->
      <div class="content-card">
        <div class="card-header">
          <h2><span class="card-accent-bar"></span>Valuation Activity</h2>
          <div class="activity-filters">
            <button class="filter-btn active">Today</button>
            <button class="filter-btn">Week</button>
            <button class="filter-btn">Month</button>
          </div>
        </div>
        <div class="activity-chart">
          <Chart v-if="valuationChartData" type="bar" :data="valuationChartData" :options="chartOptions" style="height: 180px" />
          <div v-else class="chart-placeholder">
            <i class="pi pi-chart-bar"></i>
            <p>Loading chart...</p>
          </div>
        </div>
        <div class="activity-summary">
          <div class="summary-item">
            <span class="summary-label">Completed Today</span>
            <span class="summary-value">{{ activitySummary.completedToday }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">In Progress</span>
            <span class="summary-value">{{ activitySummary.inProgress }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Pending Review</span>
            <span class="summary-value">{{ activitySummary.pendingReview }}</span>
          </div>
        </div>
      </div>

      <!-- Property Type Distribution -->
      <div v-if="propertyTypeChartData" class="content-card">
        <div class="card-header">
          <h2><span class="card-accent-bar"></span>Property Types</h2>
          <button class="view-all-btn" @click="router.push('/analytics')">
            View Analytics
            <i class="pi pi-arrow-right"></i>
          </button>
        </div>
        <div class="chart-widget">
          <Chart type="doughnut" :data="propertyTypeChartData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 180px" />
        </div>
      </div>
    </div>

    <!-- Compliance + Quick Actions -->
    <div class="compliance-section">
      <div class="compliance-card">
        <div class="compliance-header">
          <div class="compliance-icon">
            <i class="pi pi-shield"></i>
          </div>
          <div class="compliance-info">
            <h3>Proclamation 1365/2025 Compliant</h3>
            <p>All valuations follow Ethiopian government regulations</p>
          </div>
          <div class="compliance-status">
            <span class="status-badge compliant">Fully Compliant</span>
          </div>
        </div>
        <div class="compliance-metrics">
          <div class="metric-item">
            <div class="metric-value">25%</div>
            <div class="metric-label">Tax Rate Applied</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">100%</div>
            <div class="metric-label">Audit Ready</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ complianceIssues }}</div>
            <div class="metric-label">Compliance Issues</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions-card">
        <h3>Quick Actions</h3>
        <div class="quick-actions-grid">
          <button class="quick-action-btn" @click="router.push('/properties')">
            <i class="pi pi-list"></i>
            <span>All Properties</span>
          </button>
          <button class="quick-action-btn" @click="router.push('/valuations')">
            <i class="pi pi-file-pdf"></i>
            <span>Generate Reports</span>
          </button>
          <button class="quick-action-btn" @click="router.push('/analytics')">
            <i class="pi pi-chart-pie"></i>
            <span>View Analytics</span>
          </button>
          <button class="quick-action-btn" @click="router.push('/settings')">
            <i class="pi pi-cog"></i>
            <span>Settings</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const authStore = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8020'

const userName = computed(() => authStore.userName || authStore.user?.full_name || 'Admin')

const stats = ref({
  totalProperties: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0,
  propertyTrend: 0,
  valuationTrend: 0,
  marketValueTrend: 0,
  systemStatus: 'Live'
})

const vehicleStats = ref({
  totalVehicles: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0,
  trend: 0
})

const recentProperties = ref([])
const recentVehicles = ref([])
const activitySummary = ref({
  completedToday: 0,
  inProgress: 0,
  pendingReview: 0
})
const complianceIssues = ref(0)
const complianceRate = ref(0)
const valuationChartData = ref(null)
const propertyTypeChartData = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: { beginAtZero: true }
  }
}

function setComplianceRate(rate) {
  complianceRate.value = Math.round(rate ?? 0)
}

onMounted(async () => {
  await Promise.all([
    loadDashboardStats(),
    loadRecentProperties(),
    loadRecentVehicles(),
    loadVehicleStats(),
    loadActivitySummary()
  ])
})

async function loadDashboardStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/analytics/dashboard?period=month`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) {
      const errBody = await response.text()
      throw new Error(errBody || `HTTP ${response.status}`)
    }
    const data = await response.json()
    stats.value = {
      totalProperties: data.properties?.total ?? 0,
      totalValuations: data.valuations?.total ?? 0,
      totalMarketValue: data.financials?.total_market_value ?? 0,
      pendingValuations: 0,
      propertyTrend: Math.round(data.properties?.growth_rate ?? 0),
      valuationTrend: Math.round(data.valuations?.growth_rate ?? 0),
      marketValueTrend: Math.round(data.financials?.market_value_growth ?? 0),
      systemStatus: 'Live'
    }
    if (data.compliance) {
      setComplianceRate(data.compliance.compliance_rate)
      complianceIssues.value = 0
    }
    if (data.property_types && Object.keys(data.property_types).length > 0) {
      propertyTypeChartData.value = {
        labels: Object.keys(data.property_types).map((k) => k.replace(/_/g, ' ')),
        datasets: [{ data: Object.values(data.property_types), backgroundColor: ['#00d4ff', '#7b2fff', '#e8a020', '#00e676', '#94a3b8'] }]
      }
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
    stats.value = { ...stats.value, systemStatus: 'Error' }
  }
}

async function loadRecentProperties() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/properties?limit=5`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const json = await response.json()
    recentProperties.value = json.data || []
  } catch (error) {
    console.error('Failed to load recent properties:', error)
    recentProperties.value = []
  }
}

async function loadRecentVehicles() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/vehicles/?limit=5`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) return
    const json = await response.json()
    recentVehicles.value = json.data || json.vehicles || []
  } catch {
    recentVehicles.value = []
  }
}

async function loadVehicleStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/vehicles/statistics/summary`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) return
    const data = await response.json()
    vehicleStats.value = {
      totalVehicles: data.total_vehicles ?? 0,
      totalValuations: data.total_valuations ?? 0,
      totalMarketValue: data.total_market_value ?? 0,
      pendingValuations: data.pending_valuations ?? 0,
      trend: 0
    }
  } catch {
    vehicleStats.value = {
      totalVehicles: 0,
      totalValuations: 0,
      totalMarketValue: 0,
      pendingValuations: 0,
      trend: 0
    }
  }
}

async function loadActivitySummary() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/valuations?limit=100`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) return
    const json = await response.json()
    const items = json.data || []
    const today = new Date().toISOString().slice(0, 10)
    activitySummary.value = {
      completedToday: items.filter((v) => v.status === 'approved' && String(v.valuation_date || '').startsWith(today)).length,
      inProgress: items.filter((v) => v.status === 'in_progress' || v.status === 'draft').length,
      pendingReview: items.filter((v) => v.status === 'pending').length
    }
    const labels = []
    const counts = []
    const now = new Date()
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      const dayStr = d.toISOString().slice(0, 10)
      labels.push(d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }))
      counts.push(items.filter((v) => String(v.valuation_date || v.created_at || '').startsWith(dayStr)).length)
    }
    valuationChartData.value = {
      labels,
      datasets: [{ label: 'Valuations', data: counts, backgroundColor: '#00d4ff', borderRadius: 4 }]
    }
  } catch {
    activitySummary.value = { completedToday: 0, inProgress: 0, pendingReview: 0 }
  }
}

function formatCurrency(value) {
  if (value == null || isNaN(value)) return 'ETB 0'
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatPropertyType(type) {
  if (!type) return '—'
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function getStatusClass(status) {
  if (!status) return 'pending'
  const s = (status || '').toLowerCase()
  if (s === 'approved' || s === 'completed' || s === 'active') return 'completed'
  if (s === 'in_progress' || s === 'draft') return 'in-progress'
  return 'pending'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ─── Custom Properties ─────────────────────────────────────── */
.dashboard-container {
  --bg-void:       #08080f;
  --surface:       rgba(15, 15, 26, 0.8);
  --surface-hover: rgba(20, 20, 38, 0.9);
  --cyan:          #00d4ff;
  --gold:          #F59E0B;
  --violet:        #1E3A8A;
  --success:       #00e676;
  --text:          #e2e8f0;
  --muted:         #94a3b8;
  --primary:       #078160;
  --border:        rgba(7, 129, 96, 0.12);
  --border-hover:  rgba(7, 129, 96, 0.35);
  --glow-cyan:     0 0 20px rgba(0, 212, 255, 0.25);
  --glow-gold:     0 0 20px rgba(245, 158, 11, 0.25);
  --glow-primary:  0 0 20px rgba(7, 129, 96, 0.25);
  --spacing-xs:    0.25rem;
  --spacing-sm:    0.5rem;
  --spacing-md:    1rem;
  --spacing-lg:    1.5rem;
  --spacing-xl:    2rem;
  --spacing-2xl:   3rem;

  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 1.5rem 2.5rem;
  font-family: 'Inter', sans-serif;
  color: var(--text);
}

/* ─── Keyframes ─────────────────────────────────────────────── */
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.6); }
  50%       { opacity: 0.8; transform: scale(1.15); box-shadow: 0 0 0 6px rgba(0, 230, 118, 0); }
}

@keyframes card-glow {
  0%   { box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4), 0 0 0 1px var(--border); }
  100% { box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5), var(--glow-cyan), 0 0 0 1px rgba(0, 212, 255, 0.35); }
}

@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

/* ─── Welcome Header ────────────────────────────────────────── */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 2.5rem 3rem;
  background: linear-gradient(135deg, rgba(7, 129, 96, 0.08), rgba(30, 58, 138, 0.08));
  border: 1px solid rgba(7, 129, 96, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(7, 129, 96, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.welcome-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.03) 0%,
    transparent 50%,
    rgba(123, 47, 255, 0.03) 100%
  );
  pointer-events: none;
}

.system-live-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 0.25rem 0.75rem;
  background: rgba(0, 230, 118, 0.08);
  border: 1px solid rgba(0, 230, 118, 0.25);
  border-radius: 999px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse-dot 2s ease-in-out infinite;
  flex-shrink: 0;
}

.live-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--success);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.welcome-content h1 {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, var(--text) 0%, var(--cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.welcome-content p {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  color: var(--muted);
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.action-button.primary {
  background: var(--cyan);
  color: #08080f;
  border: 1px solid var(--cyan);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.25);
}

.action-button.primary:hover {
  background: #1ad9ff;
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.35);
  transform: translateY(-1px);
}

.action-button.secondary {
  background: rgba(7, 129, 96, 0.08);
  color: var(--cyan);
  border: 1px solid rgba(7, 129, 96, 0.2);
}

.action-button.secondary:hover {
  background: rgba(7, 129, 96, 0.15);
  border-color: rgba(7, 129, 96, 0.3);
  box-shadow: 0 4px 12px rgba(7, 129, 96, 0.15);
  transform: translateY(-1px);
}

/* ─── Stats Grid ─────────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 3rem;
}

.stat-card {
  position: relative;
  background: var(--surface);
  border-radius: 14px;
  padding: 1.5rem;
  border: 1px solid var(--border);
  backdrop-filter: blur(12px);
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.08);
}

.stat-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: radial-gradient(circle at 80% 20%, rgba(0, 212, 255, 0.04), transparent 60%);
  pointer-events: none;
}

.stat-card:hover {
  animation: card-glow 0.3s forwards;
  transform: translateY(-3px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 212, 255, 0.25);
}

.stat-top-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 14px 14px 0 0;
  background: linear-gradient(90deg, var(--primary), var(--gold), var(--cyan));
  box-shadow: var(--glow-primary);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.stat-card:nth-child(1) .stat-icon { background: rgba(0, 212, 255, 0.12); color: var(--cyan); }
.stat-card:nth-child(2) .stat-icon { background: rgba(0, 230, 118, 0.12); color: var(--success); }
.stat-card:nth-child(3) .stat-icon { background: rgba(232, 160, 32, 0.12); color: var(--gold); }
.stat-card:nth-child(4) .stat-icon { background: rgba(123, 47, 255, 0.12); color: var(--violet); }
.stat-card:nth-child(5) .stat-icon { background: rgba(0, 212, 255, 0.12); color: var(--cyan); }
.stat-card:nth-child(6) .stat-icon { background: rgba(232, 160, 32, 0.12); color: var(--gold); }

.stat-content h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--cyan);
  margin: 0 0 0.25rem 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.stat-content p {
  font-family: 'DM Sans', sans-serif;
  color: var(--muted);
  font-size: 0.8rem;
  font-weight: 500;
  margin: 0 0 0.6rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.stat-trend.positive {
  color: var(--success);
  background: rgba(0, 230, 118, 0.1);
}

.stat-trend.neutral {
  color: var(--muted);
  background: rgba(148, 163, 184, 0.08);
}

/* ─── Content Grid ───────────────────────────────────────────── */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.content-card {
  background: var(--surface);
  border-radius: 14px;
  border: 1px solid var(--border);
  backdrop-filter: blur(12px);
  overflow: hidden;
  transition: border-color 0.3s ease;
}

.content-card:hover {
  border-color: rgba(0, 212, 255, 0.25);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.card-header h2 {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.card-accent-bar {
  display: inline-block;
  width: 3px;
  height: 16px;
  background: linear-gradient(180deg, var(--cyan), var(--violet));
  border-radius: 2px;
  flex-shrink: 0;
}

.view-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.2);
  color: var(--cyan);
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: rgba(0, 212, 255, 0.12);
  border-color: var(--cyan);
  box-shadow: var(--glow-cyan);
}

/* ─── Property / Vehicle Items ───────────────────────────────── */
.recent-properties,
.recent-vehicles {
  padding: 0.75rem 1.5rem 1.25rem;
}

.property-item,
.vehicle-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 0.75rem;
  border-radius: 8px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.06);
  transition: background 0.2s ease;
}

.property-item:last-child,
.vehicle-item:last-child {
  border-bottom: none;
}

.property-item:hover,
.vehicle-item:hover {
  background: rgba(0, 212, 255, 0.04);
}

.property-icon,
.vehicle-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.property-icon {
  background: rgba(0, 212, 255, 0.1);
  color: var(--cyan);
}

.vehicle-icon {
  background: rgba(232, 160, 32, 0.1);
  color: var(--gold);
}

.property-info,
.vehicle-info {
  flex: 1;
  min-width: 0;
}

.property-info h4,
.vehicle-info h4 {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 0.2rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.property-info p,
.vehicle-info p {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.73rem;
  color: var(--muted);
  margin: 0 0 0.25rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.property-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--gold);
}

.vehicle-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--cyan);
}

/* ─── Status Badges ──────────────────────────────────────────── */
.status-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.status-badge.completed {
  background: rgba(0, 230, 118, 0.15);
  color: var(--success);
  border: 1px solid rgba(0, 230, 118, 0.3);
}

.status-badge.in-progress {
  background: rgba(232, 160, 32, 0.15);
  color: var(--gold);
  border: 1px solid rgba(232, 160, 32, 0.3);
}

.status-badge.pending {
  background: rgba(0, 212, 255, 0.1);
  color: var(--cyan);
  border: 1px solid rgba(0, 212, 255, 0.25);
}

.status-badge.compliant {
  background: rgba(0, 230, 118, 0.15);
  color: var(--success);
  border: 1px solid rgba(0, 230, 118, 0.3);
  font-size: 0.75rem;
  padding: 0.3rem 0.85rem;
}

/* ─── Empty State ────────────────────────────────────────────── */
.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.875rem;
}

.empty-icon {
  display: block;
  font-size: 2rem;
  color: rgba(148, 163, 184, 0.3);
  margin-bottom: 0.75rem;
}

.empty-state a {
  color: var(--cyan);
  text-decoration: none;
}

.empty-state a:hover {
  text-decoration: underline;
}

/* ─── Activity / Chart ───────────────────────────────────────── */
.activity-filters {
  display: flex;
  gap: 0.4rem;
}

.filter-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 5px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
}

.filter-btn.active {
  background: rgba(0, 212, 255, 0.12);
  color: var(--cyan);
  border-color: rgba(0, 212, 255, 0.35);
}

.filter-btn:hover:not(.active) {
  color: var(--text);
  border-color: rgba(0, 212, 255, 0.2);
}

.activity-chart {
  padding: 1.25rem 1.5rem;
  height: 220px;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.03);
  border-radius: 8px;
  color: var(--muted);
  gap: 0.5rem;
  border: 1px dashed var(--border);
}

.chart-placeholder i {
  font-size: 1.5rem;
  color: rgba(0, 212, 255, 0.3);
}

.chart-widget {
  padding: 1.25rem 1.5rem;
}

.activity-summary {
  display: flex;
  justify-content: space-around;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border);
  background: rgba(0, 212, 255, 0.02);
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}

.summary-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--cyan);
}

/* ─── Compliance Section ─────────────────────────────────────── */
.compliance-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.compliance-card {
  background: var(--surface);
  border-radius: 14px;
  padding: 2rem;
  border: 1px solid rgba(232, 160, 32, 0.2);
  backdrop-filter: blur(12px);
  box-shadow: 0 0 30px rgba(232, 160, 32, 0.06), inset 0 1px 0 rgba(232, 160, 32, 0.1);
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s ease;
}

.compliance-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--gold));
  box-shadow: var(--glow-primary);
}

.compliance-card:hover {
  border-color: rgba(232, 160, 32, 0.35);
  box-shadow: 0 0 40px rgba(232, 160, 32, 0.1), var(--glow-gold);
}

.compliance-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.compliance-icon {
  width: 48px;
  height: 48px;
  background: rgba(232, 160, 32, 0.12);
  border: 1px solid rgba(232, 160, 32, 0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold);
  font-size: 1.3rem;
  flex-shrink: 0;
  box-shadow: var(--glow-gold);
}

.compliance-info {
  flex: 1;
}

.compliance-info h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 0.25rem 0;
}

.compliance-info p {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0;
}

.compliance-metrics {
  display: flex;
  justify-content: space-around;
}

.metric-item {
  text-align: center;
  padding: 1rem 1.5rem;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid var(--border);
  border-radius: 10px;
  min-width: 120px;
}

.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--success);
  margin-bottom: 0.35rem;
  line-height: 1;
}

.metric-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ─── Quick Actions ──────────────────────────────────────────── */
.quick-actions-card {
  background: var(--surface);
  border-radius: 14px;
  padding: 1.5rem;
  border: 1px solid var(--border);
  backdrop-filter: blur(12px);
  transition: border-color 0.3s ease;
}

.quick-actions-card:hover {
  border-color: rgba(0, 212, 255, 0.2);
}

.quick-actions-card h3 {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 1.25rem 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.75rem;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.25s ease;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
}

.quick-action-btn i {
  font-size: 1.1rem;
  color: rgba(0, 212, 255, 0.5);
  transition: color 0.25s ease;
}

.quick-action-btn:hover {
  background: rgba(0, 212, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
  color: var(--cyan);
  box-shadow: var(--glow-cyan);
  transform: translateY(-2px);
}

.quick-action-btn:hover i {
  color: var(--cyan);
}

/* ─── Responsive ─────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .compliance-section {
    grid-template-columns: 1fr;
  }

  .welcome-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
    align-items: center;
  }

  .welcome-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .compliance-metrics {
    gap: 0.75rem;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .compliance-metrics {
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .activity-summary {
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
  }

  .welcome-header {
    padding: 1.5rem;
  }

  .welcome-content h1 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .welcome-actions {
    flex-direction: column;
    width: 100%;
  }

  .action-button {
    justify-content: center;
  }
}
</style>
