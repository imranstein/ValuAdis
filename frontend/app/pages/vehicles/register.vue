<template>
  <div class="register-page max-w-2xl mx-auto py-8">
    <VehicleForm @submit="handleSubmit" />
    <p v-if="error" class="text-red-600 mt-4">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VehicleForm from '~/components/VehicleForm.vue'

const router = useRouter()
const route = useRoute()
const error = ref('')

const handleSubmit = async (data: any) => {
  try {
    const propertyId = route.query.property_id

    const payload = {
      ...data,
      property_id: propertyId || null
    }

    const response = await fetch('/api/v1/vehicles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const err = await response.json()
      error.value = err.detail || 'Failed to register vehicle'
      return
    }

    const vehicle = await response.json()
    router.push('/vehicles/list')
  } catch (e) {
    error.value = 'Error registering vehicle'
  }
}
</script>
