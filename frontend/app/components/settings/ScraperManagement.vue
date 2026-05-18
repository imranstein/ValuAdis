<template>
  <div class="scraper-management">
    <div class="scraper-header">
      <div>
        <h2>Source control desk</h2>
        <p>Backend scraper targets, recent source activity, and registry records loaded from the API.</p>
      </div>
    </div>

    <div class="scraper-type-toggle">
      <button 
        @click="scraperType = 'property'"
        :class="{ active: scraperType === 'property' }"
        class="type-btn"
      >
        <i class="pi pi-building" aria-hidden="true"></i>
        Property scrapers
      </button>
      <button 
        @click="scraperType = 'vehicle'"
        :class="{ active: scraperType === 'vehicle' }"
        class="type-btn"
      >
        <i class="pi pi-car" aria-hidden="true"></i>
        Vehicle scrapers
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
      <div class="section-head">
        <h3>Scraped {{ scraperType === 'property' ? 'properties' : 'vehicles' }}</h3>
        <span class="status-pill">{{ scrapedData.length }} backend records</span>
      </div>

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
  info('Scraper run queued')
  const result = await scraperService.runScraper(scraperId)
  if (result.success) {
    success(result.data.message || 'Scraper started successfully')
    await refreshScrapers()
  } else {
    error('Failed to start scraper - Please try again')
  }
}

const deleteScraper = async (scraperId) => {
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
  display: grid;
  gap: 20px;
}

.scraper-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.scraper-header h2 {
  margin: 0 0 6px;
  color: var(--ink);
  font-family: var(--display);
  font-size: 28px;
  font-weight: 600;
}

.scraper-header p {
  margin: 0;
  color: var(--muted);
}

.scraper-type-toggle {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.type-btn {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 800;
}

.type-btn.active {
  background: var(--green);
  color: var(--surface);
  border-color: var(--green);
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-primary {
  background: var(--green);
  color: var(--surface);
  border: 1px solid var(--green);
  padding: 10px 16px;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: var(--surface);
  color: var(--ink-soft);
  border: 1px solid var(--line);
  padding: 10px 16px;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-small {
  background: var(--surface);
  color: var(--ink-soft);
  border: 1px solid var(--line);
  padding: 6px 12px;
  border-radius: 6px;
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

.data-table-container {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
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
  background: var(--surface-2);
  font-weight: 600;
  color: var(--ink-soft);
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.section-head h3 {
  margin: 0;
  color: var(--ink);
  font-family: var(--display);
  font-size: 22px;
  font-weight: 600;
}

.status-pill {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface-2);
  color: var(--muted);
  padding: 4px 9px;
  font-size: 12px;
  font-weight: 800;
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
