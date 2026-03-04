<template>
  <div style="padding: 2rem; max-width: 1200px; margin: 0 auto;">
    <div style="margin-bottom: 1.5rem;">
      <h1 style="font-size: 1.875rem; font-weight: bold; color: #111827;">Create Property</h1>
      <p style="color: #6b7280; margin-top: 0.25rem;">Add a new property to the system</p>
    </div>

    <Card>
      <template #content>
        <form @submit.prevent="handleSubmit" style="display: flex; flex-direction: column; gap: 1.5rem;">
          <!-- Address -->
          <div>
            <label for="address" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Address *
            </label>
            <InputText
              id="address"
              v-model="formData.address"
              style="width: 100%;"
              placeholder="e.g., 123 Main Street, Addis Ababa"
              required
            />
          </div>

          <!-- Municipality -->
          <div>
            <label for="municipality" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Municipality *
            </label>
            <Dropdown
              id="municipality"
              v-model="formData.municipality"
              :options="municipalities"
              placeholder="Select municipality"
              style="width: 100%;"
              required
            />
          </div>

          <!-- Property Type -->
          <div>
            <label for="property_type" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Property Type *
            </label>
            <Dropdown
              id="property_type"
              v-model="formData.property_type"
              :options="propertyTypes"
              optionLabel="label"
              optionValue="value"
              placeholder="Select property type"
              style="width: 100%;"
              required
            />
          </div>

          <!-- Land Area -->
          <div>
            <label for="area_sqm" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Land Area (m²) *
            </label>
            <InputText
              id="area_sqm"
              v-model.number="formData.area_sqm"
              type="number"
              step="0.01"
              min="0"
              style="width: 100%;"
              placeholder="e.g., 500"
              required
            />
          </div>

          <!-- Building Area (optional) -->
          <div>
            <label for="building_area_sqm" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Building Area (m²)
            </label>
            <InputText
              id="building_area_sqm"
              v-model.number="formData.building_area_sqm"
              type="number"
              step="0.01"
              min="0"
              style="width: 100%;"
              placeholder="e.g., 300"
            />
          </div>

          <!-- Year Built (optional) -->
          <div>
            <label for="year_built" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Year Built
            </label>
            <InputText
              id="year_built"
              v-model.number="formData.year_built"
              type="number"
              min="1900"
              :max="currentYear"
              style="width: 100%;"
              placeholder="e.g., 2020"
            />
          </div>

          <!-- Number of Rooms (optional) -->
          <div>
            <label for="number_of_rooms" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Number of Rooms
            </label>
            <InputText
              id="number_of_rooms"
              v-model.number="formData.number_of_rooms"
              type="number"
              min="0"
              style="width: 100%;"
              placeholder="e.g., 4"
            />
          </div>

          <!-- GPS Coordinates Section -->
          <Divider />
          <div>
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #111827; margin-bottom: 1rem;">GPS Boundaries (Optional)</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem;">
              Click on the map to add boundary points. The area will be calculated automatically.
            </p>
            
            <div id="map" style="height: 400px; border-radius: 0.5rem; border: 1px solid #e5e7eb; margin-bottom: 1rem;"></div>
            
            <div style="display: flex; gap: 0.5rem;">
              <Button
                type="button"
                label="Clear Boundaries"
                severity="secondary"
                size="small"
                @click="clearBoundaries"
                :disabled="boundaries.length === 0"
              />
              <Button
                type="button"
                label="Use Current Location"
                severity="info"
                size="small"
                icon="pi pi-map-marker"
                @click="useCurrentLocation"
              />
            </div>
          </div>

          <!-- Validation Errors -->
          <div v-if="validationErrors.length > 0" style="padding: 0.75rem; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; font-weight: 600; color: #dc2626; margin-bottom: 0.5rem;">Please fix the following errors:</p>
            <ul style="margin: 0; padding-left: 1.5rem; font-size: 0.875rem; color: #dc2626;">
              <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
          </div>

          <!-- Error Message -->
          <div v-if="error" style="padding: 0.75rem; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; color: #dc2626;">{{ error }}</p>
          </div>

          <!-- Success Message -->
          <div v-if="success" style="padding: 0.75rem; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; color: #16a34a;">{{ success }}</p>
          </div>

          <!-- Action Buttons -->
          <div style="display: flex; gap: 1rem; justify-content: flex-end; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
            <Button
              type="button"
              label="Cancel"
              severity="secondary"
              @click="goBack"
              :disabled="loading"
            />
            <Button
              type="submit"
              label="Create Property"
              style="background-color: #078160; border-color: #078160;"
              :loading="loading"
              :disabled="loading"
            />
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()

const formData = ref({
  address: '',
  municipality: '',
  property_type: '',
  area_sqm: null,
  building_area_sqm: null,
  year_built: null,
  number_of_rooms: null
})

const boundaries = ref([])
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const validationErrors = ref([])
let map = null
let polygon = null

const currentYear = computed(() => new Date().getFullYear())

const municipalities = [
  'Addis Ababa',
  'Dire Dawa',
  'Mekelle',
  'Gondar',
  'Bahir Dar',
  'Hawassa',
  'Adama',
  'Jimma',
  'Dessie',
  'Harar'
]

const propertyTypes = [
  { label: 'Residential', value: 'residential' },
  { label: 'Commercial', value: 'commercial' },
  { label: 'Industrial', value: 'industrial' },
  { label: 'Agricultural', value: 'agricultural' },
  { label: 'Mixed Use', value: 'mixed_use' }
]

onMounted(() => {
  initMap()
})

function initMap() {
  // Fix Leaflet default icon issue
  delete (L.Icon.Default.prototype)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  // Initialize Leaflet map centered on Addis Ababa
  map = L.map('map').setView([9.0320, 38.7578], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Add click handler to add boundary points
  map.on('click', (e) => {
    boundaries.value.push([e.latlng.lat, e.latlng.lng])
    updatePolygon()
  })
}

function updatePolygon() {
  if (polygon) {
    map.removeLayer(polygon)
  }

  if (boundaries.value.length > 2) {
    polygon = L.polygon(boundaries.value, {
      color: '#078160',
      fillColor: '#078160',
      fillOpacity: 0.3
    }).addTo(map)

    // Calculate area in square meters
    const area = L.GeometryUtil.geodesicArea(polygon.getLatLngs()[0])
    formData.value.area_sqm = Math.round(area * 100) / 100
  } else if (boundaries.value.length > 0) {
    // Show markers for points
    boundaries.value.forEach(point => {
      L.marker(point).addTo(map)
    })
  }
}

function clearBoundaries() {
  boundaries.value = []
  if (polygon) {
    map.removeLayer(polygon)
    polygon = null
  }
  map.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      map.removeLayer(layer)
    }
  })
}

function useCurrentLocation() {
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude
        map.setView([lat, lng], 15)
      },
      (err) => {
        error.value = 'Unable to get current location: ' + err.message
      }
    )
  } else {
    error.value = 'Geolocation is not supported by your browser'
  }
}

function validateForm() {
  validationErrors.value = []
  
  if (!formData.value.address || formData.value.address.trim().length < 3) {
    validationErrors.value.push('Address must be at least 3 characters long')
  }
  
  if (!formData.value.municipality) {
    validationErrors.value.push('Please select a municipality')
  }
  
  if (!formData.value.property_type) {
    validationErrors.value.push('Please select a property type')
  }
  
  if (!formData.value.area_sqm || formData.value.area_sqm <= 0) {
    validationErrors.value.push('Land area must be greater than 0')
  }
  
  if (formData.value.building_area_sqm && formData.value.building_area_sqm <= 0) {
    validationErrors.value.push('Building area must be greater than 0')
  }
  
  if (formData.value.year_built && (formData.value.year_built < 1900 || formData.value.year_built > currentYear.value)) {
    validationErrors.value.push(`Year built must be between 1900 and ${currentYear.value}`)
  }
  
  if (formData.value.number_of_rooms && formData.value.number_of_rooms <= 0) {
    validationErrors.value.push('Number of rooms must be greater than 0')
  }
  
  return validationErrors.value.length === 0
}

async function handleSubmit() {
  error.value = null
  success.value = null
  validationErrors.value = []
  
  if (!validateForm()) {
    return
  }
  
  loading.value = true

  try {
    const token = localStorage.getItem('valuadis_token')
    
    const payload = {
      address: formData.value.address,
      municipality: formData.value.municipality,
      property_type: formData.value.property_type,
      area_sqm: formData.value.area_sqm,
      building_area_sqm: formData.value.building_area_sqm,
      year_built: formData.value.year_built,
      number_of_rooms: formData.value.number_of_rooms,
      boundaries: boundaries.value.length > 0 ? boundaries.value : null
    }

    const response = await fetch('http://localhost:8020/api/v1/properties', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok) {
      success.value = 'Property created successfully!'
      setTimeout(() => {
        router.push('/properties')
      }, 1500)
    } else {
      error.value = data.detail || 'Failed to create property'
    }
  } catch (err) {
    error.value = 'Network error. Please check your connection.'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/properties')
}
</script>

<style scoped>
/* Leaflet marker icon fix */
:deep(.leaflet-marker-icon) {
  background-image: url('https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png');
}
</style>
