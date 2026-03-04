<template>
  <div class="vehicle-table">
    <div class="table-header">
      <h3>My Vehicles</h3>
      <div class="table-actions">
        <button @click="$emit('add-vehicle')" class="btn-primary">
          <span class="plus-icon">+</span>
          Add Vehicle
        </button>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search vehicles..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="vehicle-table-grid">
        <thead>
          <tr>
            <th @click="sortBy('make')">
              Vehicle
              <span class="sort-icon" :class="{ active: sortField === 'make' }">
                {{ sortField === 'make' ? (sortAsc ? '↑' : '↓') : '↕' }}
              </span>
            </th>
            <th @click="sortBy('year')">
              Year
              <span class="sort-icon" :class="{ active: sortField === 'year' }">
                {{ sortField === 'year' ? (sortAsc ? '↑' : '↓') : '↕' }}
              </span>
            </th>
            <th @click="sortBy('mileage')">
              Mileage
              <span class="sort-icon" :class="{ active: sortField === 'mileage' }">
                {{ sortField === 'mileage' ? (sortAsc ? '↑' : '↓') : '↕' }}
              </span>
            </th>
            <th @click="sortBy('region')">
              Region
              <span class="sort-icon" :class="{ active: sortField === 'region' }">
                {{ sortField === 'region' ? (sortAsc ? '↑' : '↓') : '↕' }}
              </span>
            </th>
            <th>Status</th>
            <th>Latest Valuation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td colspan="7" class="text-center">
              <div class="spinner"></div>
              Loading vehicles...
            </td>
          </tr>
          <tr v-else-if="filteredVehicles.length === 0" class="empty-row">
            <td colspan="7" class="text-center">
              <div class="empty-state">
                <div class="empty-icon">🚗</div>
                <p>No vehicles found</p>
                <button @click="$emit('add-vehicle')" class="btn-secondary">
                  Add Your First Vehicle
                </button>
              </div>
            </td>
          </tr>
          <tr
            v-for="vehicle in filteredVehicles"
            :key="vehicle.id"
            class="vehicle-row"
            :class="{ inactive: !vehicle.is_active }"
          >
            <td class="vehicle-info">
              <div class="vehicle-details">
                <div class="vehicle-name">
                  {{ vehicle.make }} {{ vehicle.model }}
                </div>
                <div class="vehicle-meta">
                  {{ vehicle.plate_number }} • {{ vehicle.vin.slice(-6) }}
                </div>
              </div>
            </td>
            <td>{{ vehicle.year }}</td>
            <td>
              <span v-if="vehicle.mileage" class="mileage">
                {{ formatNumber(vehicle.mileage) }} km
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td>
              <span v-if="vehicle.region" class="region-badge">
                {{ vehicle.region }}
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td>
              <span class="status-badge" :class="getStatusClass(vehicle)">
                {{ getStatusText(vehicle) }}
              </span>
            </td>
            <td>
              <div v-if="vehicle.latest_valuation" class="valuation-info">
                <div class="valuation-amount">
                  ETB {{ formatNumber(vehicle.latest_valuation.market_value) }}
                </div>
                <div class="valuation-date">
                  {{ formatDate(vehicle.latest_valuation.valuation_date) }}
                </div>
              </div>
              <span v-else class="text-gray-400">No valuation</span>
            </td>
            <td class="actions">
              <div class="action-buttons">
                <button
                  @click="$emit('view-vehicle', vehicle)"
                  class="btn-icon"
                  title="View Details"
                >
                  👁️
                </button>
                <button
                  @click="$emit('edit-vehicle', vehicle)"
                  class="btn-icon"
                  title="Edit Vehicle"
                >
                  ✏️
                </button>
                <button
                  @click="$emit('request-valuation', vehicle)"
                  class="btn-icon"
                  title="Request Valuation"
                  :disabled="!vehicle.is_active"
                >
                  💰
                </button>
                <button
                  @click="confirmDelete(vehicle)"
                  class="btn-icon danger"
                  title="Delete Vehicle"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="btn-pagination"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="btn-pagination"
      >
        Next
      </button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal.show" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <h3>Delete Vehicle</h3>
        <p>Are you sure you want to delete this vehicle?</p>
        <div class="vehicle-summary">
          <strong>{{ deleteModal.vehicle?.make }} {{ deleteModal.vehicle?.model }}</strong>
          <br>
          Plate: {{ deleteModal.vehicle?.plate_number }}
        </div>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn-secondary">
            Cancel
          </button>
          <button @click="confirmDeleteAction" class="btn-danger">
            Delete Vehicle
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  vehicles: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'add-vehicle',
  'view-vehicle',
  'edit-vehicle',
  'request-valuation',
  'delete-vehicle'
])

// Search and sorting
const searchQuery = ref('')
const sortField = ref('make')
const sortAsc = ref(true)
const currentPage = ref(1)
const itemsPerPage = 10

// Delete modal
const deleteModal = ref({
  show: false,
  vehicle: null
})

// Computed properties
const filteredVehicles = computed(() => {
  let filtered = props.vehicles

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(vehicle => 
      vehicle.make.toLowerCase().includes(query) ||
      vehicle.model.toLowerCase().includes(query) ||
      vehicle.plate_number.toLowerCase().includes(query) ||
      vehicle.vin.toLowerCase().includes(query)
    )
  }

  // Apply sorting
  filtered.sort((a, b) => {
    let aVal = a[sortField.value]
    let bVal = b[sortField.value]

    if (aVal === null || aVal === undefined) return 1
    if (bVal === null || bVal === undefined) return -1

    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }

    if (sortAsc.value) {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  // Apply pagination
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(props.vehicles.length / itemsPerPage)
})

// Methods
const sortBy = (field) => {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field
    sortAsc.value = true
  }
}

const getStatusClass = (vehicle) => {
  if (!vehicle.is_active) return 'inactive'
  if (!vehicle.is_verified) return 'pending'
  return 'active'
}

const getStatusText = (vehicle) => {
  if (!vehicle.is_active) return 'Inactive'
  if (!vehicle.is_verified) return 'Pending Verification'
  return 'Active'
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(num)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const confirmDelete = (vehicle) => {
  deleteModal.value = {
    show: true,
    vehicle
  }
}

const closeDeleteModal = () => {
  deleteModal.value = {
    show: false,
    vehicle: null
  }
}

const confirmDeleteAction = () => {
  if (deleteModal.value.vehicle) {
    emit('delete-vehicle', deleteModal.value.vehicle)
    closeDeleteModal()
  }
}
</script>

<style scoped>
.vehicle-table {
  @apply bg-white rounded-lg shadow-sm;
}

.table-header {
  @apply flex justify-between items-center p-6 border-b border-gray-200;
}

.table-header h3 {
  @apply text-lg font-semibold text-gray-900;
}

.table-actions {
  @apply flex items-center space-x-4;
}

.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700;
}

.btn-secondary {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50;
}

.btn-danger {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700;
}

.plus-icon {
  @apply mr-2 text-lg;
}

.search-box {
  @apply relative;
}

.search-input {
  @apply pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
  width: 300px;
}

.search-input::before {
  content: "🔍";
  @apply absolute left-3 top-2.5;
}

.table-container {
  @apply overflow-x-auto;
}

.vehicle-table-grid {
  @apply w-full;
}

.vehicle-table-grid th {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50;
}

.vehicle-table-grid td {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
}

.loading-row,
.empty-row {
  @apply text-center;
}

.spinner {
  @apply inline-block w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin;
  margin-right: 8px;
}

.empty-state {
  @apply py-8;
}

.empty-icon {
  @apply text-4xl mb-4;
}

.vehicle-row:hover {
  @apply bg-gray-50;
}

.vehicle-row.inactive {
  @apply opacity-60;
}

.vehicle-info {
  @apply font-medium;
}

.vehicle-name {
  @apply font-semibold;
}

.vehicle-meta {
  @apply text-xs text-gray-500;
}

.mileage {
  @apply text-gray-600;
}

.region-badge {
  @apply inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800;
}

.status-badge {
  @apply inline-flex px-2 py-1 text-xs font-medium rounded-full;
}

.status-badge.active {
  @apply bg-green-100 text-green-800;
}

.status-badge.pending {
  @apply bg-yellow-100 text-yellow-800;
}

.status-badge.inactive {
  @apply bg-gray-100 text-gray-800;
}

.valuation-info {
  @apply text-sm;
}

.valuation-amount {
  @apply font-semibold text-green-600;
}

.valuation-date {
  @apply text-xs text-gray-500;
}

.actions {
  @apply text-center;
}

.action-buttons {
  @apply flex justify-center space-x-1;
}

.btn-icon {
  @apply p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-icon.danger {
  @apply text-red-600 hover:bg-red-50;
}

.pagination {
  @apply flex justify-between items-center px-6 py-3 border-t border-gray-200;
}

.btn-pagination {
  @apply px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed;
}

.page-info {
  @apply text-sm text-gray-700;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-content {
  @apply bg-white rounded-lg p-6 max-w-md w-full mx-4;
}

.modal-content h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.vehicle-summary {
  @apply my-4 p-3 bg-gray-50 rounded text-sm;
}

.modal-actions {
  @apply flex justify-end space-x-3 mt-6;
}

.text-gray-400 {
  @apply text-gray-400;
}

.text-center {
  @apply text-center;
}
</style>
