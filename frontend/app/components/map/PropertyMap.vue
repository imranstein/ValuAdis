<template>
  <div class="property-map-container">
    <div id="property-map" class="map-wrapper"></div>
    
    <!-- Map Controls -->
    <div class="map-controls">
      <!-- Search Box -->
      <div class="search-group">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            placeholder="Search location or property..."
            class="search-input"
          />
          <button @click="performSearch" class="search-btn">
            <i class="pi pi-search"></i>
          </button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div 
            v-for="result in searchResults.slice(0, 5)" 
            :key="result.id"
            @click="selectSearchResult(result)"
            class="search-result-item"
          >
            <div class="result-title">{{ result.title }}</div>
            <div class="result-address">{{ result.address }}</div>
          </div>
        </div>
      </div>
      
      <div class="control-group">
        <button @click="resetView" class="control-btn" title="Reset View">
          <i class="pi pi-home"></i>
        </button>
        <button @click="toggleFullscreen" class="control-btn" title="Toggle Fullscreen">
          <i :class="isFullscreen ? 'pi pi-window-minimize' : 'pi pi-window-maximize'"></i>
        </button>
      </div>
      
      <!-- Drawing Tools -->
      <div class="control-group">
        <button 
          @click="toggleDrawing" 
          :class="['control-btn', { active: drawingEnabled }]"
          title="Toggle Drawing Tools"
        >
          <i class="pi pi-pencil"></i>
        </button>
        <button 
          v-if="drawingEnabled"
          @click="clearDrawings" 
          class="control-btn"
          title="Clear Drawings"
        >
          <i class="pi pi-trash"></i>
        </button>
      </div>
      
      <!-- Property Type Filter -->
      <div class="filter-group">
        <label class="filter-label">Property Type:</label>
        <select v-model="selectedType" @change="filterProperties" class="filter-select">
          <option value="all">All Types</option>
          <option value="residential">Residential</option>
          <option value="commercial">Commercial</option>
          <option value="industrial">Industrial</option>
          <option value="agricultural">Agricultural</option>
          <option value="land">Land</option>
        </select>
      </div>
      
      <!-- Status Filter -->
      <div class="filter-group">
        <label class="filter-label">Status:</label>
        <select v-model="selectedStatus" @change="filterProperties" class="filter-select">
          <option value="all">All Status</option>
          <option value="available">Available</option>
          <option value="for_rent">For Rent</option>
          <option value="sold">Sold</option>
          <option value="pending">Pending</option>
        </select>
      </div>
      
      <!-- Heat Map Controls -->
      <div class="filter-group">
        <label class="filter-label">Heat Map:</label>
        <div class="heatmap-controls">
          <select v-model="heatMapType" @change="updateHeatMap" class="filter-select">
            <option value="none">None</option>
            <option value="price">Price Density</option>
            <option value="type">Property Types</option>
            <option value="status">Availability</option>
          </select>
          <button 
            v-if="heatMapType !== 'none'" 
            @click="toggleHeatMap" 
            :class="['heatmap-toggle', { active: heatMapVisible }]"
          >
            <i :class="heatMapVisible ? 'pi pi-eye-slash' : 'pi pi-eye'"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Property Info Panel -->
    <div v-if="selectedProperty" class="property-panel">
      <div class="panel-header">
        <h3>{{ selectedProperty.title }}</h3>
        <button @click="closePropertyPanel" class="close-btn">
          <i class="pi pi-times"></i>
        </button>
      </div>
      <div class="panel-content">
        <div class="property-info">
          <p><strong>Address:</strong> {{ selectedProperty.address }}</p>
          <p><strong>Type:</strong> {{ formatPropertyType(selectedProperty.type) }}</p>
          <p><strong>Price:</strong> {{ formatPrice(selectedProperty.price) }}</p>
          <p><strong>Area:</strong> {{ selectedProperty.area }} m²</p>
          <p v-if="selectedProperty.bedrooms">
            <strong>Bedrooms:</strong> {{ selectedProperty.bedrooms }}
          </p>
          <p><strong>Status:</strong> 
            <span :class="`status-${selectedProperty.status}`">
              {{ formatStatus(selectedProperty.status) }}
            </span>
          </p>
        </div>
        <div class="property-actions">
          <button @click="viewPropertyDetails" class="btn-primary">
            <i class="pi pi-eye"></i>
            View Details
          </button>
          <button @click="navigateToProperty" class="btn-secondary">
            <i class="pi pi-map-marker"></i>
            Navigate
          </button>
        </div>
      </div>
    </div>
    
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="pi pi-spin pi-spinner"></i>
        <p>Loading map...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const propertyTypeColors = {
  residential: '#1f6b4f',
  commercial: '#365f73',
  industrial: '#6b5a1f',
  agricultural: '#54724c',
  land: '#8a6b2d',
}

// Import CSS for plugins
if (process.client) {
  import('leaflet.markercluster/dist/MarkerCluster.css')
  import('leaflet.markercluster/dist/MarkerCluster.Default.css')
  // Note: leaflet.heat and leaflet-draw CSS will be loaded via CDN or handled differently
}

// Dynamic import for Leaflet and plugins to avoid SSR issues
let L = null
let MarkerClusterGroup = null
let HeatLayer = null
let FeatureGroup = null
let DrawControl = null
let isClient = false

// Load Leaflet and MarkerCluster only on client side
if (process.client) {
  isClient = true
  
  // Load Leaflet
  import('leaflet').then(leaflet => {
    L = leaflet.default
    
    // Fix for default markers in Leaflet with webpack
    if (L && L.Icon && L.Icon.Default) {
      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      })
    }
  })
  
  // Load MarkerCluster
  import('leaflet.markercluster').then(module => {
    MarkerClusterGroup = module.default
  })
  
  // Load HeatMap
  import('leaflet.heat').then(module => {
    HeatLayer = module.default
  })
  
  // Load Drawing tools
  import('leaflet-draw').then(module => {
    FeatureGroup = module.FeatureGroup
    DrawControl = module.Control
  })
}

// Reactive state
const map = ref(null)
const markers = ref([])
const markerCluster = ref(null)
const selectedProperty = ref(null)
const loading = ref(true)
const isFullscreen = ref(false)
const selectedType = ref('all')
const selectedStatus = ref('all')
const sourceProperties = computed(() => {
  const fromApi = props.properties || []
  return fromApi
    .filter(p => (p.latitude != null && p.longitude != null) || (p.coordinates && p.coordinates.length >= 2))
    .map(p => ({
      id: p.id,
      title: p.address || p.property_ref || `Property #${p.id}`,
      address: p.address || '',
      type: p.property_type || 'residential',
      area: p.area_sqm || 0,
      price: p.market_value || 0,
      coordinates: p.latitude != null && p.longitude != null
        ? [p.latitude, p.longitude]
        : (p.coordinates && p.coordinates[0] ? [p.coordinates[0][1], p.coordinates[0][0]] : null),
      bedrooms: p.number_of_bedrooms,
      status: p.status || 'available'
    }))
    .filter(p => p.coordinates)
})
const filteredProperties = computed(() => {
  const src = sourceProperties.value
  return src.filter(property => {
    const typeMatch = selectedType.value === 'all' || property.type === selectedType.value
    const statusMatch = selectedStatus.value === 'all' || property.status === selectedStatus.value
    return typeMatch && statusMatch
  })
})
const searchQuery = ref('')
const searchResults = ref([])
const clusteringEnabled = ref(true)
const heatMapType = ref('none')
const heatMapVisible = ref(false)
const heatMapLayer = ref(null)
const drawingEnabled = ref(false)
const drawnItems = ref(null)
const drawControl = ref(null)

// Props
const props = defineProps({
  height: {
    type: String,
    default: '500px'
  },
  zoom: {
    type: Number,
    default: 6
  },
  center: {
    type: Array,
    default: () => [9.0116, 38.7616] // Addis Ababa
  },
  /** Properties to display in API format. Empty input renders an empty map. */
  properties: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['property-selected', 'property-view', 'boundary-updated'])

// Initialize map
const initMap = async () => {
  if (!isClient || !L) {
    console.error('Leaflet not available')
    loading.value = false
    return
  }
  
  loading.value = true
  
  await nextTick()
  
  // Wait a bit for Leaflet to be ready
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Create map instance
  map.value = L.map('property-map').setView(props.center, props.zoom)
  
  // Add Ethiopian basemap (using OpenStreetMap for now, can be replaced with Ethiopian-specific tiles)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors | Ethiopian Property Valuation Platform',
    maxZoom: 18
  }).addTo(map.value)
  
  // Add property markers
  addPropertyMarkers()
  
  loading.value = false
}

// Create custom marker icon based on property type
const createMarkerIcon = (property) => {
  const color = propertyTypeColors[property.type] || '#616161'
  
  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        width: 30px;
        height: 30px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 2px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="
          transform: rotate(45deg);
          color: white;
          font-size: 12px;
          font-weight: bold;
        ">
          ${property.type.charAt(0).toUpperCase()}
        </div>
      </div>
    `,
    className: 'custom-marker',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  })
}

// Add property markers to map
const addPropertyMarkers = () => {
  // Clear existing markers
  if (markerCluster.value) {
    map.value.removeLayer(markerCluster.value)
    markerCluster.value = null
  }
  markers.value.forEach(marker => marker.remove())
  markers.value = []
  
  // Create marker cluster if enabled
  if (clusteringEnabled.value && MarkerClusterGroup) {
    markerCluster.value = new MarkerClusterGroup({
      iconCreateFunction: function(cluster) {
        const count = cluster.getChildCount()
        let size = 'small'
        let className = 'marker-cluster-small'
        
        if (count > 10) {
          size = 'large'
          className = 'marker-cluster-large'
        } else if (count > 5) {
          size = 'medium'
          className = 'marker-cluster-medium'
        }
        
        return L.divIcon({
          html: `<div class="${className}">${count}</div>`,
          className: `marker-cluster ${size}`,
          iconSize: L.point(40, 40)
        })
      },
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true
    })
  }
  
  // Add markers for filtered properties
  filteredProperties.value.forEach(property => {
    const marker = L.marker([property.coordinates[0], property.coordinates[1]], {
      icon: createMarkerIcon(property)
    })
    
    // Create enhanced popup content
    const popupContent = `
      <div class="property-popup">
        <div class="popup-header">
          <h4>${property.title}</h4>
          <span class="popup-type">${formatPropertyType(property.type)}</span>
        </div>
        <div class="popup-details">
          <p><strong>Price:</strong> ${formatPrice(property.price)}</p>
          <p><strong>Area:</strong> ${property.area} m²</p>
          <p><strong>Location:</strong> ${property.address}</p>
          ${property.bedrooms ? `<p><strong>Bedrooms:</strong> ${property.bedrooms}</p>` : ''}
          <p><strong>Status:</strong> <span class="status-${property.status}">${formatStatus(property.status)}</span></p>
        </div>
        <div class="popup-actions">
          <button onclick="window.selectProperty(${property.id})" 
                  class="popup-btn primary">
            <i class="pi pi-eye"></i> View Details
          </button>
          <button onclick="window.navigateToProperty(${property.id})" 
                  class="popup-btn secondary">
            <i class="pi pi-map-marker"></i> Navigate
          </button>
        </div>
      </div>
    `
    
    marker.bindPopup(popupContent, {
      maxWidth: 300,
      className: 'custom-popup'
    })
    marker.on('click', () => selectProperty(property))
    
    if (markerCluster.value) {
      markerCluster.value.addLayer(marker)
    } else {
      marker.addTo(map.value)
    }
    
    markers.value.push(marker)
  })
  
  // Add cluster to map
  if (markerCluster.value) {
    map.value.addLayer(markerCluster.value)
  }
  
  // Fit map to show all markers
  if (markers.value.length > 0) {
    const bounds = L.latLngBounds(filteredProperties.value.map(p => p.coordinates))
    map.value.fitBounds(bounds.pad(0.1))
  }
}

// Filter properties based on selected criteria (filteredProperties is computed; just refresh markers)
const filterProperties = () => {
  addPropertyMarkers()
}

// Select a property
const selectProperty = (property) => {
  selectedProperty.value = property
  emit('property-selected', property)
  
  // Center map on selected property
  map.value.setView([property.coordinates[0], property.coordinates[1]], 15)
}

// Close property panel
const closePropertyPanel = () => {
  selectedProperty.value = null
}

// Reset map view
const resetView = () => {
  map.value.setView(props.center, props.zoom)
  selectedProperty.value = null
}

// Toggle fullscreen
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  const mapContainer = document.querySelector('.property-map-container')
  
  if (isFullscreen.value) {
    mapContainer.classList.add('fullscreen')
  } else {
    mapContainer.classList.remove('fullscreen')
  }
  
  // Refresh map after resize
  setTimeout(() => {
    map.value.invalidateSize()
  }, 300)
}

// View property details
const viewPropertyDetails = () => {
  if (selectedProperty.value) {
    emit('property-view', selectedProperty.value)
    // Navigate to property details page
    navigateTo(`/properties/${selectedProperty.value.id}`)
  }
}

// Navigate to property (could integrate with GPS navigation)
const navigateToProperty = () => {
  if (selectedProperty.value) {
    const { coordinates, address } = selectedProperty.value
    // Open in external map service
    const url = `https://www.google.com/maps?q=${coordinates[0]},${coordinates[1]}`
    window.open(url, '_blank')
  }
}

// Search methods
const handleSearch = () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  searchResults.value = filteredProperties.value.filter(property => 
    property.title.toLowerCase().includes(query) ||
    property.address.toLowerCase().includes(query) ||
    property.type.toLowerCase().includes(query) ||
    property.subcity?.toLowerCase().includes(query) ||
    property.municipality?.toLowerCase().includes(query)
  )
}

const performSearch = () => {
  handleSearch()
  if (searchResults.value.length > 0) {
    // Focus on first result
    selectSearchResult(searchResults.value[0])
  }
}

const selectSearchResult = (result) => {
  selectProperty(result)
  searchResults.value = []
  searchQuery.value = result.title
}

// Heat Map Methods
const updateHeatMap = () => {
  if (heatMapType.value === 'none') {
    removeHeatMap()
    return
  }
  
  if (heatMapVisible.value) {
    createHeatMap()
  }
}

const createHeatMap = () => {
  if (!HeatLayer || !map.value) return
  
  removeHeatMap()
  
  let heatData = []
  
  switch (heatMapType.value) {
    case 'price':
      heatData = filteredProperties.value.map(property => [
        property.coordinates[0],
        property.coordinates[1],
        property.price / 1000000 // Normalize price (in millions)
      ])
      break
      
    case 'type':
      heatData = filteredProperties.value.map(property => {
        const typeWeight = {
          residential: 1.0,
          commercial: 0.8,
          industrial: 0.6,
          agricultural: 0.4,
          land: 0.3
        }
        return [
          property.coordinates[0],
          property.coordinates[1],
          typeWeight[property.type] || 0.5
        ]
      })
      break
      
    case 'status':
      heatData = filteredProperties.value.map(property => {
        const statusWeight = {
          available: 1.0,
          for_rent: 0.7,
          pending: 0.5,
          sold: 0.3
        }
        return [
          property.coordinates[0],
          property.coordinates[1],
          statusWeight[property.status] || 0.5
        ]
      })
      break
  }
  
  if (heatData.length > 0) {
    heatMapLayer.value = HeatLayer(heatData, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      max: heatMapType.value === 'price' ? 10 : 1.0,
      gradient: {
        0.0: 'blue',
        0.25: 'cyan',
        0.5: 'lime',
        0.75: 'yellow',
        1.0: 'red'
      }
    }).addTo(map.value)
  }
}

const removeHeatMap = () => {
  if (heatMapLayer.value && map.value) {
    map.value.removeLayer(heatMapLayer.value)
    heatMapLayer.value = null
  }
}

const toggleHeatMap = () => {
  heatMapVisible.value = !heatMapVisible.value
  
  if (heatMapVisible.value) {
    createHeatMap()
  } else {
    removeHeatMap()
  }
}

// Drawing Methods
const toggleDrawing = () => {
  drawingEnabled.value = !drawingEnabled.value
  
  if (drawingEnabled.value) {
    enableDrawing()
  } else {
    disableDrawing()
  }
}

const enableDrawing = () => {
  if (!FeatureGroup || !DrawControl || !map.value) return
  
  // Create feature group for drawn items
  drawnItems.value = new FeatureGroup()
  map.value.addLayer(drawnItems.value)
  
  // Create draw control
  drawControl.value = new DrawControl({
    draw: {
      polygon: {
        allowIntersection: false,
        drawError: {
          color: '#e1e100',
          message: '<strong>Error:</strong> Shape edges cannot cross!'
        },
        shapeOptions: {
          color: '#059669',
          weight: 3,
          opacity: 0.8,
          fill: true,
          fillColor: '#059669',
          fillOpacity: 0.3
        }
      },
      polyline: {
        shapeOptions: {
          color: '#2563eb',
          weight: 4,
          opacity: 0.8
        }
      },
      circle: {
        shapeOptions: {
          color: '#dc2626',
          weight: 3,
          opacity: 0.8,
          fill: true,
          fillColor: '#dc2626',
          fillOpacity: 0.3
        }
      },
      rectangle: {
        shapeOptions: {
          color: '#d97706',
          weight: 3,
          opacity: 0.8,
          fill: true,
          fillColor: '#d97706',
          fillOpacity: 0.3
        }
      },
      marker: false,
      circlemarker: false
    },
    edit: {
      featureGroup: drawnItems.value,
      remove: true
    }
  })
  
  map.value.addControl(drawControl.value)
  
  // Listen for draw events
  map.value.on(L.Draw.Event.CREATED, handleDrawCreated)
  map.value.on(L.Draw.Event.EDITED, handleDrawEdited)
  map.value.on(L.Draw.Event.DELETED, handleDrawDeleted)
}

const disableDrawing = () => {
  if (drawControl.value && map.value) {
    map.value.removeControl(drawControl.value)
    drawControl.value = null
  }
  
  if (drawnItems.value && map.value) {
    map.value.removeLayer(drawnItems.value)
    drawnItems.value = null
  }
}

const clearDrawings = () => {
  if (drawnItems.value) {
    drawnItems.value.clearLayers()
  }
}

const handleDrawCreated = (e) => {
  const layer = e.layer
  const type = e.layerType
  
  drawnItems.value.addLayer(layer)
  emit('boundary-updated', { action: 'created', type, count: 1 })
}

const handleDrawEdited = (e) => {
  const layers = e.layers
  emit('boundary-updated', { action: 'edited', count: layers.getLayers().length })
}

const handleDrawDeleted = (e) => {
  const layers = e.layers
  emit('boundary-updated', { action: 'deleted', count: layers.getLayers().length })
}

// Export and Print Methods
const exportMap = () => {
  if (!map.value) return
  
  // Get current map bounds
  const bounds = map.value.getBounds()
  const center = map.value.getCenter()
  const zoom = map.value.getZoom()
  
  // Export data
  const exportData = {
    timestamp: new Date().toISOString(),
    mapBounds: {
      north: bounds.getNorth(),
      south: bounds.getSouth(),
      east: bounds.getEast(),
      west: bounds.getWest()
    },
    center: {
      lat: center.lat,
      lng: center.lng
    },
    zoom: zoom,
    filters: {
      type: selectedType.value,
      status: selectedStatus.value
    },
    properties: filteredProperties.value.map(p => ({
      id: p.id,
      title: p.title,
      type: p.type,
      status: p.status,
      price: p.price,
      coordinates: p.coordinates
    })),
    heatMap: {
      type: heatMapType.value,
      visible: heatMapVisible.value
    }
  }
  
  // Download as JSON
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ethiopian-properties-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const printMap = () => {
  if (!map.value) return
  
  // Create print window
  const printWindow = window.open('', '_blank')
  
  // Get map container HTML
  const mapContainer = document.getElementById('property-map')
  const mapHTML = mapContainer.innerHTML
  
  // Create print content
  const printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Ethiopian Property Map - ${new Date().toLocaleDateString()}</title>
      <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
        .header { text-align: center; margin-bottom: 20px; }
        .map-container { width: 100%; height: 600px; border: 1px solid #ccc; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat { text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #059669; }
        .stat-label { font-size: 14px; color: #666; }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Ethiopian Property Map</h1>
        <p>Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
        <p>Filters: ${selectedType.value === 'all' ? 'All Types' : selectedType.value} | 
                ${selectedStatus.value === 'all' ? 'All Status' : selectedStatus.value}</p>
      </div>
      
      <div class="stats">
        <div class="stat">
          <div class="stat-number">${filteredProperties.value.length}</div>
          <div class="stat-label">Total Properties</div>
        </div>
        <div class="stat">
          <div class="stat-number">${filteredProperties.value.filter(p => p.status === 'available').length}</div>
          <div class="stat-label">Available</div>
        </div>
        <div class="stat">
          <div class="stat-number">${filteredProperties.value.filter(p => p.type === 'residential').length}</div>
          <div class="stat-label">Residential</div>
        </div>
        <div class="stat">
          <div class="stat-number">${filteredProperties.value.filter(p => p.type === 'commercial').length}</div>
          <div class="stat-label">Commercial</div>
        </div>
      </div>
      
      <div class="map-container">
        ${mapHTML}
      </div>
      
      <div class="footer">
        <p>© Ethiopian Property Valuation Platform | Data exported for internal use only</p>
      </div>
    </body>
    </html>
  `
  
  printWindow.document.write(printContent)
  printWindow.document.close()
  
  // Wait for content to load, then print
  printWindow.onload = () => {
    printWindow.print()
    printWindow.close()
  }
}

// Format price
const formatPrice = (price) => {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}

// Format property type
const formatPropertyType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

// Format status
const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

// Global function for popup buttons
window.selectProperty = (propertyId) => {
  const property = filteredProperties.value.find(p => p.id === propertyId)
  if (property) {
    selectProperty(property)
  }
}

window.navigateToProperty = (propertyId) => {
  const property = filteredProperties.value.find(p => p.id === propertyId)
  if (property) {
    const { coordinates, address } = property
    const url = `https://www.google.com/maps?q=${coordinates[0]},${coordinates[1]}`
    window.open(url, '_blank')
  }
}

// Lifecycle hooks
// Refresh markers when properties data changes
watch(filteredProperties, () => {
  if (map.value && !loading.value) addPropertyMarkers()
}, { deep: true })

onMounted(async () => {
  if (isClient) {
    // Wait for Leaflet to load
    while (!L) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    initMap()
  }
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
.property-map-container {
  position: relative;
  width: 100%;
  height: v-bind(height);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.map-wrapper {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-width: 280px;
}

.search-group {
  position: relative;
}

.search-box {
  display: flex;
  gap: 4px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.search-btn {
  padding: 8px 12px;
  background: #059669;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  background: #047857;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001;
  margin-top: 4px;
}

.search-result-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background: #f9fafb;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-title {
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.result-address {
  font-size: 12px;
  color: #6b7280;
}

.control-group {
  display: flex;
  gap: 8px;
}

.control-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #059669;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-btn:hover {
  background: #047857;
}

.control-btn.active {
  background: #059669;
  color: white;
  box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.3);
}

.control-btn.active:hover {
  transform: translateY(-1px);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.filter-select {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  background: white;
}

.heatmap-controls {
  display: flex;
  gap: 4px;
  align-items: center;
}

.heatmap-toggle {
  padding: 6px 8px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-toggle:hover {
  background: #e5e7eb;
}

.heatmap-toggle.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

.property-panel {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 400px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.panel-content {
  padding: 16px;
}

.property-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #374151;
}

.property-info strong {
  color: #111827;
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

.property-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn-primary, .btn-secondary {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s;
}

.btn-primary {
  background: #059669;
  color: white;
}

.btn-primary:hover {
  background: #047857;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-spinner {
  text-align: center;
  color: #374151;
}

.loading-spinner i {
  font-size: 32px;
  margin-bottom: 8px;
}

.fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  border-radius: 0 !important;
}

/* Popup styles */
:global(.property-popup) {
  font-family: system-ui, -apple-system, sans-serif;
  max-width: 280px;
}

:global(.popup-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

:global(.popup-header h4) {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  flex: 1;
  margin-right: 8px;
}

:global(.popup-type) {
  background: #f3f4f6;
  color: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

:global(.popup-details) {
  margin-bottom: 12px;
}

:global(.popup-details p) {
  margin: 4px 0;
  font-size: 12px;
  color: #374151;
  line-height: 1.4;
}

:global(.popup-actions) {
  display: flex;
  gap: 6px;
}

:global(.popup-btn) {
  flex: 1;
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s;
}

:global(.popup-btn.primary) {
  background: #059669;
  color: white;
}

:global(.popup-btn.primary:hover) {
  background: #047857;
}

:global(.popup-btn.secondary) {
  background: #f3f4f6;
  color: #374151;
}

:global(.popup-btn.secondary:hover) {
  background: #e5e7eb;
}

/* Marker Cluster styles */
:global(.marker-cluster) {
  background: rgba(5, 150, 105, 0.6);
  border: 2px solid rgba(5, 150, 105, 0.8);
  border-radius: 50%;
  color: white;
  font-weight: bold;
  text-align: center;
  font-family: system-ui, -apple-system, sans-serif;
}

:global(.marker-cluster.small) {
  width: 30px;
  height: 30px;
  line-height: 26px;
  font-size: 12px;
}

:global(.marker-cluster-medium) {
  width: 40px;
  height: 40px;
  line-height: 36px;
  font-size: 14px;
}

:global(.marker-cluster-large) {
  width: 50px;
  height: 50px;
  line-height: 46px;
  font-size: 16px;
}

:global(.marker-cluster-small) {
  background: rgba(5, 150, 105, 0.6);
  border-color: rgba(5, 150, 105, 0.8);
}

:global(.marker-cluster-medium) {
  background: rgba(37, 99, 235, 0.6);
  border-color: rgba(37, 99, 235, 0.8);
}

:global(.marker-cluster-large) {
  background: rgba(220, 38, 38, 0.6);
  border-color: rgba(220, 38, 38, 0.8);
}

/* Status indicators in popups */
:global(.status-available) {
  color: #059669;
  font-weight: 600;
}

:global(.status-for_rent) {
  color: #2563eb;
  font-weight: 600;
}

:global(.status-sold) {
  color: #dc2626;
  font-weight: 600;
}

:global(.status-pending) {
  color: #d97706;
  font-weight: 600;
}
</style>
