<template>
  <div class="vehicle-details">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <button class="back-button" @click="router.back()">
          <i class="pi pi-arrow-left"></i>
          Back
        </button>
        <h1>{{ vehicle.make }} {{ vehicle.model }} {{ vehicle.year }}</h1>
        <div class="vehicle-meta">
          <span class="meta-item">{{ vehicle.vin }}</span>
          <span class="meta-item">{{ vehicle.plate_number }}</span>
          <span class="status-badge" :class="vehicle.status">{{ getStatusLabel(vehicle.status) }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="editVehicle">
          <i class="pi pi-pencil"></i>
          Edit
        </button>
        <button class="action-button primary" @click="createValuation">
          <i class="pi pi-calculator"></i>
          New Valuation
        </button>
      </div>
    </div>

    <div v-if="actionStatus" class="action-status">
      {{ actionStatus }}
    </div>

    <div class="details-content">
      <div class="content-grid">
        <!-- Vehicle Information -->
        <div class="content-section">
          <div class="section-header">
            <h2>Vehicle Information</h2>
            <button @click="toggleEdit('vehicle')" class="edit-btn">
              <i class="pi pi-pencil"></i>
            </button>
          </div>
          
          <div class="info-grid">
            <div class="info-group">
              <h3>Basic Details</h3>
              <div class="info-item">
                <span class="info-label">Make</span>
                <span class="info-value">{{ vehicle.make }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Model</span>
                <span class="info-value">{{ vehicle.model }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Year</span>
                <span class="info-value">{{ vehicle.year }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">VIN</span>
                <span class="info-value">{{ vehicle.vin }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Plate Number</span>
                <span class="info-value">{{ vehicle.plate_number }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Color</span>
                <span class="info-value">{{ vehicle.color || 'N/A' }}</span>
              </div>
            </div>

            <div class="info-group">
              <h3>Specifications</h3>
              <div class="info-item">
                <span class="info-label">Body Type</span>
                <span class="info-value">{{ vehicle.body_type || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Fuel Type</span>
                <span class="info-value">{{ vehicle.fuel_type || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Transmission</span>
                <span class="info-value">{{ vehicle.transmission || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Engine Capacity</span>
                <span class="info-value">{{ vehicle.engine_capacity ? `${vehicle.engine_capacity} cc` : 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Mileage</span>
                <span class="info-value">{{ vehicle.mileage ? `${formatNumber(vehicle.mileage)} km` : 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Previous Owners</span>
                <span class="info-value">{{ vehicle.previous_owners || 1 }}</span>
              </div>
            </div>

            <div class="info-group">
              <h3>Ethiopian Market Information</h3>
              <div class="info-item">
                <span class="info-label">Region</span>
                <span class="info-value">{{ vehicle.region || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">City</span>
                <span class="info-value">{{ vehicle.city || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Import Year</span>
                <span class="info-value">{{ vehicle.import_year || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Customs Duty</span>
                <span class="info-value">{{ vehicle.custom_duty_paid ? 'Paid' : 'Unpaid' }}</span>
              </div>
              <div class="info-item" v-if="vehicle.customs_declaration_number">
                <span class="info-label">Customs Declaration</span>
                <span class="info-value">{{ vehicle.customs_declaration_number }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Latest Valuation -->
        <div class="content-section">
          <div class="section-header">
            <h2>Latest Valuation</h2>
            <button @click="createValuation" class="action-button primary small">
              <i class="pi pi-plus"></i>
              New Valuation
            </button>
          </div>
          
          <div v-if="latestValuation" class="valuation-summary">
            <div class="valuation-card">
              <div class="valuation-header">
                <div class="valuation-date">
                  <i class="pi pi-calendar"></i>
                  <span>{{ formatDate(latestValuation.created_date) }}</span>
                </div>
                <div class="valuation-status" :class="latestValuation.status">
                  {{ getStatusLabel(latestValuation.status) }}
                </div>
              </div>
              
              <div class="valuation-values">
                <div class="value-item primary">
                  <span class="value-label">Market Value</span>
                  <span class="value-amount">{{ formatCurrency(latestValuation.market_value) }}</span>
                </div>
                <div class="value-item secondary">
                  <span class="value-label">Taxable Value</span>
                  <span class="value-amount">{{ formatCurrency(latestValuation.taxable_value) }}</span>
                </div>
                <div class="value-item tertiary">
                  <span class="value-label">Confidence</span>
                  <span class="value-amount">{{ latestValuation.confidence_score }}%</span>
                </div>
              </div>
              
              <div class="valuation-factors">
                <div class="factor-row">
                  <span class="factor-label">Regional</span>
                  <span class="factor-value">{{ latestValuation.regional_multiplier }}x</span>
                </div>
                <div class="factor-row">
                  <span class="factor-label">Customs</span>
                  <span class="factor-value">{{ latestValuation.customs_multiplier }}x</span>
                </div>
                <div class="factor-row">
                  <span class="factor-label">Make Reliability</span>
                  <span class="factor-value">{{ latestValuation.make_reliability_multiplier }}x</span>
                </div>
                <div class="factor-row">
                  <span class="factor-label">Condition</span>
                  <span class="factor-value">{{ latestValuation.condition_multiplier }}x</span>
                </div>
              </div>
              
              <div class="valuation-actions">
                <button @click="viewValuation(latestValuation)" class="action-button secondary small">
                  <i class="pi pi-eye"></i>
                  View Details
                </button>
                <button @click="downloadValuation(latestValuation)" class="action-button secondary small">
                  <i class="pi pi-download"></i>
                  Download
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="no-valuation">
            <div class="no-valuation-icon">
              <i class="pi pi-calculator"></i>
            </div>
            <h3>No Valuations Yet</h3>
            <p>Create your first valuation to see market analysis</p>
            <button @click="createValuation" class="action-button primary">
              <i class="pi pi-plus"></i>
              Create Valuation
            </button>
          </div>
        </div>

        <!-- Valuation History -->
        <div class="content-section full-width">
          <div class="section-header">
            <h2>Valuation History</h2>
            <div class="header-controls">
              <select v-model="historyFilter" class="filter-select">
                <option value="all">All Valuations</option>
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
                <option value="draft">Draft</option>
              </select>
              <button @click="exportHistory" class="action-button secondary small">
                <i class="pi pi-download"></i>
                Export
              </button>
            </div>
          </div>
          
          <div class="valuation-history">
            <div v-if="filteredValuations.length > 0" class="history-table">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Market Value</th>
                    <th>Taxable Value</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="valuation in filteredValuations" :key="valuation.id">
                    <td>
                      <span class="date">{{ formatDate(valuation.created_date) }}</span>
                    </td>
                    <td>
                      <span class="value">{{ formatCurrency(valuation.market_value) }}</span>
                    </td>
                    <td>
                      <span class="value">{{ formatCurrency(valuation.taxable_value) }}</span>
                    </td>
                    <td>
                      <span class="confidence">{{ valuation.confidence_score }}%</span>
                    </td>
                    <td>
                      <span class="status-badge" :class="valuation.status">
                        {{ getStatusLabel(valuation.status) }}
                      </span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button @click="viewValuation(valuation)" class="action-btn view" title="View">
                          <i class="pi pi-eye"></i>
                        </button>
                        <button @click="downloadValuation(valuation)" class="action-btn download" title="Download">
                          <i class="pi pi-download"></i>
                        </button>
                        <button @click="deleteValuation(valuation)" class="action-btn delete" title="Delete">
                          <i class="pi pi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-else class="no-history">
              <div class="no-history-icon">
                <i class="pi pi-history"></i>
              </div>
              <h3>No Valuation History</h3>
              <p>Valuation history will appear here once you create valuations</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Valuation Modal -->
    <div v-if="showValuationModal" class="modal-overlay" @click="closeValuationModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Valuation Details</h3>
          <button @click="closeValuationModal" class="close-button">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <VehicleValuation
            :vehicle="vehicle"
            :valuation="selectedValuation"
            @generate-report="generateReport"
            @share="shareValuation"
            @export="exportValuation"
            @print="printValuation"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VehicleValuation from '@/components/vehicle/VehicleValuation.vue'
import { getAccessToken } from '~/utils/authToken'

const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

// Reactive data
const vehicle = ref({})
const valuations = ref([])
const latestValuation = ref(null)
const historyFilter = ref('all')
const showValuationModal = ref(false)
const selectedValuation = ref(null)
const actionStatus = ref('')

// Computed properties
const filteredValuations = computed(() => {
  if (historyFilter.value === 'all') return valuations.value
  return valuations.value.filter(v => v.status === historyFilter.value)
})

// Methods
async function loadVehicle() {
  try {
    const token = getAccessToken()
    
    if (!token) {
      router.push('/login')
      return
    }

    const response = await fetch(`${apiBase}/api/v1/vehicles/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      vehicle.value = result.data || result
    } else {
      throw new Error(`HTTP ${response.status}: Failed to load vehicle`)
    }
  } catch (error) {
    actionStatus.value = error instanceof Error ? error.message : 'Failed to load vehicle.'
    vehicle.value = null
  }
}

async function loadValuations() {
  try {
    const token = getAccessToken()
    
    if (!token) {
      return
    }

    const response = await fetch(`${apiBase}/api/v1/vehicles/${route.params.id}/valuations`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      valuations.value = Array.isArray(result) ? result : (result.data || [])
      latestValuation.value = valuations.value[0] || null
    } else {
      throw new Error(`HTTP ${response.status}: Failed to load valuations`)
    }
  } catch (error) {
    actionStatus.value = error instanceof Error ? error.message : 'Failed to load valuation history.'
    valuations.value = []
  }
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

function formatNumber(value) {
  return new Intl.NumberFormat('en-ET').format(value)
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date))
}

function editVehicle() {
  router.push(`/vehicles/create?vehicle_id=${vehicle.value.id}`)
}

async function createValuation() {
  const token = getAccessToken()
  if (!token) {
    router.push('/login')
    return
  }

  const response = await fetch(`${apiBase}/api/v1/vehicles/${vehicle.value.id}/valuation`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })

  if (response.ok) {
    const valuation = await response.json()
    latestValuation.value = valuation
    valuations.value = [valuation, ...valuations.value.filter((item) => item.id !== valuation.id)]
  }
}

function viewValuation(valuation) {
  selectedValuation.value = valuation
  showValuationModal.value = true
}

function closeValuationModal() {
  showValuationModal.value = false
  selectedValuation.value = null
}

function downloadValuation(valuation) {
  downloadJson(valuation, `vehicle-valuation-${valuation.id || 'record'}.json`)
}

function deleteValuation(valuation) {
  const index = valuations.value.findIndex(v => v.id === valuation.id)
  if (index > -1) {
    valuations.value.splice(index, 1)
    actionStatus.value = 'Valuation removed from this local review list.'
    if (latestValuation.value?.id === valuation.id) {
      latestValuation.value = valuations.value[0] || null
    }
  }
}

function exportHistory() {
  const rows = valuations.value.map((valuation) => ({
    id: valuation.id,
    status: valuation.status,
    market_value: valuation.market_value,
    taxable_value: valuation.taxable_value,
    valuation_date: valuation.valuation_date || valuation.created_at,
  }))
  downloadCsv(rows, `vehicle-${vehicle.value.id || route.params.id}-valuations.csv`)
}

function generateReport() {
  const payload = {
    vehicle: vehicle.value,
    latest_valuation: latestValuation.value,
    valuation_history: valuations.value,
    generated_at: new Date().toISOString(),
  }
  downloadJson(payload, `vehicle-${vehicle.value.id || route.params.id}-report.json`)
}

function shareValuation() {
  const summary = latestValuation.value
    ? `${vehicle.value.make} ${vehicle.value.model} valuation: ${formatCurrency(latestValuation.value.market_value)}`
    : `${vehicle.value.make} ${vehicle.value.model} valuation record`
  if (navigator.share) {
    navigator.share({ title: 'ValuAdis vehicle valuation', text: summary, url: window.location.href })
      .catch(() => {
        actionStatus.value = 'Share cancelled'
      })
    return
  }
  navigator.clipboard?.writeText(`${summary} - ${window.location.href}`)
  actionStatus.value = 'Valuation link copied'
}

function exportValuation() {
  if (selectedValuation.value) {
    downloadJson(selectedValuation.value, `vehicle-valuation-${selectedValuation.value.id || 'record'}.json`)
  }
}

function printValuation() {
  window.print()
}

function downloadJson(payload, filename) {
  downloadBlob(JSON.stringify(payload, null, 2), filename, 'application/json')
}

function downloadCsv(rows, filename) {
  if (!rows.length) {
    actionStatus.value = 'No valuation history to export'
    return
  }
  const headers = Object.keys(rows[0])
  const csv = [
    headers.join(','),
    ...rows.map((row) => headers.map((header) => JSON.stringify(row[header] ?? '')).join(',')),
  ].join('\n')
  downloadBlob(csv, filename, 'text/csv')
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  actionStatus.value = `Downloaded ${filename}`
}

onMounted(async () => {
  await loadVehicle()
  await loadValuations()
})
</script>

<style scoped>
.vehicle-details {
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
  background: linear-gradient(135deg, var(--green) 0%, var(--green) 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 1rem;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.vehicle-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 0.875rem;
  opacity: 0.9;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.approved {
  background: rgba(255, 255, 255, 0.2);
  color: white;
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
  color: var(--green);
}

.action-button.primary:hover {
  background: var(--surface-2);
  transform: translateY(-1px);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.action-button.small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.action-status {
  margin: -1rem 0 1.5rem;
  padding: 0.875rem 1rem;
  border: 1px solid var(--green-soft);
  border-radius: 8px;
  background: var(--green-soft);
  color: var(--green-dark);
  font-size: 0.875rem;
  font-weight: 600;
}

/* Content Grid */
.details-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.content-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--line);
  overflow: hidden;
}

.content-section.full-width {
  grid-column: 1 / -1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink-soft);
  margin: 0;
}

.edit-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--surface-2);
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: var(--line);
  color: var(--ink-soft);
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: white;
  font-size: 0.875rem;
}

/* Information Grid */
.info-grid {
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.info-group h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink-soft);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--line);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--surface-2);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: var(--muted);
  font-size: 0.875rem;
}

.info-value {
  color: var(--ink-soft);
  font-weight: 500;
  font-size: 0.875rem;
}

/* Valuation Summary */
.valuation-summary {
  padding: 2rem;
}

.valuation-card {
  background: var(--surface-2);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--line);
}

.valuation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.valuation-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--muted);
  font-size: 0.875rem;
}

.valuation-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.valuation-status.approved {
  background: var(--green-soft);
  color: var(--green-dark);
}

.valuation-values {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.value-item {
  text-align: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--line);
}

.value-item.primary {
  border-left: 4px solid var(--green);
}

.value-item.secondary {
  border-left: 4px solid var(--blue);
}

.value-item.tertiary {
  border-left: 4px solid var(--gold);
}

.value-label {
  display: block;
  font-size: 0.75rem;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

.value-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ink-soft);
}

.valuation-factors {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.factor-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 6px;
}

.factor-label {
  font-size: 0.75rem;
  color: var(--muted);
}

.factor-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--green);
}

.valuation-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

/* No Valuation State */
.no-valuation {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--muted);
}

.no-valuation-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
  background: var(--surface-2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-size: 1.5rem;
}

.no-valuation h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink-soft);
  margin: 0 0 0.5rem 0;
}

.no-valuation p {
  margin: 0 0 2rem 0;
}

/* Valuation History */
.valuation-history {
  padding: 2rem;
}

.history-table {
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background: var(--surface-2);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--line);
}

.history-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--surface-2);
}

.date {
  color: var(--muted);
  font-size: 0.875rem;
}

.value {
  font-weight: 600;
  color: var(--green);
}

.confidence {
  font-weight: 500;
  color: var(--gold);
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
  background: var(--blue-soft);
  color: var(--blue);
}

.action-btn.view:hover {
  background: var(--blue);
  color: white;
}

.action-btn.download {
  background: var(--blue-soft);
  color: var(--blue);
}

.action-btn.download:hover {
  background: var(--blue);
  color: white;
}

.action-btn.delete {
  background: var(--red-soft);
  color: var(--red);
}

.action-btn.delete:hover {
  background: var(--red);
  color: white;
}

.no-history {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--muted);
}

.no-history-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
  background: var(--surface-2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  font-size: 1.5rem;
}

.no-history h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink-soft);
  margin: 0 0 0.5rem 0;
}

/* Modal */
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
  padding: 2rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  width: 100%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--line);
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink-soft);
  margin: 0;
}

.close-button {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--surface-2);
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
}

.close-button:hover {
  background: var(--line);
  color: var(--ink-soft);
}

.modal-body {
  padding: 2rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .details-content {
    grid-template-columns: 1fr;
  }
  
  .valuation-values {
    grid-template-columns: 1fr;
  }
  
  .valuation-factors {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .vehicle-meta {
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .valuation-actions {
    flex-direction: column;
  }
  
  .action-button {
    justify-content: center;
  }
  
  .modal-overlay {
    padding: 1rem;
  }
}
</style>
