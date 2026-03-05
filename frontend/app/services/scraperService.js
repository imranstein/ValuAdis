import { apiService } from './apiService.js'

class ScraperService {
  constructor() {
    this.endpoints = {
      scrapers: '/api/v1/scrapers/',
      stats: '/api/v1/scrapers/stats',
      logs: '/api/v1/scrapers/logs',
      properties: '/api/v1/properties',
      vehicles: '/api/v1/vehicles'
    }
  }

  getAuthToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('valuadis_token')
    }
    return null
  }

  getAuthHeaders() {
    const token = this.getAuthToken()
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  }

  async handleApiCall(call, fallbackData = null) {
    try {
      const result = await call()
      return { success: true, data: result }
    } catch (error) {
      console.error('API call failed:', error)
      return { 
        success: false, 
        error: error.message,
        data: fallbackData 
      }
    }
  }

  async getScrapers(options = {}) {
    const { skip = 0, limit = 100 } = options
    return this.handleApiCall(
      () => apiService.get(`${this.endpoints.scrapers}?skip=${skip}&limit=${limit}`, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async getScraperStats() {
    return this.handleApiCall(
      () => apiService.get(this.endpoints.stats, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async getScraperLogs(options = {}) {
    const { skip = 0, limit = 50 } = options
    return this.handleApiCall(
      () => apiService.get(`${this.endpoints.logs}?skip=${skip}&limit=${limit}`, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async getScrapedData(type, options = {}) {
    const { limit = 100 } = options
    const endpoint = type === 'property' ? this.endpoints.properties : this.endpoints.vehicles
    return this.handleApiCall(
      () => apiService.get(`${endpoint}?limit=${limit}`, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async toggleScraper(scraperId) {
    return this.handleApiCall(
      () => apiService.patch(`${this.endpoints.scrapers}${scraperId}/toggle`, {}, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async testScraper(scraperId) {
    return this.handleApiCall(
      () => apiService.post(`${this.endpoints.scrapers}${scraperId}/test`, {}, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async runScraper(scraperId) {
    return this.handleApiCall(
      () => apiService.post(`${this.endpoints.scrapers}${scraperId}/run`, {}, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async deleteScraper(scraperId) {
    return this.handleApiCall(
      () => apiService.delete(`${this.endpoints.scrapers}${scraperId}`, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async createScraper(scraperData) {
    return this.handleApiCall(
      () => apiService.post(this.endpoints.scrapers, scraperData, {
        headers: this.getAuthHeaders()
      })
    )
  }

  async updateScraper(scraperId, scraperData) {
    return this.handleApiCall(
      () => apiService.put(`${this.endpoints.scrapers}${scraperId}`, scraperData, {
        headers: this.getAuthHeaders()
      })
    )
  }
}

export const scraperService = new ScraperService()
