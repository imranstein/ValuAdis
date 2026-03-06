<template>
  <div class="map-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>🗺️ Property Map</h1>
        <p>Explore Ethiopian properties on an interactive map</p>
      </div>
      <div class="page-actions">
        <button @click="$refs.propertyMap.exportMap()" class="action-btn">
          <i class="pi pi-download"></i>
          Export
        </button>
        <button @click="$refs.propertyMap.printMap()" class="action-btn">
          <i class="pi pi-print"></i>
          Print
        </button>
      </div>
    </div>

    <!-- Map Statistics -->
    <div class="map-stats">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-map-marker"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalProperties }}</h3>
          <p>Total Properties</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon available">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ availableProperties }}</h3>
          <p>Available</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon commercial">
          <i class="pi pi-building"></i>
        </div>
        <div class="stat-content">
          <h3>{{ commercialProperties }}</h3>
          <p>Commercial</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon residential">
          <i class="pi pi-home"></i>
        </div>
        <div class="stat-content">
          <h3>{{ residentialProperties }}</h3>
          <p>Residential</p>
        </div>
      </div>
    </div>

    <!-- Main Map -->
    <div class="map-container">
      <PropertyMap
        ref="propertyMap"
        height="600px"
        :zoom="6"
        :center="[9.0116, 38.7616]"
        @property-selected="onPropertySelected"
        @property-view="onPropertyView"
      />
    </div>

    <!-- Selected Property Modal -->
    <div v-if="selectedProperty" class="property-modal-overlay" @click="closeModal">
      <div class="property-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedProperty.title }}</h2>
          <button @click="closeModal" class="close-btn">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <div class="modal-content">
          <div class="property-details">
            <div class="detail-row">
              <span class="label">Address:</span>
              <span class="value">{{ selectedProperty.address }}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Type:</span>
              <span class="value">{{ formatPropertyType(selectedProperty.type) }}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Price:</span>
              <span class="value price">{{ formatPrice(selectedProperty.price) }}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Area:</span>
              <span class="value">{{ selectedProperty.area }} m²</span>
            </div>
            
            <div v-if="selectedProperty.bedrooms" class="detail-row">
              <span class="label">Bedrooms:</span>
              <span class="value">{{ selectedProperty.bedrooms }}</span>
            </div>
            
            <div v-if="selectedProperty.bathrooms" class="detail-row">
              <span class="label">Bathrooms:</span>
              <span class="value">{{ selectedProperty.bathrooms }}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Status:</span>
              <span :class="`value status-${selectedProperty.status}`">
                {{ formatStatus(selectedProperty.status) }}
              </span>
            </div>
            
            <div v-if="selectedProperty.yearBuilt" class="detail-row">
              <span class="label">Year Built:</span>
              <span class="value">{{ selectedProperty.yearBuilt }}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Listed:</span>
              <span class="value">{{ formatDate(selectedProperty.listedDate) }}</span>
            </div>
          </div>
          
          <div v-if="selectedProperty.amenities" class="amenities">
            <h3>Amenities</h3>
            <div class="amenity-list">
              <span v-for="amenity in selectedProperty.amenities" 
                    :key="amenity" 
                    class="amenity-tag">
                {{ formatAmenity(amenity) }}
              </span>
            </div>
          </div>
          
          <div v-if="selectedProperty.description" class="description">
            <h3>Description</h3>
            <p>{{ selectedProperty.description }}</p>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="viewFullDetails" class="btn-primary">
            <i class="pi pi-external-link"></i>
            View Full Details
          </button>
          <button @click="navigateToProperty" class="btn-secondary">
            <i class="pi pi-map-marker"></i>
            Navigate
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { seedProperties } from '~/data/seedProperties.js'
import PropertyMap from '~/components/map/PropertyMap.vue'

// Router
const router = useRouter()

// Reactive state
const selectedProperty = ref(null)

// Computed properties
const totalProperties = computed(() => seedProperties.length)
const availableProperties = computed(() => 
  seedProperties.filter(p => p.status === 'available').length
)
const commercialProperties = computed(() => 
  seedProperties.filter(p => p.type === 'commercial').length
)
const residentialProperties = computed(() => 
  seedProperties.filter(p => p.type === 'residential').length
)

// Methods
const onPropertySelected = (property) => {
  selectedProperty.value = property
}

const onPropertyView = (property) => {
  viewFullDetails()
}

const closeModal = () => {
  selectedProperty.value = null
}

const viewFullDetails = () => {
  if (selectedProperty.value) {
    router.push(`/properties/${selectedProperty.value.id}`)
  }
}

const navigateToProperty = () => {
  if (selectedProperty.value) {
    const { coordinates, address } = selectedProperty.value
    const url = `https://www.google.com/maps?q=${coordinates[0]},${coordinates[1]}`
    window.open(url, '_blank')
  }
}

const exportMap = () => {
  // TODO: Implement map export functionality
  console.log('Export map functionality')
}

const printMap = () => {
  window.print()
}

// Formatting functions
const formatPrice = (price) => {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}

const formatPropertyType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatAmenity = (amenity) => {
  return amenity.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// SEO Meta
useHead({
  title: 'Property Map - Ethiopian Property Valuation Platform',
  meta: [
    { name: 'description', content: 'Interactive map showing properties across Ethiopia including Addis Ababa, Mekelle, Bahir Dar, and more.' }
  ]
})
</script>

<style scoped>
.map-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: #111827;
}

.header-content p {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.map-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #374151;
  font-size: 20px;
}

.stat-icon.available {
  background: #d1fae5;
  color: #059669;
}

.stat-icon.commercial {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.residential {
  background: #fef3c7;
  color: #d97706;
}

.stat-content h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.stat-content p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #6b7280;
}

.map-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.property-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.property-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-content {
  padding: 24px;
}

.property-details {
  margin-bottom: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: #374151;
}

.value {
  font-weight: 400;
  color: #111827;
}

.price {
  font-weight: 600;
  color: #059669;
}

.status-available {
  color: #059669;
  font-weight: 600;
}

.status-for_rent {
  color: #2563eb;
  font-weight: 600;
}

.status-sold {
  color: #dc2626;
  font-weight: 600;
}

.status-pending {
  color: #d97706;
  font-weight: 600;
}

.amenities {
  margin-bottom: 24px;
}

.amenities h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.amenity-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.amenity-tag {
  padding: 4px 8px;
  background: #f3f4f6;
  color: #374151;
  border-radius: 4px;
  font-size: 12px;
}

.description h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.description p {
  margin: 0;
  color: #6b7280;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  flex: 1;
  padding: 12px 16px;
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #047857;
}

@media (max-width: 768px) {
  .map-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .map-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .property-modal {
    width: 95%;
    margin: 20px;
  }
}

@media print {
  .page-header,
  .map-stats,
  .property-modal-overlay {
    display: none;
  }
  
  .map-container {
    height: 100vh !important;
  }
}
</style>
