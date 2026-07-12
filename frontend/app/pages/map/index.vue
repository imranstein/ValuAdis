<template>
  <div class="page-shell map-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">GIS Command</p>
        <h1 class="page-title">Asset Map</h1>
        <p class="page-subtitle">
          Spatial review for taxable assets, compliance overlays, and valuation activity across Addis Ababa corridors.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button">
          <i class="pi pi-sliders-h" aria-hidden="true"></i>
          Layers
        </button>
        <button class="btn-primary" type="button">
          <i class="pi pi-plus" aria-hidden="true"></i>
          New Valuation
        </button>
      </div>
    </section>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="map-workspace">
      <div class="panel map-panel">
        <div class="panel-head map-toolbar">
          <div>
            <h2 class="panel-title">Cadastral asset grid</h2>
            <p class="panel-subtitle">{{ mapStatus }}</p>
          </div>
          <div class="layer-tabs" aria-label="Map layers">
            <button
              v-for="layer in layers"
              :key="layer"
              class="layer-tab"
              :class="{ active: activeLayer === layer }"
              type="button"
              @click="activeLayer = layer"
            >
              {{ layer }}
            </button>
          </div>
        </div>

        <div class="civic-map" data-testid="asset-map-canvas">
          <div class="map-grid-lines" aria-hidden="true"></div>
          <div class="road primary-road" aria-hidden="true"></div>
          <div class="road secondary-road" aria-hidden="true"></div>
          <div v-if="loading" class="map-empty">Loading backend property coordinates...</div>
          <div v-else-if="loadError" class="map-empty">{{ loadError }}</div>
          <div v-else-if="assets.length === 0" class="map-empty">No geocoded backend properties are available yet.</div>
          <button
            v-for="asset in assets"
            :key="asset.id"
            class="asset-marker"
            :class="[asset.kind, { active: selectedAsset?.id === asset.id }]"
            :style="{ left: asset.x, top: asset.y }"
            type="button"
            @click="selectedAsset = asset"
          >
            <span>{{ asset.code }}</span>
          </button>
          <div class="map-scale">500 m</div>
          <div class="map-coordinates">9.0116 N / 38.7616 E</div>
        </div>
      </div>

      <aside v-if="selectedAsset" class="panel selected-panel">
        <div class="panel-head">
          <div>
            <p class="page-kicker">Active Selection</p>
            <h2 class="panel-title">{{ selectedAsset.name }}</h2>
            <p class="panel-subtitle">{{ selectedAsset.id }} · {{ selectedAsset.subCity }}</p>
          </div>
          <span class="status-pill" :class="selectedAsset.statusClass">{{ selectedAsset.status }}</span>
        </div>

        <div class="asset-summary">
          <div>
            <p class="metric-label">Valuation</p>
            <p class="asset-value">{{ selectedAsset.value }}</p>
          </div>
          <div>
            <p class="metric-label">Risk</p>
            <p class="asset-risk">{{ selectedAsset.risk }}</p>
          </div>
        </div>

        <div class="detail-list">
          <div v-for="item in selectedDetails" :key="item.label" class="detail-row">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>

        <div class="panel inspection-panel">
          <p class="metric-label">Field Note</p>
          <p>
            {{ selectedAsset.note }}
          </p>
        </div>

        <div class="page-actions">
          <NuxtLink class="btn-primary" :to="`/properties/${selectedAsset.propertyId}`">
            <i class="pi pi-file-edit" aria-hidden="true"></i>
            Open Record
          </NuxtLink>
          <button class="btn-secondary" type="button">
            <i class="pi pi-history" aria-hidden="true"></i>
            History
          </button>
        </div>
      </aside>
    </section>

    <section class="table-panel">
      <div class="panel-head map-table-head">
        <div>
          <h2 class="panel-title">Spatial Exceptions</h2>
          <p class="panel-subtitle">Assets needing field review before the next valuation run.</p>
        </div>
        <span class="status-pill warn">4 Open</span>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Asset</th>
              <th>Sub-city</th>
              <th>Exception</th>
              <th class="text-right">Value</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5" class="empty-cell">Loading spatial records...</td>
            </tr>
            <tr v-else-if="loadError">
              <td colspan="5" class="empty-cell">{{ loadError }}</td>
            </tr>
            <tr v-else-if="assets.length === 0">
              <td colspan="5" class="empty-cell">No geocoded backend properties are available yet.</td>
            </tr>
            <tr v-for="asset in assets" v-else :key="asset.id">
              <td>{{ asset.name }}</td>
              <td>{{ asset.subCity }}</td>
              <td>{{ asset.exception }}</td>
              <td class="text-right">{{ asset.value }}</td>
              <td><span class="status-pill" :class="asset.statusClass">{{ asset.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

type Asset = {
  id: string
  propertyId: number
  name: string
  subCity: string
  code: string
  x: string
  y: string
  kind: string
  value: string
  risk: string
  status: string
  statusClass: string
  exception: string
  area: string
  zoning: string
  owner: string
  note: string
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl
const layers = ['Valuation', 'Compliance', 'Transit']
const activeLayer = ref('Valuation')
const loading = ref(true)
const loadError = ref('')
const assets = ref<Asset[]>([])
const selectedAsset = ref<Asset | null>(null)

const metrics = computed(() => {
  const total = assets.value.length
  const mapped = assets.value.filter((asset) => asset.x !== '50%' || asset.y !== '50%').length
  const exceptions = assets.value.filter((asset) => asset.statusClass !== 'good').length
  const priority = mostCommon(assets.value.map((asset) => asset.subCity)) || 'Unavailable'
  return [
    { label: 'Mapped assets', value: String(total), note: `${mapped} geocoded backend records` },
    { label: 'Mapped coverage', value: total ? `${Math.round((mapped / total) * 100)}%` : '0%', note: 'Backend coordinate availability' },
    { label: 'Open exceptions', value: String(exceptions), note: 'Records needing review' },
    { label: 'Priority corridor', value: priority, note: 'Highest current record count' },
  ]
})

const mapStatus = computed(() => {
  if (loading.value) return 'Loading backend property coordinates.'
  if (loadError.value) return 'Backend spatial records unavailable.'
  return 'Backend property layer with valuation concentration and review exceptions.'
})

const selectedDetails = computed(() => [
  { label: 'Land area', value: selectedAsset.value?.area || 'Unavailable' },
  { label: 'Zoning', value: selectedAsset.value?.zoning || 'Unavailable' },
  { label: 'Owner', value: selectedAsset.value?.owner || 'Unavailable' },
  { label: 'Layer', value: activeLayer.value },
])

onMounted(loadProperties)

async function loadProperties() {
  loading.value = true
  loadError.value = ''
  try {
    const response = await fetch(`${apiBase}/api/v1/properties`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) {
      loadError.value = 'Property coordinates could not be loaded from the backend.'
      return
    }
    const payload = await response.json()
    const rows = Array.isArray(payload.data) ? payload.data : []
    assets.value = rows.map(mapPropertyToAsset)
    selectedAsset.value = assets.value[0] || null
  } catch {
    loadError.value = 'Property coordinates could not be loaded from the backend.'
  } finally {
    loading.value = false
  }
}

function mapPropertyToAsset(property: Record<string, any>, index: number): Asset {
  const status = String(property.status || 'review').toLowerCase()
  const hasCoordinates = Number.isFinite(Number(property.latitude)) && Number.isFinite(Number(property.longitude))
  return {
    id: property.property_ref || `PROPERTY-${property.id}`,
    propertyId: Number(property.id),
    name: property.address || `Property ${property.id}`,
    subCity: property.municipality || 'Unassigned',
    code: String(property.property_type || 'PR').slice(0, 2).toUpperCase(),
    x: hasCoordinates ? coordinateToPercent(Number(property.longitude), 38.68, 38.88, index) : '50%',
    y: hasCoordinates ? coordinateToPercent(Number(property.latitude), 8.92, 9.12, index, true) : '50%',
    kind: status === 'active' || status === 'approved' ? 'property' : 'review',
    value: formatCurrency(Number(property.market_value || property.ai_estimated_value || 0)),
    risk: status === 'active' || status === 'approved' ? 'Low' : 'Review',
    status: labelize(status),
    statusClass: status === 'active' || status === 'approved' ? 'good' : 'warn',
    exception: hasCoordinates ? 'Coordinate available' : 'Missing coordinate',
    area: `${formatCount(Number(property.area_sqm || property.building_area_sqm || 0))} m2`,
    zoning: labelize(property.property_type || 'Unclassified'),
    owner: 'Backend registry',
    note: hasCoordinates
      ? 'Backend record includes coordinate data and can be reviewed on the operational map.'
      : 'Backend record is missing coordinates and needs geocoding before spatial review.',
  }
}

function coordinateToPercent(value: number, min: number, max: number, index: number, invert = false) {
  const normalized = Math.min(Math.max((value - min) / (max - min), 0), 1)
  const adjusted = normalized || ((index % 7) + 1) / 8
  const percent = invert ? 100 - adjusted * 100 : adjusted * 100
  return `${Math.round(Math.min(Math.max(percent, 10), 90))}%`
}

function mostCommon(values: string[]) {
  const counts = values.reduce<Record<string, number>>((acc, value) => {
    if (value) acc[value] = (acc[value] || 0) + 1
    return acc
  }, {})
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0]
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatCount(value: number) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value || 0)
}

function labelize(value: string) {
  return String(value).replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

useHead({
  title: 'Asset Map - ValuAdis',
  meta: [{ name: 'description', content: 'GIS map for ValuAdis asset valuation operations.' }],
})
</script>

<style scoped>
.map-page {
  gap: 24px;
}

.map-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr);
  gap: 18px;
  align-items: stretch;
}

.map-panel,
.selected-panel {
  min-height: 640px;
}

.map-toolbar {
  align-items: flex-start;
}

.layer-tabs {
  display: inline-flex;
  gap: 4px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-2);
  padding: 4px;
}

.layer-tab {
  min-height: 32px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 800;
}

.layer-tab.active {
  background: var(--surface);
  color: var(--green);
  box-shadow: 0 1px 4px rgba(23, 26, 23, 0.08);
}

.civic-map {
  position: relative;
  min-height: 520px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background:
    radial-gradient(circle at 32% 38%, rgba(31, 107, 79, 0.2), transparent 22%),
    radial-gradient(circle at 72% 52%, rgba(156, 107, 29, 0.18), transparent 20%),
    linear-gradient(135deg, var(--green-soft) 0%, var(--surface) 42%, var(--green-soft) 100%);
}

.map-grid-lines {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(23, 26, 23, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 26, 23, 0.08) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.45));
}

.road {
  position: absolute;
  height: 26px;
  border: 1px solid rgba(54, 95, 115, 0.3);
  background: rgba(252, 252, 250, 0.76);
  box-shadow: 0 0 0 6px rgba(252, 252, 250, 0.28);
}

.primary-road {
  left: -8%;
  top: 45%;
  width: 118%;
  transform: rotate(-16deg);
}

.secondary-road {
  left: 28%;
  top: -6%;
  width: 26px;
  height: 112%;
  transform: rotate(18deg);
}

.asset-marker {
  position: absolute;
  z-index: 2;
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border: 3px solid var(--surface);
  border-radius: 999px;
  background: var(--green);
  color: var(--surface);
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(23, 26, 23, 0.22);
  transform: translate(-50%, -50%);
}

.asset-marker.review {
  background: var(--amber);
}

.asset-marker.vehicle {
  background: var(--blue);
}

.asset-marker.active {
  outline: 4px solid rgba(31, 107, 79, 0.18);
}

.asset-marker span {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 900;
}

.map-scale,
.map-coordinates {
  position: absolute;
  z-index: 3;
  bottom: 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(252, 252, 250, 0.9);
  color: var(--ink-soft);
  padding: 7px 10px;
  font-family: var(--mono);
  font-size: 12px;
}

.map-scale {
  left: 18px;
}

.map-coordinates {
  right: 18px;
}

.selected-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.asset-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.asset-summary > div,
.inspection-panel {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 16px;
}

.asset-value,
.asset-risk {
  margin: 7px 0 0;
  font-family: var(--display);
  font-size: 28px;
  line-height: 1;
}

.detail-list {
  display: grid;
  gap: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 13px 14px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  color: var(--muted);
  font-size: 13px;
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-row strong {
  color: var(--ink);
  font-weight: 800;
  text-align: right;
}

.inspection-panel {
  box-shadow: none;
}

.inspection-panel p:last-child {
  margin: 8px 0 0;
  color: var(--ink-soft);
  font-size: 14px;
}

.map-table-head {
  padding: 20px 22px 0;
}

@media (max-width: 1180px) {
  .map-workspace {
    grid-template-columns: 1fr;
  }

  .map-panel,
  .selected-panel {
    min-height: auto;
  }
}

@media (max-width: 720px) {
  .map-toolbar,
  .map-table-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .layer-tabs {
    width: 100%;
    overflow-x: auto;
  }

  .civic-map {
    min-height: 420px;
  }

  .asset-summary {
    grid-template-columns: 1fr;
  }
}
</style>
