<template>
  <div class="page-shell vehicles-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Vehicle asset registry</p>
        <h2 class="page-title">Vehicle valuation ledger.</h2>
        <p class="page-subtitle">
          Review registered vehicles, customs context, valuation readiness, and regional coverage from the live registry.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadVehicles">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
        <NuxtLink to="/vehicles/create" class="btn-primary">
          <i class="pi pi-plus" aria-hidden="true"></i>
          Register vehicle
        </NuxtLink>
      </div>
    </section>

    <section class="registry-toolbar panel">
      <div class="search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input v-model="searchQuery" type="search" placeholder="Search VIN, plate, make, model, or region" />
      </div>
      <select v-model="selectedRegion" class="filter-select" aria-label="Filter by region">
        <option value="">All regions</option>
        <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
      </select>
      <button class="icon-button" type="button" aria-label="Reset filters" @click="resetFilters">
        <i class="pi pi-filter-slash" aria-hidden="true"></i>
      </button>
    </section>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Vehicle records</h3>
          <p class="panel-subtitle">Showing {{ filteredVehicles.length }} of {{ vehicles.length }} backend records</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>Vehicle registry unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>VIN</th>
              <th>Vehicle</th>
              <th>Plate</th>
              <th>Region</th>
              <th>Customs</th>
              <th class="text-right">Mileage</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="8">Loading vehicle records...</td>
            </tr>
            <tr v-else-if="filteredVehicles.length === 0">
              <td colspan="8">No vehicle records match the current filters. Register a vehicle to start the valuation workflow.</td>
            </tr>
            <tr v-for="vehicle in filteredVehicles" v-else :key="vehicle.id">
              <td class="record-id">{{ vehicle.vin }}</td>
              <td>
                <strong>{{ vehicle.name }}</strong>
                <span>{{ vehicle.year }} · {{ vehicle.fuelType }}</span>
              </td>
              <td class="num">{{ vehicle.plateNumber }}</td>
              <td>{{ vehicle.region }}</td>
              <td>
                <span class="status-pill" :class="vehicle.customsClass">{{ vehicle.customsStatus }}</span>
              </td>
              <td class="text-right num">{{ vehicle.mileage }}</td>
              <td>
                <span class="status-pill" :class="vehicle.statusClass">{{ vehicle.status }}</span>
              </td>
              <td class="text-right">
                <button class="icon-button inline" type="button" aria-label="View vehicle" @click="viewVehicle(vehicle)">
                  <i class="pi pi-eye" aria-hidden="true"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const searchQuery = ref('')
const selectedRegion = ref('')
const loading = ref(true)
const errorMessage = ref('')
const vehicles = ref<any[]>([])
const summary = ref<any>(null)

const filteredVehicles = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return vehicles.value.filter((vehicle) => {
    const matchesSearch = !q || [vehicle.vin, vehicle.plateNumber, vehicle.name, vehicle.region].some((value) => value.toLowerCase().includes(q))
    const matchesRegion = !selectedRegion.value || vehicle.region === selectedRegion.value
    return matchesSearch && matchesRegion
  })
})

const regions = computed(() => Array.from(new Set(vehicles.value.map((vehicle) => vehicle.region))).filter(Boolean).sort())

const metrics = computed(() => [
  { label: 'Registered vehicles', value: String(summary.value?.total_vehicles ?? vehicles.value.length), note: 'Loaded from vehicle API' },
  { label: 'Valuations', value: String(summary.value?.total_valuations ?? 0), note: 'Linked valuation records' },
  { label: 'Market value', value: formatCurrency(summary.value?.total_market_value ?? 0), note: 'Vehicle valuation exposure' },
  { label: 'Recent valuations', value: String(summary.value?.recent_valuations ?? 0), note: 'Created in the last 30 days' },
])

onMounted(loadVehicles)

async function loadVehicles() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [vehiclesResponse, summaryResponse] = await Promise.all([
      fetch(`${apiBase}/api/v1/vehicles`, { headers: authHeaders() }),
      fetch(`${apiBase}/api/v1/vehicles/statistics/summary`, { headers: authHeaders() }),
    ])

    if (!vehiclesResponse.ok) throw new Error(`Vehicle records request failed with ${vehiclesResponse.status}`)

    const rows = await vehiclesResponse.json()
    vehicles.value = Array.isArray(rows) ? rows.map(normalizeVehicle) : []

    if (summaryResponse.ok) summary.value = await summaryResponse.json()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load vehicle records.'
  } finally {
    loading.value = false
  }
}

function authHeaders() {
  return { Authorization: `Bearer ${getAccessToken()}` }
}

function normalizeVehicle(vehicle: any) {
  const region = vehicle.region || vehicle.city || 'Unassigned'
  const customsPaid = Boolean(vehicle.custom_duty_paid)
  return {
    id: String(vehicle.id),
    vin: vehicle.vin || 'VIN pending',
    name: [vehicle.make, vehicle.model].filter(Boolean).join(' ') || 'Unnamed vehicle',
    year: vehicle.year || 'Year pending',
    fuelType: labelize(vehicle.fuel_type || vehicle.body_type || 'vehicle'),
    plateNumber: vehicle.plate_number || 'Plate pending',
    region,
    customsStatus: customsPaid ? 'Duty paid' : 'Duty pending',
    customsClass: customsPaid ? 'good' : 'warn',
    mileage: vehicle.mileage ? `${Number(vehicle.mileage).toLocaleString()} km` : 'Not recorded',
    status: vehicle.is_active === false ? 'Inactive' : 'Active',
    statusClass: vehicle.is_active === false ? 'muted' : 'good',
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedRegion.value = ''
}

function viewVehicle(vehicle: any) {
  router.push(`/vehicles/${vehicle.id}`)
}

function formatCurrency(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function labelize(value: string) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}
</script>

<style scoped>
.registry-toolbar {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(180px, 240px) 40px;
  gap: 10px;
  align-items: center;
  padding: 14px;
}

.search-field {
  min-width: 0;
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 12px;
}

.search-field input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
}

.filter-select {
  min-height: 40px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink-soft);
  padding: 0 10px;
}

@media (max-width: 820px) {
  .registry-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
