<template>
  <div class="scraper-management">
    <!-- Scraper Header -->
    <div class="scraper-header">
      <h2>🕷️ Web Scraper Management</h2>
      <p>Manage Ethiopian property and vehicle listing scrapers and data collection</p>
    </div>

    <!-- Scraper Type Toggle -->
    <div class="scraper-type-toggle">
      <button 
        @click="scraperType = 'property'"
        :class="{ active: scraperType === 'property' }"
        class="type-btn"
      >
        🏠 Property Scrapers
      </button>
      <button 
        @click="scraperType = 'vehicle'"
        :class="{ active: scraperType === 'vehicle' }"
        class="type-btn"
      >
        🚗 Vehicle Scrapers
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button @click="showAddScraperModal = true" class="btn-primary">
        <i class="pi pi-plus"></i>
        Add New {{ scraperType === 'property' ? 'Property' : 'Vehicle' }} Scraper
      </button>
      <button @click="refreshScrapers" class="btn-secondary">
        <i class="pi pi-refresh"></i>
        Refresh
      </button>
      <button @click="showRawData = !showRawData" class="btn-secondary">
        <i class="pi pi-eye"></i>
        {{ showRawData ? 'Hide' : 'Show' }} Raw Data
      </button>
    </div>

    <!-- Debug Info -->
    <div class="debug-info">
      🔍 Debug: Type={{ scraperType }}, activeTab="scraper", scrapers={{ scrapers.length }}, stats loaded={{ !!scraperStats }}
    </div>

    <!-- Scraper Stats -->
    <ScraperStats 
      :stats="scraperStats" 
      :type="scraperType"
      :loading="statsLoading"
    />

    <!-- Scraper Table -->
    <ScraperTable 
      :scrapers="scrapers"
      :type="scraperType"
      :loading="scrapersLoading"
      @toggle="toggleScraper"
      @test="testScraper"
      @run="runScraper"
      @edit="editScraper"
      @delete="deleteScraper"
    />

    <!-- Scraped Data -->
    <div class="scraped-data-section">
      <h3>📊 Scraped {{ scraperType === 'property' ? 'Properties' : 'Vehicles' }}</h3>

      <!-- Data Table with Pagination -->
      <div v-if="scrapedData.length > 0" class="data-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th v-if="scraperType === 'property'">Address</th>
              <th v-if="scraperType === 'property'">Type</th>
              <th v-if="scraperType === 'vehicle'">Make/Model</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in paginatedData" :key="item.id">
              <td>{{ (pagination.currentPage - 1) * pagination.rowsPerPage + index + 1 }}</td>
              <td v-if="scraperType === 'property'">{{ item.address || item.location }}</td>
              <td v-if="scraperType === 'property'">{{ item.property_type || item.type }}</td>
              <td v-if="scraperType === 'vehicle'">{{ item.make }} {{ item.model }}</td>
              <td>{{ formatPrice(item.price) }}</td>
              <td>
                <span :class="getStatusClass(item.status)">
                  {{ item.status || 'Available' }}
                </span>
              </td>
              <td>
                <button 
                  @click="viewDetails(item)"
                  class="btn-small"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="pagination">
          <button 
            @click="pagination.currentPage--"
            :disabled="pagination.currentPage === 1"
            class="btn-small"
          >
            Previous
          </button>
          <span>
            Page {{ pagination.currentPage }} of {{ totalPages }}
          </span>
          <button 
            @click="pagination.currentPage++"
            :disabled="pagination.currentPage === totalPages"
            class="btn-small"
          >
            Next
          </button>
        </div>
      </div>

      <div v-else class="no-data">
        <i class="pi pi-inbox"></i>
        <p>No scraped {{ scraperType }} data available</p>
      </div>
    </div>

    <!-- Add/Edit Scraper Modal -->
    <AddScraperModal
      v-if="showAddScraperModal"
      :scraper="selectedScraper"
      :is-edit-mode="isEditMode"
      :type="scraperType"
      @save="saveScraper"
      @close="closeScraperModal"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useNotifications } from '~/composables/useNotifications.js'
import { scraperService } from '~/services/scraperService.js'
import ScraperStats from '~/components/settings/ScraperStats.vue'
import ScraperTable from '~/components/settings/ScraperTable.vue'
import AddScraperModal from '~/components/settings/AddScraperModal.vue'

// Props
const props = defineProps({
  initialScraperType: {
    type: String,
    default: 'property'
  }
})

// Reactive data
const scraperType = ref(props.initialScraperType)
const showRawData = ref(false)
const showAddScraperModal = ref(false)
const selectedScraper = ref(null)
const isEditMode = ref(false)

// Data
const scrapers = ref([])
const scraperStats = ref({
  total_scrapers: 0,
  active_scrapers: 0,
  inactive_scrapers: 0,
  total_listings: 0,
  last_24h_listings: 0,
  avg_success_rate: 0,
  error_count: 0
})
const scrapedData = ref([])

// Loading states
const scrapersLoading = ref(false)
const statsLoading = ref(false)
const dataLoading = ref(false)

// Pagination
const pagination = ref({
  currentPage: 1,
  rowsPerPage: 10,
  totalRecords: 0
})

// Notifications
const { success, error, warning, info } = useNotifications()

// Computed
const paginatedData = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.rowsPerPage
  const end = start + pagination.value.rowsPerPage
  return scrapedData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.totalRecords / pagination.value.rowsPerPage)
})

// Methods
const loadScrapers = async () => {
  scrapersLoading.value = true
  try {
    const result = await scraperService.getScrapers()
    if (result.success) {
      scrapers.value = result.data
      success('Scrapers loaded successfully')
    } else {
      error('Failed to load scrapers - Please check your connection')
      scrapers.value = []
    }
  } catch (err) {
    error('Failed to connect to server - Please check your connection')
    scrapers.value = []
  } finally {
    scrapersLoading.value = false
  }
}

const loadScraperStats = async () => {
  statsLoading.value = true
  try {
    const result = await scraperService.getScraperStats()
    if (result.success) {
      scraperStats.value = result.data
      success('Scraper statistics loaded')
    } else {
      error('Failed to load scraper statistics')
      scraperStats.value = {
        total_scrapers: 0,
        active_scrapers: 0,
        inactive_scrapers: 0,
        total_listings: 0,
        last_24h_listings: 0,
        avg_success_rate: 0,
        error_count: 0
      }
    }
  } catch (err) {
    error('Failed to connect to server')
    scraperStats.value = {
      total_scrapers: 0,
      active_scrapers: 0,
      inactive_scrapers: 0,
      total_listings: 0,
      last_24h_listings: 0,
      avg_success_rate: 0,
      error_count: 0
    }
  } finally {
    statsLoading.value = false
  }
}

const loadScrapedData = async () => {
  dataLoading.value = true
  try {
    const limit = pagination.value.rowsPerPage * 5
    const result = await scraperService.getScrapedData(scraperType.value, { limit })
    
    if (result.success) {
      scrapedData.value = result.data.data || result.data || []
      pagination.value.totalRecords = result.data.total || scrapedData.value.length
      pagination.value.currentPage = 1
      success(`${scraperType.value === 'property' ? 'Property' : 'Vehicle'} data loaded`)
    } else {
      error(`Failed to load ${scraperType.value} data`)
      scrapedData.value = []
      pagination.value.totalRecords = 0
      pagination.value.currentPage = 1
    }
  } catch (err) {
    error(`Failed to connect to server`)
    scrapedData.value = []
    pagination.value.totalRecords = 0
    pagination.value.currentPage = 1
  } finally {
    dataLoading.value = false
  }
}

const refreshScrapers = async () => {
  await Promise.all([loadScrapers(), loadScraperStats(), loadScrapedData()])
}

const toggleScraper = async (scraperId) => {
  const result = await scraperService.toggleScraper(scraperId)
  if (result.success) {
    await refreshScrapers()
    success('Scraper status updated successfully')
  } else {
    error('Failed to toggle scraper - Please try again')
  }
}

const testScraper = async (scraperId) => {
  const result = await scraperService.testScraper(scraperId)
  if (result.success) {
    const testResult = result.data
    if (testResult.success) {
      success(`Test successful! Found ${testResult.items_found} items`)
    } else {
      warning(`Test completed: ${testResult.error_message || 'No items found'}`)
    }
  } else {
    error('Failed to test scraper - Please try again')
  }
}

const runScraper = async (scraperId) => {
  if (!confirm('Start scraping now? This may take several minutes.')) return
  
  const result = await scraperService.runScraper(scraperId)
  if (result.success) {
    success(result.data.message || 'Scraper started successfully')
    await refreshScrapers()
  } else {
    error('Failed to start scraper - Please try again')
  }
}

const deleteScraper = async (scraperId) => {
  if (!confirm('Are you sure you want to delete this scraper?')) return
  
  const result = await scraperService.deleteScraper(scraperId)
  if (result.success) {
    await refreshScrapers()
    success('Scraper deleted successfully')
  } else {
    error('Failed to delete scraper - Please try again')
  }
}

const editScraper = (scraper) => {
  selectedScraper.value = scraper
  isEditMode.value = true
  showAddScraperModal.value = true
}

const saveScraper = async (scraperData) => {
  const result = isEditMode.value 
    ? await scraperService.updateScraper(selectedScraper.value.id, scraperData)
    : await scraperService.createScraper(scraperData)
  
  if (result.success) {
    await refreshScrapers()
    closeScraperModal()
    success(isEditMode.value ? 'Scraper updated successfully' : 'Scraper created successfully')
  } else {
    error(result.error || 'Failed to save scraper - Please try again')
  }
}

const closeScraperModal = () => {
  showAddScraperModal.value = false
  selectedScraper.value = null
  isEditMode.value = false
}

const viewDetails = (item) => {
  if (!item || !item.id) {
    warning('Invalid data - Cannot view details')
    return
  }
  
  // Navigate to details page
  const detailsPath = scraperType.value === 'property' 
    ? `/properties/${item.id}` 
    : `/vehicles/${item.id}`
  
  navigateTo(detailsPath)
}

const formatPrice = (price) => {
  if (!price) return 'N/A'
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB'
  }).format(price)
}

const getStatusClass = (status) => {
  const classes = {
    'available': 'status-available',
    'sold': 'status-sold',
    'pending': 'status-pending',
    'under_offer': 'status-under-offer'
  }
  return classes[status?.toLowerCase()] || 'status-available'
}

// Watchers
watch(scraperType, () => {
  loadScrapedData()
})

// Lifecycle
onMounted(() => {
  refreshScrapers()
})
</script>

<style scoped>
.scraper-management {
  padding: 20px;
}

.scraper-header {
  margin-bottom: 24px;
}

.scraper-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.scraper-header p {
  margin: 0;
  color: #666;
}

.scraper-type-toggle {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.type-btn {
  padding: 12px 24px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-small {
  background: #f9fafb;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.connection-warning {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.debug-info {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 16px;
  font-family: monospace;
  font-size: 12px;
  color: #6b7280;
}

.mock-data-warning {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.data-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.status-available {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

.no-data {
  text-align: center;
  padding: 48px;
  color: #6b7280;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}
</style>
