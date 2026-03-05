<template>
  <div class="edit-property-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Edit Property</h1>
        <p v-if="propertyRef" class="ref-tag">{{ propertyRef }}</p>
        <p v-else>Update property information and details</p>
      </div>
      <div class="header-actions">
        <Button
          label="View"
          icon="pi pi-eye"
          severity="secondary"
          outlined
          @click="router.push(`/properties/${route.params.id}`)"
        />
        <Button
          label="Back"
          icon="pi pi-arrow-left"
          severity="secondary"
          outlined
          @click="router.push('/properties')"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Loading property data...</p>
    </div>

    <Message v-else-if="loadError" severity="error" :closable="false">
      {{ loadError }}
    </Message>

    <PropertyWizard v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePropertyWizardStore } from '~/stores/propertyWizard'
import PropertyWizard from '~/components/property/PropertyWizard.vue'

const router = useRouter()
const route = useRoute()
const store = usePropertyWizardStore()

const loading = ref(true)
const loadError = ref('')
const propertyRef = ref('')

onMounted(async () => {
  const propertyId = Number(route.params.id)
  if (!Number.isInteger(propertyId) || propertyId <= 0) {
    loadError.value = 'Invalid property ID in URL.'
    loading.value = false
    return
  }
  const token = localStorage.getItem('valuadis_token')
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'

  try {
    const res = await fetch(`${API_BASE}/api/v1/properties/${propertyId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      loadError.value = `Failed to load property (${res.status})`
      return
    }
    const json = await res.json()
    const property = json.data || json
    store.loadFromProperty(property)
    propertyRef.value = property.property_ref || ''
  } catch {
    loadError.value = 'Network error. Please check your connection.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.edit-property-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.75rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.18);
}

.header-content h1 { font-size: 1.75rem; font-weight: 700; margin: 0 0 0.25rem; }
.ref-tag { font-size: 0.85rem; font-family: monospace; opacity: 0.85; margin: 0; }
.header-actions { display: flex; gap: 0.75rem; }

.loading-state {
  display: flex; flex-direction: column; align-items: center; gap: 1rem;
  padding: 4rem; background: white; border-radius: 12px;
  border: 1px solid #e2e8f0; color: #64748b;
}

@media (max-width: 640px) {
  .edit-property-page { padding: 0 0.5rem 2rem; }
  .page-header { padding: 1.25rem; flex-direction: column; text-align: center; }
  .header-actions { justify-content: center; }
}
</style>
