<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
      <div class="modal-header">
        <h2>{{ editMode ? 'Edit Scraper' : 'Add New Scraper' }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <!-- Scraper Type Selection -->
        <div class="form-group">
          <label>Scraper Type *</label>
          <div style="display: flex; gap: 10px; margin: 10px 0;">
            <label style="display: flex; align-items: center; cursor: pointer;">
              <input type="radio" v-model="formData.scraper_type" value="property" style="margin-right: 8px;">
              🏠 Property
            </label>
            <label style="display: flex; align-items: center; cursor: pointer;">
              <input type="radio" v-model="formData.scraper_type" value="vehicle" style="margin-right: 8px;">
              🚗 Vehicle
            </label>
          </div>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Basic Configuration -->
          <div class="form-section">
            <h3>🔧 Basic Configuration</h3>
            
            <div class="form-group">
              <label>Domain *</label>
              <input 
                type="text" 
                v-model="formData.domain" 
                placeholder="e.g., livingethio.com"
                required
              />
            </div>

            <div class="form-group">
              <label>URL Template *</label>
              <input 
                type="text" 
                v-model="formData.url_template" 
                placeholder="https://livingethio.com/properties?page={page}"
                required
              />
              <small>Use {page} as placeholder for page number</small>
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
                  max="1000"
                />
              </div>
            </div>
          </div>

          <!-- Advanced Configuration -->
          <div class="form-section">
            <h3>⚙️ Advanced Configuration</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Request Delay (seconds)</label>
                <input 
                  type="number" 
                  v-model.number="formData.request_delay" 
                  min="0" 
                  max="60"
                  placeholder="2"
                />
                <small>Delay between requests to avoid rate limiting</small>
              </div>

              <div class="form-group">
                <label>Timeout (seconds)</label>
                <input 
                  type="number" 
                  v-model.number="formData.timeout" 
                  min="5" 
                  max="300"
                  placeholder="30"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Custom Headers (JSON)</label>
              <textarea 
                v-model="formData.custom_headers_json"
                rows="3"
                placeholder='{"User-Agent": "Mozilla/5.0...", "Accept-Language": "en-US,en"}'
              ></textarea>
              <small>Enter valid JSON format for custom HTTP headers</small>
            </div>

            <div class="form-group">
              <label>Pagination Type</label>
              <select v-model="formData.pagination_type">
                <option value="page_param">Page Parameter (?page=)</option>
                <option value="offset">Offset Parameter (?offset=)</option>
                <option value="infinite_scroll">Infinite Scroll</option>
                <option value="load_more">Load More Button</option>
                <option value="none">No Pagination</option>
              </select>
            </div>

            <div class="form-row" v-if="formData.pagination_type !== 'none'">
              <div class="form-group">
                <label>Max Items per Page</label>
                <input 
                  type="number" 
                  v-model.number="formData.items_per_page" 
                  min="1" 
                  max="100"
                  placeholder="20"
                />
              </div>

              <div class="form-group">
                <label>Pagination Selector</label>
                <input 
                  type="text" 
                  v-model="formData.pagination_selector" 
                  placeholder=".next-page, .load-more"
                />
              </div>
            </div>
          </div>

          <!-- CSS Selectors -->
          <div class="form-section">
            <h3>🎯 CSS Selectors</h3>
            
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
                <label>{{ formData.scraper_type === 'property' ? 'Location' : 'Make' }} Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.location" 
                  placeholder=".location, .make"
                />
              </div>

              <div class="form-group">
                <label>{{ formData.scraper_type === 'property' ? 'Area/Size' : 'Model' }} Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.area" 
                  placeholder=".area, .model"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>{{ formData.scraper_type === 'property' ? 'Property Type' : 'Year' }} Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.property_type" 
                  placeholder=".property-type, .year"
                />
              </div>

              <div class="form-group">
                <label>{{ formData.scraper_type === 'property' ? 'Bedrooms' : 'Mileage' }} Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.bedrooms" 
                  placeholder=".bedrooms, .mileage"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>{{ formData.scraper_type === 'property' ? 'Bathrooms' : 'Fuel Type' }} Selector</label>
                <input 
                  type="text" 
                  v-model="formData.selectors.bathrooms" 
                  placeholder=".bathrooms, .fuel-type"
                />
              </div>

              <div class="form-group">
                <label>Listing URL Selector</label>
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
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : (editMode ? 'Update Scraper' : 'Add Scraper') }}
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
  isOpen: Boolean,
  scraper: Object,
  editMode: Boolean
})

const emit = defineEmits(['close', 'save'])

const isSaving = ref(false)

const formData = ref({
  scraper_type: 'property',
  domain: '',
  url_template: '',
  enabled: true,
  schedule: 'daily',
  max_pages: 50,
  request_delay: 2,
  timeout: 30,
  custom_headers_json: '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}',
  pagination_type: 'page_param',
  items_per_page: 20,
  pagination_selector: '',
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
  if (newScraper && props.editMode) {
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
  isSaving.value = true
  try {
    await emit('save', formData.value)
    resetForm()
  } finally {
    isSaving.value = false
  }
}

const resetForm = () => {
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
