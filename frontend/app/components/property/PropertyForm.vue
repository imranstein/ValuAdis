<template>
  <div class="property-form">
    <form @submit.prevent="handleSubmit" class="form-container">
      <!-- Basic Information -->
      <Card class="form-section">
        <template #header>
          <div class="section-header">
            <i class="pi pi-home"></i>
            <h3>Basic Information</h3>
          </div>
        </template>
        <template #content>
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="address">Property Address *</label>
              <InputText
                id="address"
                v-model="formData.address"
                placeholder="e.g., 123 Main Street, Addis Ababa"
                :class="{ 'p-invalid': errors.address }"
              />
              <small class="error-message" v-if="errors.address">{{ errors.address }}</small>
            </div>

            <div class="form-group">
              <label for="municipality">Municipality *</label>
              <Dropdown
                id="municipality"
                v-model="formData.municipality"
                :options="municipalities"
                placeholder="Select municipality"
                :class="{ 'p-invalid': errors.municipality }"
                filter
              />
              <small class="error-message" v-if="errors.municipality">{{ errors.municipality }}</small>
            </div>

            <div class="form-group">
              <label for="property_type">Property Type *</label>
              <Dropdown
                id="property_type"
                v-model="formData.property_type"
                :options="propertyTypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Select property type"
                :class="{ 'p-invalid': errors.property_type }"
              />
              <small class="error-message" v-if="errors.property_type">{{ errors.property_type }}</small>
            </div>

            <div class="form-group">
              <label for="property_id">Property ID</label>
              <InputText
                id="property_id"
                v-model="formData.property_id"
                placeholder="e.g., ADD-123456"
              />
            </div>

            <div class="form-group">
              <label for="parcel_number">Parcel Number</label>
              <InputText
                id="parcel_number"
                v-model="formData.parcel_number"
                placeholder="e.g., 123/456"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Physical Characteristics -->
      <Card class="form-section">
        <template #header>
          <div class="section-header">
            <i class="pi pi-th-large"></i>
            <h3>Physical Characteristics</h3>
          </div>
        </template>
        <template #content>
          <div class="form-grid">
            <div class="form-group">
              <label for="area_sqm">Land Area (m²) *</label>
              <InputNumber
                id="area_sqm"
                v-model="formData.area_sqm"
                mode="decimal"
                :min="0"
                :maxFractionDigits="2"
                placeholder="e.g., 500"
                :class="{ 'p-invalid': errors.area_sqm }"
              />
              <small class="error-message" v-if="errors.area_sqm">{{ errors.area_sqm }}</small>
            </div>

            <div class="form-group">
              <label for="building_area_sqm">Building Area (m²)</label>
              <InputNumber
                id="building_area_sqm"
                v-model="formData.building_area_sqm"
                mode="decimal"
                :min="0"
                :maxFractionDigits="2"
                placeholder="e.g., 300"
              />
            </div>

            <div class="form-group">
              <label for="year_built">Year Built</label>
              <InputNumber
                id="year_built"
                v-model="formData.year_built"
                :min="1900"
                :max="currentYear"
                placeholder="e.g., 2020"
              />
            </div>

            <div class="form-group">
              <label for="number_of_floors">Number of Floors</label>
              <InputNumber
                id="number_of_floors"
                v-model="formData.number_of_floors"
                :min="1"
                placeholder="e.g., 2"
              />
            </div>

            <div class="form-group">
              <label for="number_of_rooms">Number of Rooms</label>
              <InputNumber
                id="number_of_rooms"
                v-model="formData.number_of_rooms"
                :min="0"
                placeholder="e.g., 4"
              />
            </div>

            <div class="form-group">
              <label for="construction_quality">Construction Quality</label>
              <Dropdown
                id="construction_quality"
                v-model="formData.construction_quality"
                :options="constructionQualities"
                optionLabel="label"
                optionValue="value"
                placeholder="Select quality"
              />
            </div>

            <div class="form-group">
              <label for="condition">Property Condition</label>
              <Dropdown
                id="condition"
                v-model="formData.condition"
                :options="propertyConditions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select condition"
              />
            </div>

            <div class="form-group">
              <label for="parking_spaces">Parking Spaces</label>
              <InputNumber
                id="parking_spaces"
                v-model="formData.parking_spaces"
                :min="0"
                placeholder="e.g., 2"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Spatial Information -->
      <Card class="form-section">
        <template #header>
          <div class="section-header">
            <i class="pi pi-map"></i>
            <h3>Spatial Information</h3>
          </div>
        </template>
        <template #content>
          <PropertyMapEditor
            v-model="formData.boundaries"
            :readonly="readonly"
            @area-calculated="handleAreaCalculated"
          />
          
          <div class="form-grid" style="margin-top: 1rem;">
            <div class="form-group">
              <label for="latitude">Latitude</label>
              <InputNumber
                id="latitude"
                v-model="formData.latitude"
                mode="decimal"
                :min="-90"
                :max="90"
                :maxFractionDigits="6"
                placeholder="e.g., 9.0320"
              />
            </div>

            <div class="form-group">
              <label for="longitude">Longitude</label>
              <InputNumber
                id="longitude"
                v-model="formData.longitude"
                mode="decimal"
                :min="-180"
                :max="180"
                :maxFractionDigits="6"
                placeholder="e.g., 38.7578"
              />
            </div>

            <div class="form-group">
              <label for="zone">Zone/Block</label>
              <InputText
                id="zone"
                v-model="formData.zone"
                placeholder="e.g., Zone 4, Block 12"
              />
            </div>

            <div class="form-group">
              <label for="neighborhood">Neighborhood</label>
              <InputText
                id="neighborhood"
                v-model="formData.neighborhood"
                placeholder="e.g., Bole"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Ownership Information -->
      <Card class="form-section">
        <template #header>
          <div class="section-header">
            <i class="pi pi-user"></i>
            <h3>Ownership Information</h3>
          </div>
        </template>
        <template #content>
          <div class="form-grid">
            <div class="form-group">
              <label for="owner_name">Owner Name</label>
              <InputText
                id="owner_name"
                v-model="formData.owner_name"
                placeholder="e.g., John Doe"
              />
            </div>

            <div class="form-group">
              <label for="owner_phone">Owner Phone</label>
              <InputText
                id="owner_phone"
                v-model="formData.owner_phone"
                placeholder="e.g., +251911234567"
              />
            </div>

            <div class="form-group">
              <label for="owner_email">Owner Email</label>
              <InputText
                id="owner_email"
                v-model="formData.owner_email"
                placeholder="e.g., owner@example.com"
              />
            </div>

            <div class="form-group">
              <label for="ownership_type">Ownership Type</label>
              <Dropdown
                id="ownership_type"
                v-model="formData.ownership_type"
                :options="ownershipTypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Select ownership type"
              />
            </div>

            <div class="form-group full-width">
              <label for="legal_description">Legal Description</label>
              <Textarea
                id="legal_description"
                v-model="formData.legal_description"
                rows="3"
                placeholder="Legal description of the property"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Documents & Photos -->
      <Card class="form-section">
        <template #header>
          <div class="section-header">
            <i class="pi pi-file"></i>
            <h3>Documents & Photos</h3>
          </div>
        </template>
        <template #content>
          <div class="document-upload">
            <div class="upload-section">
              <h4>Property Photos</h4>
              <FileUpload
                name="photos"
                :multiple="true"
                accept="image/*"
                :maxFileSize="5000000"
                :auto="false"
                choose-label="Choose Photos"
                @select="handlePhotoSelect"
                @remove="handlePhotoRemove"
              />
            </div>

            <div class="upload-section">
              <h4>Legal Documents</h4>
              <FileUpload
                name="documents"
                :multiple="true"
                accept=".pdf,.doc,.docx"
                :maxFileSize="10000000"
                :auto="false"
                choose-label="Choose Documents"
                @select="handleDocumentSelect"
                @remove="handleDocumentRemove"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Form Actions -->
      <div class="form-actions">
        <Button
          label="Cancel"
          severity="secondary"
          @click="$emit('cancel')"
          :disabled="loading"
        />
        <Button
          label="Save Draft"
          severity="info"
          @click="saveDraft"
          :disabled="loading"
        />
        <Button
          type="submit"
          :label="isEdit ? 'Update Property' : 'Create Property'"
          :loading="loading"
          :disabled="loading"
        />
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import PropertyMapEditor from './PropertyMapEditor.vue'

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel', 'save-draft'])

// Form data
const formData = ref({
  address: '',
  municipality: '',
  property_type: '',
  property_id: '',
  parcel_number: '',
  area_sqm: null,
  building_area_sqm: null,
  year_built: null,
  number_of_floors: null,
  number_of_rooms: null,
  construction_quality: '',
  condition: '',
  parking_spaces: null,
  boundaries: [],
  latitude: null,
  longitude: null,
  zone: '',
  neighborhood: '',
  owner_name: '',
  owner_phone: '',
  owner_email: '',
  ownership_type: '',
  legal_description: '',
  photos: [],
  documents: []
})

// Validation errors
const errors = ref({})

// Computed
const isEdit = computed(() => !!props.initialData.id)
const currentYear = computed(() => new Date().getFullYear())

// Options
const municipalities = [
  'Addis Ababa', 'Dire Dawa', 'Mekelle', 'Gondar', 'Bahir Dar',
  'Hawassa', 'Adama', 'Jimma', 'Dessie', 'Harar', 'Shashamane',
  'Arba Minch', 'Jijiga', 'Debre Berhan', 'Hosaena'
]

const propertyTypes = [
  { label: 'Residential', value: 'residential' },
  { label: 'Commercial', value: 'commercial' },
  { label: 'Industrial', value: 'industrial' },
  { label: 'Agricultural', value: 'agricultural' },
  { label: 'Mixed Use', value: 'mixed_use' },
  { label: 'Institutional', value: 'institutional' },
  { label: 'Recreational', value: 'recreational' }
]

const constructionQualities = [
  { label: 'Premium', value: 'premium' },
  { label: 'Good', value: 'good' },
  { label: 'Average', value: 'average' },
  { label: 'Poor', value: 'poor' },
  { label: 'Very Poor', value: 'very_poor' }
]

const propertyConditions = [
  { label: 'Excellent', value: 'excellent' },
  { label: 'Good', value: 'good' },
  { label: 'Fair', value: 'fair' },
  { label: 'Poor', value: 'poor' },
  { label: 'Very Poor', value: 'very_poor' }
]

const ownershipTypes = [
  { label: 'Private', value: 'private' },
  { label: 'Government', value: 'government' },
  { label: 'Corporate', value: 'corporate' },
  { label: 'Joint Venture', value: 'joint_venture' },
  { label: 'Trust', value: 'trust' }
]

// Watch for initial data changes
watch(() => props.initialData, (newData) => {
  if (newData) {
    formData.value = { ...formData.value, ...newData }
  }
}, { immediate: true, deep: true })

onMounted(() => {
  if (props.initialData) {
    formData.value = { ...formData.value, ...props.initialData }
  }
})

function validateForm() {
  errors.value = {}

  if (!formData.value.address?.trim()) {
    errors.value.address = 'Address is required'
  }

  if (!formData.value.municipality) {
    errors.value.municipality = 'Municipality is required'
  }

  if (!formData.value.property_type) {
    errors.value.property_type = 'Property type is required'
  }

  if (!formData.value.area_sqm || formData.value.area_sqm <= 0) {
    errors.value.area_sqm = 'Land area must be greater than 0'
  }

  return Object.keys(errors.value).length === 0
}

function handleSubmit() {
  if (validateForm()) {
    emit('submit', { ...formData.value })
  }
}

function saveDraft() {
  emit('save-draft', { ...formData.value })
}

function handleAreaCalculated(area) {
  if (area > 0 && !formData.value.area_sqm) {
    formData.value.area_sqm = Math.round(area * 100) / 100
  }
}

function handlePhotoSelect(event) {
  formData.value.photos = [...formData.value.photos, ...event.files]
}

function handlePhotoRemove(event) {
  const removedFile = event.file
  formData.value.photos = formData.value.photos.filter(photo => photo !== removedFile)
}

function handleDocumentSelect(event) {
  formData.value.documents = [...formData.value.documents, ...event.files]
}

function handleDocumentRemove(event) {
  const removedFile = event.file
  formData.value.documents = formData.value.documents.filter(doc => doc !== removedFile)
}
</script>

<style scoped>
.property-form {
  max-width: 1200px;
  margin: 0 auto;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-section {
  border-radius: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.section-header i {
  font-size: 1.25rem;
  color: #059669;
}

.section-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.error-message {
  color: #dc2626;
  font-size: 0.75rem;
}

.document-upload {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 1.5rem;
}

.upload-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .document-upload {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
