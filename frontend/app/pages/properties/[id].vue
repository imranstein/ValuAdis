<template>
  <div class="property-detail-page">
    <PropertyDetailView
      :property="property"
      :valuations="valuations"
      :readonly="readonly"
      @back="goBack"
      @edit="editProperty"
      @create-valuation="createValuation"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <ProgressSpinner />
      <p>Loading property details...</p>
    </div>
    
    <!-- Error State -->
    <Message v-if="error" severity="error" :closable="false">
      {{ error }}
    </Message>
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

onMounted(async () => {
  await loadProperty()
  await loadValuations()
})

async function loadProperty() {
  loading.value = true
  error.value = null

  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`http://localhost:8020/api/v1/properties/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      property.value = result.data || result
    } else {
      error.value = 'Property not found'
    }
  } catch (err) {
    error.value = 'Failed to load property details'
  } finally {
    loading.value = false
  }
}

async function loadValuations() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`http://localhost:8020/api/v1/valuations?property_id=${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      valuations.value = result.data || []
    }
  } catch (err) {
    console.error('Failed to load valuations:', err)
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
