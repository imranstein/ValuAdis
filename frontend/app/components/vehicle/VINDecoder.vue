<template>
  <div class="vin-decoder">
    <div class="decoder-header">
      <h3>VIN Decoder</h3>
      <p>Enter a 17-character VIN to instantly decode vehicle information</p>
    </div>

    <div class="decoder-input">
      <div class="input-group">
        <input
          v-model="vinInput"
          @input="handleVinInput"
          @blur="decodeVin"
          type="text"
          placeholder="Enter 17-character VIN (e.g., 1HGBH41JXMN109186)"
          maxlength="17"
          class="vin-input-field"
          :class="{ 'error': errors.vin, 'loading': loading }"
        />
        <button 
          @click="decodeVin"
          :disabled="!isValidVin || loading"
          class="decode-button"
        >
          <i v-if="loading" class="pi pi-spin pi-spinner"></i>
          <i v-else class="pi pi-search"></i>
          {{ loading ? 'Decoding...' : 'Decode' }}
        </button>
      </div>
      
      <div v-if="errors.vin" class="error-message">
        <i class="pi pi-exclamation-triangle"></i>
        <span>{{ errors.vin }}</span>
      </div>
      
      <div v-if="vinInput && vinInput.length === 17" class="vin-status">
        <i :class="getStatusIcon()"></i>
        <span>{{ getStatusText() }}</span>
      </div>
    </div>

    <div v-if="decodedData" class="decoded-results">
      <div class="results-header">
        <h4>Decoded Vehicle Information</h4>
        <button @click="applyDecodedData" class="apply-button">
          <i class="pi pi-check"></i>
          Apply to Vehicle Form
        </button>
      </div>

      <div class="vehicle-summary">
        <div class="summary-main">
          <div class="vehicle-name">
            {{ decodedData.make }} {{ decodedData.model }} {{ decodedData.year }}
          </div>
          <div class="vehicle-details">
            <span class="detail-item">{{ decodedData.trim || 'Standard' }}</span>
            <span class="detail-item">{{ decodedData.body_type || 'N/A' }}</span>
          </div>
        </div>
        
        <div class="summary-value">
          <div class="estimated-value">
            <span class="value-label">Est. Value</span>
            <span class="value-amount">{{ formatCurrency(estimatedValue) }}</span>
          </div>
        </div>
      </div>

      <div class="results-grid">
        <!-- Basic Information -->
        <div class="result-section">
          <h5>Basic Information</h5>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Make</span>
              <span class="info-value">{{ decodedData.make || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Model</span>
              <span class="info-value">{{ decodedData.model || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Year</span>
              <span class="info-value">{{ decodedData.year || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Trim</span>
              <span class="info-value">{{ decodedData.trim || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Manufacturer</span>
              <span class="info-value">{{ decodedData.manufacturer || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Plant Country</span>
              <span class="info-value">{{ decodedData.plant_country || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Specifications -->
        <div class="result-section">
          <h5>Specifications</h5>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Engine</span>
              <span class="info-value">{{ decodedData.engine || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Displacement</span>
              <span class="info-value">{{ decodedData.displacement_cc ? `${decodedData.displacement_cc} cc` : 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Cylinders</span>
              <span class="info-value">{{ decodedData.number_of_cylinders || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Fuel Type</span>
              <span class="info-value">{{ formatFuelType(decodedData.fuel_type) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Transmission</span>
              <span class="info-value">{{ formatTransmission(decodedData.transmission) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Drive Type</span>
              <span class="info-value">{{ decodedData.drive_type || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Safety Features -->
        <div class="result-section">
          <h5>Safety Features</h5>
          <div class="features-grid">
            <div class="feature-item" :class="{ 'has-feature': decodedData.abs }">
              <i class="pi pi-shield"></i>
              <span>ABS</span>
            </div>
            <div class="feature-item" :class="{ 'has-feature': decodedData.airbags }">
              <i class="pi pi-heart"></i>
              <span>Airbags</span>
            </div>
            <div class="feature-item" :class="{ 'has-feature': decodedData.traction_control }">
              <i class="pi pi-lock"></i>
              <span>Traction Control</span>
            </div>
            <div class="feature-item" :class="{ 'has-feature': decodedData.stability_control }">
              <i class="pi pi-sync"></i>
              <span>Stability Control</span>
            </div>
            <div class="feature-item" :class="{ 'has-feature': decodedData.backup_camera }">
              <i class="pi pi-camera"></i>
              <span>Backup Camera</span>
            </div>
            <div class="feature-item" :class="{ 'has-feature': decodedData.bluetooth }">
              <i class="pi pi-mobile"></i>
              <span>Bluetooth</span>
            </div>
          </div>
        </div>

        <!-- Additional Information -->
        <div class="result-section">
          <h5>Additional Information</h5>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Vehicle Type</span>
              <span class="info-value">{{ decodedData.vehicle_type || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Valve Train</span>
              <span class="info-value">{{ decodedData.valve_train_design || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Fuel Delivery</span>
              <span class="info-value">{{ decodedData.fuel_delivery || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Notes</span>
              <span class="info-value">{{ decodedData.notes || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="results-footer">
        <div class="data-source">
          <i class="pi pi-info-circle"></i>
          <span>Data source: NHTSA vPIC API</span>
        </div>
        <div class="decode-timestamp">
          <i class="pi pi-clock"></i>
          <span>Decoded {{ formatDate(decodedAt) }}</span>
        </div>
      </div>
    </div>

    <div v-if="!decodedData && !loading && !errors.vin" class="decoder-tips">
      <h4>VIN Tips</h4>
      <ul class="tips-list">
        <li>VIN is a 17-character code unique to each vehicle</li>
        <li>Found on your vehicle registration, insurance card, or dashboard</li>
        <li>No letters I, O, or Q are used in VINs to avoid confusion</li>
        <li>First character indicates country of origin (1/4/5 = USA)</li>
        <li>10th character indicates model year</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { decodeVehicleVin } from '@/services/vehicleDataService'

const props = defineProps({
  onDecoded: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['decoded', 'apply-data'])

// Reactive data
const vinInput = ref('')
const decodedData = ref(null)
const loading = ref(false)
const errors = ref({})
const decodedAt = ref(null)

// Computed properties
const isValidVin = computed(() => {
  return vinInput.value && vinInput.value.length === 17 && isValidVinFormat(vinInput.value)
})

const estimatedValue = computed(() => {
  if (!decodedData.value) return 0
  
  // Simple estimation based on year and make
  let baseValue = 600000
  const year = parseInt(decodedData.value.year)
  const currentYear = new Date().getFullYear()
  const age = currentYear - year
  
  // Apply depreciation
  baseValue *= Math.max(0.2, 1 - (age * 0.1))
  
  // Apply make adjustment
  const makeAdjustments = {
    'Toyota': 1.1,
    'Honda': 1.05,
    'Mercedes': 1.2,
    'BMW': 1.15,
    'Audi': 1.1,
    'Hyundai': 0.9,
    'Kia': 0.85
  }
  
  if (decodedData.value.make && makeAdjustments[decodedData.value.make]) {
    baseValue *= makeAdjustments[decodedData.value.make]
  }
  
  return Math.round(baseValue)
})

// Methods
function handleVinInput() {
  errors.value = {}
  decodedData.value = null
  
  if (vinInput.value) {
    if (vinInput.value.length === 17) {
      if (!isValidVinFormat(vinInput.value)) {
        errors.value.vin = 'VIN contains invalid characters (I, O, Q not allowed)'
      }
    } else if (vinInput.value.length > 0) {
      errors.value.vin = 'VIN must be exactly 17 characters'
    }
  }
}

function isValidVinFormat(vin) {
  const invalidChars = ['I', 'O', 'Q']
  return !invalidChars.some(char => vin.toUpperCase().includes(char))
}

async function decodeVin() {
  if (!isValidVin.value) return
  
  loading.value = true
  errors.value = {}
  
  try {
    const data = await decodeVehicleVin(vinInput.value.toUpperCase())
    decodedData.value = data
    decodedAt.value = new Date()
    
    emit('decoded', data)
    props.onDecoded?.(data)
  } catch (error) {
    console.error('VIN decode error:', error)
    errors.value.vin = 'Failed to decode VIN. Please check the VIN and try again.'
  } finally {
    loading.value = false
  }
}

function applyDecodedData() {
  if (!decodedData.value) return
  
  emit('apply-data', {
    make: decodedData.value.make,
    model: decodedData.value.model,
    year: parseInt(decodedData.value.year),
    vin: vinInput.value.toUpperCase(),
    body_type: decodedData.value.body_type?.toLowerCase(),
    fuel_type: decodedData.value.fuel_type?.toLowerCase(),
    transmission: decodedData.value.transmission?.toLowerCase(),
    engine_capacity: decodedData.value.displacement_cc,
    trim: decodedData.value.trim,
    manufacturer: decodedData.value.manufacturer,
    plant_country: decodedData.value.plant_country
  })
}

function getStatusIcon() {
  if (errors.value.vin) return 'pi pi-exclamation-circle error'
  if (isValidVin.value) return 'pi pi-check-circle success'
  return 'pi pi-info-circle neutral'
}

function getStatusText() {
  if (errors.value.vin) return 'Invalid VIN'
  if (isValidVin.value) return 'Valid VIN'
  return 'Enter 17 characters'
}

function formatFuelType(fuelType) {
  if (!fuelType) return 'N/A'
  return fuelType.charAt(0).toUpperCase() + fuelType.slice(1).toLowerCase()
}

function formatTransmission(transmission) {
  if (!transmission) return 'N/A'
  return transmission.charAt(0).toUpperCase() + transmission.slice(1).toLowerCase()
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-ET', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(date)
}

// Watch for changes
watch(vinInput, (newValue) => {
  if (newValue.length === 17 && isValidVinFormat(newValue)) {
    decodeVin()
  }
})
</script>

<style scoped>
.vin-decoder {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.decoder-header {
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.decoder-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.decoder-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.decoder-input {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.input-group {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.vin-input-field {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  transition: all 0.2s;
}

.vin-input-field:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.vin-input-field.error {
  border-color: #ef4444;
}

.vin-input-field.loading {
  background: #f8fafc;
}

.decode-button {
  padding: 0.75rem 1.5rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.decode-button:hover:not(:disabled) {
  background: #047857;
}

.decode-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.vin-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.vin-status .success {
  color: #059669;
}

.vin-status .error {
  color: #dc2626;
}

.vin-status .neutral {
  color: #6b7280;
}

.decoded-results {
  padding: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.results-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.apply-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.apply-button:hover {
  background: #047857;
}

.vehicle-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.summary-main {
  flex: 1;
}

.vehicle-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.vehicle-details {
  display: flex;
  gap: 1rem;
}

.detail-item {
  font-size: 0.75rem;
  color: #64748b;
  padding: 0.25rem 0.75rem;
  background: white;
  border-radius: 12px;
}

.summary-value {
  text-align: right;
}

.value-label {
  font-size: 0.75rem;
  color: #64748b;
  display: block;
}

.value-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.result-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
}

.result-section h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 0.75rem;
  color: #374151;
  font-weight: 500;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  background: #f3f4f6;
  color: #9ca3af;
  font-size: 0.75rem;
}

.feature-item.has-feature {
  background: #dcfce7;
  color: #166534;
}

.results-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  margin-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
  font-size: 0.75rem;
  color: #6b7280;
}

.decoder-tips {
  padding: 1.5rem;
}

.decoder-tips h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.tips-list {
  margin: 0;
  padding-left: 1.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.tips-list li {
  margin-bottom: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .input-group {
    flex-direction: column;
  }
  
  .vehicle-summary {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .results-footer {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>
