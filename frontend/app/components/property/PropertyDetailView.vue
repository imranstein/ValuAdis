<template>
  <article class="property-detail">
    <header class="detail-hero">
      <button class="btn btn-ghost" type="button" @click="$emit('back')">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Back
      </button>

      <div class="hero-main">
        <p class="eyebrow">Property dossier</p>
        <h1>{{ property.address }}</h1>
        <div class="hero-meta">
          <span>{{ formatStatus(property.status) }}</span>
          <span>{{ labelize(property.property_type || 'unknown') }}</span>
          <span>{{ property.municipality || 'Unassigned municipality' }}</span>
        </div>
      </div>

      <div class="hero-actions">
        <button class="btn btn-secondary" type="button" :disabled="readonly" @click="$emit('edit', property.id)">
          <i class="pi pi-pencil" aria-hidden="true"></i>
          Edit
        </button>
        <button class="btn btn-primary" type="button" @click="$emit('create-valuation', property.id)">
          <i class="pi pi-calculator" aria-hidden="true"></i>
          Create valuation
        </button>
        <button class="btn btn-secondary" type="button" @click="exportProperty">
          <i class="pi pi-download" aria-hidden="true"></i>
          Export
        </button>
      </div>
    </header>

    <section class="summary-strip">
      <div>
        <span class="metric-label">Market value</span>
        <strong>{{ formatEtb(property.market_value || property.ai_estimated_value) }}</strong>
      </div>
      <div>
        <span class="metric-label">Land area</span>
        <strong>{{ formatArea(property.area_sqm) }}</strong>
      </div>
      <div>
        <span class="metric-label">Condition</span>
        <strong>{{ formatCondition(property.condition) }}</strong>
      </div>
      <div>
        <span class="metric-label">Record status</span>
        <strong>{{ formatStatus(property.status) }}</strong>
      </div>
    </section>

    <div class="detail-grid">
      <section class="panel">
        <div class="panel-head">
          <i class="pi pi-home" aria-hidden="true"></i>
          <h2>Property Overview</h2>
        </div>
        <dl class="facts-list">
          <div>
            <dt>Type</dt>
            <dd>{{ labelize(property.property_type || 'unknown') }}</dd>
          </div>
          <div>
            <dt>Municipality</dt>
            <dd>{{ property.municipality || 'N/A' }}</dd>
          </div>
          <div>
            <dt>Neighborhood</dt>
            <dd>{{ property.neighborhood || property.subcity || 'N/A' }}</dd>
          </div>
          <div>
            <dt>Parcel number</dt>
            <dd class="num">{{ property.parcel_number || property.property_id || property.id || 'N/A' }}</dd>
          </div>
          <div>
            <dt>Ownership type</dt>
            <dd>{{ formatOwnership(property.ownership_type) }}</dd>
          </div>
        </dl>
      </section>

      <section class="panel">
        <div class="panel-head">
          <i class="pi pi-th-large" aria-hidden="true"></i>
          <h2>Physical Characteristics</h2>
        </div>
        <div class="stat-grid">
          <div>
            <span>Land area</span>
            <strong>{{ formatArea(property.area_sqm) }}</strong>
          </div>
          <div>
            <span>Building area</span>
            <strong>{{ formatArea(property.building_area_sqm) }}</strong>
          </div>
          <div>
            <span>Floors</span>
            <strong>{{ property.number_of_floors || 'N/A' }}</strong>
          </div>
          <div>
            <span>Rooms</span>
            <strong>{{ property.number_of_rooms || 'N/A' }}</strong>
          </div>
          <div>
            <span>Parking</span>
            <strong>{{ property.parking_spaces || 'N/A' }}</strong>
          </div>
          <div>
            <span>Year built</span>
            <strong>{{ property.year_built || 'N/A' }}</strong>
          </div>
        </div>
      </section>

      <section v-if="hasCoordinates || hasBoundaries" class="panel map-panel">
        <div class="panel-head">
          <i class="pi pi-map" aria-hidden="true"></i>
          <h2>Location</h2>
        </div>
        <div id="detail-map" class="map"></div>
        <div v-if="hasCoordinates" class="coordinate-row">
          <span>Lat {{ Number(property.latitude).toFixed(6) }}</span>
          <span>Lng {{ Number(property.longitude).toFixed(6) }}</span>
        </div>
      </section>

      <section class="panel valuation-panel">
        <div class="panel-head">
          <i class="pi pi-chart-line" aria-hidden="true"></i>
          <h2>Valuation History</h2>
        </div>
        <div v-if="valuations.length === 0" class="empty-state">
          <p>No valuations found for this property.</p>
          <button class="btn btn-primary" type="button" @click="$emit('create-valuation', property.id)">
            <i class="pi pi-plus" aria-hidden="true"></i>
            Create first valuation
          </button>
        </div>
        <div v-else class="valuation-list">
          <div v-for="valuation in valuations" :key="valuation.id" class="valuation-row">
            <div>
              <strong>{{ formatEtb(valuation.market_value) }}</strong>
              <span>{{ formatDate(valuation.valuation_date || valuation.created_at) }}</span>
            </div>
            <span class="status-pill">{{ formatStatus(valuation.status) }}</span>
          </div>
        </div>
      </section>

      <section v-if="hasDocuments || hasPhotos" class="panel documents-panel">
        <div class="panel-head">
          <i class="pi pi-file" aria-hidden="true"></i>
          <h2>Documents & Photos</h2>
        </div>
        <div v-if="hasPhotos" class="photo-grid">
          <img v-for="(photo, index) in property.photos" :key="index" :src="photo.url || photo" :alt="`Property photo ${index + 1}`" />
        </div>
        <div v-if="hasDocuments" class="document-list">
          <button v-for="(doc, index) in property.documents" :key="index" class="document-row" type="button" @click="downloadDocument(doc)">
            <i class="pi pi-download" aria-hidden="true"></i>
            {{ doc.name || `Document ${index + 1}` }}
          </button>
        </div>
      </section>
    </div>
  </article>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  property: {
    type: Object,
    required: true
  },
  valuations: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

defineEmits(['back', 'edit', 'create-valuation'])

let map = null

const hasBoundaries = computed(() => props.property.boundaries && props.property.boundaries.length > 2)
const hasCoordinates = computed(() => props.property.latitude && props.property.longitude)
const hasDocuments = computed(() => props.property.documents && props.property.documents.length > 0)
const hasPhotos = computed(() => props.property.photos && props.property.photos.length > 0)

onMounted(async () => {
  if (hasBoundaries.value || hasCoordinates.value) {
    await nextTick()
    initMap()
  }
})

onUnmounted(() => {
  if (map) map.remove()
})

function initMap() {
  const defaultIcon = L.Icon.Default.prototype
  delete defaultIcon._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  const center = hasCoordinates.value
    ? [props.property.latitude, props.property.longitude]
    : props.property.boundaries[0]

  map = L.map('detail-map', { zoomControl: true }).setView(center, hasCoordinates.value ? 16 : 15)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  if (hasBoundaries.value) {
    const polygon = L.polygon(props.property.boundaries, {
      color: '#0f6b4f',
      fillColor: '#0f6b4f',
      fillOpacity: 0.18
    }).addTo(map)
    map.fitBounds(polygon.getBounds(), { padding: [40, 40] })
  }

  if (hasCoordinates.value) {
    L.marker([props.property.latitude, props.property.longitude]).addTo(map)
  }
}

function formatStatus(status) {
  return labelize(status || 'pending')
}

function formatOwnership(type) {
  return labelize(type || 'N/A')
}

function formatCondition(condition) {
  return labelize(condition || 'N/A')
}

function formatArea(value) {
  return value ? `${Math.round(Number(value)).toLocaleString()} m²` : 'N/A'
}

function formatEtb(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function labelize(value) {
  return String(value).replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function exportProperty() {
  downloadJson(
    {
      property: props.property,
      valuations: props.valuations,
      exported_at: new Date().toISOString(),
    },
    `property-${props.property.property_id || props.property.id || 'record'}.json`
  )
}

function downloadDocument(doc) {
  const href = doc.url || doc.href
  if (href) {
    const link = document.createElement('a')
    link.href = href
    link.download = doc.name || 'property-document'
    link.rel = 'noopener'
    document.body.appendChild(link)
    link.click()
    link.remove()
    return
  }

  downloadJson(doc, `${doc.name || 'property-document'}.json`)
}

function downloadJson(payload, filename) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.property-detail {
  display: grid;
  gap: 18px;
  color: #171717;
}

.detail-hero,
.summary-strip,
.panel {
  border: 1px solid #e3e0d8;
  background: #fffefb;
  box-shadow: 0 16px 36px rgba(27, 37, 31, 0.08);
}

.detail-hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 22px;
  align-items: start;
  padding: 24px;
  border-radius: 8px;
}

.eyebrow,
.metric-label,
.stat-grid span,
.facts-list dt {
  margin: 0;
  color: #6c6a62;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-main h1 {
  margin: 6px 0 12px;
  max-width: 880px;
  font-size: clamp(1.8rem, 3vw, 3rem);
  line-height: 1.05;
  letter-spacing: 0;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-meta span,
.status-pill {
  border: 1px solid #d6d1c6;
  border-radius: 999px;
  padding: 5px 10px;
  background: #f6f3eb;
  color: #334039;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.btn {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
  border: 1px solid #d8d4cb;
  padding: 0 14px;
  font-weight: 800;
  cursor: pointer;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.btn-primary {
  border-color: #0f6b4f;
  background: #0f6b4f;
  color: #fff;
}

.btn-secondary,
.btn-ghost {
  background: #fffefb;
  color: #26322d;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-radius: 8px;
}

.summary-strip > div {
  display: grid;
  gap: 6px;
  padding: 18px;
  border-right: 1px solid #e3e0d8;
}

.summary-strip > div:last-child {
  border-right: 0;
}

.summary-strip strong,
.stat-grid strong,
.valuation-row strong {
  font-family: "JetBrains Mono", monospace;
  font-variant-numeric: tabular-nums;
}

.summary-strip strong {
  font-size: 1.25rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.panel {
  border-radius: 8px;
  padding: 20px;
}

.panel-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.1rem;
}

.panel-head i {
  color: #0f6b4f;
}

.facts-list {
  display: grid;
  gap: 12px;
  margin: 0;
}

.facts-list div {
  display: grid;
  grid-template-columns: 160px minmax(0, 1fr);
  gap: 16px;
  align-items: baseline;
  padding-bottom: 12px;
  border-bottom: 1px solid #ede9df;
}

.facts-list div:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.facts-list dd {
  margin: 0;
  font-weight: 800;
}

.num {
  font-family: "JetBrains Mono", monospace;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.stat-grid div {
  display: grid;
  gap: 8px;
  min-height: 92px;
  padding: 14px;
  border: 1px solid #ebe6dc;
  border-radius: 6px;
  background: #faf8f1;
}

.stat-grid strong {
  align-self: end;
  font-size: 1.1rem;
}

.map-panel,
.valuation-panel,
.documents-panel {
  grid-column: span 2;
}

.map {
  height: 340px;
  border: 1px solid #e3e0d8;
  border-radius: 6px;
  overflow: hidden;
}

.coordinate-row {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  color: #5f635e;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.82rem;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 88px;
  border: 1px dashed #d8d4cb;
  border-radius: 6px;
  padding: 16px;
}

.empty-state p {
  margin: 0;
  color: #5f635e;
}

.valuation-list,
.document-list {
  display: grid;
  gap: 10px;
}

.valuation-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid #ede9df;
  padding-bottom: 10px;
}

.valuation-row div {
  display: grid;
  gap: 4px;
}

.valuation-row span {
  color: #6c6a62;
  font-size: 0.86rem;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.photo-grid img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 6px;
}

.document-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  border: 1px solid #d8d4cb;
  border-radius: 6px;
  background: #fffefb;
  padding: 10px 12px;
  font-weight: 800;
}

@media (max-width: 980px) {
  .detail-hero {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .summary-strip,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .summary-strip > div {
    border-right: 0;
    border-bottom: 1px solid #e3e0d8;
  }

  .summary-strip > div:last-child {
    border-bottom: 0;
  }

  .map-panel,
  .valuation-panel,
  .documents-panel {
    grid-column: span 1;
  }

  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .facts-list div,
  .stat-grid {
    grid-template-columns: 1fr;
  }

  .hero-main h1 {
    font-size: 1.8rem;
  }
}
</style>
