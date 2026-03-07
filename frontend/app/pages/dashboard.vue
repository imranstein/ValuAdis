<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <div class="welcome-header">
      <div class="welcome-content">
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
        <div class="stat-icon">
          <i class="pi pi-building"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalProperties }}</h3>
          <p>Total Properties</p>
          <span class="stat-trend positive" v-if="stats.propertyTrend > 0">
            <i class="pi pi-arrow-up"></i> {{ stats.propertyTrend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-car"></i>
        </div>
        <div class="stat-content">
          <h3>{{ vehicleStats.totalVehicles }}</h3>
          <p>Total Vehicles</p>
          <span class="stat-trend positive" v-if="vehicleStats.trend > 0">
            <i class="pi pi-arrow-up"></i> {{ vehicleStats.trend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-calculator"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalValuations }}</h3>
          <p>Total Valuations</p>
          <span class="stat-trend positive" v-if="stats.valuationTrend > 0">
            <i class="pi pi-arrow-up"></i> {{ stats.valuationTrend }}% from last month
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatCurrency(stats.totalMarketValue + vehicleStats.totalMarketValue) }}</h3>
          <p>Total Market Value</p>
          <span class="stat-trend positive" v-if="stats.marketValueTrend > 0">
            <i class="pi pi-arrow-up"></i> {{ stats.marketValueTrend }}% growth
          </span>
          <span class="stat-trend neutral" v-else>—</span>
        </div>
      </div>

      <div class="stat-card">
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
          <h2>Recent Properties</h2>
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
            <p>No properties yet. <NuxtLink to="/properties/create">Add your first property</NuxtLink></p>
          </div>
        </div>
      </div>

      <!-- Recent Vehicles -->
      <div class="content-card">
        <div class="card-header">
          <h2>Recent Vehicles</h2>
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
            <p>No vehicles yet. <NuxtLink to="/vehicles/create">Add your first vehicle</NuxtLink></p>
          </div>
        </div>
      </div>

      <!-- Valuation Activity -->
      <div class="content-card">
        <div class="card-header">
          <h2>Valuation Activity</h2>
          <div class="activity-filters">
            <button class="filter-btn active">Today</button>
            <button class="filter-btn">Week</button>
            <button class="filter-btn">Month</button>
          </div>
        </div>
        <div class="activity-chart">
          <div class="chart-placeholder">
            <i class="pi pi-chart-bar"></i>
            <p>Valuation trends chart</p>
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
    </div>

    <!-- Compliance Status -->
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
    const response = await fetch(`${apiBase}/api/v1/vehicles?limit=5`, {
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
.dashboard-container { max-width: 1400px; margin: 0 auto; padding: 0; }
.welcome-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #059669 0%, #047857 100%); border-radius: 16px; color: white; box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2); }
.welcome-content h1 { font-size: 2rem; font-weight: 700; margin: 0 0 0.5rem 0; }
.welcome-content p { font-size: 1.125rem; opacity: 0.9; margin: 0; }
.welcome-actions { display: flex; gap: 1rem; }
.action-button { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.action-button.primary { background: white; color: #059669; }
.action-button.primary:hover { background: #f8fafc; transform: translateY(-2px); }
.action-button.secondary { background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); }
.action-button.secondary:hover { background: rgba(255, 255, 255, 0.3); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; margin-bottom: 1rem; }
.stat-card:nth-child(1) .stat-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
.stat-card:nth-child(2) .stat-icon { background: linear-gradient(135deg, #10b981, #059669); color: white; }
.stat-card:nth-child(3) .stat-icon { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
.stat-card:nth-child(4) .stat-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; }
.stat-content h3 { font-size: 2rem; font-weight: 700; color: #1e293b; margin: 0 0 0.25rem 0; }
.stat-content p { color: #64748b; font-size: 0.875rem; margin: 0 0 0.75rem 0; }
.stat-trend { display: flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 600; }
.stat-trend.positive { color: #10b981; }
.stat-trend.neutral { color: #64748b; }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
.content-card { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; overflow: hidden; }
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid #e2e8f0; }
.card-header h2 { font-size: 1.25rem; font-weight: 600; color: #1e293b; margin: 0; }
.view-all-btn { display: flex; align-items: center; gap: 0.5rem; background: none; border: 1px solid #e2e8f0; color: #64748b; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; }
.view-all-btn:hover { background: #f8fafc; border-color: #cbd5e1; }
.recent-properties, .recent-vehicles { padding: 1.5rem; }
.property-item, .vehicle-item { display: flex; align-items: center; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid #f1f5f9; }
.property-item:last-child, .vehicle-item:last-child { border-bottom: none; }
.property-icon, .vehicle-icon { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.property-icon { background: #f8fafc; color: #64748b; }
.vehicle-icon { background: #fef3c7; color: #d97706; }
.property-info, .vehicle-info { flex: 1; }
.property-info h4, .vehicle-info h4 { font-size: 0.875rem; font-weight: 600; color: #1e293b; margin: 0 0 0.25rem 0; }
.property-info p, .vehicle-info p { font-size: 0.75rem; color: #64748b; margin: 0 0 0.25rem 0; }
.property-value { font-size: 0.875rem; font-weight: 600; color: #059669; }
.vehicle-value { font-size: 0.875rem; font-weight: 600; color: #d97706; }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.status-badge.completed { background: #dcfce7; color: #166534; }
.status-badge.in-progress { background: #fef3c7; color: #92400e; }
.status-badge.pending { background: #f1f5f9; color: #475569; }
.status-badge.compliant { background: #dcfce7; color: #166534; }
.empty-state { padding: 2rem; text-align: center; color: #64748b; font-size: 0.9rem; }
.empty-state a { color: #059669; text-decoration: none; }
.empty-state a:hover { text-decoration: underline; }
.activity-filters { display: flex; gap: 0.5rem; }
.filter-btn { padding: 0.5rem 1rem; border: 1px solid #e2e8f0; background: white; color: #64748b; border-radius: 6px; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; }
.filter-btn.active { background: #059669; color: white; border-color: #059669; }
.activity-chart { padding: 1.5rem; height: 200px; }
.chart-placeholder { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f8fafc; border-radius: 8px; color: #64748b; }
.activity-summary { display: flex; justify-content: space-around; padding: 1rem 1.5rem; border-top: 1px solid #f1f5f9; }
.summary-item { text-align: center; }
.summary-label { display: block; font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem; }
.summary-value { font-size: 1.25rem; font-weight: 700; color: #1e293b; }
.compliance-section { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
.compliance-card { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; }
.compliance-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.compliance-icon { width: 48px; height: 48px; background: linear-gradient(135deg, #059669, #047857); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem; }
.compliance-metrics { display: flex; justify-content: space-around; }
.metric-value { font-size: 2rem; font-weight: 700; color: #059669; margin-bottom: 0.25rem; }
.metric-label { font-size: 0.875rem; color: #64748b; }
.quick-actions-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; }
.quick-actions-card h3 { font-size: 1.125rem; font-weight: 600; color: #1e293b; margin: 0 0 1.5rem 0; }
.quick-actions-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.quick-action-btn { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; color: #64748b; cursor: pointer; transition: all 0.2s; }
.quick-action-btn:hover { background: #f1f5f9; border-color: #cbd5e1; color: #475569; }
@media (max-width: 1024px) { .content-grid { grid-template-columns: 1fr; } .compliance-section { grid-template-columns: 1fr; } .welcome-header { flex-direction: column; gap: 1.5rem; text-align: center; } .welcome-actions { justify-content: center; } }
@media (max-width: 768px) { .stats-grid { grid-template-columns: 1fr; } .quick-actions-grid { grid-template-columns: 1fr; } .compliance-metrics { flex-direction: column; gap: 1rem; } .activity-summary { flex-direction: column; gap: 1rem; } }
</style>
