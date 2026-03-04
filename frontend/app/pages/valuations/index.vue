<template>
  <div class="valuations-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Valuations</h1>
        <p>Manage and track all property valuations and assessments</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportValuations">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button class="action-button primary" @click="router.push('/valuations/quick')">
          <i class="pi pi-plus"></i>
          Quick Valuation
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="search-filters">
      <div class="search-section">
        <div class="search-bar">
          <i class="pi pi-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search valuations by property address, owner, or ID..."
          />
        </div>
      </div>
      
      <div class="filter-section">
        <select v-model="selectedStatus" class="filter-dropdown">
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="expired">Expired</option>
        </select>
        
        <select v-model="selectedMunicipality" class="filter-dropdown">
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
        
        <select v-model="selectedType" class="filter-dropdown">
          <option value="">All Types</option>
          <option value="residential">Residential</option>
          <option value="commercial">Commercial</option>
          <option value="industrial">Industrial</option>
          <option value="agricultural">Agricultural</option>
          <option value="mixed_use">Mixed Use</option>
        </select>
        
        <button class="reset-button" @click="resetFilters">
          <i class="pi pi-refresh"></i>
          Reset
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-file-text"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalValuations }}</h3>
          <p>Total Valuations</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>12% from last month</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-clock"></i>
        </div>
        <div class="stat-content">
          <h3>{{ pendingValuations }}</h3>
          <p>Pending Review</p>
          <div class="stat-trend neutral">
            <i class="pi pi-minus"></i>
            <span>No change</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ approvedValuations }}</h3>
          <p>Approved</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>8% from last month</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-money-bill"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatCurrency(totalMarketValue) }}</h3>
          <p>Total Market Value</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>15% from last month</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Valuations Registry -->
    <div class="valuations-registry">
      <div class="registry-header">
        <h2>Valuation Registry</h2>
        <div class="registry-info">
          <span>{{ filteredValuations.length }} valuations</span>
          <div class="view-toggle">
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'table' }"
              @click="viewMode = 'table'"
            >
              <i class="pi pi-table"></i>
            </button>
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="pi pi-th-large"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="table-container">
        <table class="valuations-table">
          <thead>
            <tr>
              <th @click="sortBy('valuation_id')">
                Valuation ID
                <i class="pi" :class="getSortIcon('valuation_id')"></i>
              </th>
              <th @click="sortBy('property_address')">
                Property Address
                <i class="pi" :class="getSortIcon('property_address')"></i>
              </th>
              <th @click="sortBy('owner_name')">
                Owner
                <i class="pi" :class="getSortIcon('owner_name')"></i>
              </th>
              <th @click="sortBy('municipality')">
                Municipality
                <i class="pi" :class="getSortIcon('municipality')"></i>
              </th>
              <th @click="sortBy('property_type')">
                Type
                <i class="pi" :class="getSortIcon('property_type')"></i>
              </th>
              <th @click="sortBy('market_value')">
                Market Value
                <i class="pi" :class="getSortIcon('market_value')"></i>
              </th>
              <th @click="sortBy('status')">
                Status
                <i class="pi" :class="getSortIcon('status')"></i>
              </th>
              <th @click="sortBy('created_date')">
                Date
                <i class="pi" :class="getSortIcon('created_date')"></i>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="valuation in paginatedValuations" :key="valuation.id">
              <td>
                <span class="valuation-id">{{ valuation.valuation_id }}</span>
              </td>
              <td>
                <div class="property-info">
                  <i class="pi pi-map-marker"></i>
                  <span>{{ valuation.property_address }}</span>
                </div>
              </td>
              <td>
                <div class="owner-info">
                  <div class="owner-avatar">{{ getInitials(valuation.owner_name) }}</div>
                  <span>{{ valuation.owner_name }}</span>
                </div>
              </td>
              <td>
                <span class="municipality-badge">{{ valuation.municipality }}</span>
              </td>
              <td>
                <span class="type-badge" :class="valuation.property_type">{{ getPropertyTypeLabel(valuation.property_type) }}</span>
              </td>
              <td>
                <div class="value-info">
                  <div class="market-value">{{ formatCurrency(valuation.market_value) }}</div>
                  <div class="taxable-value">{{ formatCurrency(valuation.taxable_value) }}</div>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="valuation.status">{{ getStatusLabel(valuation.status) }}</span>
              </td>
              <td>
                <span class="date">{{ formatDate(valuation.created_date) }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view" @click="viewValuation(valuation)" title="View">
                    <i class="pi pi-eye"></i>
                  </button>
                  <button class="action-btn edit" @click="editValuation(valuation)" title="Edit">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="action-btn download" @click="downloadValuation(valuation)" title="Download">
                    <i class="pi pi-download"></i>
                  </button>
                  <button class="action-btn delete" @click="deleteValuation(valuation)" title="Delete">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Grid View -->
      <div v-else class="grid-container">
        <div v-for="valuation in paginatedValuations" :key="valuation.id" class="valuation-card">
          <div class="card-header">
            <div class="valuation-info">
              <span class="valuation-id">{{ valuation.valuation_id }}</span>
              <span class="status-badge" :class="valuation.status">{{ getStatusLabel(valuation.status) }}</span>
            </div>
            <div class="card-actions">
              <button class="action-btn view" @click="viewValuation(valuation)">
                <i class="pi pi-eye"></i>
              </button>
            </div>
          </div>
          
          <div class="card-content">
            <div class="property-details">
              <h4>{{ valuation.property_address }}</h4>
              <div class="property-meta">
                <span class="municipality-badge">{{ valuation.municipality }}</span>
                <span class="type-badge" :class="valuation.property_type">{{ getPropertyTypeLabel(valuation.property_type) }}</span>
              </div>
            </div>
            
            <div class="owner-details">
              <div class="owner-avatar">{{ getInitials(valuation.owner_name) }}</div>
              <span>{{ valuation.owner_name }}</span>
            </div>
            
            <div class="value-details">
              <div class="market-value">{{ formatCurrency(valuation.market_value) }}</div>
              <div class="taxable-value">Taxable: {{ formatCurrency(valuation.taxable_value) }}</div>
            </div>
          </div>
          
          <div class="card-footer">
            <span class="date">{{ formatDate(valuation.created_date) }}</span>
            <div class="card-actions">
              <button class="action-btn edit" @click="editValuation(valuation)">
                <i class="pi pi-pencil"></i>
              </button>
              <button class="action-btn download" @click="downloadValuation(valuation)">
                <i class="pi pi-download"></i>
              </button>
              <button class="action-btn delete" @click="deleteValuation(valuation)">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredValuations.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="pi pi-file-text"></i>
        </div>
        <h3>No valuations found</h3>
        <p>Create your first valuation to get started</p>
        <button class="action-button primary" @click="router.push('/valuations/quick')">
          <i class="pi pi-plus"></i>
          Create Valuation
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredValuations.length > itemsPerPage" class="pagination">
      <div class="pagination-info">
        <span>Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredValuations.length) }} of {{ filteredValuations.length }} valuations</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedMunicipality = ref('')
const selectedType = ref('')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const sortField = ref('created_date')
const sortDirection = ref('desc')

const valuations = ref([
  {
    id: 1,
    valuation_id: 'VAL-2024-001',
    property_address: 'Bole Medhanialem, Addis Ababa',
    owner_name: 'Abebe Kebede',
    municipality: 'Addis Ababa',
    property_type: 'commercial',
    market_value: 2500000,
    taxable_value: 625000,
    status: 'approved',
    created_date: '2024-01-15'
  },
  {
    id: 2,
    valuation_id: 'VAL-2024-002',
    property_address: 'Kirkos, Addis Ababa',
    owner_name: 'Tigist Haile',
    municipality: 'Addis Ababa',
    property_type: 'residential',
    market_value: 850000,
    taxable_value: 212500,
    status: 'pending',
    created_date: '2024-01-18'
  },
  {
    id: 3,
    valuation_id: 'VAL-2024-003',
    property_address: 'Mekelle Industrial Zone',
    owner_name: 'Dawit Mengistu',
    municipality: 'Mekelle',
    property_type: 'industrial',
    market_value: 4500000,
    taxable_value: 1125000,
    status: 'draft',
    created_date: '2024-01-20'
  }
])

// Computed properties
const filteredValuations = computed(() => {
  let filtered = valuations.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(v => 
      v.property_address.toLowerCase().includes(query) ||
      v.owner_name.toLowerCase().includes(query) ||
      v.valuation_id.toLowerCase().includes(query)
    )
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(v => v.status === selectedStatus.value)
  }

  if (selectedMunicipality.value) {
    filtered = filtered.filter(v => v.municipality === selectedMunicipality.value)
  }

  if (selectedType.value) {
    filtered = filtered.filter(v => v.property_type === selectedType.value)
  }

  // Sort
  filtered.sort((a, b) => {
    let aVal = a[sortField.value]
    let bVal = b[sortField.value]
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return filtered
})

const paginatedValuations = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredValuations.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredValuations.value.length / itemsPerPage.value)
})

const totalValuations = computed(() => valuations.value.length)
const pendingValuations = computed(() => valuations.value.filter(v => v.status === 'pending').length)
const approvedValuations = computed(() => valuations.value.filter(v => v.status === 'approved').length)
const totalMarketValue = computed(() => valuations.value.reduce((sum, v) => sum + v.market_value, 0))

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

function resetFilters() {
  searchQuery.value = ''
  selectedStatus.value = ''
  selectedMunicipality.value = ''
  selectedType.value = ''
  currentPage.value = 1
}

function viewValuation(valuation) {
  router.push(`/valuations/${valuation.id}`)
}

function editValuation(valuation) {
  router.push(`/valuations/${valuation.id}/edit`)
}

function downloadValuation(valuation) {
  // Download functionality
  console.log('Downloading valuation:', valuation.valuation_id)
}

function deleteValuation(valuation) {
  if (confirm(`Are you sure you want to delete valuation ${valuation.valuation_id}?`)) {
    const index = valuations.value.findIndex(v => v.id === valuation.id)
    if (index > -1) {
      valuations.value.splice(index, 1)
    }
  }
}

function exportValuations() {
  // Export functionality
  console.log('Exporting valuations')
}

onMounted(() => {
  // Load valuations from API
  console.log('Loading valuations...')
})
</script>

<style scoped>
/* Valuations Container */
.valuations-container {
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

/* Search and Filters */
.search-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
}

.search-bar i {
  color: #64748b;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  font-size: 0.875rem;
}

.filter-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-dropdown {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 0.875rem;
  min-width: 150px;
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
}

.reset-button:hover {
  background: #f8fafc;
  border-color: #059669;
  color: #059669;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #059669, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
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
  margin: 0 0 0.5rem 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.neutral {
  color: #6b7280;
}

.stat-trend.negative {
  color: #ef4444;
}

/* Valuations Registry */
.valuations-registry {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.registry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #f1f5f9;
}

.registry-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.registry-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.registry-info span {
  color: #64748b;
  font-size: 0.875rem;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

/* Table Styles */
.table-container {
  overflow-x: auto;
}

.valuations-table {
  width: 100%;
  border-collapse: collapse;
}

.valuations-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  user-select: none;
}

.valuations-table th:hover {
  background: #f1f5f9;
}

.valuations-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.valuation-id {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #059669;
}

.property-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.property-info i {
  color: #6b7280;
}

.owner-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.owner-avatar {
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

.municipality-badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
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

.type-badge.agricultural {
  background: #bbf7d0;
  color: #059669;
}

.type-badge.mixed_use {
  background: #fef3c7;
  color: #d97706;
}

.value-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.market-value {
  font-weight: 600;
  color: #1e293b;
}

.taxable-value {
  font-size: 0.75rem;
  color: #059669;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.approved {
  background: #bbf7d0;
  color: #059669;
}

.status-badge.rejected {
  background: #fecaca;
  color: #dc2626;
}

.status-badge.expired {
  background: #e5e7eb;
  color: #6b7280;
}

.date {
  color: #64748b;
  font-size: 0.875rem;
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

.action-btn.edit {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.edit:hover {
  background: #6b7280;
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

.action-btn.delete {
  background: #fecaca;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #dc2626;
  color: white;
}

/* Grid View */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.valuation-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s;
}

.valuation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.valuation-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-content {
  padding: 1.5rem;
}

.property-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.property-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.owner-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1rem 0;
}

.value-details {
  margin: 1rem 0;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
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
  margin: 0 0 2rem 0;
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
  
  .filter-section {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .registry-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .grid-container {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
