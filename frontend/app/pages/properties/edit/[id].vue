<template>
  <div class="edit-property-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Edit Property</h1>
        <p>Update property information and details</p>
      </div>
      <div class="header-actions">
        <Button
          label="View Property"
          icon="pi pi-eye"
          severity="secondary"
          @click="viewProperty"
        />
        <Button
          label="Back to Properties"
          icon="pi pi-arrow-left"
          severity="secondary"
          @click="goBack"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingProperty" class="loading-container">
      <ProgressSpinner />
      <p>Loading property data...</p>
    </div>

    <!-- Property Form -->
    <div v-else class="form-container">
      <PropertyForm
        :initial-data="formData"
        :loading="loading"
        @submit="handleSubmit"
        @cancel="goBack"
        @save-draft="saveDraft"
      />
    </div>

    <!-- Messages -->
    <Message v-if="error" severity="error" :closable="false">
      {{ error }}
    </Message>

    <Message v-if="success" severity="success" :closable="false">
      {{ success }}
    </Message>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PropertyForm from '~/components/property/PropertyForm.vue'

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

function viewProperty() {
  router.push(`/properties/${route.params.id}`)
}

function saveDraft(data) {
  // Save draft to localStorage
  localStorage.setItem('property_draft_edit', JSON.stringify(data))
  success.value = 'Draft saved successfully!'
}

function goBack() {
  router.push('/properties')
}
</script>

<style scoped>
.edit-property-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.header-content p {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.loading-container p {
  margin-top: 1rem;
  color: #64748b;
  font-size: 1rem;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
}
</style>
