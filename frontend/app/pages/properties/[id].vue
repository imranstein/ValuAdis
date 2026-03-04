<template>
  <div class="property-detail-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <ProgressSpinner />
      <p>Loading property details...</p>
    </div>
    
    <!-- Error State -->
    <Message v-if="error" severity="error" :closable="false">
      {{ error }}
    </Message>
    
    <!-- Property Detail View - only render when data is ready -->
    <PropertyDetailView
      v-if="!loading && !error && property && Object.keys(property).length > 0"
      :property="property"
      :valuations="valuations"
      :readonly="readonly"
      @back="goBack"
      @edit="editProperty"
      @create-valuation="createValuation"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PropertyDetailView from '~/components/property/PropertyDetailView.vue'

const router = useRouter()
const route = useRoute()

const property = ref({})
const valuations = ref([])
const loading = ref(true)
const error = ref(null)
const readonly = ref(false)

// Authenticated fetch helper
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('valuadis_token')
  
  if (!token) {
    router.push('/login')
    throw new Error('No authentication token')
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP ${response.status}: ${errorText}`)
  }
  
  return response
}

onMounted(async () => {
  // Run both fetches in parallel for better performance
  try {
    const [propertyResponse, valuationsResponse] = await Promise.allSettled([
      loadProperty(),
      loadValuations()
    ])
    
    // Handle individual failures
    if (propertyResponse.status === 'rejected') {
      error.value = propertyResponse.reason.message || 'Failed to load property details'
    }
    
    if (valuationsResponse.status === 'rejected') {
      console.error('Failed to load valuations:', valuationsResponse.reason)
      // Don't set main error for valuations failure, just log it
    }
  } catch (err) {
    error.value = 'Failed to load property details'
  } finally {
    loading.value = false
  }
})

async function loadProperty() {
  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'
    const response = await fetchWithAuth(`${API_BASE}/api/v1/properties/${route.params.id}`)
    
    const result = await response.json()
    property.value = result.data || result
  } catch (err) {
    throw err // Re-throw to be handled by Promise.allSettled
  }
}

async function loadValuations() {
  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'
    const response = await fetchWithAuth(`${API_BASE}/api/v1/valuations?property_id=${route.params.id}`)
    
    const result = await response.json()
    valuations.value = result.data || []
  } catch (err) {
    console.error('Failed to load valuations:', err)
    throw err // Re-throw to be handled by Promise.allSettled
  }
}

function goBack() {
  router.push('/properties')
}

function editProperty(id) {
  router.push(`/properties/edit/${id}`)
}

function createValuation(id) {
  router.push(`/valuations/create?property_id=${id}`)
}
</script>

<style scoped>
.property-detail-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  z-index: 1000;
}

.loading-overlay p {
  color: #64748b;
  font-size: 1rem;
}
</style>
