<template>
  <div style="padding: 2rem; max-width: 1200px; margin: 0 auto;">
    <div style="margin-bottom: 1.5rem;">
      <h1 style="font-size: 1.875rem; font-weight: bold; color: #111827;">Edit Property</h1>
      <p style="color: #6b7280; margin-top: 0.25rem;">Update property information</p>
    </div>

    <div v-if="loadingProperty" style="text-align: center; padding: 3rem;">
      <ProgressBar mode="indeterminate" style="height: 6px;" />
      <p style="margin-top: 1rem; color: #6b7280;">Loading property...</p>
    </div>

    <Card v-else>
      <template #content>
        <form @submit.prevent="handleSubmit" style="display: flex; flex-direction: column; gap: 1.5rem;">
          <div>
            <label for="address" style="display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.5rem;">
              Address *
            </label>
            <InputText
              id="address"
              v-model="formData.address"
              style="width: 100%;"
              required
            />
          </div>

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
              required
            />
          </div>

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
            />
          </div>

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
            />
          </div>

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
            />
          </div>

          <div v-if="error" style="padding: 0.75rem; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; color: #dc2626;">{{ error }}</p>
          </div>

          <div v-if="success" style="padding: 0.75rem; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 0.5rem;">
            <p style="font-size: 0.875rem; color: #16a34a;">{{ success }}</p>
          </div>

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
              label="Update Property"
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
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const formData = ref({
  address: '',
  municipality: '',
  property_type: '',
  area_sqm: null,
  building_area_sqm: null,
  year_built: null,
  number_of_rooms: null
})

const loadingProperty = ref(true)
const loading = ref(false)
const error = ref(null)
const success = ref(null)

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

onMounted(async () => {
  await loadProperty()
})

async function loadProperty() {
  loadingProperty.value = true
  try {
    const token = localStorage.getItem('valuadis_token')
    const propertyId = route.params.id

    const response = await fetch(`http://localhost:8020/api/v1/properties/${propertyId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      const property = result.data || result
      
      formData.value = {
        address: property.address || '',
        municipality: property.municipality || '',
        property_type: property.property_type || '',
        area_sqm: property.area_sqm || null,
        building_area_sqm: property.building_area_sqm || null,
        year_built: property.year_built || null,
        number_of_rooms: property.number_of_rooms || null
      }
    } else {
      error.value = 'Failed to load property'
    }
  } catch (err) {
    error.value = 'Network error. Please check your connection.'
  } finally {
    loadingProperty.value = false
  }
}

async function handleSubmit() {
  error.value = null
  success.value = null
  loading.value = true

  try {
    const token = localStorage.getItem('valuadis_token')
    const propertyId = route.params.id

    const response = await fetch(`http://localhost:8020/api/v1/properties/${propertyId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(formData.value)
    })

    const data = await response.json()

    if (response.ok) {
      success.value = 'Property updated successfully!'
      setTimeout(() => {
        router.push('/properties')
      }, 1500)
    } else {
      error.value = data.detail || 'Failed to update property'
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
