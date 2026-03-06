<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <div class="welcome-header">
      <div class="welcome-content">
        <h1>Welcome back, Admin</h1>
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
      <!-- Property Stats -->
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-building"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalProperties }}</h3>
          <p>Total Properties</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 12% from last month
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-car"></i>
        </div>
        <div class="stat-content">
          <h3>{{ vehicleStats.totalVehicles }}</h3>
          <p>Total Vehicles</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 8% from last month
          </span>
        </div>
      </div>

      <!-- Valuation Stats -->
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-calculator"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalValuations }}</h3>
          <p>Total Valuations</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 8% from last month
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-chart-line"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatCurrency(stats.totalMarketValue + vehicleStats.totalMarketValue) }}</h3>
          <p>Total Market Value</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 23% growth
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ calculateComplianceRate() }}%</h3>
          <p>Compliance Rate</p>
          <span class="stat-trend neutral">
            <i class="pi pi-minus"></i> No change
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.pendingValuations + vehicleStats.pendingValuations }}</h3>
          <p>Pending Review</p>
          <span class="stat-trend neutral">
            <i class="pi pi-minus"></i> No change
          </span>
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
          <div class="property-item">
            <div class="property-icon">
              <i class="pi pi-home"></i>
            </div>
            <div class="property-info">
              <h4>123 Test Street</h4>
              <p>Addis Ababa • Residential</p>
              <span class="property-value">ETB 450,000</span>
            </div>
            <div class="property-status">
              <span class="status-badge completed">Completed</span>
            </div>
          </div>
          
          <div class="property-item">
            <div class="property-icon">
              <i class="pi pi-building"></i>
            </div>
            <div class="property-info">
              <h4>Bole Commercial Center</h4>
              <p>Addis Ababa • Commercial</p>
              <span class="property-value">ETB 1.2M</span>
            </div>
            <div class="property-status">
              <span class="status-badge in-progress">In Progress</span>
            </div>
          </div>
          
          <div class="property-item">
            <div class="property-icon">
              <i class="pi pi-home"></i>
            </div>
            <div class="property-info">
              <h4>Mekelle Office Complex</h4>
              <p>Mekelle • Mixed Use</p>
              <span class="property-value">ETB 850,000</span>
            </div>
            <div class="property-status">
              <span class="status-badge pending">Pending</span>
            </div>
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
          <div class="vehicle-item">
            <div class="vehicle-icon">
              <i class="pi pi-car"></i>
            </div>
            <div class="vehicle-info">
              <h4>Toyota Corolla 2020</h4>
              <p>Addis Ababa • Sedan • AA-123-BC</p>
              <span class="vehicle-value">ETB 850,000</span>
            </div>
            <div class="vehicle-status">
              <span class="status-badge completed">Approved</span>
            </div>
          </div>
          
          <div class="vehicle-item">
            <div class="vehicle-icon">
              <i class="pi pi-car"></i>
            </div>
            <div class="vehicle-info">
              <h4>Hyundai Tucson 2021</h4>
              <p>Oromia • SUV • BB-456-DE</p>
              <span class="vehicle-value">ETB 1.2M</span>
            </div>
            <div class="vehicle-status">
              <span class="status-badge in-progress">Pending</span>
            </div>
          </div>
          
          <div class="vehicle-item">
            <div class="vehicle-icon">
              <i class="pi pi-truck"></i>
            </div>
            <div class="vehicle-info">
              <h4>Isuzu NPR 2019</h4>
              <p>Amhara • Truck • CC-789-FG</p>
              <span class="vehicle-value">ETB 1.5M</span>
            </div>
            <div class="vehicle-status">
              <span class="status-badge pending">Draft</span>
            </div>
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
            <span class="summary-value">12</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">In Progress</span>
            <span class="summary-value">5</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Pending Review</span>
            <span class="summary-value">3</span>
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
            <div class="metric-value">0</div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  totalProperties: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0,
  systemStatus: 'Live'
})

const vehicleStats = ref({
  totalVehicles: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0
})

onMounted(async () => {
  await loadStats()
  await loadVehicleStats()
})

async function loadStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch('http://localhost:8020/api/v1/properties/stats', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      stats.value = data
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    stats.value = {
      totalProperties: 0,
      totalValuations: 0,
      totalMarketValue: 0,
      pendingValuations: 0,
      systemStatus: 'Error'
    }
  }
}

async function loadVehicleStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch('http://localhost:8020/api/v1/vehicles/statistics/summary', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      vehicleStats.value = data
    }
  } catch (error) {
    console.error('Failed to load vehicle stats:', error)
    vehicleStats.value = {
      totalVehicles: 0,
      totalValuations: 0,
      totalMarketValue: 0,
      pendingValuations: 0
    }
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function calculateComplianceRate() {
  const totalItems = stats.value.totalProperties + vehicleStats.value.totalVehicles
  if (totalItems === 0) return 0
  // This will be calculated from real data when valuations are loaded
  return 0
}
</script>

<style scoped>
/* Dashboard Container */
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* Welcome Header */
.welcome-header {
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

.welcome-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.welcome-content p {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.welcome-actions {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.stat-card:nth-child(1) .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.stat-card:nth-child(2) .stat-icon {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.stat-card:nth-child(3) .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.stat-card:nth-child(4) .stat-icon {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.stat-content p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 0.75rem 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.neutral {
  color: #64748b;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.view-all-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

/* Recent Properties */
.recent-properties {
  padding: 1.5rem;
}

.property-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.property-item:last-child {
  border-bottom: none;
}

.property-icon {
  width: 40px;
  height: 40px;
  background: #f8fafc;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.property-info {
  flex: 1;
}

.property-info h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.property-info p {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0 0 0.25rem 0;
}

.property-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}

/* Recent Vehicles */
.recent-vehicles {
  padding: 1.5rem;
}

.vehicle-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.vehicle-item:last-child {
  border-bottom: none;
}

.vehicle-icon {
  width: 40px;
  height: 40px;
  background: #fef3c7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d97706;
}

.vehicle-info {
  flex: 1;
}

.vehicle-info h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.vehicle-info p {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0 0 0.25rem 0;
}

.vehicle-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #d97706;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.in-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.pending {
  background: #f1f5f9;
  color: #475569;
}

.status-badge.compliant {
  background: #dcfce7;
  color: #166534;
}

/* Activity Filters */
.activity-filters {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

.filter-btn:hover:not(.active) {
  background: #f8fafc;
}

/* Activity Chart */
.activity-chart {
  padding: 1.5rem;
  height: 200px;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 8px;
  color: #64748b;
}

.chart-placeholder i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.activity-summary {
  display: flex;
  justify-content: space-around;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

/* Compliance Section */
.compliance-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.compliance-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.compliance-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.compliance-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #059669, #047857);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.compliance-info {
  flex: 1;
}

.compliance-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.compliance-info p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.compliance-metrics {
  display: flex;
  justify-content: space-around;
}

.metric-item {
  text-align: center;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #059669;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.875rem;
  color: #64748b;
}

/* Quick Actions */
.quick-actions-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.quick-actions-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.quick-action-btn i {
  font-size: 1.25rem;
}

.quick-action-btn span {
  font-size: 0.75rem;
  font-weight: 500;
}

/* Responsive Design */
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
  }
  
  .welcome-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .compliance-metrics {
    flex-direction: column;
    gap: 1rem;
  }
  
  .activity-summary {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
