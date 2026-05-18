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
                <div class="empty-icon"><i class="pi pi-car" aria-hidden="true"></i></div>
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
                  <i class="pi pi-eye" aria-hidden="true"></i>
                </button>
                <button
                  @click="$emit('edit-vehicle', vehicle)"
                  class="btn-icon"
                  title="Edit Vehicle"
                >
                  <i class="pi pi-pencil" aria-hidden="true"></i>
                </button>
                <button
                  @click="$emit('request-valuation', vehicle)"
                  class="btn-icon"
                  title="Request Valuation"
                  :disabled="!vehicle.is_active"
                >
                  <i class="pi pi-calculator" aria-hidden="true"></i>
                </button>
                <button
                  @click="confirmDelete(vehicle)"
                  class="btn-icon danger"
                  title="Delete Vehicle"
                >
                  <i class="pi pi-trash" aria-hidden="true"></i>
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
.search-input::before {
  content: "";
}
</style>
