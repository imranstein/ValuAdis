<template>
  <div class="vehicles-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Vehicle Valuations</h1>
        <p>Manage and track all vehicle valuations and assessments</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="exportVehicles">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button class="action-button primary" @click="router.push('/vehicles/create')">
          <i class="pi pi-plus"></i>
          Add Vehicle
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
            placeholder="Search vehicles by make, model, VIN, or plate..."
          />
        </div>
      </div>
      
      <div class="filter-section">
        <select v-model="selectedMake" class="filter-dropdown">
          <option value="">All Makes</option>
          <option v-for="make in makes" :key="make" :value="make">
            {{ make }}
          </option>
        </select>
        
        <select v-model="selectedYear" class="filter-dropdown">
          <option value="">All Years</option>
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        
        <select v-model="selectedRegion" class="filter-dropdown">
          <option value="">All Regions</option>
          <option value="Addis Ababa">Addis Ababa</option>
          <option value="Oromia">Oromia</option>
          <option value="Amhara">Amhara</option>
          <option value="Tigray">Tigray</option>
          <option value="Southern">Southern</option>
          <option value="Somali">Somali</option>
          <option value="Afar">Afar</option>
          <option value="Benishangul">Benishangul</option>
          <option value="Gambela">Gambela</option>
          <option value="Harari">Harari</option>
          <option value="Dire Dawa">Dire Dawa</option>
        </select>
        
        <select v-model="selectedStatus" class="filter-dropdown">
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="expired">Expired</option>
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
          <i class="pi pi-car"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalVehicles }}</h3>
          <p>Total Vehicles</p>
          <div class="stat-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>8% from last month</span>
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
            <span>12% from last month</span>
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
            <span>18% from last month</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Vehicle Registry -->
    <div class="vehicles-registry">
      <div class="registry-header">
        <h2>Vehicle Registry</h2>
        <div class="registry-info">
          <span>{{ filteredVehicles.length }} vehicles</span>
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
        <table class="vehicles-table">
          <thead>
            <tr>
              <th @click="sortBy('vehicle_name')">
                Vehicle
                <i class="pi" :class="getSortIcon('vehicle_name')"></i>
              </th>
              <th @click="sortBy('year')">
                Year
                <i class="pi" :class="getSortIcon('year')"></i>
              </th>
              <th @click="sortBy('vin')">
                VIN
                <i class="pi" :class="getSortIcon('vin')"></i>
              </th>
              <th @click="sortBy('plate_number')">
                Plate
                <i class="pi" :class="getSortIcon('plate_number')"></i>
              </th>
              <th @click="sortBy('region')">
                Region
                <i class="pi" :class="getSortIcon('region')"></i>
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
            <tr v-for="vehicle in paginatedVehicles" :key="vehicle.id">
              <td>
                <div class="vehicle-info">
                  <div class="vehicle-name">{{ vehicle.make }} {{ vehicle.model }}</div>
                  <div class="vehicle-details">{{ vehicle.body_type || 'N/A' }}</div>
                </div>
              </td>
              <td>
                <span class="year-badge">{{ vehicle.year }}</span>
              </td>
              <td>
                <span class="vin-text">{{ vehicle.vin }}</span>
              </td>
              <td>
                <span class="plate-number">{{ vehicle.plate_number }}</span>
              </td>
              <td>
                <span class="region-badge">{{ vehicle.region || 'N/A' }}</span>
              </td>
              <td>
                <div class="value-info">
                  <div class="market-value">{{ formatCurrency(vehicle.market_value) }}</div>
                  <div class="taxable-value">Tax: {{ formatCurrency(vehicle.taxable_value) }}</div>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="vehicle.status">{{ getStatusLabel(vehicle.status) }}</span>
              </td>
              <td>
                <span class="date">{{ formatDate(vehicle.created_date) }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view" @click="viewVehicle(vehicle)" title="View">
                    <i class="pi pi-eye"></i>
                  </button>
                  <button class="action-btn edit" @click="editVehicle(vehicle)" title="Edit">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="action-btn valuation" @click="createValuation(vehicle)" title="Valuate">
                    <i class="pi pi-calculator"></i>
                  </button>
                  <button class="action-btn download" @click="downloadVehicle(vehicle)" title="Download">
                    <i class="pi pi-download"></i>
                  </button>
                  <button class="action-btn delete" @click="deleteVehicle(vehicle)" title="Delete">
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
        <div v-for="vehicle in paginatedVehicles" :key="vehicle.id" class="vehicle-card">
          <div class="card-header">
            <div class="vehicle-info">
              <div class="vehicle-name">{{ vehicle.make }} {{ vehicle.model }}</div>
              <span class="status-badge" :class="vehicle.status">{{ getStatusLabel(vehicle.status) }}</span>
            </div>
            <div class="card-actions">
              <button class="action-btn view" @click="viewVehicle(vehicle)">
                <i class="pi pi-eye"></i>
              </button>
            </div>
          </div>
          
          <div class="card-content">
            <div class="vehicle-details">
              <div class="year-info">
                <span class="year-badge">{{ vehicle.year }}</span>
                <span class="body-type">{{ vehicle.body_type || 'N/A' }}</span>
              </div>
              <div class="identification">
                <div class="vin-info">
                  <span class="label">VIN:</span>
                  <span class="value">{{ vehicle.vin }}</span>
                </div>
                <div class="plate-info">
                  <span class="label">Plate:</span>
                  <span class="value">{{ vehicle.plate_number }}</span>
                </div>
              </div>
            </div>
            
            <div class="location-info">
              <span class="region-badge">{{ vehicle.region || 'N/A' }}</span>
            </div>
            
            <div class="value-details">
              <div class="market-value">{{ formatCurrency(vehicle.market_value) }}</div>
              <div class="taxable-value">Taxable: {{ formatCurrency(vehicle.taxable_value) }}</div>
            </div>
          </div>
          
          <div class="card-footer">
            <span class="date">{{ formatDate(vehicle.created_date) }}</span>
            <div class="card-actions">
              <button class="action-btn edit" @click="editVehicle(vehicle)">
                <i class="pi pi-pencil"></i>
              </button>
              <button class="action-btn valuation" @click="createValuation(vehicle)">
                <i class="pi pi-calculator"></i>
              </button>
              <button class="action-btn download" @click="downloadVehicle(vehicle)">
                <i class="pi pi-download"></i>
              </button>
              <button class="action-btn delete" @click="deleteVehicle(vehicle)">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredVehicles.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="pi pi-car"></i>
        </div>
        <h3>No vehicles found</h3>
        <p>Add your first vehicle to get started with valuations</p>
        <button class="action-button primary" @click="router.push('/vehicles/create')">
          <i class="pi pi-plus"></i>
          Add Vehicle
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="filteredVehicles.length > itemsPerPage" class="pagination">
      <div class="pagination-info">
        <span>Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredVehicles.length) }} of {{ filteredVehicles.length }} vehicles</span>
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
const selectedMake = ref('')
const selectedYear = ref('')
const selectedRegion = ref('')
const selectedStatus = ref('')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const sortField = ref('created_date')
const sortDirection = ref('desc')

const vehicles = ref([
  {
    id: 1,
    make: 'Toyota',
    model: 'Corolla',
    year: 2020,
    vin: '1HGBH41JXMN109186',
    plate_number: 'AA-123-BC',
    body_type: 'Sedan',
    fuel_type: 'Gasoline',
    transmission: 'Automatic',
    engine_capacity: 1798,
    mileage: 45000,
    color: 'White',
    region: 'Addis Ababa',
    city: 'Addis Ababa',
    import_year: 2020,
    custom_duty_paid: true,
    market_value: 850000,
    taxable_value: 212500,
    status: 'approved',
    created_date: '2024-01-15'
  },
  {
    id: 2,
    make: 'Hyundai',
    model: 'Tucson',
    year: 2021,
    vin: '2HMNU5AE7MH123456',
    plate_number: 'BB-456-DE',
    body_type: 'SUV',
    fuel_type: 'Gasoline',
    transmission: 'Automatic',
    engine_capacity: 1998,
    mileage: 35000,
    color: 'Silver',
    region: 'Oromia',
    city: 'Adama',
    import_year: 2021,
    custom_duty_paid: true,
    market_value: 1200000,
    taxable_value: 300000,
    status: 'pending',
    created_date: '2024-01-18'
  },
  {
    id: 3,
    make: 'Isuzu',
    model: 'NPR',
    year: 2019,
    vin: 'JALBE41V9L1234567',
    plate_number: 'CC-789-FG',
    body_type: 'Truck',
    fuel_type: 'Diesel',
    transmission: 'Manual',
    engine_capacity: 2999,
    mileage: 85000,
    color: 'Blue',
    region: 'Amhara',
    city: 'Bahir Dar',
    import_year: 2019,
    custom_duty_paid: false,
    market_value: 1500000,
    taxable_value: 375000,
    status: 'draft',
    created_date: '2024-01-20'
  }
])

// Available makes and years for filters
const makes = ref(['Toyota', 'Hyundai', 'Isuzu', 'Nissan', 'Honda', 'Mazda', 'Kia', 'Mercedes-Benz', 'BMW', 'Audi'])
const years = ref(Array.from({ length: 35 }, (_, i) => 2024 - i))

// Computed properties
const filteredVehicles = computed(() => {
  let filtered = vehicles.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(v => 
      v.make.toLowerCase().includes(query) ||
      v.model.toLowerCase().includes(query) ||
      v.vin.toLowerCase().includes(query) ||
      v.plate_number.toLowerCase().includes(query)
    )
  }

  if (selectedMake.value) {
    filtered = filtered.filter(v => v.make === selectedMake.value)
  }

  if (selectedYear.value) {
    filtered = filtered.filter(v => v.year === parseInt(selectedYear.value))
  }

  if (selectedRegion.value) {
    filtered = filtered.filter(v => v.region === selectedRegion.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(v => v.status === selectedStatus.value)
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

const paginatedVehicles = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredVehicles.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredVehicles.value.length / itemsPerPage.value)
})

const totalVehicles = computed(() => vehicles.value.length)
const pendingValuations = computed(() => vehicles.value.filter(v => v.status === 'pending').length)
const approvedValuations = computed(() => vehicles.value.filter(v => v.status === 'approved').length)
const totalMarketValue = computed(() => vehicles.value.reduce((sum, v) => sum + v.market_value, 0))

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
  selectedMake.value = ''
  selectedYear.value = ''
  selectedRegion.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
}

function viewVehicle(vehicle) {
  router.push(`/vehicles/${vehicle.id}`)
}

function editVehicle(vehicle) {
  router.push(`/vehicles/${vehicle.id}/edit`)
}

function createValuation(vehicle) {
  router.push(`/vehicles/${vehicle.id}/valuation`)
}

function downloadVehicle(vehicle) {
  // Download functionality
  console.log('Downloading vehicle:', vehicle.make, vehicle.model)
}

function deleteVehicle(vehicle) {
  if (confirm(`Are you sure you want to delete ${vehicle.make} ${vehicle.model}?`)) {
    const index = vehicles.value.findIndex(v => v.id === vehicle.id)
    if (index > -1) {
      vehicles.value.splice(index, 1)
    }
  }
}

function exportVehicles() {
  // Export functionality
  console.log('Exporting vehicles')
}

onMounted(() => {
  // Load vehicles from API
  console.log('Loading vehicles...')
})
</script>

<style scoped>
/* Vehicles Container */
.vehicles-container {
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

/* Vehicles Registry */
.vehicles-registry {
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

.vehicles-table {
  width: 100%;
  border-collapse: collapse;
}

.vehicles-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  user-select: none;
}

.vehicles-table th:hover {
  background: #f1f5f9;
}

.vehicles-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.vehicle-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.vehicle-name {
  font-weight: 600;
  color: #1e293b;
}

.vehicle-details {
  font-size: 0.875rem;
  color: #6b7280;
}

.year-badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.vin-text {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #6b7280;
}

.plate-number {
  font-weight: 500;
  color: #374151;
}

.region-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
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

.action-btn.valuation {
  background: #e0f2fe;
  color: #0369a1;
}

.action-btn.valuation:hover {
  background: #0369a1;
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

.vehicle-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s;
}

.vehicle-card:hover {
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

.vehicle-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-content {
  padding: 1.5rem;
}

.vehicle-details {
  margin-bottom: 1rem;
}

.year-info {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.body-type {
  font-size: 0.875rem;
  color: #6b7280;
}

.identification {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.vin-info, .plate-info {
  display: flex;
  font-size: 0.875rem;
}

.label {
  font-weight: 500;
  color: #6b7280;
  min-width: 40px;
}

.value {
  color: #374151;
}

.location-info {
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
