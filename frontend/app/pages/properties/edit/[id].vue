<template>
  <div class="page-shell edit-property-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Property registry</p>
        <h1 class="page-title">Edit property.</h1>
        <p class="page-subtitle">
          {{ propertyRef ? propertyRef : 'Update property information and details.' }}
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="router.push(`/properties/${route.params.id}`)">
          <i class="pi pi-eye" aria-hidden="true"></i>
          View
        </button>
        <button class="btn-secondary" type="button" @click="router.push('/properties')">
          <i class="pi pi-arrow-left" aria-hidden="true"></i>
          Properties
        </button>
      </div>
    </section>

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
import { getAccessToken } from '~/utils/authToken'

const router = useRouter()
const route = useRoute()
const store = usePropertyWizardStore()

const loading = ref(true)
const loadError = ref('')
const propertyRef = ref('')
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

onMounted(async () => {
  const propertyId = Number(route.params.id)
  if (!Number.isInteger(propertyId) || propertyId <= 0) {
    loadError.value = 'Invalid property ID in URL.'
    loading.value = false
    return
  }
  const token = getAccessToken()

  try {
    const res = await fetch(`${apiBase}/api/v1/properties/${propertyId}`, {
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
  gap: 24px;
}

.loading-state {
  display: flex; flex-direction: column; align-items: center; gap: 1rem;
  padding: 4rem; background: var(--surface); border-radius: var(--radius-lg);
  border: 1px solid var(--line); color: var(--muted);
}

@media (max-width: 640px) {
  .edit-property-page .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
