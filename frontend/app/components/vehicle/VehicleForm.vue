<template>
  <div class="vehicle-form">
    <div class="form-header">
      <h3>{{ isEdit ? 'Edit Vehicle' : 'Add New Vehicle' }}</h3>
      <p class="text-gray-600">Enter vehicle information for valuation</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information -->
      <div class="form-section">
        <h4 class="section-title">Basic Information</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label">Make *</label>
            <input
              v-model="form.make"
              type="text"
              class="form-input"
              :class="{ 'error': errors.make }"
              placeholder="e.g., Toyota, Honda"
              required
            />
            <span v-if="errors.make" class="error-text">{{ errors.make }}</span>
          </div>

          <div>
            <label class="form-label">Model *</label>
            <input
              v-model="form.model"
              type="text"
              class="form-input"
              :class="{ 'error': errors.model }"
              placeholder="e.g., Corolla, Civic"
              required
            />
            <span v-if="errors.model" class="error-text">{{ errors.model }}</span>
          </div>

          <div>
            <label class="form-label">Year *</label>
            <input
              v-model.number="form.year"
              type="number"
              class="form-input"
              :class="{ 'error': errors.year }"
              :min="1900"
              :max="new Date().getFullYear() + 1"
              placeholder="e.g., 2020"
              required
            />
            <span v-if="errors.year" class="error-text">{{ errors.year }}</span>
          </div>

          <div>
            <label class="form-label">VIN *</label>
            <input
              v-model="form.vin"
              type="text"
              class="form-input"
              :class="{ 'error': errors.vin }"
              placeholder="17-character VIN"
              maxlength="17"
              required
            />
            <span v-if="errors.vin" class="error-text">{{ errors.vin }}</span>
          </div>

          <div>
            <label class="form-label">Plate Number *</label>
            <input
              v-model="form.plate_number"
              type="text"
              class="form-input"
              :class="{ 'error': errors.plate_number }"
              placeholder="e.g., AA-123-BC"
              required
            />
            <span v-if="errors.plate_number" class="error-text">{{ errors.plate_number }}</span>
          </div>

          <div>
            <label class="form-label">Color</label>
            <input
              v-model="form.color"
              type="text"
              class="form-input"
              placeholder="e.g., White, Black, Silver"
            />
          </div>
        </div>
      </div>

      <!-- Vehicle Specifications -->
      <div class="form-section">
        <h4 class="section-title">Specifications</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label">Body Type</label>
            <select v-model="form.body_type" class="form-select">
              <option value="">Select body type</option>
              <option value="sedan">Sedan</option>
              <option value="suv">SUV</option>
              <option value="hatchback">Hatchback</option>
              <option value="pickup">Pickup</option>
              <option value="truck">Truck</option>
              <option value="van">Van</option>
              <option value="coupe">Coupe</option>
              <option value="convertible">Convertible</option>
            </select>
          </div>

          <div>
            <label class="form-label">Fuel Type</label>
            <select v-model="form.fuel_type" class="form-select">
              <option value="">Select fuel type</option>
              <option value="gasoline">Gasoline</option>
              <option value="diesel">Diesel</option>
              <option value="hybrid">Hybrid</option>
              <option value="electric">Electric</option>
              <option value="lpg">LPG</option>
            </select>
          </div>

          <div>
            <label class="form-label">Transmission</label>
            <select v-model="form.transmission" class="form-select">
              <option value="">Select transmission</option>
              <option value="manual">Manual</option>
              <option value="automatic">Automatic</option>
              <option value="cvt">CVT</option>
            </select>
          </div>

          <div>
            <label class="form-label">Engine Capacity (cc)</label>
            <input
              v-model.number="form.engine_capacity"
              type="number"
              class="form-input"
              placeholder="e.g., 1500"
              min="0"
            />
          </div>

          <div>
            <label class="form-label">Current Mileage (km)</label>
            <input
              v-model.number="form.mileage"
              type="number"
              class="form-input"
              placeholder="e.g., 50000"
              min="0"
            />
          </div>

          <div>
            <label class="form-label">Previous Owners</label>
            <input
              v-model.number="form.previous_owners"
              type="number"
              class="form-input"
              placeholder="Number of previous owners"
              min="1"
            />
          </div>
        </div>
      </div>

      <!-- Ethiopian Specific -->
      <div class="form-section">
        <h4 class="section-title">Ethiopian Market Information</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label">Region</label>
            <select v-model="form.region" class="form-select">
              <option value="">Select region</option>
              <option value="Addis Ababa">Addis Ababa</option>
              <option value="Oromia">Oromia</option>
              <option value="Amhara">Amhara</option>
              <option value="Tigray">Tigray</option>
              <option value="Southern">Southern</option>
              <option value="Somali">Somali</option>
              <option value="Afar">Afar</option>
              <option value="Benishangul">Benishangul</option>
              <option value="Gambela">Gambela</option>
              <option value="Harari">Harari</option>
              <option value="Dire Dawa">Dire Dawa</option>
            </select>
          </div>

          <div>
            <label class="form-label">City</label>
            <input
              v-model="form.city"
              type="text"
              class="form-input"
              placeholder="e.g., Addis Ababa, Bahir Dar"
            />
          </div>

          <div>
            <label class="form-label">Import Year</label>
            <input
              v-model.number="form.import_year"
              type="number"
              class="form-input"
              :min="1900"
              :max="new Date().getFullYear()"
              placeholder="Year vehicle was imported to Ethiopia"
            />
          </div>

          <div class="flex items-center">
            <input
              v-model="form.custom_duty_paid"
              type="checkbox"
              id="custom_duty_paid"
              class="form-checkbox"
            />
            <label for="custom_duty_paid" class="ml-2 text-sm">
              Custom duty paid
            </label>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn-secondary"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="btn-primary"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting" class="spinner"></span>
          {{ isSubmitting ? 'Saving...' : (isEdit ? 'Update Vehicle' : 'Add Vehicle') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const isSubmitting = ref(false)
const errors = reactive({})

// Form data
const form = reactive({
  make: '',
  model: '',
  year: new Date().getFullYear(),
  vin: '',
  plate_number: '',
  body_type: '',
  fuel_type: '',
  transmission: '',
  engine_capacity: null,
  mileage: null,
  color: '',
  custom_duty_paid: false,
  import_year: null,
  previous_owners: 1,
  region: '',
  city: ''
})

// Initialize form with initial data
watch(() => props.initialData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(form, newData)
  }
}, { immediate: true })

// Validation
const validateForm = () => {
  const newErrors = {}
  
  // Required fields
  if (!form.make.trim()) newErrors.make = 'Make is required'
  if (!form.model.trim()) newErrors.model = 'Model is required'
  if (!form.year) newErrors.year = 'Year is required'
  if (form.year < 1900 || form.year > new Date().getFullYear() + 1) {
    newErrors.year = 'Please enter a valid year'
  }
  if (!form.vin.trim()) newErrors.vin = 'VIN is required'
  if (form.vin.length !== 17) newErrors.vin = 'VIN must be 17 characters'
  if (!form.plate_number.trim()) newErrors.plate_number = 'Plate number is required'
  
  // VIN validation (basic)
  if (form.vin && !/^[A-HJ-NPR-Z0-9]{17}$/.test(form.vin)) {
    newErrors.vin = 'Invalid VIN format'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

// Submit handler
const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  try {
    await emit('submit', { ...form })
  } finally {
    isSubmitting.value = false
  }
}

// Clear errors when user types
watch(() => form.make, () => delete errors.make)
watch(() => form.model, () => delete errors.model)
watch(() => form.year, () => delete errors.year)
watch(() => form.vin, () => delete errors.vin)
watch(() => form.plate_number, () => delete errors.plate_number)
</script>

<style scoped>
.vehicle-form {
  @apply bg-white rounded-lg shadow-sm p-6;
}

.form-header {
  @apply mb-6;
}

.form-header h3 {
  @apply text-lg font-semibold text-gray-900 mb-1;
}

.form-header p {
  @apply text-sm;
}

.form-section {
  @apply mb-8;
}

.section-title {
  @apply text-base font-medium text-gray-900 mb-4 pb-2 border-b border-gray-200;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-input,
.form-select {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.form-input.error,
.form-select.error {
  @apply border-red-300 focus:ring-red-500 focus:border-red-500;
}

.error-text {
  @apply text-xs text-red-600 mt-1;
}

.form-checkbox {
  @apply h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded;
}

.form-actions {
  @apply flex justify-end space-x-3 pt-6 border-t border-gray-200;
}

.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500;
}

.spinner {
  @apply inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
