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
    <template v-if="!loading && !error && property && Object.keys(property).length > 0">
      <PropertyDetailView
        :property="property"
        :valuations="valuations"
        :readonly="readonly"
        @back="goBack"
        @edit="editProperty"
        @create-valuation="createValuation"
      />

      <!-- Reviewer Valuation Panel -->
      <ValuationReviewPanel
        v-if="isReviewer && aiEstimate"
        :property-id="property.id"
        :ai-estimate="aiEstimate"
        :trust-score="trustMetrics?.trust_score ?? null"
        :total-reviews="trustMetrics?.total_reviews"
        :property-context="propertyContext"
        class="review-panel-wrapper"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PropertyDetailView from '~/components/property/PropertyDetailView.vue'
import ValuationReviewPanel from '~/components/property/ValuationReviewPanel.vue'
import { getAccessToken } from '~/utils/authToken'

const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const property = ref({})
const valuations = ref([])
const loading = ref(true)
const error = ref(null)
const readonly = ref(false)
const currentUser = ref(null)
const trustMetrics = ref(null)

const reviewerRoles = ['valuer', 'firm_admin', 'municipal_admin', 'system_admin']
const isReviewer = computed(() => {
  const user = currentUser.value
  if (!user) return false
  // Handle single string role, array of role strings, or array of role objects
  const role = user.role
  if (!role) return false
  const roleNames = Array.isArray(role)
    ? role.map((r) => (typeof r === 'string' ? r : r?.name ?? ''))
    : [typeof role === 'string' ? role : role?.name ?? '']
  return roleNames.some((r) => reviewerRoles.includes(r))
})
const aiEstimate = computed(() => property.value?.ai_estimated_value ?? null)

// Build the context dict sent to the valuation feedback service so it can
// learn from property-type / condition / area patterns.
const propertyContext = computed(() => ({
  property_type: property.value?.property_type ?? null,
  municipality: property.value?.municipality ?? null,
  condition: property.value?.condition ?? null,
  area_sqm: property.value?.area_sqm ?? null,
}))

// Authenticated fetch helper
async function fetchWithAuth(url, options = {}) {
  const token = getAccessToken()
  
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
  // Load current user from localStorage
  const userJson = localStorage.getItem('valuadis_user')
  if (userJson) {
    try { currentUser.value = JSON.parse(userJson) } catch {}
  }

  // Run all fetches in parallel for better performance
  try {
    const [propertyResponse, valuationsResponse] = await Promise.allSettled([
      loadProperty(),
      loadValuations(),
      loadTrustMetrics(),
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
    const response = await fetchWithAuth(`${apiBase}/api/v1/properties/${route.params.id}`)
    
    const result = await response.json()
    property.value = result.data || result
  } catch (err) {
    throw err // Re-throw to be handled by Promise.allSettled
  }
}

async function loadValuations() {
  try {
    const response = await fetchWithAuth(`${apiBase}/api/v1/valuations?property_id=${route.params.id}`)
    
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
  router.push(`/valuations/quick?property_id=${id}`)
}

async function loadTrustMetrics() {
  try {
    const token = getAccessToken()
    const res = await fetch(`${apiBase}/api/v1/valuation-feedback/metrics`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (res.ok) trustMetrics.value = await res.json()
  } catch {}
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

.review-panel-wrapper {
  max-width: 560px;
  margin: 1.5rem auto 0;
}
</style>
