<template>
  <div class="page-shell property-form-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Property registry</p>
        <h1 class="page-title">Register property.</h1>
        <p class="page-subtitle">Complete the property record, location, valuation, ownership, and document fields.</p>
      </div>
      <button class="btn-secondary" type="button" @click="router.push('/properties')">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Properties
      </button>
    </section>

    <PropertyWizard />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import PropertyWizard from '~/components/property/PropertyWizard.vue'

const router = useRouter()
</script>

<style scoped>
.property-form-page {
  max-width: 960px;
  margin: 0 auto;
  gap: 24px;
}

@media (max-width: 768px) {
  .property-form-page .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
