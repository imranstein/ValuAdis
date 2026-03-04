<template>
  <div class="reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Reports</h1>
        <p>Generate comprehensive reports and insights for property valuations</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="viewScheduledReports">
          <i class="pi pi-clock"></i>
          Scheduled
        </button>
        <button class="action-button primary" @click="createNewReport">
          <i class="pi pi-plus"></i>
          New Report
        </button>
      </div>
    </div>

    <!-- Report Types Grid -->
    <div class="report-types">
      <div class="section-header">
        <h2>Report Types</h2>
        <p>Choose from predefined report templates</p>
      </div>
      
      <div class="report-grid">
        <div class="report-card" @click="generateReport('valuation_summary')">
          <div class="report-icon">
            <i class="pi pi-file-text"></i>
          </div>
          <div class="report-content">
            <h3>Valuation Summary</h3>
            <p>Complete overview of all property valuations with market trends and analysis</p>
            <div class="report-features">
              <span class="feature">Market Analysis</span>
              <span class="feature">Trends</span>
              <span class="feature">Statistics</span>
            </div>
          </div>
        </div>

        <div class="report-card" @click="generateReport('municipal_performance')">
          <div class="report-icon">
            <i class="pi pi-chart-bar"></i>
          </div>
          <div class="report-content">
            <h3>Municipal Performance</h3>
            <p>Detailed performance metrics by municipality with comparative analysis</p>
            <div class="report-features">
              <span class="feature">By Municipality</span>
              <span class="feature">Comparisons</span>
              <span class="feature">Rankings</span>
            </div>
          </div>
        </div>

        <div class="report-card" @click="generateReport('property_type_analysis')">
          <div class="report-icon">
            <i class="pi pi-chart-pie"></i>
          </div>
          <div class="report-content">
            <h3>Property Type Analysis</h3>
            <p>Comprehensive breakdown by property types with valuation distributions</p>
            <div class="report-features">
              <span class="feature">Type Distribution</span>
              <span class="feature">Value Ranges</span>
              <span class="feature">Growth Rates</span>
            </div>
          </div>
        </div>

        <div class="report-card" @click="generateReport('tax_revenue')">
          <div class="report-icon">
            <i class="pi pi-money-bill"></i>
          </div>
          <div class="report-content">
            <h3>Tax Revenue Report</h3>
            <p>Taxable value calculations and revenue projections by municipality</p>
            <div class="report-features">
              <span class="feature">Revenue Projections</span>
              <span class="feature">Tax Analysis</span>
              <span class="feature">Compliance</span>
            </div>
          </div>
        </div>

        <div class="report-card" @click="generateReport('market_trends')">
          <div class="report-icon">
            <i class="pi pi-chart-line"></i>
          </div>
          <div class="report-content">
            <h3>Market Trends</h3>
            <p>Historical market trends and future projections for property values</p>
            <div class="report-features">
              <span class="feature">Historical Data</span>
              <span class="feature">Projections</span>
              <span class="feature">Forecasts</span>
            </div>
          </div>
        </div>

        <div class="report-card" @click="generateReport('compliance_audit')">
          <div class="report-icon">
            <i class="pi pi-shield"></i>
          </div>
          <div class="report-content">
            <h3>Compliance Audit</h3>
            <p>Proclamation 1365/2025 compliance status and audit trail</p>
            <div class="report-features">
              <span class="feature">Compliance Status</span>
              <span class="feature">Audit Trail</span>
              <span class="feature">Violations</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Report Builder -->
    <div class="custom-report">
      <div class="section-header">
        <h2>Custom Report Builder</h2>
        <p>Create tailored reports with specific parameters and filters</p>
      </div>
      
      <div class="report-builder">
        <div class="builder-section">
          <h3>Report Parameters</h3>
          <div class="parameter-grid">
            <div class="parameter-field">
              <label>Report Name *</label>
              <input type="text" v-model="customReport.name" placeholder="Enter report name" />
            </div>
            
            <div class="parameter-field">
              <label>Date Range *</label>
              <select v-model="customReport.dateRange">
                <option value="">Select range</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="1y">Last Year</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            
            <div class="parameter-field">
              <label>Municipality</label>
              <select v-model="customReport.municipality">
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
            
            <div class="parameter-field">
              <label>Property Type</label>
              <select v-model="customReport.propertyType">
                <option value="">All Types</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="industrial">Industrial</option>
                <option value="agricultural">Agricultural</option>
                <option value="mixed_use">Mixed Use</option>
              </select>
            </div>
          </div>
        </div>

        <div class="builder-section">
          <h3>Data Fields</h3>
          <div class="field-selection">
            <div class="field-group">
              <h4>Basic Information</h4>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.valuation_id" />
                  <span>Valuation ID</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.property_address" />
                  <span>Property Address</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.owner_name" />
                  <span>Owner Name</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.municipality" />
                  <span>Municipality</span>
                </label>
              </div>
            </div>
            
            <div class="field-group">
              <h4>Valuation Data</h4>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.market_value" />
                  <span>Market Value</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.taxable_value" />
                  <span>Taxable Value</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.property_type" />
                  <span>Property Type</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.land_area" />
                  <span>Land Area</span>
                </label>
              </div>
            </div>
            
            <div class="field-group">
              <h4>Additional Fields</h4>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.status" />
                  <span>Status</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.created_date" />
                  <span>Created Date</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.valuation_method" />
                  <span>Valuation Method</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="customReport.fields.assessor_name" />
                  <span>Assessor Name</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="builder-section">
          <h3>Output Format</h3>
          <div class="format-options">
            <label class="radio-item">
              <input type="radio" v-model="customReport.format" value="pdf" />
              <span>PDF Report</span>
            </label>
            <label class="radio-item">
              <input type="radio" v-model="customReport.format" value="excel" />
              <span>Excel Spreadsheet</span>
            </label>
            <label class="radio-item">
              <input type="radio" v-model="customReport.format" value="csv" />
              <span>CSV Data</span>
            </label>
            <label class="radio-item">
              <input type="radio" v-model="customReport.format" value="json" />
              <span>JSON Data</span>
            </label>
          </div>
        </div>

        <div class="builder-actions">
          <button class="action-button secondary" @click="resetCustomReport">
            <i class="pi pi-refresh"></i>
            Reset
          </button>
          <button class="action-button secondary" @click="saveTemplate">
            <i class="pi pi-save"></i>
            Save Template
          </button>
          <button class="action-button primary" @click="generateCustomReport" :disabled="!canGenerateCustom">
            <i class="pi pi-cog"></i>
            Generate Report
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Reports -->
    <div class="recent-reports">
      <div class="section-header">
        <h2>Recent Reports</h2>
        <div class="header-actions">
          <button class="view-all-btn" @click="viewAllReports">
            View All
            <i class="pi pi-arrow-right"></i>
          </button>
        </div>
      </div>
      
      <div class="reports-list">
        <div v-for="report in recentReports" :key="report.id" class="report-item">
          <div class="report-info">
            <div class="report-icon-small">
              <i :class="getReportIcon(report.type)"></i>
            </div>
            <div class="report-details">
              <h4>{{ report.name }}</h4>
              <p>{{ report.description }}</p>
              <div class="report-meta">
                <span class="report-type">{{ getReportTypeLabel(report.type) }}</span>
                <span class="report-date">{{ formatDate(report.created_date) }}</span>
                <span class="report-status" :class="report.status">{{ getStatusLabel(report.status) }}</span>
              </div>
            </div>
          </div>
          <div class="report-actions">
            <button class="action-btn view" @click="viewReport(report)" title="View">
              <i class="pi pi-eye"></i>
            </button>
            <button class="action-btn download" @click="downloadReport(report)" title="Download">
              <i class="pi pi-download"></i>
            </button>
            <button class="action-btn share" @click="shareReport(report)" title="Share">
              <i class="pi pi-share-alt"></i>
            </button>
            <button class="action-btn delete" @click="deleteReport(report)" title="Delete">
              <i class="pi pi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scheduled Reports -->
    <div class="scheduled-reports">
      <div class="section-header">
        <h2>Scheduled Reports</h2>
        <div class="header-actions">
          <button class="action-button secondary" @click="manageSchedules">
            <i class="pi pi-cog"></i>
            Manage Schedules
          </button>
        </div>
      </div>
      
      <div class="schedules-list">
        <div v-for="schedule in scheduledReports" :key="schedule.id" class="schedule-item">
          <div class="schedule-info">
            <div class="schedule-icon">
              <i class="pi pi-clock"></i>
            </div>
            <div class="schedule-details">
              <h4>{{ schedule.name }}</h4>
              <p>{{ schedule.description }}</p>
              <div class="schedule-meta">
                <span class="schedule-frequency">{{ getFrequencyLabel(schedule.frequency) }}</span>
                <span class="schedule-next">Next: {{ formatDate(schedule.next_run) }}</span>
                <span class="schedule-status" :class="schedule.status">{{ getStatusLabel(schedule.status) }}</span>
              </div>
            </div>
          </div>
          <div class="schedule-actions">
            <button class="action-btn edit" @click="editSchedule(schedule)" title="Edit">
              <i class="pi pi-pencil"></i>
            </button>
            <button class="action-btn play" @click="runSchedule(schedule)" title="Run Now">
              <i class="pi pi-play"></i>
            </button>
            <button class="action-btn pause" @click="pauseSchedule(schedule)" title="Pause">
              <i class="pi pi-pause"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Modal -->
    <div v-if="showReportModal" class="modal-overlay" @click="showReportModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ reportData?.title }}</h2>
          <button class="close-btn" @click="showReportModal = false">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Loading State -->
          <div v-if="isLoading" class="loading-state">
            <i class="pi pi-spin pi-spinner"></i>
            <p>Generating report...</p>
          </div>
          
          <!-- Report Content -->
          <div v-else-if="reportData" class="report-content">
            <!-- Summary Section -->
            <div class="report-summary">
              <h3>📊 Executive Summary</h3>
              <div class="summary-grid">
                <div v-for="(value, key) in reportData.summary" :key="key" class="summary-item">
                  <div class="summary-label">{{ formatSummaryKey(key) }}</div>
                  <div class="summary-value">{{ formatSummaryValue(value, key) }}</div>
                </div>
              </div>
            </div>
            
            <!-- Report Type Specific Content -->
            <div class="report-details">
              <!-- Valuation Summary -->
              <div v-if="currentReportType === 'valuation_summary'" class="valuation-summary">
                <h3>📈 Valuation Overview</h3>
                <div class="stats-grid">
                  <div class="stat-card">
                    <h4>Total Valuations</h4>
                    <p>{{ reportData.summary.total_valuations }}</p>
                  </div>
                  <div class="stat-card">
                    <h4>Total Market Value</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.total_market_value) }}</p>
                  </div>
                  <div class="stat-card">
                    <h4>Total Taxable Value</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.total_taxable_value) }}</p>
                  </div>
                  <div class="stat-card">
                    <h4>Average Value</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.avg_value) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Municipal Performance -->
              <div v-if="currentReportType === 'municipal_performance'" class="municipal-performance">
                <h3>🏛️ Municipal Performance</h3>
                <div class="municipality-grid">
                  <div v-for="(data, municipality) in reportData.data" :key="municipality" class="municipality-card">
                    <h4>{{ municipality }}</h4>
                    <div class="municipality-stats">
                      <div class="stat">
                        <span class="label">Valuations:</span>
                        <span class="value">{{ data.count }}</span>
                      </div>
                      <div class="stat">
                        <span class="label">Total Value:</span>
                        <span class="value">ETB {{ formatCurrency(data.total_value) }}</span>
                      </div>
                      <div class="stat">
                        <span class="label">Tax Revenue:</span>
                        <span class="value">ETB {{ formatCurrency(data.total_taxable) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Property Type Analysis -->
              <div v-if="currentReportType === 'property_type_analysis'" class="property-type-analysis">
                <h3>🏠 Property Type Analysis</h3>
                <div class="type-grid">
                  <div v-for="(data, type) in reportData.data" :key="type" class="type-card">
                    <h4>{{ formatPropertyType(type) }}</h4>
                    <div class="type-stats">
                      <div class="stat">
                        <span class="label">Count:</span>
                        <span class="value">{{ data.count }}</span>
                      </div>
                      <div class="stat">
                        <span class="label">Total Value:</span>
                        <span class="value">ETB {{ formatCurrency(data.total_value) }}</span>
                      </div>
                      <div class="stat">
                        <span class="label">Average:</span>
                        <span class="value">ETB {{ formatCurrency(data.avg_value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tax Revenue Report -->
              <div v-if="currentReportType === 'tax_revenue'" class="tax-revenue">
                <h3>💰 Tax Revenue Analysis</h3>
                <div class="tax-stats">
                  <div class="tax-card">
                    <h4>Total Tax Revenue</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.total_tax_revenue) }}</p>
                  </div>
                  <div class="tax-card">
                    <h4>Total Market Value</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.total_market_value) }}</p>
                  </div>
                  <div class="tax-card">
                    <h4>Effective Tax Rate</h4>
                    <p>{{ reportData.summary.tax_rate.toFixed(2) }}%</p>
                  </div>
                  <div class="tax-card">
                    <h4>Revenue per Property</h4>
                    <p>ETB {{ formatCurrency(reportData.summary.revenue_per_property) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Market Trends -->
              <div v-if="currentReportType === 'market_trends'" class="market-trends">
                <h3>📈 Market Trends</h3>
                <div class="trends-chart">
                  <div class="trend-summary">
                    <p><strong>Total Days Analyzed:</strong> {{ reportData.summary.total_days }}</p>
                    <p><strong>Peak Activity Day:</strong> {{ reportData.summary.peak_day }}</p>
                  </div>
                  <div class="trends-data">
                    <div v-for="date in reportData.sorted_dates" :key="date" class="trend-item">
                      <div class="trend-date">{{ date }}</div>
                      <div class="trend-stats">
                        <span>{{ reportData.data[date].count }} valuations</span>
                        <span>ETB {{ formatCurrency(reportData.data[date].total_value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Compliance Audit -->
              <div v-if="currentReportType === 'compliance_audit'" class="compliance-audit">
                <h3>✅ Compliance Audit</h3>
                <div class="compliance-stats">
                  <div class="compliance-card">
                    <h4>Total Valuations</h4>
                    <p>{{ reportData.data.total_valuations }}</p>
                  </div>
                  <div class="compliance-card compliant">
                    <h4>Compliant</h4>
                    <p>{{ reportData.data.compliant_valuations }}</p>
                  </div>
                  <div class="compliance-card pending">
                    <h4>Pending</h4>
                    <p>{{ reportData.data.pending_valuations }}</p>
                  </div>
                  <div class="compliance-card draft">
                    <h4>Draft</h4>
                    <p>{{ reportData.data.draft_valuations }}</p>
                  </div>
                </div>
                <div class="compliance-rate">
                  <h4>Compliance Rate: {{ reportData.summary.compliance_rate.toFixed(1) }}%</h4>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: reportData.summary.compliance_rate + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Error State -->
          <div v-else-if="errorMessage" class="error-state">
            <i class="pi pi-exclamation-triangle"></i>
            <p>{{ errorMessage }}</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="action-button secondary" @click="showReportModal = false">
            Close
          </button>
          <button class="action-button primary" @click="exportReport">
            <i class="pi pi-download"></i>
            Export PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const isLoading = ref(false)
const errorMessage = ref('')
const reportData = ref(null)
const showReportModal = ref(false)
const currentReportType = ref('')

const customReport = ref({
  name: '',
  dateRange: '',
  municipality: '',
  property_type: '',
  include_charts: true,
  include_tables: true,
  include_summary: true,
  fields: {
    property_address: true,
    market_value: true,
    taxable_value: true,
    property_type: true,
    land_area: false,
    status: true,
    created_date: true,
    valuation_method: false,
    assessor_name: false
  },
  format: 'pdf'
})

const recentReports = ref([
  {
    id: 1,
    name: 'Monthly Valuation Summary',
    type: 'valuation_summary',
    description: 'Complete overview of January 2024 valuations',
    created_date: '2024-01-31',
    status: 'completed'
  },
  {
    id: 2,
    name: 'Addis Ababa Performance Q4',
    type: 'municipal_performance',
    description: 'Q4 2023 performance metrics for Addis Ababa',
    created_date: '2024-01-28',
    status: 'completed'
  },
  {
    id: 3,
    name: 'Tax Revenue Projection',
    type: 'tax_revenue',
    description: '2024 tax revenue projections by municipality',
    created_date: '2024-01-25',
    status: 'processing'
  }
])

const scheduledReports = ref([
  {
    id: 1,
    name: 'Weekly Valuation Report',
    description: 'Automated weekly summary of all valuations',
    frequency: 'weekly',
    next_run: '2024-02-05',
    status: 'active'
  },
  {
    id: 2,
    name: 'Monthly Municipal Performance',
    description: 'Monthly performance metrics by municipality',
    frequency: 'monthly',
    next_run: '2024-02-01',
    status: 'active'
  }
])

// Computed properties
const canGenerateCustom = computed(() => {
  return customReport.value.name && 
         customReport.value.dateRange && 
         Object.values(customReport.value.fields).some(field => field)
})

// Methods
async function generateReport(type) {
  console.log('Generating report:', type)
  
  // Show loading state
  isLoading.value = true
  
  try {
    const token = localStorage.getItem('valuadis_token')
    
    switch(type) {
      case 'valuation_summary':
        await generateValuationSummary(token)
        break
      case 'municipal_performance':
        await generateMunicipalPerformance(token)
        break
      case 'property_type_analysis':
        await generatePropertyTypeAnalysis(token)
        break
      case 'tax_revenue':
        await generateTaxRevenueReport(token)
        break
      case 'market_trends':
        await generateMarketTrends(token)
        break
      case 'compliance_audit':
        await generateComplianceAudit(token)
        break
      default:
        console.error('Unknown report type:', type)
    }
  } catch (error) {
    console.error('Error generating report:', error)
    errorMessage.value = 'Failed to generate report. Please try again.'
  } finally {
    isLoading.value = false
  }
}

function createNewReport() {
  console.log('Creating new report')
}

function viewScheduledReports() {
  console.log('Viewing scheduled reports')
}

// Report Generation Functions
async function generateValuationSummary(token) {
  try {
    // Get valuations data
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      reportData.value = {
        type: 'valuation_summary',
        title: 'Valuation Summary Report',
        data: data,
        summary: {
          total_valuations: data.length || 0,
          total_market_value: data.reduce((sum, v) => sum + (v.market_value || 0), 0),
          total_taxable_value: data.reduce((sum, v) => sum + (v.taxable_value || 0), 0),
          avg_value: data.length > 0 ? data.reduce((sum, v) => sum + (v.market_value || 0), 0) / data.length : 0
        }
      }
      showReportModal.value = true
      currentReportType.value = 'valuation_summary'
    }
  } catch (error) {
    console.error('Error generating valuation summary:', error)
    throw error
  }
}

async function generateMunicipalPerformance(token) {
  try {
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Group by municipality
      const municipalityData = data.reduce((acc, valuation) => {
        const municipality = valuation.municipality || 'Unknown'
        if (!acc[municipality]) {
          acc[municipality] = {
            count: 0,
            total_value: 0,
            total_taxable: 0,
            valuations: []
          }
        }
        acc[municipality].count++
        acc[municipality].total_value += valuation.market_value || 0
        acc[municipality].total_taxable += valuation.taxable_value || 0
        acc[municipality].valuations.push(valuation)
        return acc
      }, {})
      
      reportData.value = {
        type: 'municipal_performance',
        title: 'Municipal Performance Report',
        data: municipalityData,
        summary: {
          total_municipalities: Object.keys(municipalityData).length,
          top_municipality: Object.entries(municipalityData)
            .sort(([,a], [,b]) => b.total_value - a.total_value)[0]?.[0] || 'N/A'
        }
      }
      showReportModal.value = true
      currentReportType.value = 'municipal_performance'
    }
  } catch (error) {
    console.error('Error generating municipal performance:', error)
    throw error
  }
}

async function generatePropertyTypeAnalysis(token) {
  try {
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Group by property type
      const typeData = data.reduce((acc, valuation) => {
        const type = valuation.property_type || 'unknown'
        if (!acc[type]) {
          acc[type] = {
            count: 0,
            total_value: 0,
            avg_value: 0,
            valuations: []
          }
        }
        acc[type].count++
        acc[type].total_value += valuation.market_value || 0
        acc[type].valuations.push(valuation)
        return acc
      }, {})
      
      // Calculate averages
      Object.keys(typeData).forEach(type => {
        typeData[type].avg_value = typeData[type].count > 0 
          ? typeData[type].total_value / typeData[type].count 
          : 0
      })
      
      reportData.value = {
        type: 'property_type_analysis',
        title: 'Property Type Analysis Report',
        data: typeData,
        summary: {
          total_types: Object.keys(typeData).length,
          most_common_type: Object.entries(typeData)
            .sort(([,a], [,b]) => b.count - a.count)[0]?.[0] || 'N/A'
        }
      }
      showReportModal.value = true
      currentReportType.value = 'property_type_analysis'
    }
  } catch (error) {
    console.error('Error generating property type analysis:', error)
    throw error
  }
}

async function generateTaxRevenueReport(token) {
  try {
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      const totalTaxRevenue = data.reduce((sum, v) => sum + (v.taxable_value || 0), 0)
      const totalMarketValue = data.reduce((sum, v) => sum + (v.market_value || 0), 0)
      
      reportData.value = {
        type: 'tax_revenue',
        title: 'Tax Revenue Report',
        data: data,
        summary: {
          total_tax_revenue: totalTaxRevenue,
          total_market_value: totalMarketValue,
          tax_rate: totalMarketValue > 0 ? (totalTaxRevenue / totalMarketValue) * 100 : 0,
          revenue_per_property: data.length > 0 ? totalTaxRevenue / data.length : 0
        }
      }
      showReportModal.value = true
      currentReportType.value = 'tax_revenue'
    }
  } catch (error) {
    console.error('Error generating tax revenue report:', error)
    throw error
  }
}

async function generateMarketTrends(token) {
  try {
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Group by valuation date
      const trendsData = data.reduce((acc, valuation) => {
        const date = new Date(valuation.valuation_date).toLocaleDateString()
        if (!acc[date]) {
          acc[date] = {
            count: 0,
            total_value: 0,
            avg_value: 0
          }
        }
        acc[date].count++
        acc[date].total_value += valuation.market_value || 0
        return acc
      }, {})
      
      // Calculate averages and sort by date
      Object.keys(trendsData).forEach(date => {
        trendsData[date].avg_value = trendsData[date].count > 0 
          ? trendsData[date].total_value / trendsData[date].count 
          : 0
      })
      
      const sortedDates = Object.keys(trendsData).sort()
      
      reportData.value = {
        type: 'market_trends',
        title: 'Market Trends Report',
        data: trendsData,
        sorted_dates: sortedDates,
        summary: {
          total_days: sortedDates.length,
          peak_day: sortedDates.length > 0 
            ? sortedDates.reduce((a, b) => trendsData[a].total_value > trendsData[b].total_value ? a : b)
            : 'N/A'
        }
      }
      showReportModal.value = true
      currentReportType.value = 'market_trends'
    }
  } catch (error) {
    console.error('Error generating market trends:', error)
    throw error
  }
}

async function generateComplianceAudit(token) {
  try {
    const response = await fetch('http://localhost:8020/api/v1/valuations/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Compliance checks
      const complianceData = {
        total_valuations: data.length,
        compliant_valuations: data.filter(v => v.status === 'approved').length,
        pending_valuations: data.filter(v => v.status === 'pending').length,
        draft_valuations: data.filter(v => v.status === 'draft').length,
        rejected_valuations: data.filter(v => v.status === 'rejected').length,
        compliance_rate: data.length > 0 ? (data.filter(v => v.status === 'approved').length / data.length) * 100 : 0
      }
      
      reportData.value = {
        type: 'compliance_audit',
        title: 'Compliance Audit Report',
        data: complianceData,
        summary: {
          compliance_rate: complianceData.compliance_rate,
          needs_attention: complianceData.pending_valuations + complianceData.draft_valuations
        }
      }
      showReportModal.value = true
      currentReportType.value = 'compliance_audit'
    }
  } catch (error) {
    console.error('Error generating compliance audit:', error)
    throw error
  }
}

function generateCustomReport() {
  console.log('Generating custom report:', customReport.value)
}

function resetCustomReport() {
  customReport.value = {
    name: '',
    dateRange: '',
    municipality: '',
    propertyType: '',
    fields: {
      valuation_id: true,
      property_address: true,
      owner_name: false,
      municipality: true,
      market_value: true,
      taxable_value: true,
      property_type: true,
      land_area: false,
      status: true,
      created_date: true,
      valuation_method: false,
      assessor_name: false
    },
    format: 'pdf'
  }
}

function saveTemplate() {
  console.log('Saving report template')
}

function viewAllReports() {
  console.log('Viewing all reports')
}

function viewReport(report) {
  console.log('Viewing report:', report.name)
}

function downloadReport(report) {
  console.log('Downloading report:', report.name)
}

function shareReport(report) {
  console.log('Sharing report:', report.name)
}

function deleteReport(report) {
  if (confirm(`Are you sure you want to delete report "${report.name}"?`)) {
    const index = recentReports.value.findIndex(r => r.id === report.id)
    if (index > -1) {
      recentReports.value.splice(index, 1)
    }
  }
}

function manageSchedules() {
  console.log('Managing report schedules')
}

function editSchedule(schedule) {
  console.log('Editing schedule:', schedule.name)
}

function runSchedule(schedule) {
  console.log('Running schedule:', schedule.name)
}

function pauseSchedule(schedule) {
  console.log('Pausing schedule:', schedule.name)
}

function getReportIcon(type) {
  const icons = {
    valuation_summary: 'pi pi-file-text',
    municipal_performance: 'pi pi-chart-bar',
    property_type_analysis: 'pi pi-chart-pie',
    tax_revenue: 'pi pi-money-bill',
    market_trends: 'pi pi-chart-line',
    compliance_audit: 'pi pi-shield'
  }
  return icons[type] || 'pi pi-file'
}

function getReportTypeLabel(type) {
  const labels = {
    valuation_summary: 'Valuation Summary',
    municipal_performance: 'Municipal Performance',
    property_type_analysis: 'Property Type Analysis',
    tax_revenue: 'Tax Revenue',
    market_trends: 'Market Trends',
    compliance_audit: 'Compliance Audit'
  }
  return labels[type] || type
}

function getStatusLabel(status) {
  const labels = {
    completed: 'Completed',
    processing: 'Processing',
    pending: 'Pending',
    failed: 'Failed',
    active: 'Active',
    paused: 'Paused'
  }
  return labels[status] || status
}

function getFrequencyLabel(frequency) {
  const labels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    quarterly: 'Quarterly',
    yearly: 'Yearly'
  }
  return labels[frequency] || frequency
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Utility Functions
function formatCurrency(value) {
  if (!value || value === 0) return '0'
  return new Intl.NumberFormat('en-US').format(Math.round(value))
}

function formatSummaryKey(key) {
  return key.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

function formatSummaryValue(value, key) {
  if (typeof value === 'number') {
    if (key.includes('rate') || key.includes('percentage')) {
      return `${value.toFixed(1)}%`
    } else if (key.includes('value') || key.includes('revenue')) {
      return `ETB ${formatCurrency(value)}`
    } else {
      return value.toLocaleString()
    }
  }
  return value
}

function formatPropertyType(type) {
  const typeMap = {
    'residential': 'Residential Properties',
    'commercial': 'Commercial Properties',
    'agricultural': 'Agricultural Land',
    'unknown': 'Unknown Type'
  }
  return typeMap[type] || type
}

function exportReport() {
  console.log('Exporting report:', reportData.value?.title)
  // TODO: Implement PDF export functionality
  alert('PDF export functionality will be implemented soon!')
}
</script>

<style scoped>
/* Reports Container */
.reports-container {
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

/* Section Headers */
.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.section-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* Report Types Grid */
.report-types {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.report-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #059669;
}

.report-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.report-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.report-content p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.report-features {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.feature {
  background: white;
  color: #059669;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid #dcfce7;
}

/* Custom Report Builder */
.custom-report {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.report-builder {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.builder-section {
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.builder-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.parameter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.parameter-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.parameter-field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.parameter-field input,
.parameter-field select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
}

.field-selection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.field-group h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.75rem 0;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.checkbox-item input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #059669;
}

.format-options {
  display: flex;
  gap: 1rem;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.radio-item input[type="radio"] {
  width: auto;
  margin: 0;
  accent-color: #059669;
}

.builder-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Recent Reports */
.recent-reports {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.report-item:hover {
  background: #f1f5f9;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.report-icon-small {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.report-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.report-details p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.report-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.report-type {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.report-date {
  color: #64748b;
}

.report-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.report-status.completed {
  background: #bbf7d0;
  color: #059669;
}

.report-status.processing {
  background: #fef3c7;
  color: #d97706;
}

.report-status.pending {
  background: #e0f2fe;
  color: #0369a1;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #1e40af;
  color: white;
}

.action-btn.download {
  background: #e0f2fe;
  color: #0369a1;
}

.action-btn.download:hover {
  background: #0369a1;
  color: white;
}

.action-btn.share {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.share:hover {
  background: #6b7280;
  color: white;
}

.action-btn.delete {
  background: #fecaca;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #dc2626;
  color: white;
}

/* Scheduled Reports */
.scheduled-reports {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.schedules-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.schedule-item:hover {
  background: #f1f5f9;
}

.schedule-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.schedule-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.schedule-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.schedule-details p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.schedule-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.schedule-frequency {
  background: #dcfce7;
  color: #059669;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.schedule-next {
  color: #64748b;
}

.schedule-status.active {
  background: #bbf7d0;
  color: #059669;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.schedule-status.paused {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.schedule-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn.edit {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.edit:hover {
  background: #6b7280;
  color: white;
}

.action-btn.play {
  background: #dcfce7;
  color: #059669;
}

.action-btn.play:hover {
  background: #059669;
  color: white;
}

.action-btn.pause {
  background: #fef3c7;
  color: #d97706;
}

.action-btn.pause:hover {
  background: #d97706;
  color: white;
}

/* View All Button */
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
  
  .report-grid {
    grid-template-columns: 1fr;
  }
  
  .parameter-grid {
    grid-template-columns: 1fr;
  }
  
  .field-selection {
    grid-template-columns: 1fr;
  }
  
  .format-options {
    flex-direction: column;
  }
  
  .builder-actions {
    flex-direction: column;
  }
  
  .report-item,
  .schedule-item {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .report-actions,
  .schedule-actions {
    justify-content: center;
  }
  
  .report-meta,
  .schedule-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* Modal Styles */
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
  max-width: 90vw;
  max-height: 90vh;
  width: 900px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Report Content Styles */
.report-summary {
  margin-bottom: 2rem;
}

.report-summary h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.summary-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.stat-card p {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

/* Municipality Grid */
.municipality-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.municipality-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.municipality-card h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.municipality-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.municipality-stats .stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.municipality-stats .label {
  font-size: 0.875rem;
  color: #64748b;
}

.municipality-stats .value {
  font-weight: 600;
  color: #1e293b;
}

/* Property Type Grid */
.type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.type-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.type-card h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.type-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.type-stats .stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-stats .label {
  font-size: 0.875rem;
  color: #64748b;
}

.type-stats .value {
  font-weight: 600;
  color: #1e293b;
}

/* Tax Stats */
.tax-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.tax-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.tax-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.tax-card p {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

/* Compliance Stats */
.compliance-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.compliance-card {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.compliance-card.compliant {
  background: #f0fdf4;
  border-color: #22c55e;
}

.compliance-card.pending {
  background: #fef3c7;
  border-color: #f59e0b;
}

.compliance-card.draft {
  background: #f1f5f9;
  border-color: #64748b;
}

.compliance-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.compliance-card p {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.compliance-rate {
  text-align: center;
}

.compliance-rate h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.progress-bar {
  width: 100%;
  height: 1rem;
  background: #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #22c55e;
  transition: width 0.3s ease;
}

/* Loading and Error States */
.loading-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.error-state {
  text-align: center;
  padding: 3rem;
  color: #ef4444;
}

.error-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* Market Trends */
.trends-chart {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.trend-summary {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.trend-summary p {
  margin: 0.25rem 0;
  color: #64748b;
}

.trends-data {
  max-height: 300px;
  overflow-y: auto;
}

.trend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.trend-item:last-child {
  border-bottom: none;
}

.trend-date {
  font-weight: 500;
  color: #1e293b;
}

.trend-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748b;
}
</style>
