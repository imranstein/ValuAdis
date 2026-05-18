<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-map-marker text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Location & Mapping</h2>
        <p class="step-subtitle">Pin the exact location and optionally draw the property boundary</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Error banner -->
      <div v-if="errors.location" class="error-banner">
        <i class="pi pi-exclamation-circle" />
        {{ errors.location }}
      </div>

      <!-- Address geocode hint -->
      <div class="geocode-bar">
        <span class="text-sm text-slate-600">
          <i class="pi pi-info-circle text-emerald-600 mr-1" />
          Click anywhere on the map to drop a pin, or draw a polygon to mark the boundary.
          Map is centered on: <strong>{{ form.address || form.municipality || 'Addis Ababa' }}</strong>
        </span>
        <Button
          label="Center on Address"
          severity="secondary"
          size="small"
          icon="pi pi-crosshairs"
          @click="geocodeAddress"
          :loading="geocoding"
        />
      </div>

      <!-- Map -->
      <div class="map-container" ref="mapContainer" />

      <!-- Coordinate inputs -->
      <div class="coords-grid">
        <div class="coord-field">
          <label>Latitude</label>
          <InputText
            :model-value="form.latitude?.toFixed(6) ?? ''"
            readonly
            placeholder="Click map to set"
            class="w-full font-mono text-sm"
          />
        </div>
        <div class="coord-field">
          <label>Longitude</label>
          <InputText
            :model-value="form.longitude?.toFixed(6) ?? ''"
            readonly
            placeholder="Click map to set"
            class="w-full font-mono text-sm"
          />
        </div>
        <div class="coord-field" v-if="form.boundaries.length > 0">
          <label>Boundary Points</label>
          <InputText
            :model-value="`${form.boundaries.length} coordinates`"
            readonly
            class="w-full text-sm text-emerald-700"
          />
        </div>
      </div>

      <!-- Neighborhood info -->
      <div v-if="form.latitude && form.longitude" class="location-info">
        <i class="pi pi-map-marker text-emerald-600" />
        <span>
          Location set at
          <strong>{{ form.latitude?.toFixed(4) }}, {{ form.longitude?.toFixed(4) }}</strong>
          <span v-if="form.neighborhood"> — {{ form.neighborhood }}</span>
        </span>
        <Tag severity="success" value="Located" class="ml-auto" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const form = store.formData
const errors = computed(() => store.stepErrors[2] || {})

const mapContainer = ref<HTMLElement | null>(null)
const geocoding = ref(false)
let mapInstance: any = null
let markerInstance: any = null
let drawnItems: any = null

onMounted(async () => {
  if (!process.client) return
  await nextTick()

  const L = (await import('leaflet')).default
  await import('leaflet/dist/leaflet.css')
  await import('leaflet-draw/dist/leaflet.draw.css')
  await import('leaflet-draw')

  // Fix default icon paths for Nuxt
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  const center: [number, number] = form.latitude && form.longitude
    ? [form.latitude, form.longitude]
    : [9.0320, 38.7468] // Addis Ababa

  mapInstance = L.map(mapContainer.value!, { zoomControl: true }).setView(center, 14)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(mapInstance)

  // Drawn items layer
  drawnItems = new (L as any).FeatureGroup()
  mapInstance.addLayer(drawnItems)

  // Restore existing boundary
  if (form.boundaries.length > 0) {
    const latlngs: Array<[number, number]> = form.boundaries.map(([lng, lat]: number[]) => [lat, lng])
    const polygon = L.polygon(latlngs, { color: '#059669', fillOpacity: 0.15 })
    drawnItems.addLayer(polygon)
  }

  // Restore existing marker
  if (form.latitude && form.longitude) {
    markerInstance = L.marker([form.latitude, form.longitude]).addTo(mapInstance)
  }

  // Draw controls
  const drawControl = new (L as any).Control.Draw({
    edit: { featureGroup: drawnItems },
    draw: {
      polygon: { shapeOptions: { color: '#059669', fillOpacity: 0.15 } },
      polyline: false, circle: false, circlemarker: false, rectangle: false, marker: false,
    },
  })
  mapInstance.addControl(drawControl)

  // Click to place marker
  mapInstance.on('click', (e: any) => {
    const { lat, lng } = e.latlng
    form.latitude = lat
    form.longitude = lng
    if (store.stepErrors[2]) delete (store.stepErrors[2] as any).location

    if (markerInstance) mapInstance.removeLayer(markerInstance)
    markerInstance = L.marker([lat, lng]).addTo(mapInstance)
      .bindPopup(`${lat.toFixed(5)}, ${lng.toFixed(5)}`).openPopup()
  })

  // Capture drawn polygon
  mapInstance.on((L as any).Draw.Event.CREATED, (e: any) => {
    drawnItems.addLayer(e.layer)
    const latlngs = e.layer.getLatLngs()[0]
    form.boundaries = latlngs.map((ll: any) => [ll.lng, ll.lat])
    // Close polygon
    if (form.boundaries.length > 0 && JSON.stringify(form.boundaries[0]) !== JSON.stringify(form.boundaries[form.boundaries.length - 1])) {
      form.boundaries.push(form.boundaries[0])
    }
  })

  // Update stored boundaries when the user edits an existing polygon vertex
  mapInstance.on((L as any).Draw.Event.EDITED, (e: any) => {
    e.layers.eachLayer((layer: any) => {
      const latlngs = layer.getLatLngs()[0]
      form.boundaries = latlngs.map((ll: any) => [ll.lng, ll.lat])
      // Ensure the polygon is closed (GeoJSON requirement)
      if (
        form.boundaries.length > 0 &&
        JSON.stringify(form.boundaries[0]) !== JSON.stringify(form.boundaries[form.boundaries.length - 1])
      ) {
        form.boundaries.push(form.boundaries[0])
      }
    })
  })

  mapInstance.on((L as any).Draw.Event.DELETED, () => {
    form.boundaries = []
  })
})

onUnmounted(() => {
  if (mapInstance) mapInstance.remove()
})

async function geocodeAddress() {
  const query = [form.address, form.subcity, form.municipality, 'Ethiopia'].filter(Boolean).join(', ')
  if (!query) return
  geocoding.value = true
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
    )
    const data = await res.json()
    if (data.length > 0) {
      const lat = parseFloat(data[0].lat)
      const lng = parseFloat(data[0].lon)
      form.latitude = lat
      form.longitude = lng
      mapInstance?.setView([lat, lng], 16)

      const L = (await import('leaflet')).default
      if (markerInstance) mapInstance.removeLayer(markerInstance)
      markerInstance = L.marker([lat, lng]).addTo(mapInstance)
        .bindPopup(`${lat.toFixed(5)}, ${lng.toFixed(5)}`).openPopup()
    }
  } finally {
    geocoding.value = false
  }
}
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}
.step-icon-wrap {
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.2); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.2rem; }
.step-subtitle { font-size: 0.875rem; opacity: 0.85; margin: 0; }

.step-body { padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.25rem; }

.error-banner {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 8px; color: #dc2626; font-size: 0.875rem;
}

.geocode-bar {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;
}

.map-container {
  width: 100%; height: 420px;
  border-radius: 10px; overflow: hidden;
  border: 2px solid #e2e8f0;
  z-index: 0;
}

.coords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.coord-field { display: flex; flex-direction: column; gap: 0.4rem; }
.coord-field label { font-size: 0.8rem; font-weight: 600; color: #475569; }

.location-info {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4; border: 1px solid #bbf7d0;
  border-radius: 8px; font-size: 0.875rem; color: #166534;
}

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .map-container { height: 300px; }
  .geocode-bar { flex-direction: column; align-items: flex-start; }
}
</style>
