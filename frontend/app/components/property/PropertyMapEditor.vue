<template>
  <div class="map-editor-container">
    <div class="map-header">
      <h3>Property Boundaries</h3>
      <div class="map-controls">
        <Button
          label="Draw Mode"
          :severity="drawMode ? 'success' : 'secondary'"
          size="small"
          icon="pi pi-pencil"
          @click="toggleDrawMode"
        />
        <Button
          label="Clear"
          severity="danger"
          size="small"
          icon="pi pi-trash"
          @click="clearBoundaries"
          :disabled="!hasBoundaries"
        />
        <Button
          label="Use GPS"
          severity="info"
          size="small"
          icon="pi pi-map-marker"
          @click="useCurrentLocation"
        />
      </div>
    </div>
    
    <div class="map-stats">
      <div class="stat-item">
        <span class="label">Area:</span>
        <span class="value">{{ formatArea(calculatedArea) }} m²</span>
      </div>
      <div class="stat-item">
        <span class="label">Perimeter:</span>
        <span class="value">{{ formatArea(calculatedPerimeter) }} m</span>
      </div>
      <div class="stat-item">
        <span class="label">Points:</span>
        <span class="value">{{ boundaries.length }}</span>
      </div>
    </div>

    <div 
      id="property-map" 
      ref="mapContainer"
      class="map-container"
      :class="{ 'draw-mode': drawMode }"
    ></div>

    <div class="map-tools">
      <div class="tool-section">
        <h4>Coordinate Input</h4>
        <div class="coordinate-input">
          <div class="coord-pair">
            <InputNumber
              v-model="manualLat"
              placeholder="Latitude"
              :min="-90"
              :max="90"
              :precision="6"
              size="small"
            />
            <InputNumber
              v-model="manualLng"
              placeholder="Longitude"
              :min="-180"
              :max="180"
              :precision="6"
              size="small"
            />
            <Button
              label="Add Point"
              size="small"
              @click="addManualPoint"
              :disabled="!manualLat || !manualLng"
            />
          </div>
        </div>
      </div>

      <div class="tool-section">
        <h4>Boundary Import</h4>
        <div class="import-section">
          <FileUpload
            mode="basic"
            accept=".json,.geojson,.kml"
            :auto="true"
            custom-upload
            @uploader="importBoundaries"
            choose-label="Import Boundaries"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  },
  center: {
    type: Array,
    default: () => [9.0320, 38.7578] // Addis Ababa
  },
  zoom: {
    type: Number,
    default: 15
  }
})

const emit = defineEmits(['update:modelValue', 'area-calculated', 'boundary-change'])

// Map instance
const mapContainer = ref(null)
let map = null
let currentPolygon = null

// State
const drawMode = ref(false)
const boundaries = ref([])
const manualLat = ref(null)
const manualLng = ref(null)

// Computed
const hasBoundaries = computed(() => boundaries.value.length > 0)
const calculatedArea = computed(() => {
  if (!currentPolygon || boundaries.value.length < 3) return 0
  return L.GeometryUtil.geodesicArea(currentPolygon.getLatLngs()[0])
})
const calculatedPerimeter = computed(() => {
  if (!currentPolygon || boundaries.value.length < 2) return 0
  const latLngs = currentPolygon.getLatLngs()[0]
  let perimeter = 0
  for (let i = 0; i < latLngs.length; i++) {
    const next = (i + 1) % latLngs.length
    perimeter += latLngs[i].distanceTo(latLngs[next])
  }
  return perimeter
})

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  if (newVal && newVal.length > 0) {
    boundaries.value = [...newVal]
    updatePolygon()
  }
}, { immediate: true })

watch(boundaries, (newVal) => {
  emit('update:modelValue', newVal)
  emit('boundary-change', newVal)
})

onMounted(() => {
  initMap()
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

  // Initialize map
  map = L.map(mapContainer.value).setView(props.center, props.zoom)

  // Add tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Add click handler for manual boundary drawing
  if (!props.readonly) {
    map.on('click', handleMapClick)
  }

  // Load existing boundaries
  if (props.modelValue && props.modelValue.length > 0) {
    boundaries.value = [...props.modelValue]
    updatePolygon()
  }
}

function handleMapClick(e) {
  if (drawMode.value) {
    boundaries.value.push([e.latlng.lat, e.latlng.lng])
    updatePolygon()
  }
}

function updatePolygon() {
  if (currentPolygon) {
    map.removeLayer(currentPolygon)
  }

  if (boundaries.value.length > 2) {
    currentPolygon = L.polygon(boundaries.value, {
      color: '#059669',
      fillColor: '#059669',
      fillOpacity: 0.3
    })
    map.addLayer(currentPolygon)
    
    // Fit map to polygon bounds
    const bounds = currentPolygon.getBounds()
    map.fitBounds(bounds, { padding: [50, 50] })
  }
}

function toggleDrawMode() {
  drawMode.value = !drawMode.value
  // You could enable/disable drawing tools based on this state
}

function clearBoundaries() {
  boundaries.value = []
  if (currentPolygon) {
    map.removeLayer(currentPolygon)
    currentPolygon = null
  }
}

function useCurrentLocation() {
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude
        map.setView([lat, lng], 17)
        
        // Add a marker at current location
        L.marker([lat, lng]).addTo(map)
      },
      (err) => {
        console.error('Unable to get current location:', err)
      }
    )
  }
}

function addManualPoint() {
  if (manualLat.value && manualLng.value) {
    boundaries.value.push([manualLat.value, manualLng.value])
    updatePolygon()
    
    // Clear inputs
    manualLat.value = null
    manualLng.value = null
    
    // Add marker
    L.marker([manualLat.value, manualLng.value]).addTo(map)
  }
}

function importBoundaries(event) {
  const file = event.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target.result
      let imported = []

      if (file.name.endsWith('.json') || file.name.endsWith('.geojson')) {
        const geojson = JSON.parse(content)
        imported = parseGeoJSON(geojson)
      } else if (file.name.endsWith('.kml')) {
        imported = parseKML(content)
      }

      if (imported.length > 0) {
        boundaries.value = imported
        updatePolygon()
      }
    } catch (error) {
      console.error('Failed to import boundaries:', error)
    }
  }
  reader.readAsText(file)
}

function parseGeoJSON(geojson) {
  const coordinates = []
  
  if (geojson.type === 'FeatureCollection') {
    geojson.features.forEach(feature => {
      if (feature.geometry.type === 'Polygon') {
        coordinates.push(...feature.geometry.coordinates[0])
      }
    })
  } else if (geojson.type === 'Feature') {
    if (geojson.geometry.type === 'Polygon') {
      coordinates.push(...geojson.geometry.coordinates[0])
    }
  }
  
  return coordinates.map(coord => [coord[1], coord[0]]) // Convert [lng, lat] to [lat, lng]
}

function parseKML(kmlContent) {
  // Basic KML parsing - you might want to use a proper KML parser library
  const coordinates = []
  const coordRegex = /<coordinates>([^<]+)<\/coordinates>/g
  let match
  
  while ((match = coordRegex.exec(kmlContent)) !== null) {
    const coords = match[1].trim().split(' ')
    coords.forEach(coord => {
      const [lng, lat] = coord.split(',').map(Number)
      if (!isNaN(lat) && !isNaN(lng)) {
        coordinates.push([lat, lng])
      }
    })
  }
  
  return coordinates
}

function formatArea(value) {
  return Math.round(value * 100) / 100
}
</script>

<style scoped>
.map-editor-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.map-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.map-controls {
  display: flex;
  gap: 0.5rem;
}

.map-stats {
  display: flex;
  gap: 2rem;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  gap: 0.5rem;
}

.stat-item .label {
  color: #64748b;
  font-size: 0.875rem;
}

.stat-item .value {
  font-weight: 600;
  color: #1e293b;
}

.map-container {
  height: 400px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  overflow: hidden;
}

.map-container.draw-mode {
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.map-tools {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.tool-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.coordinate-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.coord-pair {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.coord-pair > div {
  flex: 1;
}

.import-section {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .map-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .map-controls {
    justify-content: center;
  }
  
  .map-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .map-tools {
    grid-template-columns: 1fr;
  }
}
</style>
