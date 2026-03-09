<template>
  <div class="properties-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Properties</h1>
        <p>Manage and track all property records and valuations</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportProperties">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button class="action-button primary" @click="router.push('/properties/create')">
          <i class="pi pi-plus"></i>
          Create Property
        </button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="search-bar">
        <i class="pi pi-search"></i>
        <input 
          type="text" 
          placeholder="Search properties by address, municipality, or type..."
          v-model="searchQuery"
        />
      </div>
      <div class="filter-controls">
        <select v-model="selectedMunicipality" class="filter-select">
          <option value="">All Municipalities</option>
          <option value="Addis Ababa">Addis Ababa</option>
          <option value="Mekelle">Mekelle</option>
          <option value="Dire Dawa">Dire Dawa</option>
          <option value="Bahir Dar">Bahir Dar</option>
        </select>
        <select v-model="selectedType" class="filter-select">
          <option value="">All Types</option>
          <option value="residential">Residential</option>
          <option value="commercial">Commercial</option>
          <option value="industrial">Industrial</option>
          <option value="agricultural">Agricultural</option>
        </select>
        <button class="filter-button" @click="resetFilters">
          <i class="pi pi-refresh"></i>
          Reset
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
          <h3>{{ filteredProperties.length }}</h3>
          <p>Total Properties</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 12% from last month
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-map"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalArea.toLocaleString() }}</h3>
          <p>Total Area (m²)</p>
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
          <h3>{{ averageArea.toLocaleString() }}</h3>
          <p>Average Area (m²)</p>
          <span class="stat-trend neutral">
            <i class="pi pi-minus"></i> No change
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ completedValuations }}</h3>
          <p>Completed Valuations</p>
          <span class="stat-trend positive">
            <i class="pi pi-arrow-up"></i> 15% from last month
          </span>
        </div>
      </div>
    </div>

    <!-- Properties Table -->
    <div class="properties-table">
      <div class="table-header">
        <h2>Property Registry</h2>
        <div class="table-actions">
          <span class="results-count">{{ filteredProperties.length }} properties</span>
          <div class="view-toggle">
            <button class="view-btn active" @click="viewMode = 'table'">
              <i class="pi pi-table"></i>
            </button>
            <button class="view-btn" @click="viewMode = 'grid'">
              <i class="pi pi-th-large"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th @click="sortBy('address')">
                Address
                <i class="pi pi-sort"></i>
              </th>
              <th @click="sortBy('municipality')">
                Municipality
                <i class="pi pi-sort"></i>
              </th>
              <th @click="sortBy('property_type')">
                Type
                <i class="pi pi-sort"></i>
              </th>
              <th @click="sortBy('area_sqm')">
                Area (m²)
                <i class="pi pi-sort"></i>
              </th>
              <th @click="sortBy('market_value')">
                Market Value
                <i class="pi pi-sort"></i>
              </th>
              <th @click="sortBy('status')">
                Status
                <i class="pi pi-sort"></i>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="property in paginatedProperties" :key="property.id" class="table-row">
              <td class="address-cell">
                <div class="address-content">
                  <i class="pi pi-map-marker"></i>
                  <div>
                    <strong>{{ property.address }}</strong>
                    <small v-if="property.property_id">ID: {{ property.property_id }}</small>
                  </div>
                </div>
              </td>
              <td>
                <span class="municipality-badge">{{ property.municipality }}</span>
              </td>
              <td>
                <span class="type-badge" :class="property.property_type">
                  {{ property.property_type }}
                </span>
              </td>
              <td class="area-cell">
                <div class="area-content">
                  <strong>{{ Math.round(property.area_sqm || 0).toLocaleString() }}</strong>
                  <small>m²</small>
                </div>
              </td>
              <td class="value-cell">
                <div class="value-content">
                  <strong>ETB {{ formatCurrency(property.market_value || 0) }}</strong>
                  <small v-if="property.taxable_value">
                    Taxable: ETB {{ formatCurrency(property.taxable_value) }}
                  </small>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="property.status || 'pending'">
                  {{ formatStatus(property.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="action-buttons">
                  <button class="action-btn view" @click="viewProperty(property.id)" title="View Details">
                    <i class="pi pi-eye"></i>
                  </button>
                  <button class="action-btn edit" @click="editProperty(property.id)" title="Edit Property">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="action-btn valuation" @click="createValuation(property.id)" title="Create Valuation">
                    <i class="pi pi-calculator"></i>
                  </button>
                  <button class="action-btn delete" @click="confirmDelete(property)" title="Delete Property">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredProperties.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="pi pi-inbox"></i>
          </div>
          <h3>No properties found</h3>
          <p>{{ searchQuery || selectedMunicipality || selectedType ? 'Try adjusting your filters' : 'Create your first property to get started' }}</p>
          <button v-if="!searchQuery && !selectedMunicipality && !selectedType" class="action-button primary" @click="router.push('/properties/create')">
            <i class="pi pi-plus"></i>
            Create Property
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else class="grid-container">
        <div v-for="property in paginatedProperties" :key="property.id" class="property-card">
          <div class="card-header">
            <div class="property-type-icon">
              <i :class="getPropertyTypeIcon(property.property_type)"></i>
            </div>
            <span class="status-badge" :class="property.status || 'pending'">
              {{ formatStatus(property.status) }}
            </span>
          </div>
          <div class="card-body">
            <h4>{{ property.address }}</h4>
            <div class="property-details">
              <div class="detail-item">
                <i class="pi pi-map-marker"></i>
                <span>{{ property.municipality }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-tag"></i>
                <span>{{ property.property_type }}</span>
              </div>
              <div class="detail-item">
                <i class="pi pi-th-large"></i>
                <span>{{ Math.round(property.area_sqm || 0).toLocaleString() }} m²</span>
              </div>
            </div>
            <div class="property-value">
              <strong>ETB {{ formatCurrency(property.market_value || 0) }}</strong>
              <small v-if="property.taxable_value">Taxable: ETB {{ formatCurrency(property.taxable_value) }}</small>
            </div>
          </div>
          <div class="card-footer">
            <button class="card-action-btn primary" @click="viewProperty(property.id)">
              <i class="pi pi-eye"></i>
              View
            </button>
            <button class="card-action-btn secondary" @click="editProperty(property.id)">
              <i class="pi pi-pencil"></i>
              Edit
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredProperties.length > itemsPerPage" class="pagination">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1" 
          @click="currentPage--"
        >
          <i class="pi pi-chevron-left"></i>
        </button>
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const properties = ref([])
const loading = ref(false)
const deleteDialog = ref(false)
const propertyToDelete = ref(null)

const searchQuery = ref('')
const selectedMunicipality = ref('')
const selectedType = ref('')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const sortField = ref('address')
const sortDirection = ref('asc')

const totalArea = computed(() => {
  return filteredProperties.value.reduce((sum, prop) => sum + (prop.area_sqm || 0), 0)
})

const averageArea = computed(() => {
  if (filteredProperties.value.length === 0) return 0
  return Math.round(totalArea.value / filteredProperties.value.length)
})

const completedValuations = computed(() => {
  return filteredProperties.value.filter(p => p.status === 'completed').length
})

const filteredProperties = computed(() => {
  let filtered = properties.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(property => 
      property.address?.toLowerCase().includes(query) ||
      property.municipality?.toLowerCase().includes(query) ||
      property.property_type?.toLowerCase().includes(query)
    )
  }

  if (selectedMunicipality.value) {
    filtered = filtered.filter(property => property.municipality === selectedMunicipality.value)
  }

  if (selectedType.value) {
    filtered = filtered.filter(property => property.property_type === selectedType.value)
  }

  return filtered
})

const paginatedProperties = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredProperties.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredProperties.value.length / itemsPerPage.value)
})

onMounted(async () => {
  await loadProperties()
})

async function loadProperties() {
  loading.value = true
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch('http://localhost:8020/api/v1/properties?limit=50', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      properties.value = result.data || []
    }
  } catch (error) {
    console.error('Failed to load properties:', error)
  } finally {
    loading.value = false
  }
}

function viewProperty(id) {
  router.push(`/properties/${id}`)
}

function editProperty(id) {
  router.push(`/properties/edit/${id}`)
}

function createValuation(id) {
  router.push(`/valuations/create?property_id=${id}`)
}

function confirmDelete(property) {
  if (window.confirm(`Are you sure you want to delete "${property.address}"?`)) {
    deleteProperty(property.id)
  }
}

async function deleteProperty(id) {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`http://localhost:8020/api/v1/properties/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      await loadProperties()
    }
  } catch (error) {
    console.error('Failed to delete property:', error)
  }
}

function sortBy(field) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedMunicipality.value = ''
  selectedType.value = ''
  currentPage.value = 1
}

function exportProperties() {
  // Export filtered properties to CSV
  const propertiesToExport = filteredProperties.value
  
  if (propertiesToExport.length === 0) {
    alert('No properties to export')
    return
  }
  
  // CSV headers
  const headers = [
    'Property Reference',
    'Address',
    'Municipality',
    'Type',
    'Land Area (m²)',
    'Building Area (m²)',
    'Market Value (ETB)',
    'Status',
    'Created Date'
  ]
  
  // Convert properties to CSV rows
  const rows = propertiesToExport.map(property => [
    property.property_ref || 'N/A',
    property.address || 'N/A',
    property.municipality || 'N/A',
    property.property_type || 'N/A',
    property.land_area_sqm || '0',
    property.building_area_sqm || '0',
    property.market_value || '0',
    property.status || 'N/A',
    property.created_at ? new Date(property.created_at).toLocaleDateString() : 'N/A'
  ])
  
  // Combine headers and rows
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `properties_export_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function formatCurrency(value) {
  if (!value) return '0'
  return Number(value).toLocaleString()
}

function formatStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || 'Pending'
}

function getPropertyTypeIcon(type) {
  const iconMap = {
    'residential': 'pi pi-home',
    'commercial': 'pi pi-building',
    'industrial': 'pi pi-industry',
    'agricultural': 'pi pi-sun'
  }
  return iconMap[type] || 'pi pi-home'
}
</script>

<style scoped>
/* Properties Container */
.properties-container {
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

/* Filters Section */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.search-bar i {
  color: #64748b;
  font-size: 1rem;
}

.search-bar input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 0.875rem;
  color: #1e293b;
}

.search-bar input::placeholder {
  color: #64748b;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #475569;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-select:hover {
  border-color: #cbd5e1;
}

.filter-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #475569;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-button:hover {
  background: #e2e8f0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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

/* Properties Table */
.properties-table {
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
  border-bottom: 1px solid #e2e8f0;
}

.table-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.results-count {
  color: #64748b;
  font-size: 0.875rem;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 6px;
}

.view-btn {
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn.active {
  background: white;
  color: #059669;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Modern Table */
.table-container {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}

.modern-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.modern-table th:hover {
  background: #f1f5f9;
}

.modern-table th i {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.table-row:hover {
  background: #f8fafc;
}

/* Table Cell Styles */
.address-cell {
  font-weight: 600;
}

.address-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.address-content i {
  color: #059669;
  font-size: 1rem;
}

.address-content small {
  display: block;
  color: #64748b;
  font-weight: 400;
  margin-top: 0.25rem;
}

.municipality-badge {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  color: #166534;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-badge.residential {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
}

.type-badge.commercial {
  background: linear-gradient(135deg, #fef3c7, #fed7aa);
  color: #92400e;
}

.type-badge.industrial {
  background: linear-gradient(135deg, #e9d5ff, #d8b4fe);
  color: #6b21a8;
}

.type-badge.agricultural {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  color: #166534;
}

.area-cell .area-content strong {
  color: #1e293b;
  font-size: 0.875rem;
}

.area-cell .area-content small {
  color: #64748b;
  margin-left: 0.25rem;
}

.value-cell .value-content strong {
  color: #059669;
  font-size: 0.875rem;
}

.value-cell .value-content small {
  display: block;
  color: #64748b;
  margin-top: 0.25rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.pending {
  background: #f1f5f9;
  color: #475569;
}

.status-badge.in_progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}

.action-btn.edit {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.edit:hover {
  background: #e5e7eb;
}

.action-btn.valuation {
  background: #dcfce7;
  color: #166534;
}

.action-btn.valuation:hover {
  background: #bbf7d0;
}

.action-btn.delete {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn.delete:hover {
  background: #fecaca;
}

/* Grid View */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.property-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s;
}

.property-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.property-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
}

.property-type-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.property-card .card-body {
  padding: 1.5rem;
}

.property-card .card-body h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.property-details {
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
}

.detail-item i {
  font-size: 0.75rem;
}

.property-value {
  margin-bottom: 1rem;
}

.property-value strong {
  color: #059669;
  font-size: 1.125rem;
}

.property-value small {
  display: block;
  color: #64748b;
  margin-top: 0.25rem;
}

.property-card .card-footer {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.card-action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.card-action-btn.primary {
  background: #059669;
  color: white;
}

.card-action-btn.primary:hover {
  background: #047857;
}

.card-action-btn.secondary {
  background: #f1f5f9;
  color: #475569;
}

.card-action-btn.secondary:hover {
  background: #e2e8f0;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #475569;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 1.5rem 0;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  color: #475569;
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
}

/* Responsive Design */
@media (max-width: 1024px) {
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
  
  .grid-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .property-card .card-footer {
    flex-direction: column;
  }
}
</style>
