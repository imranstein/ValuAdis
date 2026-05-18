<template>
<div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
      <div class="modal-header">
        <h2>{{ props.isEditMode ? 'Edit Scraper' : 'Add New Scraper' }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- Basic Configuration -->
          <div v-if="validationError" class="validation-error">
            {{ validationError }}
          </div>

          <div class="form-section">
            <h3>Basic Configuration</h3>
            
            <div class="form-group">
              <label>Domain *</label>
              <input 
                type="text" 
                v-model="formData.domain" 
                placeholder="e.g., mekelleproperty.com"
                required
              />
              <small>Domain name of the Ethiopian property website</small>
            </div>

            <div class="form-group">
              <label>URL Template *</label>
              <input 
                type="text" 
                v-model="formData.url_template" 
                placeholder="https://mekelleproperty.com/properties?page={page}"
                required
              />
              <small>Must include {page} placeholder for pagination</small>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Schedule</label>
                <select v-model="formData.schedule">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="custom">Custom</option>
                  <option value="manual">Manual</option>
                </select>
              </div>

              <div class="form-group">
                <label>Max Pages</label>
                <input 
                  type="number" 
                  v-model.number="formData.max_pages" 
                  min="1" 
                  max="100"
                />
              </div>
            </div>

            <div class="form-group">
              <label>
                <input type="checkbox" v-model="formData.enabled">
                Enable scraper
              </label>
              <small>Scraping will only run when enabled</small>
            </div>
          </div>

          <!-- CSS Selectors -->
          <div class="form-section">
            <h3>CSS Selectors</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Title Selector *</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.title" 
                  placeholder=".property-title, .listing-title"
                  required
                />
              </div>

              <div class="form-group">
                <label>Price Selector *</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.price" 
                  placeholder=".property-price, .price"
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Location Selector *</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.location" 
                  placeholder=".location, .address"
                />
              </div>

              <div class="form-group">
                <label>Area/Size Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.area" 
                  placeholder=".area, .size"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Property Type Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.property_type" 
                  placeholder=".property-type, .type"
                />
              </div>

              <div class="form-group">
                <label>Bedrooms Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.bedrooms" 
                  placeholder=".bedrooms, .rooms"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Bathrooms Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.bathrooms" 
                  placeholder=".bathrooms, .baths"
                />
              </div>

              <div class="form-group">
                <label>Listing URL Selector *</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.listing_url" 
                  placeholder=".property-link a, .listing-link"
                />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="$emit('close')">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : (props.isEditMode ? 'Update Scraper' : 'Add Scraper') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  scraper: Object,
  isEditMode: Boolean
})

const emit = defineEmits(['close', 'save'])

const isSaving = ref(false)
const validationError = ref('')

const formData = ref({
  domain: '',
  url_template: '',
  enabled: true,
  schedule: 'daily',
  max_pages: 50,
  selectors: {
    title: '',
    price: '',
    location: '',
    listing_url: '',
    area: '',
    property_type: '',
    bedrooms: '',
    bathrooms: ''
  }
})

watch(() => props.scraper, (newScraper) => {
  if (newScraper && props.isEditMode) {
    formData.value = {
      domain: newScraper.domain,
      url_template: newScraper.url_template,
      enabled: newScraper.enabled,
      schedule: newScraper.schedule,
      max_pages: newScraper.max_pages,
      selectors: { ...newScraper.selectors }
    }
  }
}, { immediate: true })

const handleSubmit = async () => {
  validationError.value = ''

  if (!formData.value.url_template.includes('{page}')) {
    validationError.value = 'URL template must contain the {page} placeholder.'
    return
  }
  
  const requiredSelectors = ['title', 'price', 'location', 'listing_url']
  const missingSelectors = requiredSelectors.filter(selector => !formData.value.selectors[selector])
  if (missingSelectors.length > 0) {
    validationError.value = `Missing required selectors: ${missingSelectors.join(', ')}.`
    return
  }
  
  isSaving.value = true
  try {
    await emit('save', formData.value)
    resetForm()
  } finally {
    isSaving.value = false
  }
}

const resetForm = () => {
  validationError.value = ''
  formData.value = {
    domain: '',
    url_template: '',
    enabled: true,
    schedule: 'daily',
    max_pages: 50,
    selectors: {
      title: '',
      price: '',
      location: '',
      listing_url: '',
      area: '',
      property_type: '',
      bedrooms: '',
      bathrooms: ''
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #1f2937;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
}

.validation-error {
  margin-bottom: 1.5rem;
  padding: 0.875rem 1rem;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #991b1b;
  font-size: 0.875rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #059669;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.selectors-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.selectors-section h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: #1f2937;
}

.help-text {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-secondary,
.btn-primary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Form Sections */
.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.form-actions {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: #f9fafb;
}
</style>
