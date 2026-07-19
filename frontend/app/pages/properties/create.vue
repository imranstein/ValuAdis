<template>
  <div class="page-shell property-form-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Property registry</p>
        <h1 class="page-title">Register property.</h1>
        <p class="page-subtitle">Complete the property record, location, valuation, ownership, and document fields.</p>
      </div>
      <button class="btn-secondary" type="button" @click="router.push(backTarget)">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        {{ backLabel }}
      </button>
    </section>

    <PropertyWizard />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import PropertyWizard from '~/components/property/PropertyWizard.vue'
import { usePersona } from '~/composables/usePersona'

const router = useRouter()
// Phase E: property owners reach this page from /rentals/my-listings and
// cannot open the staff /properties registry — send them back to their own
// shell instead of a route the permission matrix will immediately bounce.
const { isOwner } = usePersona()
const backTarget = computed(() => (isOwner.value ? '/rentals/my-listings' : '/properties'))
const backLabel = computed(() => (isOwner.value ? 'My listings' : 'Properties'))
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
