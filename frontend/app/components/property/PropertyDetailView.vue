<template>
  <div class="property-detail-view">
    <!-- Premium Header with Enhanced Design -->
    <div class="detail-header bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 rounded-2xl shadow-2xl overflow-hidden relative">
      <div class="absolute inset-0 bg-black opacity-10"></div>
      <div class="absolute top-0 right-0 w-48 h-48 bg-white opacity-5 rounded-full -mr-24 -mt-24"></div>
      <div class="absolute bottom-0 left-0 w-40 h-40 bg-white opacity-5 rounded-full -ml-20 -mb-20"></div>
      
      <div class="relative z-10 p-8">
        <div class="header-info flex items-center gap-6 mb-6">
          <Button
            icon="pi pi-arrow-left"
            label="Back"
            severity="secondary"
            outlined
            @click="$emit('back')"
            class="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
          />
          <div class="property-title flex-1">
            <h1 class="text-3xl font-bold text-white mb-2 tracking-tight">{{ property.address }}</h1>
            <p v-if="property.property_id" class="text-emerald-100 text-lg font-medium">ID: {{ property.property_id }}</p>
          </div>
        </div>
        
        <div class="header-actions flex gap-3 flex-wrap">
          <Button
            icon="pi pi-pencil"
            label="Edit"
            severity="secondary"
            @click="$emit('edit', property.id)"
            :disabled="readonly"
            class="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
          />
          <Button
            icon="pi pi-calculator"
            label="Create Valuation"
            @click="$emit('create-valuation', property.id)"
            class="bg-white text-emerald-600 hover:bg-emerald-50 border-white font-semibold"
          />
          <Button
            icon="pi pi-download"
            label="Export"
            severity="info"
            @click="exportProperty"
            class="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
          />
        </div>
      </div>
    </div>

    <!-- Enhanced Status Banner -->
    <div class="status-banner rounded-2xl shadow-lg overflow-hidden" :class="property.status || 'pending'">
      <div class="flex justify-between items-center p-6">
        <div class="status-content flex items-center gap-4">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" :class="getStatusIconClass(property.status)">
            <i :class="getStatusIcon(property.status)" class="text-white text-xl"></i>
          </div>
          <div>
            <span class="text-xl font-bold">{{ formatStatus(property.status) }}</span>
            <div class="text-sm opacity-80 mt-1">Property Status</div>
          </div>
        </div>
        <div class="status-meta text-right">
          <span v-if="property.last_valuation_date" class="block text-sm font-medium">
            <i class="pi pi-calendar mr-2"></i>
            Last valued: {{ formatDate(property.last_valuation_date) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Professional Content Grid -->
    <div class="detail-grid grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
      <!-- Enhanced Property Overview -->
      <Card class="overview-card bg-white rounded-2xl shadow-xl overflow-hidden border-0 hover:shadow-2xl transition-all duration-300">
        <template #header>
          <div class="card-header bg-gradient-to-r from-emerald-50 to-teal-50 p-6 border-b border-emerald-100">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
                <i class="pi pi-home text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-bold text-gray-800">Property Overview</h3>
            </div>
          </div>
        </template>
        <template #content>
          <div class="overview-content p-6 space-y-4">
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-tag text-emerald-500"></i>
                  Type
                </span>
                <span class="font-bold text-gray-800 bg-emerald-100 px-3 py-1 rounded-full">{{ property.property_type }}</span>
              </div>
            </div>
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-building text-emerald-500"></i>
                  Municipality
                </span>
                <span class="font-bold text-gray-800">{{ property.municipality }}</span>
              </div>
            </div>
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-th-large text-emerald-500"></i>
                  Zone/Block
                </span>
                <span class="font-bold text-gray-800">{{ property.zone || 'N/A' }}</span>
              </div>
            </div>
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-users text-emerald-500"></i>
                  Neighborhood
                </span>
                <span class="font-bold text-gray-800">{{ property.neighborhood || 'N/A' }}</span>
              </div>
            </div>
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-hashtag text-emerald-500"></i>
                  Parcel Number
                </span>
                <span class="font-bold text-gray-800 font-mono">{{ property.parcel_number || 'N/A' }}</span>
              </div>
            </div>
            <div class="overview-item bg-gray-50 rounded-xl p-4 hover:bg-emerald-50 transition-colors">
              <div class="flex justify-between items-center">
                <span class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                  <i class="pi pi-id-card text-emerald-500"></i>
                  Ownership Type
                </span>
                <span class="font-bold text-gray-800 bg-blue-100 px-3 py-1 rounded-full">{{ formatOwnership(property.ownership_type) }}</span>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Enhanced Physical Characteristics -->
      <Card class="characteristics-card bg-white rounded-2xl shadow-xl overflow-hidden border-0 hover:shadow-2xl transition-all duration-300">
        <template #header>
          <div class="card-header bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border-b border-blue-100">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
                <i class="pi pi-th-large text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-bold text-gray-800">Physical Characteristics</h3>
            </div>
          </div>
        </template>
        <template #content>
          <div class="p-6 space-y-6">
            <div class="characteristics-grid grid grid-cols-2 md:grid-cols-3 gap-4">
              <div class="char-item bg-gradient-to-br from-emerald-500 to-teal-500 text-white rounded-2xl p-6 text-center shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                <div class="char-icon text-3xl mb-3">
                  <i class="pi pi-map"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold block">{{ formatNumber(property.area_sqm) }} m²</span>
                  <span class="char-label text-sm opacity-90">Land Area</span>
                </div>
              </div>
              <div class="char-item bg-gradient-to-br from-blue-500 to-indigo-500 text-white rounded-2xl p-6 text-center shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                <div class="char-icon text-3xl mb-3">
                  <i class="pi pi-building"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold block">{{ formatNumber(property.building_area_sqm) }} m²</span>
                  <span class="char-label text-sm opacity-90">Building Area</span>
                </div>
              </div>
              <div class="char-item bg-gray-50 rounded-2xl p-6 text-center hover:bg-gray-100 transition-all duration-300">
                <div class="char-icon text-3xl mb-3 text-gray-600">
                  <i class="pi pi-sort-numeric-up"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold text-gray-800 block">{{ property.number_of_floors || 'N/A' }}</span>
                  <span class="char-label text-sm text-gray-600">Floors</span>
                </div>
              </div>
              <div class="char-item bg-gray-50 rounded-2xl p-6 text-center hover:bg-gray-100 transition-all duration-300">
                <div class="char-icon text-3xl mb-3 text-gray-600">
                  <i class="pi pi-door-open"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold text-gray-800 block">{{ property.number_of_rooms || 'N/A' }}</span>
                  <span class="char-label text-sm text-gray-600">Rooms</span>
                </div>
              </div>
              <div class="char-item bg-gray-50 rounded-2xl p-6 text-center hover:bg-gray-100 transition-all duration-300">
                <div class="char-icon text-3xl mb-3 text-gray-600">
                  <i class="pi pi-car"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold text-gray-800 block">{{ property.parking_spaces || 'N/A' }}</span>
                  <span class="char-label text-sm text-gray-600">Parking</span>
                </div>
              </div>
              <div class="char-item bg-gray-50 rounded-2xl p-6 text-center hover:bg-gray-100 transition-all duration-300">
                <div class="char-icon text-3xl mb-3 text-gray-600">
                  <i class="pi pi-calendar"></i>
                </div>
                <div class="char-content">
                  <span class="char-value text-2xl font-bold text-gray-800 block">{{ property.year_built || 'N/A' }}</span>
                  <span class="char-label text-sm text-gray-600">Year Built</span>
                </div>
              </div>
            </div>
            
            <div class="quality-section grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="quality-item bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-bold text-gray-700 flex items-center gap-2">
                    <i class="pi pi-star text-yellow-500"></i>
                    Construction Quality
                  </span>
                  <span class="quality-badge px-3 py-1 rounded-full text-sm font-semibold" :class="property.construction_quality">
                    {{ formatQuality(property.construction_quality) }}
                  </span>
                </div>
              </div>
              <div class="quality-item bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-bold text-gray-700 flex items-center gap-2">
                    <i class="pi pi-shield text-blue-500"></i>
                    Property Condition
                  </span>
                  <span class="condition-badge px-3 py-1 rounded-full text-sm font-semibold" :class="property.condition">
                    {{ formatCondition(property.condition) }}
                  </span>
                </div>
              </div>
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

function getStatusIconClass(status) {
  const classMap = {
    'pending': 'bg-gray-500',
    'in_progress': 'bg-amber-500',
    'completed': 'bg-emerald-500',
    'cancelled': 'bg-red-500'
  }
  return classMap[status] || 'bg-gray-500'
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
/* Professional Property Detail Styles */
.property-detail-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* Status Banner Styles */
.status-banner.pending {
  @apply bg-gray-100 text-gray-700;
}

.status-banner.in_progress {
  @apply bg-amber-100 text-amber-700;
}

.status-banner.completed {
  @apply bg-emerald-100 text-emerald-700;
}

.status-banner.cancelled {
  @apply bg-red-100 text-red-700;
}

/* Quality and Condition Badge Styles */
.quality-badge.premium, .condition-badge.excellent {
  @apply bg-amber-100 text-amber-700;
}

.quality-badge.good, .condition-badge.good {
  @apply bg-emerald-100 text-emerald-700;
}

.quality-badge.average, .condition-badge.fair {
  @apply bg-blue-100 text-blue-700;
}

.quality-badge.poor, .condition-badge.poor {
  @apply bg-orange-100 text-orange-700;
}

.quality-badge.very_poor, .condition-badge.very_poor {
  @apply bg-red-100 text-red-700;
}

/* Enhanced Map Styles */
.map-container {
  @apply p-6;
}

.map {
  @apply h-80 rounded-2xl border-2 border-gray-200 overflow-hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.location-info {
  @apply flex gap-8 p-6 text-sm bg-gray-50 rounded-xl;
}

.coord-item {
  @apply flex gap-2;
}

.coord-item .label {
  @apply text-gray-600 font-semibold;
}

.coord-item .value {
  @apply font-mono text-gray-800 font-bold;
}

/* Enhanced Ownership Styles */
.ownership-content {
  @apply p-6 space-y-6;
}

.owner-info {
  @apply flex gap-4 p-4 bg-gray-50 rounded-2xl;
}

.owner-avatar {
  @apply w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-2xl shadow-lg;
}

.owner-details h4 {
  @apply text-xl font-bold text-gray-800 mb-2;
}

.owner-details p {
  @apply text-gray-600 text-sm mb-1;
}

.legal-section {
  @apply p-4 bg-blue-50 rounded-2xl;
}

.legal-section h5 {
  @apply text-lg font-bold text-gray-800 mb-3;
}

.legal-section p {
  @apply text-gray-700 leading-relaxed;
}

/* Enhanced Valuation Styles */
.valuation-content {
  @apply p-6;
}

.empty-valuations {
  @apply text-center p-8 text-gray-600;
}

.empty-valuations i {
  @apply text-5xl mb-4 opacity-50 text-gray-400;
}

.valuation-list {
  @apply flex flex-col gap-4;
}

.valuation-item {
  @apply p-6 bg-gradient-to-r from-gray-50 to-emerald-50 rounded-2xl border border-emerald-200 hover:shadow-lg transition-all duration-300;
}

.valuation-main {
  @apply flex justify-between items-center mb-3;
}

.valuation-date {
  @apply font-bold text-gray-800;
}

.valuation-value {
  @apply text-2xl font-bold text-emerald-600;
}

.valuation-meta {
  @apply flex gap-4 text-sm;
}

.valuation-type {
  @apply text-gray-600 font-medium;
}

.valuation-status {
  @apply px-3 py-1 rounded-full font-semibold text-xs;
}

.valuation-status.pending {
  @apply bg-gray-100 text-gray-700;
}

.valuation-status.in_progress {
  @apply bg-amber-100 text-amber-700;
}

.valuation-status.completed {
  @apply bg-emerald-100 text-emerald-700;
}

/* Enhanced Document Styles */
.documents-content {
  @apply p-6 space-y-8;
}

.document-section h4 {
  @apply text-lg font-bold text-gray-800 mb-4 flex items-center gap-2;
}

.photo-gallery {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.photo-item img {
  @apply w-full h-48 object-cover rounded-2xl border-2 border-gray-200 hover:border-emerald-300 transition-all duration-300 hover:shadow-lg;
}

.document-list {
  @apply flex flex-col gap-3;
}

.document-item {
  @apply flex items-center gap-3 p-4 bg-gray-50 rounded-2xl hover:bg-emerald-50 transition-all duration-300 border border-gray-200 hover:border-emerald-300;
}

.document-item i {
  @apply text-red-500 text-xl;
}

.document-item span {
  @apply flex-1 text-gray-700 font-medium;
}

/* Professional Responsive Design */
@media (max-width: 1024px) {
  .detail-grid {
    @apply grid-cols-1 lg:grid-cols-2;
  }
}

@media (max-width: 768px) {
  .detail-header {
    @apply p-6;
  }
  
  .header-info {
    @apply flex-col text-center gap-4;
  }
  
  .header-actions {
    @apply justify-center;
  }
  
  .detail-grid {
    @apply grid-cols-1 gap-6;
  }
  
  .characteristics-grid {
    @apply grid-cols-1;
  }
  
  .quality-section {
    @apply grid-cols-1;
  }
  
  .location-info {
    @apply flex-col gap-2;
  }
  
  .status-banner {
    @apply flex-col gap-4 text-center;
  }
}

/* Professional Animations */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.overview-card,
.characteristics-card,
.map-card,
.ownership-card,
.valuation-card,
.documents-card {
  animation: slideInUp 0.6s ease-out;
}

.overview-card {
  animation-delay: 0.1s;
}

.characteristics-card {
  animation-delay: 0.2s;
}

.map-card {
  animation-delay: 0.3s;
}

.ownership-card {
  animation-delay: 0.4s;
}

.valuation-card {
  animation-delay: 0.5s;
}

.documents-card {
  animation-delay: 0.6s;
}

/* Enhanced Hover Effects */
.overview-card:hover,
.characteristics-card:hover,
.map-card:hover,
.ownership-card:hover,
.valuation-card:hover,
.documents-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Professional Typography */
.property-title h1 {
  letter-spacing: -0.05em;
  line-height: 1.1;
}

.card-header h3 {
  letter-spacing: -0.025em;
  line-height: 1.2;
}

/* Enhanced Button Styles */
.header-actions button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-actions button:hover {
  transform: translateY(-2px);
}
</style>
