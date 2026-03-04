<template>
  <div class="analytics-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Analytics</h1>
        <p>Comprehensive insights and performance metrics for property valuations</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportReport">
          <i class="pi pi-download"></i>
          Export Report
        </button>
        <button class="action-button primary" @click="refreshData">
          <i class="pi pi-refresh"></i>
          Refresh Data
        </button>
      </div>
    </div>

    <!-- Date Range Filter -->
    <div class="date-filter">
      <div class="filter-controls">
        <div class="date-range">
          <label>Date Range:</label>
          <select v-model="dateRange" class="date-select">
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        
        <div v-if="dateRange === 'custom'" class="custom-dates">
          <input type="date" v-model="customStartDate" class="date-input">
          <span>to</span>
          <input type="date" v-model="customEndDate" class="date-input">
        </div>
        
        <div class="municipality-filter">
          <label>Municipality:</label>
          <select v-model="selectedMunicipality" class="municipality-select">
            <option value="">All Municipalities</option>
            <option value="addis_ababa">Addis Ababa</option>
            <option value="dire_dawa">Dire Dawa</option>
            <option value="mekelle">Mekelle</option>
            <option value="gondar">Gondar</option>
            <option value="bahir_dar">Bahir Dar</option>
            <option value="hawassa">Hawassa</option>
            <option value="adama">Adama</option>
            <option value="jimma">Jimma</option>
            <option value="dessie">Dessie</option>
            <option value="harar">Harar</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Key Metrics Overview -->
    <div class="metrics-overview">
      <div class="metric-card">
        <div class="metric-header">
          <div class="metric-icon">
            <i class="pi pi-file-text"></i>
          </div>
          <div class="metric-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+12%</span>
          </div>
        </div>
        <div class="metric-content">
          <h3>{{ totalValuations }}</h3>
          <p>Total Valuations</p>
          <span class="metric-period">{{ selectedPeriod }}</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="metric-icon">
            <i class="pi pi-money-bill"></i>
          </div>
          <div class="metric-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+18%</span>
          </div>
        </div>
        <div class="metric-content">
          <h3>{{ formatCurrency(totalMarketValue) }}</h3>
          <p>Total Market Value</p>
          <span class="metric-period">{{ selectedPeriod }}</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="metric-icon">
            <i class="pi pi-chart-line"></i>
          </div>
          <div class="metric-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>+8%</span>
          </div>
        </div>
        <div class="metric-content">
          <h3>{{ formatCurrency(averagePropertyValue) }}</h3>
          <p>Average Property Value</p>
          <span class="metric-period">{{ selectedPeriod }}</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="metric-icon">
            <i class="pi pi-clock"></i>
          </div>
          <div class="metric-trend negative">
            <i class="pi pi-arrow-down"></i>
            <span>-5%</span>
          </div>
        </div>
        <div class="metric-content">
          <h3>{{ averageProcessingTime }} days</h3>
          <p>Avg. Processing Time</p>
          <span class="metric-period">{{ selectedPeriod }}</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <!-- Valuation Trends Chart -->
      <div class="chart-container">
        <div class="chart-header">
          <h2>Valuation Trends</h2>
          <div class="chart-controls">
            <button 
              v-for="period in trendPeriods" 
              :key="period.value"
              class="period-btn"
              :class="{ active: selectedTrendPeriod === period.value }"
              @click="selectedTrendPeriod = period.value"
            >
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div 
                v-for="(bar, index) in trendData" 
                :key="index"
                class="chart-bar"
                :style="{ height: bar.height + '%' }"
              >
                <div class="bar-tooltip">{{ bar.value }}</div>
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(label, index) in trendLabels" :key="index">{{ label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Property Type Distribution -->
      <div class="chart-container">
        <div class="chart-header">
          <h2>Property Type Distribution</h2>
          <div class="chart-legend">
            <div v-for="type in propertyTypes" :key="type.value" class="legend-item">
              <div class="legend-color" :style="{ backgroundColor: type.color }"></div>
              <span>{{ type.label }}</span>
            </div>
          </div>
        </div>
        <div class="chart-content">
          <div class="pie-chart-placeholder">
            <div class="pie-segments">
              <div 
                v-for="(segment, index) in pieSegments" 
                :key="index"
                class="pie-segment"
                :style="{ 
                  background: `conic-gradient(${segment.color} 0deg ${segment.degrees}deg, transparent ${segment.degrees}deg 360deg)`
                }"
              ></div>
            </div>
            <div class="pie-center">
              <div class="pie-total">{{ totalValuations }}</div>
              <div class="pie-label">Total</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Municipal Performance -->
      <div class="chart-container full-width">
        <div class="chart-header">
          <h2>Municipal Performance</h2>
          <div class="performance-summary">
            <span>Top Performer: {{ topPerformer }}</span>
          </div>
        </div>
        <div class="chart-content">
          <div class="municipal-bars">
            <div 
              v-for="municipal in municipalData" 
              :key="municipal.name"
              class="municipal-bar-container"
            >
              <div class="municipal-info">
                <span class="municipal-name">{{ municipal.name }}</span>
                <span class="municipal-count">{{ municipal.count }}</span>
              </div>
              <div class="municipal-bar-wrapper">
                <div 
                  class="municipal-bar"
                  :style="{ width: municipal.percentage + '%' }"
                ></div>
              </div>
              <span class="municipal-percentage">{{ municipal.percentage }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Tables -->
    <div class="tables-section">
      <!-- Recent Valuations -->
      <div class="table-container">
        <div class="table-header">
          <h2>Recent Valuations</h2>
          <button class="view-all-btn" @click="router.push('/valuations')">
            View All
            <i class="pi pi-arrow-right"></i>
          </button>
        </div>
        <div class="table-content">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Valuation ID</th>
                <th>Property Address</th>
                <th>Owner</th>
                <th>Market Value</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="valuation in recentValuations" :key="valuation.id">
                <td>
                  <span class="valuation-id">{{ valuation.valuation_id }}</span>
                </td>
                <td>{{ valuation.property_address }}</td>
                <td>{{ valuation.owner_name }}</td>
                <td class="value">{{ formatCurrency(valuation.market_value) }}</td>
                <td>
                  <span class="status-badge" :class="valuation.status">{{ getStatusLabel(valuation.status) }}</span>
                </td>
                <td>{{ formatDate(valuation.created_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Properties -->
      <div class="table-container">
        <div class="table-header">
          <h2>Highest Value Properties</h2>
          <div class="value-summary">
            <span>Total: {{ formatCurrency(topPropertiesTotal) }}</span>
          </div>
        </div>
        <div class="table-content">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Property Address</th>
                <th>Type</th>
                <th>Market Value</th>
                <th>Municipality</th>
                <th>Valuation Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(property, index) in topProperties" :key="property.id">
                <td>
                  <div class="rank-badge" :class="getRankClass(index + 1)">
                    {{ index + 1 }}
                  </div>
                </td>
                <td>{{ property.property_address }}</td>
                <td>
                  <span class="type-badge" :class="property.property_type">{{ getPropertyTypeLabel(property.property_type) }}</span>
                </td>
                <td class="value">{{ formatCurrency(property.market_value) }}</td>
                <td>{{ property.municipality }}</td>
                <td>{{ formatDate(property.created_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const dateRange = ref('30d')
const customStartDate = ref('')
const customEndDate = ref('')
const selectedMunicipality = ref('')
const selectedTrendPeriod = ref('monthly')

// Mock data
const totalValuations = ref(1247)
const totalMarketValue = ref(2847500000)
const averagePropertyValue = ref(2285000)
const averageProcessingTime = ref(3.2)

const trendPeriods = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Yearly', value: 'yearly' }
]

const propertyTypes = [
  { label: 'Residential', value: 'residential', color: '#3b82f6' },
  { label: 'Commercial', value: 'commercial', color: '#f59e0b' },
  { label: 'Industrial', value: 'industrial', color: '#8b5cf6' },
  { label: 'Agricultural', value: 'agricultural', color: '#10b981' },
  { label: 'Mixed Use', value: 'mixed_use', color: '#ef4444' }
]

const recentValuations = ref([
  {
    id: 1,
    valuation_id: 'VAL-2024-145',
    property_address: 'Bole Medhanialem, Addis Ababa',
    owner_name: 'Abebe Kebede',
    market_value: 2500000,
    status: 'approved',
    created_date: '2024-01-28'
  },
  {
    id: 2,
    valuation_id: 'VAL-2024-146',
    property_address: 'Kirkos, Addis Ababa',
    owner_name: 'Tigist Haile',
    market_value: 850000,
    status: 'pending',
    created_date: '2024-01-27'
  },
  {
    id: 3,
    valuation_id: 'VAL-2024-147',
    property_address: 'Mekelle Industrial Zone',
    owner_name: 'Dawit Mengistu',
    market_value: 4500000,
    status: 'approved',
    created_date: '2024-01-26'
  }
])

const topProperties = ref([
  {
    id: 1,
    property_address: 'Bole International Airport Area',
    property_type: 'commercial',
    market_value: 15000000,
    municipality: 'Addis Ababa',
    created_date: '2024-01-15'
  },
  {
    id: 2,
    property_address: 'Mekelle Industrial Park',
    property_type: 'industrial',
    market_value: 8500000,
    municipality: 'Mekelle',
    created_date: '2024-01-18'
  },
  {
    id: 3,
    property_address: 'Hawassa Resort Complex',
    property_type: 'commercial',
    market_value: 6200000,
    municipality: 'Hawassa',
    created_date: '2024-01-20'
  }
])

// Computed properties
const selectedPeriod = computed(() => {
  const ranges = {
    '7d': 'Last 7 Days',
    '30d': 'Last 30 Days',
    '90d': 'Last 90 Days',
    '1y': 'Last Year'
  }
  return ranges[dateRange.value] || 'Custom Range'
})

const trendData = computed(() => {
  const data = {
    daily: [
      { height: 75, value: 45 },
      { height: 60, value: 38 },
      { height: 85, value: 52 },
      { height: 70, value: 43 },
      { height: 90, value: 55 },
      { height: 80, value: 48 },
      { height: 95, value: 58 }
    ],
    weekly: [
      { height: 65, value: 180 },
      { height: 80, value: 220 },
      { height: 75, value: 205 },
      { height: 90, value: 245 }
    ],
    monthly: [
      { height: 70, value: 850 },
      { height: 85, value: 1020 },
      { height: 75, value: 920 },
      { height: 90, value: 1080 },
      { height: 80, value: 980 },
      { height: 95, value: 1150 }
    ],
    yearly: [
      { height: 60, value: 8500 },
      { height: 75, value: 10200 },
      { height: 85, value: 11500 },
      { height: 90, value: 12400 }
    ]
  }
  return data[selectedTrendPeriod.value] || data.monthly
})

const trendLabels = computed(() => {
  const labels = {
    daily: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    weekly: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    monthly: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    yearly: ['2021', '2022', '2023', '2024']
  }
  return labels[selectedTrendPeriod.value] || labels.monthly
})

const pieSegments = computed(() => {
  const total = 100
  let currentAngle = 0
  
  return propertyTypes.map((type, index) => {
    const percentages = [35, 25, 20, 15, 5] // Mock percentages
    const percentage = percentages[index]
    const degrees = (percentage / 100) * 360
    
    const segment = {
      color: type.color,
      degrees: currentAngle + degrees
    }
    
    currentAngle += degrees
    return segment
  })
})

const municipalData = computed(() => [
  { name: 'Addis Ababa', count: 523, percentage: 42 },
  { name: 'Dire Dawa', count: 187, percentage: 15 },
  { name: 'Mekelle', count: 224, percentage: 18 },
  { name: 'Bahir Dar', count: 149, percentage: 12 },
  { name: 'Hawassa', count: 87, percentage: 7 },
  { name: 'Others', count: 77, percentage: 6 }
])

const topPerformer = computed(() => 'Addis Ababa')

const topPropertiesTotal = computed(() => 
  topProperties.value.reduce((sum, prop) => sum + prop.market_value, 0)
)

// Methods
function formatCurrency(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatDate(date) {
  return new Date(date).toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function getStatusLabel(status) {
  const labels = {
    draft: 'Draft',
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected',
    expired: 'Expired'
  }
  return labels[status] || status
}

function getPropertyTypeLabel(type) {
  const labels = {
    residential: 'Residential',
    commercial: 'Commercial',
    industrial: 'Industrial',
    agricultural: 'Agricultural',
    mixed_use: 'Mixed Use'
  }
  return labels[type] || type
}

function getRankClass(rank) {
  if (rank === 1) return 'gold'
  if (rank === 2) return 'silver'
  if (rank === 3) return 'bronze'
  return 'standard'
}

function exportReport() {
  console.log('Exporting analytics report...')
}

function refreshData() {
  console.log('Refreshing analytics data...')
}

onMounted(() => {
  console.log('Analytics page mounted')
})
</script>

<style scoped>
/* Analytics Container */
.analytics-container {
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

/* Date Filter */
.date-filter {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.filter-controls {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
}

.date-range label,
.municipality-filter label {
  font-weight: 600;
  color: #374151;
  margin-right: 0.5rem;
}

.date-select,
.municipality-select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 0.875rem;
}

.custom-dates {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
}

/* Metrics Overview */
.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-icon {
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

.metric-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.metric-trend.positive {
  background: #dcfce7;
  color: #16a34a;
}

.metric-trend.negative {
  background: #fef2f2;
  color: #dc2626;
}

.metric-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.metric-content p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 0.25rem 0;
}

.metric-period {
  color: #94a3b8;
  font-size: 0.75rem;
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.chart-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.period-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

.chart-legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.performance-summary {
  font-size: 0.875rem;
  color: #64748b;
}

.chart-content {
  padding: 2rem;
}

/* Chart Placeholders */
.chart-placeholder {
  height: 300px;
  position: relative;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  margin-bottom: 1rem;
}

.chart-bar {
  width: 40px;
  background: linear-gradient(135deg, #059669, #047857);
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: all 0.3s;
}

.chart-bar:hover {
  opacity: 0.8;
}

.bar-tooltip {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s;
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  font-size: 0.75rem;
  color: #64748b;
}

/* Pie Chart */
.pie-chart-placeholder {
  height: 300px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-segments {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  position: relative;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.pie-total {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.pie-label {
  font-size: 0.75rem;
  color: #64748b;
}

/* Municipal Performance */
.municipal-bars {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.municipal-bar-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.municipal-info {
  min-width: 120px;
}

.municipal-name {
  display: block;
  font-weight: 500;
  color: #1e293b;
}

.municipal-count {
  font-size: 0.75rem;
  color: #64748b;
}

.municipal-bar-wrapper {
  flex: 1;
  height: 24px;
  background: #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.municipal-bar {
  height: 100%;
  background: linear-gradient(135deg, #059669, #047857);
  border-radius: 12px;
  transition: width 0.5s ease;
}

.municipal-percentage {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: #059669;
}

/* Tables Section */
.tables-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.table-container {
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
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.table-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.view-all-btn:hover {
  border-color: #059669;
  color: #059669;
}

.value-summary {
  font-size: 0.875rem;
  color: #64748b;
}

.table-content {
  overflow-x: auto;
}

.analytics-table {
  width: 100%;
  border-collapse: collapse;
}

.analytics-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.analytics-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.valuation-id {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #059669;
}

.value {
  font-weight: 600;
  color: #1e293b;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.approved {
  background: #bbf7d0;
  color: #059669;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.rejected {
  background: #fecaca;
  color: #dc2626;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.type-badge.residential {
  background: #dbeafe;
  color: #1e40af;
}

.type-badge.commercial {
  background: #fed7aa;
  color: #c2410c;
}

.type-badge.industrial {
  background: #e9d5ff;
  color: #7c3aed;
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.rank-badge.standard {
  background: #6b7280;
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
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .metrics-overview {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .tables-section {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>
