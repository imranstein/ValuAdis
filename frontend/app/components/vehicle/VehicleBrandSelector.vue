<template>
  <div class="vehicle-brand-selector">
    <div class="selector-header">
      <h3>Vehicle Selection</h3>
      <p class="text-sm text-gray-600">Select your vehicle brand, model, and year</p>
    </div>

    <!-- Brand Selection -->
    <div class="selection-group">
      <label class="selection-label">Brand *</label>
      <div class="selection-input-wrapper">
        <select 
          v-model="selectedBrand" 
          @change="handleBrandChange"
          :disabled="loading.brands"
          class="selection-select"
          :class="{ 'error': errors.brand }"
        >
          <option value="">Select Brand</option>
          <option 
            v-for="brand in brands" 
            :key="brand" 
            :value="brand"
          >
            {{ brand }}
          </option>
        </select>
        <div v-if="loading.brands" class="loading-spinner">
          <i class="pi pi-spin pi-spinner"></i>
        </div>
      </div>
      <span v-if="errors.brand" class="error-text">{{ errors.brand }}</span>
    </div>

    <!-- Model Selection -->
    <div class="selection-group">
      <label class="selection-label">Model *</label>
      <div class="selection-input-wrapper">
        <select 
          v-model="selectedModel" 
          @change="handleModelChange"
          :disabled="!selectedBrand || loading.models"
          class="selection-select"
          :class="{ 'error': errors.model }"
        >
          <option value="">Select Model</option>
          <option 
            v-for="model in models" 
            :key="model" 
            :value="model"
          >
            {{ model }}
          </option>
        </select>
        <div v-if="loading.models" class="loading-spinner">
          <i class="pi pi-spin pi-spinner"></i>
        </div>
      </div>
      <span v-if="errors.model" class="error-text">{{ errors.model }}</span>
    </div>

    <!-- Year Selection -->
    <div class="selection-group">
      <label class="selection-label">Year *</label>
      <div class="selection-input-wrapper">
        <select 
          v-model="selectedYear" 
          @change="handleYearChange"
          :disabled="!selectedModel || loading.years"
          class="selection-select"
          :class="{ 'error': errors.year }"
        >
          <option value="">Select Year</option>
          <option 
            v-for="year in years" 
            :key="year" 
            :value="year"
          >
            {{ year }}
          </option>
        </select>
        <div v-if="loading.years" class="loading-spinner">
          <i class="pi pi-spin pi-spinner"></i>
        </div>
      </div>
      <span v-if="errors.year" class="error-text">{{ errors.year }}</span>
    </div>

    <!-- Vehicle Information Display -->
    <div v-if="selectedBrand && selectedModel && selectedYear" class="vehicle-info">
      <div class="info-header">
        <h4>Selected Vehicle</h4>
        <button 
          @click="fetchVehicleSpecs"
          :disabled="loading.specs"
          class="specs-button"
        >
          <i v-if="loading.specs" class="pi pi-spin pi-spinner"></i>
          <i v-else class="pi pi-search"></i>
          {{ loading.specs ? 'Loading...' : 'Get Specifications' }}
        </button>
      </div>
      
      <div class="vehicle-display">
        <div class="vehicle-name">
          {{ selectedBrand }} {{ selectedModel }} {{ selectedYear }}
        </div>
        
        <div v-if="vehicleSpecs" class="vehicle-specs">
          <div class="spec-item" v-if="vehicleSpecs.body_type">
            <span class="spec-label">Body Type:</span>
            <span class="spec-value">{{ formatBodyType(vehicleSpecs.body_type) }}</span>
          </div>
          <div class="spec-item" v-if="vehicleSpecs.engine">
            <span class="spec-label">Engine:</span>
            <span class="spec-value">{{ vehicleSpecs.engine }}</span>
          </div>
          <div class="spec-item" v-if="vehicleSpecs.fuel_type">
            <span class="spec-label">Fuel Type:</span>
            <span class="spec-value">{{ formatFuelType(vehicleSpecs.fuel_type) }}</span>
          </div>
          <div class="spec-item" v-if="vehicleSpecs.transmission">
            <span class="spec-label">Transmission:</span>
            <span class="spec-value">{{ formatTransmission(vehicleSpecs.transmission) }}</span>
          </div>
          <div class="spec-item" v-if="vehicleSpecs.drive_type">
            <span class="spec-label">Drive Type:</span>
            <span class="spec-value">{{ formatDriveType(vehicleSpecs.drive_type) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Alternative: VIN Input -->
    <div class="vin-alternative">
      <div class="vin-header">
        <h4>Or Enter VIN Number</h4>
        <p class="text-sm text-gray-600">Auto-populate all vehicle information</p>
      </div>
      
      <div class="vin-input-group">
        <input
          v-model="vinInput"
          @input="handleVinInput"
          @blur="decodeVin"
          type="text"
          placeholder="Enter 17-character VIN"
          maxlength="17"
          class="vin-input"
          :class="{ 'error': errors.vin }"
        />
        <button 
          @click="decodeVin"
          :disabled="!vinInput || vinInput.length !== 17 || loading.vin"
          class="vin-decode-button"
        >
          <i v-if="loading.vin" class="pi pi-spin pi-spinner"></i>
          <i v-else class="pi pi-search"></i>
          Decode
        </button>
      </div>
      <span v-if="errors.vin" class="error-text">{{ errors.vin }}</span>
      
      <div v-if="vinData" class="vin-results">
        <div class="vin-success">
          <i class="pi pi-check-circle"></i>
          <span>VIN decoded successfully!</span>
        </div>
        <div class="vin-vehicle-info">
          <strong>{{ vinData.make }} {{ vinData.model }} {{ vinData.year }}</strong>
          <button @click="applyVinData" class="apply-vin-button">
            Apply This Data
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { fetchVehicleBrands, fetchVehicleModels, decodeVehicleVin } from '@/services/vehicleDataService'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['selection-change', 'specs-updated', 'vin-decoded'])

// Reactive data
const selectedBrand = ref('')
const selectedModel = ref('')
const selectedYear = ref('')
const vinInput = ref('')

const brands = ref([])
const models = ref([])
const years = ref([])
const vehicleSpecs = ref(null)
const vinData = ref(null)

const loading = reactive({
  brands: false,
  models: false,
  years: false,
  specs: false,
  vin: false
})

const errors = reactive({
  brand: '',
  model: '',
  year: '',
  vin: ''
})

// Initialize with initial data
watch(() => props.initialData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    selectedBrand.value = newData.make || ''
    selectedModel.value = newData.model || ''
    selectedYear.value = newData.year || ''
    vinInput.value = newData.vin || ''
  }
}, { immediate: true })

// Load brands on mount
onMounted(async () => {
  await loadBrands()
})

// Methods
const loadBrands = async () => {
  loading.brands = true
  errors.brand = ''
  
  try {
    brands.value = await fetchVehicleBrands()
  } catch (error) {
    errors.brand = 'Failed to load vehicle brands'
  } finally {
    loading.brands = false
  }
}

const handleBrandChange = async () => {
  if (!selectedBrand.value) {
    models.value = []
    years.value = []
    vehicleSpecs.value = null
    return
  }
  
  loading.models = true
  errors.model = ''
  models.value = []
  years.value = []
  vehicleSpecs.value = null
  
  try {
    models.value = await fetchVehicleModels(selectedBrand.value)
    emitSelectionChange()
  } catch (error) {
    errors.model = 'Failed to load models for this brand'
  } finally {
    loading.models = false
  }
}

const handleModelChange = () => {
  if (!selectedModel.value) {
    years.value = []
    vehicleSpecs.value = null
    return
  }
  
  // Generate years (current year back to 1990)
  const currentYear = new Date().getFullYear()
  years.value = Array.from({ length: currentYear - 1990 + 1 }, (_, i) => currentYear - i)
  
  emitSelectionChange()
}

const handleYearChange = () => {
  vehicleSpecs.value = null
  emitSelectionChange()
}

const fetchVehicleSpecs = async () => {
  if (!selectedBrand.value || !selectedModel.value || !selectedYear.value) {
    return
  }
  
  loading.specs = true
  
  try {
    // In a real implementation, this would call an API to get specifications
    // For now, we'll simulate with some basic data
    vehicleSpecs.value = {
      body_type: 'Sedan',
      engine: '2.0L',
      fuel_type: 'Gasoline',
      transmission: 'Automatic',
      drive_type: 'FWD'
    }
    
    emit('specs-updated', vehicleSpecs.value)
  } catch (error) {
    errors.model = 'Failed to fetch vehicle specifications'
  } finally {
    loading.specs = false
  }
}

const handleVinInput = () => {
  errors.vin = ''
  vinData.value = null
  
  // Validate VIN format
  if (vinInput.value && vinInput.value.length === 17) {
    const invalidChars = ['I', 'O', 'Q']
    const hasInvalidChars = invalidChars.some(char => 
      vinInput.value.toUpperCase().includes(char)
    )
    
    if (hasInvalidChars) {
      errors.vin = 'VIN cannot contain characters I, O, or Q'
    }
  }
}

const decodeVin = async () => {
  if (!vinInput.value || vinInput.value.length !== 17) {
    return
  }
  
  loading.vin = true
  errors.vin = ''
  vinData.value = null
  
  try {
    const decoded = await decodeVehicleVin(vinInput.value)
    vinData.value = decoded
    
    emit('vin-decoded', decoded)
  } catch (error) {
    errors.vin = 'Failed to decode VIN. Please check the VIN and try again.'
  } finally {
    loading.vin = false
  }
}

const applyVinData = () => {
  if (!vinData.value) return
  
  selectedBrand.value = vinData.value.make
  selectedModel.value = vinData.value.model
  selectedYear.value = parseInt(vinData.value.year)
  
  // Load models for the selected brand
  handleBrandChange()
  
  // Clear VIN input
  vinInput.value = ''
  vinData.value = null
  
  emitSelectionChange()
}

const emitSelectionChange = () => {
  emit('selection-change', {
    make: selectedBrand.value,
    model: selectedModel.value,
    year: selectedYear.value ? parseInt(selectedYear.value) : null,
    vin: vinInput.value
  })
}

// Formatting functions
const formatBodyType = (bodyType) => {
  return bodyType.split(' ').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ')
}

const formatFuelType = (fuelType) => {
  return fuelType.charAt(0).toUpperCase() + fuelType.slice(1).toLowerCase()
}

const formatTransmission = (transmission) => {
  return transmission.charAt(0).toUpperCase() + transmission.slice(1).toLowerCase()
}

const formatDriveType = (driveType) => {
  return driveType.toUpperCase()
}

// Clear errors when user makes selections
watch(selectedBrand, () => delete errors.brand)
watch(selectedModel, () => delete errors.model)
watch(selectedYear, () => delete errors.year)
watch(vinInput, () => delete errors.vin)
</script>

<style scoped>
.vehicle-brand-selector {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.selector-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.selector-header p {
  font-size: 0.875rem;
  color: #6b7280;
}

.selection-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selection-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.selection-input-wrapper {
  position: relative;
}

.selection-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  outline: none;
  appearance: none;
  padding-right: 2.5rem;
}

.selection-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.selection-select.error {
  border-color: #ef4444;
}

.selection-select.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.selection-select:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.loading-spinner {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #3b82f6;
}

.error-text {
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.vehicle-info {
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-header h4 {
  font-size: 1rem;
  font-weight: 500;
  color: #1e3a8a;
}

.specs-button {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #1d4ed8;
  background-color: #dbeafe;
  border-radius: 0.375rem;
  cursor: pointer;
  border: none;
}

.specs-button:hover {
  background-color: #bfdbfe;
}

.specs-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.vehicle-display {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.vehicle-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e3a8a;
}

.vehicle-specs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.spec-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.spec-label {
  font-weight: 500;
  color: #6b7280;
}

.spec-value {
  color: #111827;
}

.vin-alternative {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.vin-header h4 {
  font-size: 1rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.25rem;
}

.vin-header p {
  font-size: 0.875rem;
  color: #6b7280;
}

.vin-input-group {
  display: flex;
  gap: 0.5rem;
}

.vin-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  outline: none;
}

.vin-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.vin-input.error {
  border-color: #ef4444;
}

.vin-input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.vin-decode-button {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  background-color: #3b82f6;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.vin-decode-button:hover {
  background-color: #2563eb;
}

.vin-decode-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.vin-decode-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vin-results {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.vin-success {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #15803d;
  font-weight: 500;
}

.vin-vehicle-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.apply-vin-button {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #15803d;
  background-color: #bbf7d0;
  border-radius: 0.375rem;
  cursor: pointer;
  border: none;
}

.apply-vin-button:hover {
  background-color: #86efac;
}

.apply-vin-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
</style>
