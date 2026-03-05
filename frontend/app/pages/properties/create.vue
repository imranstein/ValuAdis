<template>
  <div class="create-property-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Register Property</h1>
        <p>Complete the 7-step wizard to register a new property</p>
      </div>
      <Button
        label="Back to Properties"
        icon="pi pi-arrow-left"
        severity="secondary"
        outlined
        @click="router.push('/properties')"
      />
    </div>

    <PropertyWizard />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import PropertyWizard from '~/components/property/PropertyWizard.vue'

const router = useRouter()
</script>

<style scoped>
.create-property-page {
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
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 24px rgba(5, 150, 105, 0.18);
}

.header-content h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
}

.header-content p {
  font-size: 0.95rem;
  opacity: 0.88;
  margin: 0;
}

@media (max-width: 640px) {
  .create-property-page { padding: 0 0.5rem 2rem; }
  .page-header { padding: 1.25rem; flex-direction: column; text-align: center; }
}
</style>
