<template>
  <div class="quick-valuation-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Quick Valuation</h1>
        <p>Professional property valuation calculator compliant with Proclamation 1365/2025</p>
      </div>
      <div class="header-actions">
        <button class="action-button secondary" @click="loadSavedValuation">
          <i class="pi pi-folder-open"></i>
          Load Saved
        </button>
        <button class="action-button primary" @click="exportResults" v-if="result">
          <i class="pi pi-download"></i>
          Export PDF
        </button>
      </div>
    </div>

    <!-- Progress Indicator -->
    <div class="progress-indicator">
      <div class="progress-step" :class="{ active: currentStep >= 1 }">
        <div class="step-number">1</div>
        <div class="step-label">Property Details</div>
      </div>
      <div class="progress-line" :class="{ active: currentStep >= 2 }"></div>
      <div class="progress-step" :class="{ active: currentStep >= 2 }">
        <div class="step-number">2</div>
        <div class="step-label">Location & Area</div>
      </div>
      <div class="progress-line" :class="{ active: currentStep >= 3 }"></div>
      <div class="progress-step" :class="{ active: currentStep >= 3 }">
        <div class="step-number">3</div>
        <div class="step-label">Building Info</div>
      </div>
      <div class="progress-line" :class="{ active: currentStep >= 4 }"></div>
      <div class="progress-step" :class="{ active: currentStep >= 4 }">
        <div class="step-number">4</div>
        <div class="step-label">Valuation</div>
      </div>
    </div>

    <!-- Main Form -->
    <div class="form-container">
      <form @submit.prevent="calculateValuation" class="valuation-form">
        <!-- Section 1: Property Details -->
        <div class="form-section">
          <div class="section-header">
            <h2>Property Details</h2>
            <p>Basic information about the property</p>
          </div>
          
          <div class="form-grid">
            <div class="form-field">
              <label>Property Type *</label>
              <select v-model="formData.property_type" required>
                <option value="">Select property type</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="industrial">Industrial</option>
                <option value="agricultural">Agricultural</option>
                <option value="mixed_use">Mixed Use</option>
                <option value="government">Government</option>
                <option value="religious">Religious</option>
                <option value="educational">Educational</option>
                <option value="healthcare">Healthcare</option>
              </select>
            </div>

            <div class="form-field">
              <label>Property Category *</label>
              <select v-model="formData.property_category" required>
                <option value="">Select category</option>
                <option value="vacant_land">Vacant Land</option>
                <option value="single_family">Single Family</option>
                <option value="multi_family">Multi Family</option>
                <option value="apartment">Apartment Building</option>
                <option value="office">Office Building</option>
                <option value="retail">Retail Space</option>
                <option value="warehouse">Warehouse</option>
                <option value="factory">Factory</option>
                <option value="farm">Farm Land</option>
              </select>
            </div>

            <div class="form-field">
              <label>Ownership Type *</label>
              <select v-model="formData.ownership_type" required>
                <option value="">Select ownership type</option>
                <option value="private">Private</option>
                <option value="government">Government</option>
                <option value="state_owned">State-Owned Enterprise</option>
                <option value="municipal">Municipal</option>
                <option value="religious_institution">Religious Institution</option>
                <option value="ngo">NGO</option>
                <option value="foreign">Foreign Investor</option>
              </select>
            </div>

            <div class="form-field">
              <label>Tax Identification Number</label>
              <input 
                type="text" 
                v-model="formData.tin_number"
                placeholder="e.g., 123456789"
                maxlength="10"
              />
            </div>
          </div>
        </div>

        <!-- Section 2: Location & Area -->
        <div class="form-section">
          <div class="section-header">
            <h2>Location & Land Area</h2>
            <p>Geographic information and land measurements</p>
          </div>
          
          <div class="form-grid">
            <div class="form-field full-width">
              <label>Property Address *</label>
              <input 
                type="text" 
                v-model="formData.address"
                placeholder="Enter full property address"
                required
              />
            </div>

            <div class="form-field">
              <label>Municipality/City *</label>
              <select v-model="formData.municipality" required>
                <option value="">Select municipality</option>
                <option value="addis_ababa">Addis Ababa</option>
                <option value="dire_dawa">Dire Dawa</option>
                <option value="mekelle">Mekelle</option>
                <option value="gondar">Gondar</option>
                <option value="bahir_dar">Bahir Dar</option>
                <option value="hawassa">Hawassa</option>
                <option value="adama">Adama</option>
                <option value="jimma">Jimma</option>
                <option value="dessie">Dessie</option>
                <option value="harar">Harar</option>
                <option value="shashamane">Shashamane</option>
                <option value="nazret">Nazret</option>
              </select>
            </div>

            <div class="form-field">
              <label>Sub-City/Zone</label>
              <input 
                type="text" 
                v-model="formData.sub_city"
                placeholder="e.g., Bole, Kirkos"
              />
            </div>

            <div class="form-field">
              <label>Kebele/Woreda</label>
              <input 
                type="text" 
                v-model="formData.kebele"
                placeholder="e.g., Kebele 01"
              />
            </div>

            <div class="form-field">
              <label>Land Area (m²) *</label>
              <input 
                type="number" 
                v-model.number="formData.land_area_sqm"
                step="0.01"
                min="0"
                placeholder="e.g., 500"
                required
              />
            </div>

            <div class="form-field">
              <label>Land Area (hectares)</label>
              <input 
                type="number" 
                v-model.number="formData.land_area_hectares"
                step="0.001"
                min="0"
                placeholder="Auto-calculated"
                readonly
              />
            </div>

            <div class="form-field">
              <label>Frontage (meters)</label>
              <input 
                type="number" 
                v-model.number="formData.frontage_meters"
                step="0.1"
                min="0"
                placeholder="e.g., 20"
              />
            </div>

            <div class="form-field">
              <label>Depth (meters)</label>
              <input 
                type="number" 
                v-model.number="formData.depth_meters"
                step="0.1"
                min="0"
                placeholder="e.g., 25"
              />
            </div>

            <div class="form-field">
              <label>Zone Classification *</label>
              <select v-model="formData.zone_classification" required>
                <option value="">Select zone</option>
                <option value="commercial_a">Commercial Zone A</option>
                <option value="commercial_b">Commercial Zone B</option>
                <option value="commercial_c">Commercial Zone C</option>
                <option value="residential_a">Residential Zone A</option>
                <option value="residential_b">Residential Zone B</option>
                <option value="residential_c">Residential Zone C</option>
                <option value="industrial">Industrial Zone</option>
                <option value="mixed_use">Mixed Use Zone</option>
                <option value="special">Special Economic Zone</option>
              </select>
            </div>

            <div class="form-field">
              <label>Land Use Permit Number</label>
              <input 
                type="text" 
                v-model="formData.land_use_permit"
                placeholder="e.g., LU-2023-001234"
              />
            </div>
          </div>
        </div>

        <!-- Section 3: Building Information -->
        <div class="form-section">
          <div class="section-header">
            <h2>Building Information</h2>
            <p>Construction details and building specifications</p>
          </div>
          
          <div class="form-grid">
            <div class="form-field">
              <label>Building Area (m²)</label>
              <input 
                type="number" 
                v-model.number="formData.building_area_sqm"
                step="0.01"
                min="0"
                placeholder="e.g., 300"
              />
            </div>

            <div class="form-field">
              <label>Number of Floors</label>
              <input 
                type="number" 
                v-model.number="formData.number_of_floors"
                min="1"
                max="50"
                placeholder="e.g., 3"
              />
            </div>

            <div class="form-field">
              <label>Year Built</label>
              <input 
                type="number" 
                v-model.number="formData.year_built"
                min="1900"
                :max="currentYear"
                placeholder="e.g., 2020"
              />
            </div>

            <div class="form-field">
              <label>Building Condition *</label>
              <select v-model="formData.building_condition" required>
                <option value="">Select condition</option>
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
                <option value="very_poor">Very Poor</option>
                <option value="ruined">Ruined</option>
              </select>
            </div>

            <div class="form-field">
              <label>Construction Type *</label>
              <select v-model="formData.construction_type" required>
                <option value="">Select construction type</option>
                <option value="reinforced_concrete">Reinforced Concrete</option>
                <option value="steel_frame">Steel Frame</option>
                <option value="wood_frame">Wood Frame</option>
                <option value="masonry">Masonry</option>
                <option value="concrete_block">Concrete Block</option>
                <option value="stone">Stone</option>
                <option value="mixed">Mixed Construction</option>
                <option value="traditional">Traditional</option>
              </select>
            </div>

            <div class="form-field">
              <label>Roof Type *</label>
              <select v-model="formData.roof_type" required>
                <option value="">Select roof type</option>
                <option value="concrete_slab">Concrete Slab</option>
                <option value="corrugated_metal">Corrugated Metal</option>
                <option value="tile">Tile</option>
                <option value="thatch">Thatch</option>
                <option value="asphalt">Asphalt</option>
                <option value="green_roof">Green Roof</option>
              </select>
            </div>

            <div class="form-field">
              <label>Foundation Type</label>
              <select v-model="formData.foundation_type">
                <option value="">Select foundation</option>
                <option value="strip_footing">Strip Footing</option>
                <option value="isolated_footing">Isolated Footing</option>
                <option value="raft_foundation">Raft Foundation</option>
                <option value="pile_foundation">Pile Foundation</option>
                <option value="stone_foundation">Stone Foundation</option>
              </select>
            </div>

            <div class="form-field">
              <label>Building Permit Number</label>
              <input 
                type="text" 
                v-model="formData.building_permit"
                placeholder="e.g., BP-2023-005678"
              />
            </div>

            <div class="form-field full-width">
              <label>Building Quality Features</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_elevator" />
                  <span>Elevator</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_parking" />
                  <span>Parking</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_air_conditioning" />
                  <span>Air Conditioning</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_fire_safety" />
                  <span>Fire Safety System</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_security_system" />
                  <span>Security System</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_backup_power" />
                  <span>Backup Power</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: Additional Information -->
        <div class="form-section">
          <div class="section-header">
            <h2>Additional Information</h2>
            <p>Market data and property usage details</p>
          </div>
          
          <div class="form-grid">
            <div class="form-field">
              <label>Purpose of Valuation *</label>
              <select v-model="formData.valuation_purpose" required>
                <option value="">Select purpose</option>
                <option value="tax_assessment">Tax Assessment</option>
                <option value="sale_transaction">Sale Transaction</option>
                <option value="mortgage">Mortgage/Loan</option>
                <option value="insurance">Insurance</option>
                <option value="legal_dispute">Legal Dispute</option>
                <option value="investment">Investment Analysis</option>
                <option value="expropriation">Expropriation Compensation</option>
                <option value="inheritance">Inheritance/Estate</option>
              </select>
            </div>

            <div class="form-field">
              <label>Market Sector *</label>
              <select v-model="formData.market_sector" required>
                <option value="">Select sector</option>
                <option value="primary">Primary Market</option>
                <option value="secondary">Secondary Market</option>
                <option value="tertiary">Tertiary Market</option>
              </select>
            </div>

            <div class="form-field">
              <label>Neighborhood Quality</label>
              <select v-model="formData.neighborhood_quality">
                <option value="">Select quality</option>
                <option value="premium">Premium</option>
                <option value="above_average">Above Average</option>
                <option value="average">Average</option>
                <option value="below_average">Below Average</option>
                <option value="poor">Poor</option>
              </select>
            </div>

            <div class="form-field">
              <label>Accessibility Rating</label>
              <select v-model="formData.accessibility_rating">
                <option value="">Select rating</option>
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="moderate">Moderate</option>
                <option value="poor">Poor</option>
                <option value="isolated">Isolated</option>
              </select>
            </div>

            <div class="form-field full-width">
              <label>Infrastructure Access</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_road_access" />
                  <span>Paved Road Access</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_water_supply" />
                  <span>Water Supply</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_electricity" />
                  <span>Electricity</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_sewerage" />
                  <span>Sewerage System</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_telephone" />
                  <span>Telephone/Internet</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="formData.has_public_transport" />
                  <span>Public Transport</span>
                </label>
              </div>
            </div>

            <div class="form-field full-width">
              <label>Special Considerations</label>
              <textarea 
                v-model="formData.special_considerations"
                rows="3"
                placeholder="Any special factors affecting property value (e.g., heritage status, environmental factors, legal restrictions)"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" class="action-button secondary" @click="resetForm">
            <i class="pi pi-refresh"></i>
            Reset Form
          </button>
          <button type="button" class="action-button secondary" @click="saveDraft">
            <i class="pi pi-save"></i>
            Save Draft
          </button>
          <button type="submit" class="action-button primary" :disabled="loading">
            <i class="pi pi-calculator"></i>
            {{ loading ? 'Calculating...' : 'Calculate Valuation' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Results Card -->
    <Card v-if="result" style="margin-top: 2rem; background: linear-gradient(to right, #f0fdf4, #dbeafe);">
      <template #header>
        <div style="padding: 1.5rem; border-bottom: 1px solid #e5e7eb;">
          <h2 style="font-size: 1.5rem; font-weight: 600; color: #111827;">Valuation Results</h2>
        </div>
      </template>
      <template #content>
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
          <!-- Market Value -->
          <div style="padding: 1rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb;">
            <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">Market Value</p>
            <p style="font-size: 2rem; font-weight: bold; color: #1E3A8A;">
              {{ formatCurrency(result.market_value) }} ETB
            </p>
          </div>

          <!-- Taxable Value -->
          <div style="padding: 1rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb;">
            <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
              Taxable Value (25% of Market Value)
            </p>
            <p style="font-size: 2rem; font-weight: bold; color: #078160;">
              {{ formatCurrency(result.taxable_value) }} ETB
            </p>
          </div>

          <!-- Compliance Badge -->
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background-color: white; border-radius: 0.5rem; border: 2px solid #078160;">
            <div style="display: flex; align-items: center; gap: 1rem;">
              <div style="width: 3rem; height: 3rem; background-color: #078160; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                <i class="pi pi-shield" style="font-size: 1.5rem; color: white;"></i>
              </div>
              <div>
                <h3 style="font-size: 1.125rem; font-weight: 600; color: #111827;">Proclamation 1365/2025 Compliant</h3>
                <p style="font-size: 0.875rem; color: #6b7280;">25% taxable value calculation applied</p>
              </div>
            </div>
            <Badge value="✓ Compliant" severity="success" size="large" />
          </div>

          <!-- Calculation Details -->
          <Divider />
          <div>
            <h3 style="font-size: 1rem; font-weight: 600; color: #111827; margin-bottom: 1rem;">Calculation Details</h3>
            <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.875rem;">
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #6b7280;">Property Type:</span>
                <span style="font-weight: 500; color: #111827;">{{ getPropertyTypeLabel(formData.property_type) }}</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #6b7280;">Municipality:</span>
                <span style="font-weight: 500; color: #111827;">{{ formData.municipality }}</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #6b7280;">Land Area:</span>
                <span style="font-weight: 500; color: #111827;">{{ formData.area_sqm }} m²</span>
              </div>
              <div v-if="formData.building_area_sqm" style="display: flex; justify-content: space-between;">
                <span style="color: #6b7280;">Building Area:</span>
                <span style="font-weight: 500; color: #111827;">{{ formData.building_area_sqm }} m²</span>
              </div>
              <div v-if="formData.year_built" style="display: flex; justify-content: space-between;">
                <span style="color: #6b7280;">Year Built:</span>
                <span style="font-weight: 500; color: #111827;">{{ formData.year_built }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div style="display: flex; gap: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
            <Button
              label="Calculate Again"
              severity="secondary"
              @click="resetForm"
            />
            <Button
              label="Save as Property"
              icon="pi pi-save"
              style="background-color: #078160; border-color: #078160;"
              @click="saveAsProperty"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Error Message -->
    <Card v-if="error" style="margin-top: 2rem; background-color: #fef2f2; border: 1px solid #fecaca;">
      <template #content>
        <p style="color: #dc2626;">{{ error }}</p>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentStep = ref(1)
const formData = ref({
  // Property Details
  property_type: '',
  property_category: '',
  ownership_type: '',
  tin_number: '',
  
  // Location & Area
  address: '',
  municipality: '',
  sub_city: '',
  kebele: '',
  land_area_sqm: null,
  land_area_hectares: null,
  frontage_meters: null,
  depth_meters: null,
  zone_classification: '',
  land_use_permit: '',
  
  // Building Information
  building_area_sqm: null,
  number_of_floors: null,
  year_built: null,
  building_condition: '',
  construction_type: '',
  roof_type: '',
  foundation_type: '',
  building_permit: '',
  
  // Building Quality Features
  has_elevator: false,
  has_parking: false,
  has_air_conditioning: false,
  has_fire_safety: false,
  has_security_system: false,
  has_backup_power: false,
  
  // Additional Information
  valuation_purpose: '',
  market_sector: '',
  neighborhood_quality: '',
  accessibility_rating: '',
  special_considerations: '',
  
  // Infrastructure Access
  has_road_access: false,
  has_water_supply: false,
  has_electricity: false,
  has_sewerage: false,
  has_telephone: false,
  has_public_transport: false
})

const result = ref(null)
const loading = ref(false)
const error = ref(null)

const currentYear = computed(() => new Date().getFullYear())

// Auto-calculate hectares from square meters
watch(() => formData.value.land_area_sqm, (newValue) => {
  if (newValue) {
    formData.value.land_area_hectares = newValue / 10000
  } else {
    formData.value.land_area_hectares = null
  }
})

// Update progress step based on form completion
watch(formData, (newData) => {
  const step1Complete = newData.property_type && newData.property_category && newData.ownership_type
  const step2Complete = newData.address && newData.municipality && newData.land_area_sqm && newData.zone_classification
  const step3Complete = newData.building_condition && newData.construction_type && newData.roof_type
  const step4Complete = newData.valuation_purpose && newData.market_sector
  
  if (step4Complete) {
    currentStep.value = 4
  } else if (step3Complete) {
    currentStep.value = 3
  } else if (step2Complete) {
    currentStep.value = 2
  } else if (step1Complete) {
    currentStep.value = 1
  }
}, { deep: true })

async function calculateValuation() {
  error.value = null
  loading.value = true
  currentStep.value = 4

  try {
    const token = localStorage.getItem('valuadis_token')
    
    // Prepare comprehensive valuation data
    const valuationData = {
      ...formData.value,
      // Map legacy field names for API compatibility
      area_sqm: formData.value.land_area_sqm,
      building_area_sqm: formData.value.building_area_sqm,
      year_built: formData.value.year_built
    }
    
    const response = await fetch('http://localhost:8020/api/v1/valuations/quick', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(valuationData)
    })

    const data = await response.json()

    if (response.ok) {
      result.value = data.data || data
      // Scroll to results
      setTimeout(() => {
        document.querySelector('.results-section')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } else {
      error.value = data.detail || 'Failed to calculate valuation'
      currentStep.value = 3
    }
  } catch (err) {
    error.value = 'Network error. Please check your connection.'
    currentStep.value = 3
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  if (!value) return '0.00'
  return new Intl.NumberFormat('en-ET', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

function resetForm() {
  result.value = null
  error.value = null
  currentStep.value = 1
  formData.value = {
    property_type: '',
    property_category: '',
    ownership_type: '',
    tin_number: '',
    address: '',
    municipality: '',
    sub_city: '',
    kebele: '',
    land_area_sqm: null,
    land_area_hectares: null,
    frontage_meters: null,
    depth_meters: null,
    zone_classification: '',
    land_use_permit: '',
    building_area_sqm: null,
    number_of_floors: null,
    year_built: null,
    building_condition: '',
    construction_type: '',
    roof_type: '',
    foundation_type: '',
    building_permit: '',
    has_elevator: false,
    has_parking: false,
    has_air_conditioning: false,
    has_fire_safety: false,
    has_security_system: false,
    has_backup_power: false,
    valuation_purpose: '',
    market_sector: '',
    neighborhood_quality: '',
    accessibility_rating: '',
    special_considerations: '',
    has_road_access: false,
    has_water_supply: false,
    has_electricity: false,
    has_sewerage: false,
    has_telephone: false,
    has_public_transport: false
  }
}

function getPropertyTypeLabel(type) {
  const labels = {
    'residential': 'Residential',
    'commercial': 'Commercial',
    'industrial': 'Industrial',
    'agricultural': 'Agricultural',
    'mixed_use': 'Mixed Use',
    'government': 'Government',
    'religious': 'Religious',
    'educational': 'Educational',
    'healthcare': 'Healthcare'
  }
  return labels[type] || type
}

function saveDraft() {
  // Save form data to localStorage
  localStorage.setItem('valuation_draft', JSON.stringify(formData.value))
  // Show success message (you could add a toast notification here)
  alert('Draft saved successfully!')
}

function loadSavedValuation() {
  const savedDraft = localStorage.getItem('valuation_draft')
  if (savedDraft) {
    try {
      const draft = JSON.parse(savedDraft)
      formData.value = { ...formData.value, ...draft }
      alert('Draft loaded successfully!')
    } catch (error) {
      alert('Failed to load draft')
    }
  } else {
    alert('No saved draft found')
  }
}

function exportResults() {
  // Placeholder for PDF export functionality
  alert('PDF export feature coming soon!')
}

function saveAsProperty() {
  router.push({
    path: '/properties/create',
    query: {
      property_type: formData.value.property_type,
      property_category: formData.value.property_category,
      ownership_type: formData.value.ownership_type,
      address: formData.value.address,
      municipality: formData.value.municipality,
      sub_city: formData.value.sub_city,
      kebele: formData.value.kebele,
      land_area_sqm: formData.value.land_area_sqm,
      building_area_sqm: formData.value.building_area_sqm,
      year_built: formData.value.year_built,
      building_condition: formData.value.building_condition,
      construction_type: formData.value.construction_type,
      roof_type: formData.value.roof_type
    }
  })
}
</script>

<style scoped>
/* Quick Valuation Container */
.quick-valuation-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 10px 30px rgba(5, 150, 105, 0.2);
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

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-button {
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

.action-button.primary {
  background: white;
  color: #059669;
}

.action-button.primary:hover {
  background: #f8fafc;
  transform: translateY(-2px);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Progress Indicator */
.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.3s;
}

.progress-step.active .step-number {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  transform: scale(1.1);
}

.step-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  text-align: center;
}

.progress-step.active .step-label {
  color: #059669;
  font-weight: 600;
}

.progress-line {
  flex: 1;
  height: 2px;
  background: #e2e8f0;
  margin: 0 1rem;
  margin-top: -20px;
  transition: all 0.3s;
}

.progress-line.active {
  background: linear-gradient(90deg, #059669, #047857);
}

/* Form Container */
.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.valuation-form {
  padding: 0;
}

/* Form Sections */
.form-section {
  padding: 2rem;
  border-bottom: 1px solid #f1f5f9;
}

.form-section:last-child {
  border-bottom: none;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.section-header p {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-field input,
.form-field select,
.form-field textarea {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
  background: white;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-field input[readonly] {
  background: #f8fafc;
  color: #64748b;
}

.form-field textarea {
  resize: vertical;
  min-height: 100px;
}

/* Checkbox Group */
.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.checkbox-item input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #059669;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.form-actions .action-button {
  padding: 0.875rem 2rem;
  font-size: 0.875rem;
}

/* Results Section */
.results-section {
  margin-top: 2rem;
  scroll-margin-top: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .progress-indicator {
    flex-direction: column;
    gap: 1rem;
  }
  
  .progress-line {
    width: 2px;
    height: 20px;
    margin: 0;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
}

/* Enhanced Field Styling */
.form-field input:invalid,
.form-field select:invalid {
  border-color: #ef4444;
}

.form-field input:valid,
.form-field select:valid {
  border-color: #10b981;
}

/* Loading State */
.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Hover Effects */
.form-section {
  transition: all 0.3s;
}

.form-section:hover {
  background: #fafbfc;
}

/* Professional Styling */
.valuation-form {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Enhanced Visual Hierarchy */
.form-field label::after {
  content: '';
}

.form-field label:has(+ input[required])::after,
.form-field label:has(+ select[required])::after {
  content: ' *';
  color: #ef4444;
}

/* Modern Input Styling */
.form-field input::placeholder,
.form-field select::placeholder,
.form-field textarea::placeholder {
  color: #9ca3af;
}

/* Focus Management */
.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  transform: translateY(-1px);
}

/* Animation for Progress */
.progress-step {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Professional Card Styling */
.form-container {
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
