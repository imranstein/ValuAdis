<template>
  <form class="vehicle-form bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100" @submit.prevent="submitForm">
    <!-- Header with Gradient -->
    <div class="form-header bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-black opacity-10"></div>
      <div class="absolute top-0 right-0 w-40 h-40 bg-white opacity-5 rounded-full -mr-20 -mt-20"></div>
      <div class="absolute bottom-0 left-0 w-32 h-32 bg-white opacity-5 rounded-full -ml-16 -mb-16"></div>

      <div class="relative z-10 flex items-center gap-6">
        <div class="icon-wrap bg-white/20 backdrop-blur-sm p-4 rounded-2xl border border-white/30 shadow-lg">
          <i class="pi pi-car text-4xl text-white"></i>
        </div>
        <div class="flex-1">
          <h2 class="text-3xl font-bold text-white mb-2 tracking-tight">Vehicle Information</h2>
          <p class="text-emerald-50 text-lg font-medium">Register your vehicle details</p>
        </div>
      </div>
    </div>

    <div class="form-body p-10 space-y-8">
      <!-- Vehicle Classification -->
      <section class="form-section bg-gradient-to-br from-gray-50 to-emerald-50 rounded-2xl p-8 border border-gray-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-tag text-white text-xl"></i>
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-800">Vehicle Classification</h3>
            <p class="text-gray-600 text-sm mt-1">Enter your vehicle type and details</p>
          </div>
        </div>

        <div class="space-y-6">
          <!-- Vehicle Type -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Vehicle Type <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.type"
              type="text"
              placeholder="e.g., Sedan, SUV, Truck"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <!-- Make -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Make <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.make"
              type="text"
              placeholder="e.g., Toyota, BMW, Mercedes"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <!-- Model -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Model <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.model"
              type="text"
              placeholder="e.g., Camry, X5, C-Class"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <!-- Year -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Year <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.year"
              type="number"
              min="1900"
              :max="currentYear"
              placeholder="e.g., 2022"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>
        </div>
      </section>

      <!-- VIN & Registration -->
      <section class="form-section bg-gradient-to-br from-gray-50 to-emerald-50 rounded-2xl p-8 border border-gray-200 shadow-sm">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg">
            <i class="pi pi-id-card text-white text-xl"></i>
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-800">Identification</h3>
            <p class="text-gray-600 text-sm mt-1">VIN and registration details</p>
          </div>
        </div>

        <div class="space-y-6">
          <!-- VIN -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              VIN <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.vin"
              type="text"
              placeholder="Vehicle Identification Number"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>

          <!-- Registration Number -->
          <div class="field">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Registration/Plate Number <span class="required text-red-500">*</span>
            </label>
            <input
              v-model="form.registration"
              type="text"
              placeholder="e.g., AA-1234"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              required
            />
          </div>
        </div>
      </section>

      <!-- Submit Button -->
      <div class="flex gap-4">
        <button
          type="submit"
          class="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold py-3 rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300"
        >
          <i class="pi pi-check mr-2"></i>
          Save Vehicle
        </button>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const currentYear = new Date().getFullYear()

const form = reactive({
  type: '',
  make: '',
  model: '',
  year: currentYear,
  vin: '',
  registration: ''
})

const emit = defineEmits(['submit'])

const submitForm = () => {
  // Validate required fields
  if (!form.type || !form.make || !form.model || !form.year || !form.vin || !form.registration) {
    console.error('All fields are required')
    return
  }

  emit('submit', {
    type: form.type,
    make: form.make,
    model: form.model,
    year: form.year,
    vin: form.vin,
    registration: form.registration,
    plate_number: form.registration
  })
}
</script>

<style scoped>
.vehicle-form {
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

.field {
  position: relative;
}

input:focus {
  outline: none;
}
</style>
