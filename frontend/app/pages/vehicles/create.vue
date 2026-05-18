<template>
  <div class="vehicle-create-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <button class="back-button" @click="router.back()">
          <i class="pi pi-arrow-left"></i>
          Back
        </button>
        <h1>Add New Vehicle</h1>
        <p>Enter vehicle details and create valuation</p>
      </div>
    </div>

    <div class="create-content">
      <div class="form-sections">
        <!-- Vehicle Selection Section -->
        <div class="form-section">
          <div class="section-header">
            <h2>Vehicle Selection</h2>
            <p>Choose your vehicle by brand/model/year or enter VIN</p>
          </div>
          
          <VehicleBrandSelector
            :initial-data="vehicleSelection"
            @selection-change="handleSelectionChange"
            @specs-updated="handleSpecsUpdate"
            @vin-decoded="handleVinDecoded"
          />
        </div>

        <!-- Vehicle Details Section -->
        <div class="form-section">
          <div class="section-header">
            <h2>Vehicle Details</h2>
            <p>Complete vehicle information</p>
          </div>
          
          <form @submit.prevent="handleSubmit" class="vehicle-form">
            <div class="form-grid">
              <!-- Basic Information -->
              <div class="form-group">
                <h3>Basic Information</h3>
                <div class="form-row">
                  <div class="form-field">
                    <label>Make *</label>
                    <input
                      v-model="form.make"
                      type="text"
                      :class="{ 'error': errors.make }"
                      placeholder="e.g., Toyota, Honda"
                      required
                    />
                    <span v-if="errors.make" class="error-text">{{ errors.make }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>Model *</label>
                    <input
                      v-model="form.model"
                      type="text"
                      :class="{ 'error': errors.model }"
                      placeholder="e.g., Corolla, Civic"
                      required
                    />
                    <span v-if="errors.model" class="error-text">{{ errors.model }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>Year *</label>
                    <input
                      v-model="form.year"
                      type="number"
                      :class="{ 'error': errors.year }"
                      :min="1990"
                      :max="currentYear"
                      placeholder="e.g., 2020"
                      required
                    />
                    <span v-if="errors.year" class="error-text">{{ errors.year }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>VIN *</label>
                    <input
                      v-model="form.vin"
                      type="text"
                      :class="{ 'error': errors.vin }"
                      maxlength="17"
                      placeholder="17-character VIN"
                      required
                    />
                    <span v-if="errors.vin" class="error-text">{{ errors.vin }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>Plate Number *</label>
                    <input
                      v-model="form.plate_number"
                      type="text"
                      :class="{ 'error': errors.plate_number }"
                      placeholder="e.g., AA-123-BC"
                      required
                    />
                    <span v-if="errors.plate_number" class="error-text">{{ errors.plate_number }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>Color</label>
                    <input
                      v-model="form.color"
                      type="text"
                      placeholder="e.g., White, Black, Silver"
                    />
                  </div>
                </div>
              </div>

              <!-- Specifications -->
              <div class="form-group">
                <h3>Specifications</h3>
                <div class="form-row">
                  <div class="form-field">
                    <label>Body Type</label>
                    <select v-model="form.body_type" class="form-select">
                      <option value="">Select Body Type</option>
                      <option value="sedan">Sedan</option>
                      <option value="suv">SUV</option>
                      <option value="hatchback">Hatchback</option>
                      <option value="pickup">Pickup</option>
                      <option value="truck">Truck</option>
                      <option value="van">Van</option>
                      <option value="coupe">Coupe</option>
                      <option value="convertible">Convertible</option>
                      <option value="station_wagon">Station Wagon</option>
                    </select>
                  </div>
                  
                  <div class="form-field">
                    <label>Fuel Type</label>
                    <select v-model="form.fuel_type" class="form-select">
                      <option value="">Select Fuel Type</option>
                      <option value="gasoline">Gasoline</option>
                      <option value="diesel">Diesel</option>
                      <option value="hybrid">Hybrid</option>
                      <option value="electric">Electric</option>
                      <option value="lpg">LPG</option>
                      <option value="cng">CNG</option>
                    </select>
                  </div>
                  
                  <div class="form-field">
                    <label>Transmission</label>
                    <select v-model="form.transmission" class="form-select">
                      <option value="">Select Transmission</option>
                      <option value="manual">Manual</option>
                      <option value="automatic">Automatic</option>
                      <option value="cvt">CVT</option>
                    </select>
                  </div>
                  
                  <div class="form-field">
                    <label>Engine Capacity (cc)</label>
                    <input
                      v-model="form.engine_capacity"
                      type="number"
                      min="0"
                      max="10000"
                      placeholder="e.g., 1798"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label>Mileage (km)</label>
                    <input
                      v-model="form.mileage"
                      type="number"
                      min="0"
                      max="10000000"
                      placeholder="e.g., 45000"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label>Previous Owners</label>
                    <input
                      v-model="form.previous_owners"
                      type="number"
                      min="1"
                      max="50"
                      placeholder="e.g., 1"
                    />
                  </div>
                </div>
              </div>

              <!-- Ethiopian Market Information -->
              <div class="form-group">
                <h3>Ethiopian Market Information</h3>
                <div class="form-row">
                  <div class="form-field">
                    <label>Region *</label>
                    <select v-model="form.region" class="form-select" required>
                      <option value="">Select Region</option>
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
                    <span v-if="errors.region" class="error-text">{{ errors.region }}</span>
                  </div>
                  
                  <div class="form-field">
                    <label>City</label>
                    <input
                      v-model="form.city"
                      type="text"
                      placeholder="e.g., Addis Ababa, Adama, Bahir Dar"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label>Import Year</label>
                    <input
                      v-model="form.import_year"
                      type="number"
                      :min="1990"
                      :max="currentYear"
                      placeholder="e.g., 2020"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label>Customs Duty Status *</label>
                    <div class="checkbox-group">
                      <label class="checkbox-label">
                        <input
                          type="checkbox"
                          v-model="form.custom_duty_paid"
                        />
                        <span>Customs duty has been paid</span>
                      </label>
                    </div>
                  </div>
                  
                  <div class="form-field">
                    <label>Customs Declaration Number</label>
                    <input
                      v-model="form.customs_declaration_number"
                      type="text"
                      placeholder="e.g., CD-123456"
                      :disabled="!form.custom_duty_paid"
                    />
                  </div>
                </div>
              </div>

              <!-- Additional Information -->
              <div class="form-group">
                <h3>Additional Information</h3>
                <div class="form-row">
                  <div class="form-field full-width">
                    <label>Description</label>
                    <textarea
                      v-model="form.description"
                      class="form-textarea"
                      placeholder="Add any additional details about the vehicle..."
                      rows="3"
                    ></textarea>
                  </div>
                  
                  <div class="form-field full-width">
                    <label>Features</label>
                    <textarea
                      v-model="form.features"
                      class="form-textarea"
                      placeholder="List additional features (e.g., GPS, Bluetooth, Sunroof)..."
                      rows="2"
                    ></textarea>
                  </div>
                  
                  <div class="form-field full-width">
                    <label>Notes</label>
                    <textarea
                      v-model="form.notes"
                      class="form-textarea"
                      placeholder="Any additional notes or observations..."
                      rows="2"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="router.back()">
                Cancel
              </button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                <i v-if="submitting" class="pi pi-spin pi-spinner"></i>
                <i v-else class="pi pi-save"></i>
                {{ submitting ? 'Saving...' : 'Save Vehicle' }}
              </button>
            </div>
            <p v-if="submitStatus" class="submit-status" data-testid="vehicle-create-status">{{ submitStatus }}</p>
          </form>
        </div>

        <!-- Valuation Preview Section -->
        <div class="form-section">
          <div class="section-header">
            <h2>Valuation Preview</h2>
            <p>Estimated market value based on Ethiopian market factors</p>
          </div>
          
          <div class="valuation-preview">
            <div v-if="!canPreview" class="preview-placeholder">
              <i class="pi pi-chart-line"></i>
              <p>Complete vehicle information to see valuation preview</p>
            </div>
            
            <div v-else class="preview-content">
              <div class="preview-header">
                <h3>{{ form.make }} {{ form.model }} {{ form.year }}</h3>
                <span class="preview-status">Estimated</span>
              </div>
              
              <div class="preview-values">
                <div class="value-item">
                  <span class="value-label">Market Value</span>
                  <span class="value-amount">{{ formatCurrency(estimatedValue) }}</span>
                </div>
                <div class="value-item">
                  <span class="value-label">Taxable Value</span>
                  <span class="value-amount">{{ formatCurrency(estimatedValue * 0.25) }}</span>
                </div>
              </div>
              
              <div class="preview-factors">
                <h4>Ethiopian Market Factors</h4>
                <div class="factor-list">
                  <div class="factor-item">
                    <span class="factor-label">Regional Demand</span>
                    <span class="factor-value">{{ getRegionalMultiplier() }}x</span>
                  </div>
                  <div class="factor-item">
                    <span class="factor-label">Customs Status</span>
                    <span class="factor-value">{{ form.custom_duty_paid ? 'Paid (+5%)' : 'Unpaid (-20%)' }}</span>
                  </div>
                  <div class="factor-item">
                    <span class="factor-label">Import Year</span>
                    <span class="factor-value">{{ getImportYearAdjustment() }}x</span>
                  </div>
                  <div class="factor-item">
                    <span class="factor-label">Make Reliability</span>
                    <span class="factor-value">{{ getMakeReliability() }}x</span>
                  </div>
                </div>
              </div>
              
              <div class="preview-disclaimer">
                <i class="pi pi-info-circle"></i>
                <span>This is an estimate. Final valuation will be calculated after saving the vehicle.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VehicleBrandSelector from '@/components/vehicle/VehicleBrandSelector.vue'
import { getAccessToken } from '~/utils/authToken'

const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()

// Reactive data
const currentYear = new Date().getFullYear()
const submitting = ref(false)
const submitStatus = ref('')
const editingVehicleId = computed(() => {
  const id = Number(route.query.vehicle_id)
  return Number.isInteger(id) && id > 0 ? id : null
})

const vehicleSelection = ref({})

const form = reactive({
  make: '',
  model: '',
  year: '',
  vin: '',
  plate_number: '',
  body_type: '',
  fuel_type: '',
  transmission: '',
  engine_capacity: '',
  mileage: '',
  color: '',
  previous_owners: 1,
  region: '',
  city: '',
  import_year: '',
  custom_duty_paid: false,
  customs_declaration_number: '',
  description: '',
  features: '',
  notes: ''
})

const errors = reactive({})

// Computed properties
const canPreview = computed(() => {
  return form.make && form.model && form.year && form.region
})

const estimatedValue = computed(() => {
  if (!canPreview.value) return 0
  
  // Base value calculation (simplified)
  let baseValue = 600000 // Default base value
  
  // Adjust for year
  const age = currentYear - parseInt(form.year)
  const depreciation = Math.min(age * 0.1, 0.8)
  baseValue *= (1 - depreciation)
  
  // Apply Ethiopian market factors
  const regionalMultiplier = getRegionalMultiplier()
  const customsFactor = form.custom_duty_paid ? 1.05 : 0.8
  const importFactor = getImportYearAdjustment()
  const makeFactor = getMakeReliability()
  
  return baseValue * regionalMultiplier * customsFactor * importFactor * makeFactor
})

// Methods
function handleSelectionChange(selection) {
  Object.assign(form, selection)
  clearErrors()
}

function handleSpecsUpdate(specs) {
  // Auto-populate specifications from API
  if (specs.body_type) form.body_type = specs.body_type.toLowerCase()
  if (specs.engine) {
    const engineMatch = specs.engine.match(/(\d+\.?\d*)L/)
    if (engineMatch) {
      form.engine_capacity = Math.round(parseFloat(engineMatch[1]) * 1000)
    }
  }
  if (specs.fuel_type) form.fuel_type = specs.fuel_type.toLowerCase()
  if (specs.transmission) form.transmission = specs.transmission.toLowerCase()
}

function handleVinDecoded(vinData) {
  // Auto-populate from VIN decode
  if (vinData.make) form.make = vinData.make
  if (vinData.model) form.model = vinData.model
  if (vinData.year) form.year = parseInt(vinData.year)
  if (vinData.vin) form.vin = vinData.vin
  
  // Auto-populate specifications
  if (vinData.body_type) form.body_type = vinData.body_type.toLowerCase()
  if (vinData.engine) {
    const engineMatch = vinData.engine.match(/(\d+\.?\d*)L/)
    if (engineMatch) {
      form.engine_capacity = Math.round(parseFloat(engineMatch[1]) * 1000)
    }
  }
  if (vinData.fuel_type) form.fuel_type = vinData.fuel_type.toLowerCase()
  if (vinData.transmission) form.transmission = vinData.transmission.toLowerCase()
}

function getRegionalMultiplier() {
  const multipliers = {
    'Addis Ababa': 1.15,
    'Oromia': 1.0,
    'Amhara': 0.95,
    'Tigray': 0.9,
    'Southern': 0.85,
    'Somali': 0.8,
    'Afar': 0.75,
    'Benishangul': 0.8,
    'Gambela': 0.8,
    'Harari': 0.9,
    'Dire Dawa': 0.95
  }
  return multipliers[form.region] || 1.0
}

function getImportYearAdjustment() {
  if (!form.import_year) return 1.0
  
  const currentYear = new Date().getFullYear()
  const importAge = currentYear - parseInt(form.import_year)
  
  if (importAge <= 1) return 1.1
  if (importAge <= 3) return 1.0
  if (importAge <= 5) return 0.95
  return 0.85
}

function getMakeReliability() {
  const reliability = {
    'Toyota': 0.95,
    'Honda': 0.90,
    'Mazda': 0.85,
    'Nissan': 0.80,
    'Hyundai': 0.75,
    'Kia': 0.75,
    'BMW': 0.85,
    'Mercedes': 0.85,
    'Audi': 0.80,
    'Volkswagen': 0.80,
    'Isuzu': 0.85,
    'Hino': 0.85
  }
  return reliability[form.make] || 0.7
}

function validateForm() {
  const newErrors = {}
  
  if (!form.make) newErrors.make = 'Make is required'
  if (!form.model) newErrors.model = 'Model is required'
  if (!form.year) newErrors.year = 'Year is required'
  if (!form.vin) newErrors.vin = 'VIN is required'
  if (form.vin && form.vin.length !== 17) newErrors.vin = 'VIN must be 17 characters'
  if (!form.plate_number) newErrors.plate_number = 'Plate number is required'
  if (!form.region) newErrors.region = 'Region is required'
  
  // Validate VIN format
  if (form.vin && form.vin.length === 17) {
    const invalidChars = ['I', 'O', 'Q']
    if (invalidChars.some(char => form.vin.toUpperCase().includes(char))) {
      newErrors.vin = 'VIN cannot contain characters I, O, or Q'
    }
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

function clearErrors() {
  Object.keys(errors).forEach(key => delete errors[key])
}

async function handleSubmit() {
  if (!validateForm()) {
    submitStatus.value = 'Review the highlighted fields before saving'
    return
  }
  
  submitting.value = true
  submitStatus.value = 'Saving vehicle'
  
  try {
    const token = getAccessToken()
    if (!token) {
      router.push('/login')
      return
    }

    const response = await fetch(
      editingVehicleId.value
        ? `${config.public.apiBaseUrl}/api/v1/vehicles/${editingVehicleId.value}`
        : `${config.public.apiBaseUrl}/api/v1/vehicles/`,
      {
      method: editingVehicleId.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        make: form.make,
        model: form.model,
        year: Number(form.year),
        vin: form.vin,
        plate_number: form.plate_number,
        body_type: form.body_type || null,
        fuel_type: form.fuel_type || null,
        transmission: form.transmission || null,
        engine_capacity: form.engine_capacity ? Number(form.engine_capacity) : null,
        mileage: form.mileage ? Number(form.mileage) : null,
        color: form.color || null,
        previous_owners: Number(form.previous_owners || 1),
        region: form.region || null,
        city: form.city || null,
        import_year: form.import_year ? Number(form.import_year) : null,
        custom_duty_paid: form.custom_duty_paid,
        customs_declaration_number: form.customs_declaration_number || null,
        description: form.description || null,
        features: form.features || null,
        notes: form.notes || null,
      }),
    })

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.detail || 'Failed to save vehicle')
    }

    submitStatus.value = editingVehicleId.value ? 'Vehicle updated' : 'Vehicle saved'
    router.push('/vehicles')
  } catch (error) {
    submitStatus.value = error.message || 'Failed to save vehicle'
  } finally {
    submitting.value = false
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

onMounted(() => {
  if (editingVehicleId.value) {
    loadVehicleForEdit(editingVehicleId.value)
  }
})

async function loadVehicleForEdit(vehicleId) {
  const token = getAccessToken()
  if (!token) {
    router.push('/login')
    return
  }

  const response = await fetch(`${config.public.apiBaseUrl}/api/v1/vehicles/${vehicleId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    submitStatus.value = `Vehicle ${vehicleId} could not be loaded`
    return
  }
  const vehicle = await response.json()
  Object.assign(form, {
    make: vehicle.make || '',
    model: vehicle.model || '',
    year: vehicle.year || '',
    vin: vehicle.vin || '',
    plate_number: vehicle.plate_number || '',
    body_type: vehicle.body_type || '',
    fuel_type: vehicle.fuel_type || '',
    transmission: vehicle.transmission || '',
    engine_capacity: vehicle.engine_capacity || '',
    mileage: vehicle.mileage || '',
    color: vehicle.color || '',
    previous_owners: vehicle.previous_owners || 1,
    region: vehicle.region || '',
    city: vehicle.city || '',
    import_year: vehicle.import_year || '',
    custom_duty_paid: Boolean(vehicle.custom_duty_paid),
    customs_declaration_number: vehicle.customs_declaration_number || '',
    description: vehicle.description || '',
    features: vehicle.features || '',
    notes: vehicle.notes || '',
  })
  submitStatus.value = `Loaded vehicle ${vehicle.plate_number || vehicleId}`
}
</script>

<style scoped>
.vehicle-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 1rem;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.header-content p {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

/* Create Content */
.create-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

/* Form Sections */
.form-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.section-header {
  padding: 1.5rem 2rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.section-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* Form Styles */
.vehicle-form {
  padding: 2rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-field input,
.form-field select,
.form-field textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-field input.error,
.form-field select.error {
  border-color: #ef4444;
}

.form-field input.error:focus,
.form-field select.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.error-text {
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 2rem;
}

.submit-status {
  margin: 1rem 0 0;
  color: #065f46;
  font-weight: 700;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #059669;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #047857;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* Valuation Preview */
.valuation-preview {
  padding: 2rem;
}

.preview-placeholder {
  text-align: center;
  padding: 3rem 2rem;
  color: #6b7280;
}

.preview-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.preview-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.preview-status {
  background: #fef3c7;
  color: #d97706;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.preview-values {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.value-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.value-label {
  font-weight: 500;
  color: #374151;
}

.value-amount {
  font-weight: 600;
  color: #059669;
  font-size: 1.125rem;
}

.preview-factors h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.factor-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.factor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
}

.factor-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.factor-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.preview-disclaimer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
  font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .create-content {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem;
  }
  
  .header-content h1 {
    font-size: 1.5rem;
  }
  
  .vehicle-form {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>
