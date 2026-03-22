<template>
  <div class="vehicles-page">
    <!-- Header -->
    <div class="page-header bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-8 rounded-2xl mb-8 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-4xl font-bold mb-2">My Vehicles</h1>
          <p class="text-emerald-50">Manage and value your vehicle portfolio</p>
        </div>
        <button
          @click="goToRegister"
          class="bg-white text-emerald-600 font-semibold px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300"
        >
          <i class="pi pi-plus mr-2"></i>
          Add Vehicle
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <i class="pi pi-spin pi-spinner text-4xl text-emerald-600 animate-spin"></i>
      <p class="text-gray-600 mt-4">Loading vehicles...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="vehicles.length === 0" class="text-center py-12 bg-gradient-to-br from-gray-50 to-emerald-50 rounded-2xl border border-gray-200">
      <i class="pi pi-car text-6xl text-gray-300 mb-4"></i>
      <p class="text-gray-600 text-lg">No vehicles registered yet</p>
      <button
        @click="goToRegister"
        class="mt-6 bg-emerald-600 text-white font-semibold px-6 py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300"
      >
        <i class="pi pi-plus mr-2"></i>
        Register Your First Vehicle
      </button>
    </div>

    <!-- Vehicles Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="vehicle in vehicles"
        :key="vehicle.id"
        class="vehicle-card bg-white rounded-2xl shadow-lg hover:shadow-xl border border-gray-100 overflow-hidden transform hover:scale-105 transition-all duration-300"
      >
        <!-- Card Header -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xl font-bold">{{ vehicle.make }} {{ vehicle.model }}</h3>
            <span class="bg-white/20 px-3 py-1 rounded-full text-sm font-semibold">{{ vehicle.year }}</span>
          </div>
          <p class="text-emerald-50">{{ vehicle.type }}</p>
        </div>

        <!-- Card Body -->
        <div class="p-6 space-y-4">
          <!-- Vehicle Details -->
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <i class="pi pi-id-card text-emerald-600 text-xl"></i>
              <div>
                <p class="text-xs text-gray-500">VIN</p>
                <p class="text-sm font-semibold text-gray-800 truncate">{{ vehicle.vin }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <i class="pi pi-tag text-emerald-600 text-xl"></i>
              <div>
                <p class="text-xs text-gray-500">Plate Number</p>
                <p class="text-sm font-semibold text-gray-800">{{ vehicle.plate_number }}</p>
              </div>
            </div>
            <div v-if="vehicle.region" class="flex items-center gap-3">
              <i class="pi pi-map-marker text-emerald-600 text-xl"></i>
              <div>
                <p class="text-xs text-gray-500">Region</p>
                <p class="text-sm font-semibold text-gray-800">{{ vehicle.region }}</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-4 border-t border-gray-200">
            <button
              @click="editVehicle(vehicle.id)"
              class="flex-1 bg-emerald-50 text-emerald-600 font-semibold py-2 rounded-lg hover:bg-emerald-100 transition-all duration-200"
            >
              <i class="pi pi-pencil mr-2"></i>
              Edit
            </button>
            <button
              @click="deleteVehicle(vehicle.id)"
              class="flex-1 bg-red-50 text-red-600 font-semibold py-2 rounded-lg hover:bg-red-100 transition-all duration-200"
            >
              <i class="pi pi-trash mr-2"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const vehicles = ref([])
const loading = ref(true)

const fetchVehicles = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/v1/vehicles', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      vehicles.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching vehicles:', error)
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/vehicles/register')
}

const editVehicle = (id: number) => {
  router.push(`/vehicles/edit/${id}`)
}

const deleteVehicle = async (id: number) => {
  if (!confirm('Are you sure you want to delete this vehicle?')) return

  try {
    const response = await fetch(`/api/v1/vehicles/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      vehicles.value = vehicles.value.filter(v => v.id !== id)
    }
  } catch (error) {
    console.error('Error deleting vehicle:', error)
  }
}

onMounted(() => {
  fetchVehicles()
})
</script>

<style scoped>
.vehicle-card {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
