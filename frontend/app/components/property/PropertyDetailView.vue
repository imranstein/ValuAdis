<template>
  <div class="property-detail-view">
    <!-- Header Actions -->
    <div class="detail-header">
      <div class="header-info">
        <Button
          icon="pi pi-arrow-left"
          label="Back"
          severity="secondary"
          @click="$emit('back')"
        />
        <div class="property-title">
          <h1>{{ property.address }}</h1>
          <p v-if="property.property_id">ID: {{ property.property_id }}</p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          icon="pi pi-pencil"
          label="Edit"
          severity="secondary"
          @click="$emit('edit', property.id)"
          :disabled="readonly"
        />
        <Button
          icon="pi pi-calculator"
          label="Create Valuation"
          @click="$emit('create-valuation', property.id)"
        />
        <Button
          icon="pi pi-download"
          label="Export"
          severity="info"
          @click="exportProperty"
        />
      </div>
    </div>

    <!-- Status Banner -->
    <div class="status-banner" :class="property.status || 'pending'">
      <div class="status-content">
        <i :class="getStatusIcon(property.status)"></i>
        <span>{{ formatStatus(property.status) }}</span>
      </div>
      <div class="status-meta">
        <span v-if="property.last_valuation_date">
          Last valued: {{ formatDate(property.last_valuation_date) }}
        </span>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="detail-grid">
      <!-- Property Overview -->
      <Card class="overview-card">
        <template #header>
          <div class="card-header">
            <i class="pi pi-home"></i>
            <h3>Property Overview</h3>
          </div>
        </template>
        <template #content>
          <div class="overview-content">
            <div class="overview-item">
              <span class="label">Type</span>
              <span class="value">{{ property.property_type }}</span>
            </div>
            <div class="overview-item">
              <span class="label">Municipality</span>
              <span class="value">{{ property.municipality }}</span>
            </div>
            <div class="overview-item">
              <span class="label">Zone/Block</span>
              <span class="value">{{ property.zone || 'N/A' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">Neighborhood</span>
              <span class="value">{{ property.neighborhood || 'N/A' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">Parcel Number</span>
              <span class="value">{{ property.parcel_number || 'N/A' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">Ownership Type</span>
              <span class="value">{{ formatOwnership(property.ownership_type) }}</span>
            </div>
          </div>
        </template>
      </Card>

      <!-- Physical Characteristics -->
      <Card class="characteristics-card">
        <template #header>
          <div class="card-header">
            <i class="pi pi-th-large"></i>
            <h3>Physical Characteristics</h3>
          </div>
        </template>
        <template #content>
          <div class="characteristics-grid">
            <div class="char-item primary">
              <div class="char-icon">
                <i class="pi pi-map"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ formatNumber(property.area_sqm) }} m²</span>
                <span class="char-label">Land Area</span>
              </div>
            </div>
            <div class="char-item secondary">
              <div class="char-icon">
                <i class="pi pi-building"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ formatNumber(property.building_area_sqm) }} m²</span>
                <span class="char-label">Building Area</span>
              </div>
            </div>
            <div class="char-item">
              <div class="char-icon">
                <i class="pi pi-sort-numeric-up"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ property.number_of_floors || 'N/A' }}</span>
                <span class="char-label">Floors</span>
              </div>
            </div>
            <div class="char-item">
              <div class="char-icon">
                <i class="pi pi-door-open"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ property.number_of_rooms || 'N/A' }}</span>
                <span class="char-label">Rooms</span>
              </div>
            </div>
            <div class="char-item">
              <div class="char-icon">
                <i class="pi pi-car"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ property.parking_spaces || 'N/A' }}</span>
                <span class="char-label">Parking</span>
              </div>
            </div>
            <div class="char-item">
              <div class="char-icon">
                <i class="pi pi-calendar"></i>
              </div>
              <div class="char-content">
                <span class="char-value">{{ property.year_built || 'N/A' }}</span>
                <span class="char-label">Year Built</span>
              </div>
            </div>
          </div>
          
          <div class="quality-section">
            <div class="quality-item">
              <span class="label">Construction Quality</span>
              <span class="quality-badge" :class="property.construction_quality">
                {{ formatQuality(property.construction_quality) }}
              </span>
            </div>
            <div class="quality-item">
              <span class="label">Property Condition</span>
              <span class="condition-badge" :class="property.condition">
                {{ formatCondition(property.condition) }}
              </span>
            </div>
          </div>
        </template>
      </Card>

      <!-- Map View -->
      <Card class="map-card" v-if="hasBoundaries || hasCoordinates">
        <template #header>
          <div class="card-header">
            <i class="pi pi-map"></i>
            <h3>Location</h3>
          </div>
        </template>
        <template #content>
          <div class="map-container">
            <div id="detail-map" class="map"></div>
          </div>
          <div class="location-info" v-if="hasCoordinates">
            <div class="coord-item">
              <span class="label">Latitude:</span>
              <span class="value">{{ property.latitude?.toFixed(6) }}</span>
            </div>
            <div class="coord-item">
              <span class="label">Longitude:</span>
              <span class="value">{{ property.longitude?.toFixed(6) }}</span>
            </div>
          </div>
        </template>
      </Card>

      <!-- Ownership Information -->
      <Card class="ownership-card" v-if="property.owner_name">
        <template #header>
          <div class="card-header">
            <i class="pi pi-user"></i>
            <h3>Ownership Information</h3>
          </div>
        </template>
        <template #content>
          <div class="ownership-content">
            <div class="owner-info">
              <div class="owner-avatar">
                <i class="pi pi-user"></i>
              </div>
              <div class="owner-details">
                <h4>{{ property.owner_name }}</h4>
                <p v-if="property.owner_phone">{{ property.owner_phone }}</p>
                <p v-if="property.owner_email">{{ property.owner_email }}</p>
              </div>
            </div>
            <div class="legal-section" v-if="property.legal_description">
              <h5>Legal Description</h5>
              <p>{{ property.legal_description }}</p>
            </div>
          </div>
        </template>
      </Card>

      <!-- Valuation History -->
      <Card class="valuation-card">
        <template #header>
          <div class="card-header">
            <i class="pi pi-chart-line"></i>
            <h3>Valuation History</h3>
          </div>
        </template>
        <template #content>
          <div class="valuation-content">
            <div v-if="valuations.length === 0" class="empty-valuations">
              <i class="pi pi-inbox"></i>
              <p>No valuations found</p>
              <Button
                label="Create First Valuation"
                icon="pi pi-plus"
                @click="$emit('create-valuation', property.id)"
              />
            </div>
            <div v-else class="valuation-list">
              <div v-for="valuation in valuations" :key="valuation.id" class="valuation-item">
                <div class="valuation-main">
                  <div class="valuation-date">
                    {{ formatDate(valuation.valuation_date) }}
                  </div>
                  <div class="valuation-value">
                    ETB {{ formatCurrency(valuation.market_value) }}
                  </div>
                </div>
                <div class="valuation-meta">
                  <span class="valuation-type">{{ valuation.valuation_type }}</span>
                  <span class="valuation-status" :class="valuation.status">
                    {{ formatStatus(valuation.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Documents & Photos -->
      <Card class="documents-card" v-if="hasDocuments || hasPhotos">
        <template #header>
          <div class="card-header">
            <i class="pi pi-file"></i>
            <h3>Documents & Photos</h3>
          </div>
        </template>
        <template #content>
          <div class="documents-content">
            <div class="document-section" v-if="hasPhotos">
              <h4>Property Photos</h4>
              <div class="photo-gallery">
                <div v-for="(photo, index) in property.photos" :key="index" class="photo-item">
                  <img :src="photo.url || photo" :alt="`Property photo ${index + 1}`" />
                </div>
              </div>
            </div>
            
            <div class="document-section" v-if="hasDocuments">
              <h4>Legal Documents</h4>
              <div class="document-list">
                <div v-for="(doc, index) in property.documents" :key="index" class="document-item">
                  <i class="pi pi-file-pdf"></i>
                  <span>{{ doc.name || `Document ${index + 1}` }}</span>
                  <Button icon="pi pi-download" size="small" @click="downloadDocument(doc)" />
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

const emit = defineEmits(['back', 'edit', 'create-valuation'])

let map = null

// Computed
const hasBoundaries = computed(() => 
  props.property.boundaries && props.property.boundaries.length > 2
)
const hasCoordinates = computed(() => 
  props.property.latitude && props.property.longitude
)
const hasDocuments = computed(() => 
  props.property.documents && props.property.documents.length > 0
)
const hasPhotos = computed(() => 
  props.property.photos && props.property.photos.length > 0
)

onMounted(() => {
  if (hasBoundaries.value || hasCoordinates.value) {
    initMap()
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})

function initMap() {
  // Fix Leaflet default icon issue
  delete (L.Icon.Default.prototype)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  // Determine map center and zoom
  let center, zoom
  if (hasCoordinates.value) {
    center = [props.property.latitude, props.property.longitude]
    zoom = 16
  } else if (hasBoundaries.value) {
    center = props.property.boundaries[0]
    zoom = 15
  }

  // Initialize map
  map = L.map('detail-map').setView(center, zoom)

  // Add tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Add property boundary if available
  if (hasBoundaries.value) {
    const polygon = L.polygon(props.property.boundaries, {
      color: '#059669',
      fillColor: '#059669',
      fillOpacity: 0.3
    }).addTo(map)
    
    // Fit map to boundary
    map.fitBounds(polygon.getBounds(), { padding: [50, 50] })
  }

  // Add marker if coordinates available
  if (hasCoordinates.value) {
    L.marker([props.property.latitude, props.property.longitude]).addTo(map)
  }
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

function getStatusIcon(status) {
  const iconMap = {
    'pending': 'pi pi-clock',
    'in_progress': 'pi pi-spin pi-spinner',
    'completed': 'pi pi-check-circle',
    'cancelled': 'pi pi-times-circle'
  }
  return iconMap[status] || 'pi pi-clock'
}

function formatOwnership(type) {
  const typeMap = {
    'private': 'Private',
    'government': 'Government',
    'corporate': 'Corporate',
    'joint_venture': 'Joint Venture',
    'trust': 'Trust'
  }
  return typeMap[type] || 'N/A'
}

function formatQuality(quality) {
  const qualityMap = {
    'premium': 'Premium',
    'good': 'Good',
    'average': 'Average',
    'poor': 'Poor',
    'very_poor': 'Very Poor'
  }
  return qualityMap[quality] || 'N/A'
}

function formatCondition(condition) {
  const conditionMap = {
    'excellent': 'Excellent',
    'good': 'Good',
    'fair': 'Fair',
    'poor': 'Poor',
    'very_poor': 'Very Poor'
  }
  return conditionMap[condition] || 'N/A'
}

function formatNumber(value) {
  return value ? Math.round(value).toLocaleString() : 'N/A'
}

function formatCurrency(value) {
  return value ? Number(value).toLocaleString() : '0'
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function exportProperty() {
  // Export functionality
  console.log('Export property:', props.property)
}

function downloadDocument(doc) {
  // Download functionality
  console.log('Download document:', doc)
}
</script>

<style scoped>
.property-detail-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.property-title h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.property-title p {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.status-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.status-banner.pending {
  background: #f1f5f9;
  color: #475569;
}

.status-banner.in_progress {
  background: #fef3c7;
  color: #92400e;
}

.status-banner.completed {
  background: #dcfce7;
  color: #166534;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.status-meta {
  font-size: 0.875rem;
  opacity: 0.8;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.card-header i {
  font-size: 1.25rem;
  color: #059669;
}

.card-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.overview-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.overview-item:last-child {
  border-bottom: none;
}

.overview-item .label {
  color: #64748b;
  font-size: 0.875rem;
}

.overview-item .value {
  font-weight: 600;
  color: #1e293b;
}

.characteristics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.char-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.char-item.primary {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
}

.char-item.secondary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.char-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.char-value {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.char-label {
  font-size: 0.75rem;
  opacity: 0.8;
}

.quality-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 0 1.5rem 1.5rem;
}

.quality-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quality-badge, .condition-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.quality-badge.premium, .condition-badge.excellent {
  background: #fef3c7;
  color: #92400e;
}

.quality-badge.good, .condition-badge.good {
  background: #dcfce7;
  color: #166534;
}

.quality-badge.average, .condition-badge.fair {
  background: #dbeafe;
  color: #1e40af;
}

.quality-badge.poor, .condition-badge.poor {
  background: #fed7aa;
  color: #92400e;
}

.quality-badge.very_poor, .condition-badge.very_poor {
  background: #fee2e2;
  color: #991b1b;
}

.map-container {
  padding: 1.5rem;
}

.map {
  height: 300px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.location-info {
  display: flex;
  gap: 2rem;
  padding: 0 1.5rem 1.5rem;
  font-size: 0.875rem;
}

.coord-item {
  display: flex;
  gap: 0.5rem;
}

.coord-item .label {
  color: #64748b;
}

.coord-item .value {
  font-family: monospace;
  color: #1e293b;
}

.ownership-content {
  padding: 1.5rem;
}

.owner-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.owner-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #64748b;
}

.owner-details h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.owner-details p {
  margin: 0.25rem 0;
  color: #64748b;
  font-size: 0.875rem;
}

.legal-section h5 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
}

.legal-section p {
  color: #64748b;
  line-height: 1.6;
}

.valuation-content {
  padding: 1.5rem;
}

.empty-valuations {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.empty-valuations i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.valuation-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.valuation-item {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.valuation-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.valuation-date {
  font-weight: 600;
  color: #1e293b;
}

.valuation-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #059669;
}

.valuation-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.valuation-type {
  color: #64748b;
}

.valuation-status {
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-weight: 600;
}

.documents-content {
  padding: 1.5rem;
}

.document-section {
  margin-bottom: 2rem;
}

.document-section:last-child {
  margin-bottom: 0;
}

.document-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
}

.photo-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.photo-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.document-item i {
  color: #dc2626;
  font-size: 1.25rem;
}

.document-item span {
  flex: 1;
  color: #475569;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-info {
    flex-direction: column;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .characteristics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quality-section {
    grid-template-columns: 1fr;
  }
  
  .location-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
