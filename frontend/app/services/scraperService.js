import { apiService } from './apiService.js'
import { getAccessToken } from '~/utils/authToken'

class ScraperService
{
  constructor ()
  {
    this.endpoints = {
      scrapers: '/api/v1/scrapers/',
      stats: '/api/v1/scrapers/stats',
      logs: '/api/v1/scrapers/logs',
      properties: '/api/v1/properties',
      vehicles: '/api/v1/vehicles'
    }
  }

  getAuthHeaders ()
  {
    const token = getAccessToken()
    return token ? { 'Authorization': `Bearer ${ token }` } : {}
  }

  getAuthCredentials ()
  {
    // Include credentials for API calls
    return { credentials: 'include' }
  }

  async handleApiCall ( call, fallbackData = null )
  {
    try
    {
      const result = await call()
      return { success: true, data: result }
    } catch ( error )
    {
      console.error( 'API call failed:', error )
      return {
        success: false,
        error: error.message,
        data: fallbackData
      }
    }
  }

  async getScrapers ( options = {} )
  {
    const { skip = 0, limit = 100 } = options
    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.scrapers }?skip=${ skip }&limit=${ limit }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getScraperStats ()
  {
    return this.handleApiCall(
      () => apiService.get( this.endpoints.stats, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getScraperLogs ( options = {} )
  {
    const { skip = 0, limit = 50 } = options
    return this.handleApiCall(
      () => apiService.get( `${ this.endpoints.logs }?skip=${ skip }&limit=${ limit }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async getScrapedData ( type, options = {} )
  {
    const { limit = 100 } = options
    const endpoint = type === 'property' ? this.endpoints.properties : this.endpoints.vehicles
    return this.handleApiCall(
      () => apiService.get( `${ endpoint }?limit=${ limit }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async toggleScraper ( scraperId )
  {
    return this.handleApiCall(
      () => apiService.patch( `${ this.endpoints.scrapers }${ scraperId }/toggle`, {}, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async testScraper ( scraperId )
  {
    return this.handleApiCall(
      () => apiService.post( `${ this.endpoints.scrapers }${ scraperId }/test`, {}, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async runScraper ( scraperId )
  {
    return this.handleApiCall(
      () => apiService.post( `${ this.endpoints.scrapers }${ scraperId }/run`, {}, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async deleteScraper ( scraperId )
  {
    return this.handleApiCall(
      () => apiService.delete( `${ this.endpoints.scrapers }${ scraperId }`, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async createScraper ( scraperData )
  {
    return this.handleApiCall(
      () => apiService.post( this.endpoints.scrapers, scraperData, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }

  async updateScraper ( scraperId, scraperData )
  {
    return this.handleApiCall(
      () => apiService.put( `${ this.endpoints.scrapers }${ scraperId }`, scraperData, {
        headers: this.getAuthHeaders(),
        ...this.getAuthCredentials()
      } )
    )
  }
}

export const scraperService = new ScraperService()
