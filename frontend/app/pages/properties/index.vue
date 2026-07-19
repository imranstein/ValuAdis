<template>
  <div class="page-shell properties-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Property registry</p>
        <h2 class="page-title">Registered civic assets.</h2>
        <p class="page-subtitle">
          Review land titles, buildings, municipal coverage, valuation readiness, and record status without leaving the registry surface.
        </p>
      </div>
      <div class="page-actions">
        <NuxtLink to="/properties/import" class="btn-secondary">
          <i class="pi pi-upload" aria-hidden="true"></i>
          Import
        </NuxtLink>
        <button class="btn-secondary" type="button" @click="exportProperties">
          <i class="pi pi-download" aria-hidden="true"></i>
          Export
        </button>
        <NuxtLink to="/properties/create" class="btn-primary">
          <i class="pi pi-plus" aria-hidden="true"></i>
          Create property
        </NuxtLink>
      </div>
    </section>

    <section class="registry-toolbar panel">
      <div class="search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input v-model="searchQuery" type="search" placeholder="Search by address or property ID" />
      </div>
      <select v-model="selectedMunicipality" class="filter-select" aria-label="Filter by municipality">
        <option value="">All municipalities</option>
        <option value="Addis Ababa">Addis Ababa</option>
        <option value="Mekelle">Mekelle</option>
        <option value="Dire Dawa">Dire Dawa</option>
        <option value="Bahir Dar">Bahir Dar</option>
      </select>
      <select v-model="selectedType" class="filter-select" aria-label="Filter by property type">
        <option value="">All types</option>
        <option value="residential">Residential</option>
        <option value="commercial">Commercial</option>
        <option value="industrial">Industrial</option>
        <option value="agricultural">Agricultural</option>
      </select>
      <button class="icon-button" type="button" aria-label="Reset filters" @click="resetFilters">
        <i class="pi pi-refresh" aria-hidden="true"></i>
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
          <h3 class="panel-title">Property records</h3>
          <p class="panel-subtitle">Showing {{ filteredProperties.length }} of {{ allProperties.length }} backend records</p>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Property ID</th>
              <th>Address</th>
              <th>Type</th>
              <th>Municipality</th>
              <th class="text-right">Market value</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7">Loading property records...</td>
            </tr>
            <tr v-else-if="filteredProperties.length === 0">
              <td colspan="7">No property records match the current filters.</td>
            </tr>
            <tr v-for="property in filteredProperties" v-else :key="property.id">
              <td class="record-id">{{ property.id }}</td>
              <td>
                <strong>{{ property.address }}</strong>
                <span>{{ property.area }}</span>
              </td>
              <td>
                <span class="status-pill">{{ property.typeLabel }}</span>
              </td>
              <td>{{ property.municipality }}</td>
              <td class="text-right num">{{ property.value }}</td>
              <td>
                <span class="status-pill" :class="property.statusClass">{{ property.status }}</span>
              </td>
              <td class="text-right">
                <button class="icon-button inline" type="button" aria-label="View property" @click="viewProperty(property)">
                  <i class="pi pi-eye" aria-hidden="true"></i>
                </button>
                <button class="icon-button inline" type="button" aria-label="Edit property" @click="editProperty(property)">
                  <i class="pi pi-pencil" aria-hidden="true"></i>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
// Saved filters (U8): persist the operator's registry filter selection per
// device so it survives navigation and reloads.
const FILTER_STORAGE_KEY = 'valuadis_property_filters'
const searchQuery = ref('')
const selectedMunicipality = ref('')
const selectedType = ref('')

function restoreFilters() {
  if (!process.client) return
  try {
    const saved = JSON.parse(localStorage.getItem(FILTER_STORAGE_KEY) || '{}')
    searchQuery.value = saved.search || ''
    selectedMunicipality.value = saved.municipality || ''
    selectedType.value = saved.type || ''
  } catch {
    /* ignore malformed saved filters */
  }
}

watch([searchQuery, selectedMunicipality, selectedType], ([search, municipality, type]) => {
  if (!process.client) return
  localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify({ search, municipality, type }))
})
const loading = ref(true)
const allProperties = ref<any[]>([])
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const filteredProperties = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return allProperties.value.filter((property) => {
    const matchesSearch = !q || property.address.toLowerCase().includes(q) || property.id.toLowerCase().includes(q)
    const matchesMunicipality = !selectedMunicipality.value || property.municipality === selectedMunicipality.value
    const matchesType = !selectedType.value || property.type === selectedType.value
    return matchesSearch && matchesMunicipality && matchesType
  })
})

const metrics = computed(() => [
  { label: 'Total properties', value: String(allProperties.value.length), note: 'Loaded from registry API' },
  { label: 'Commercial assets', value: String(allProperties.value.filter((property) => property.type === 'commercial').length), note: 'Commercial portfolio count' },
  { label: 'Residential', value: String(allProperties.value.filter((property) => property.type === 'residential').length), note: 'Residential portfolio count' },
  { label: 'Under review', value: String(allProperties.value.filter((property) => property.statusClass === 'warn').length), note: 'Require valuation attention' }
])

onMounted(() => {
  restoreFilters()
  loadProperties()
})

async function loadProperties() {
  loading.value = true
  try {
    const response = await fetch(`${apiBase}/api/v1/properties`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) return
    const json = await response.json()
    const rows = Array.isArray(json.data) ? json.data : []
    allProperties.value = rows.map(normalizeProperty)
  } finally {
    loading.value = false
  }
}

function normalizeProperty(property: any) {
  const status = property.status || 'active'
  return {
    id: String(property.id),
    address: property.address || 'Unaddressed property',
    area: [property.neighborhood, property.subcity, property.region].filter(Boolean).join(', ') || `${Number(property.area_sqm || 0).toLocaleString()} m²`,
    type: property.property_type || 'unknown',
    typeLabel: labelize(property.property_type || 'unknown'),
    municipality: property.municipality || 'Unassigned',
    value: formatCurrency(property.market_value || property.ai_estimated_value || 0),
    status: labelize(status),
    statusClass: ['pending', 'review', 'draft'].includes(String(status).toLowerCase()) ? 'warn' : 'good',
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedMunicipality.value = ''
  selectedType.value = ''
}

function viewProperty(property: { id: string }) {
  router.push(`/properties/${property.id}`)
}

function editProperty(property: { id: string }) {
  router.push(`/properties/edit/${property.id}`)
}

async function exportProperties() {
  const response = await fetch(`${apiBase}/api/v1/properties/export?format=csv`, {
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  })
  if (!response.ok) return
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'properties_export.csv'
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function labelize(value: string) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}

useHead({
  title: 'Property Registry - ValuAdis',
  meta: [{ name: 'description', content: 'Federal property database management.' }]
})
</script>

<style scoped>
.registry-toolbar {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 210px 180px 40px;
  gap: 10px;
  align-items: center;
  padding: 14px;
}

.search-field {
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

.table-head {
  margin: 0;
  padding: 20px 22px;
  border-bottom: 1px solid var(--line);
}

.record-id {
  color: var(--green);
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 800;
}

.data-table td strong,
.data-table td span:not(.status-pill) {
  display: block;
}

.data-table td span:not(.status-pill) {
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
}

.icon-button.inline {
  display: inline-grid;
  margin-left: 6px;
}

@media (max-width: 1000px) {
  .registry-toolbar {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .registry-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
