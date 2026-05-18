/**
 * Vehicle Data Service
 * 
 * Service for fetching vehicle data from the backend API
 * including makes, models, years, and VIN decoding.
 */

import api from './api'

class VehicleDataService {
  basePath = '/api/v1/vehicle-data'

  /**
   * Get all vehicle brands from NHTSA API
   * @returns {Promise<Array<string>>} List of vehicle brands
   */
  async getVehicleBrands() {
    try {
      return await api.get(`${this.basePath}/brands`)
    } catch (error) {
      throw new Error('Failed to fetch vehicle brands')
    }
  }

  /**
   * Get models for a specific vehicle brand
   * @param {string} brand - Vehicle brand name
   * @returns {Promise<Array<string>>} List of models for the brand
   */
  async getVehicleModels(brand) {
    try {
      return await api.get(`${this.basePath}/models/${encodeURIComponent(brand)}`)
    } catch (error) {
      throw new Error(`Failed to fetch models for ${brand}`)
    }
  }

  /**
   * Decode a VIN to get vehicle specifications
   * @param {string} vin - 17-character VIN
   * @returns {Promise<Object>} Decoded vehicle information
   */
  async decodeVehicleVin(vin) {
    try {
      return await api.get(`${this.basePath}/decode-vin/${encodeURIComponent(vin)}`)
    } catch (error) {
      throw new Error(`Failed to decode VIN ${vin}`)
    }
  }

  /**
   * Get vehicle types for a specific brand
   * @param {string} brand - Vehicle brand name
   * @returns {Promise<Array<string>>} List of vehicle types
   */
  async getVehicleTypesForMake(brand) {
    try {
      return await api.get(`${this.basePath}/types/${encodeURIComponent(brand)}`)
    } catch (error) {
      throw new Error(`Failed to fetch vehicle types for ${brand}`)
    }
  }

  /**
   * Search for vehicles by make or model
   * @param {string} query - Search query
   * @returns {Promise<Array<Object>>} List of matching vehicles
   */
  async searchVehicles(query) {
    try {
      return await api.get(`${this.basePath}/search`, {
        params: { query }
      })
    } catch (error) {
      throw new Error(`Failed to search vehicles`)
    }
  }

  /**
   * Validate VIN format
   * @param {string} vin - VIN to validate
   * @returns {Promise<Object>} Validation results
   */
  async validateVin(vin) {
    try {
      return await api.get(`${this.basePath}/validate-vin/${encodeURIComponent(vin)}`)
    } catch (error) {
      throw new Error(`Failed to validate VIN ${vin}`)
    }
  }

  /**
   * Get cache information (admin only)
   * @returns {Promise<Object>} Cache statistics
   */
  async getCacheInfo() {
    try {
      return await api.get(`${this.basePath}/cache-info`)
    } catch (error) {
      throw new Error('Failed to get cache info')
    }
  }

  /**
   * Clear cache (admin only)
   * @returns {Promise<Object>} Clear cache result
   */
  async clearCache() {
    try {
      return await api.post(`${this.basePath}/clear-cache`)
    } catch (error) {
      throw new Error('Failed to clear cache')
    }
  }

  /**
   * Get popular brands (cached first few brands for quick access)
   * @returns {Promise<Array<string>>} List of popular brands
   */
  async getPopularBrands() {
    try {
      const brands = await this.getVehicleBrands()
      
      // Return popular Ethiopian market brands first
      const popularBrands = [
        'Toyota', 'Hyundai', 'Kia', 'Nissan', 'Honda', 'Mazda',
        'Isuzu', 'Hino', 'Mercedes-Benz', 'BMW', 'Audi', 'Volkswagen'
      ]
      
      const availablePopular = popularBrands.filter(brand => 
        brands.some(b => b.toLowerCase() === brand.toLowerCase())
      )
      
      // Add other brands alphabetically
      const otherBrands = brands
        .filter(brand => !availablePopular.some(pb => pb.toLowerCase() === brand.toLowerCase()))
        .sort()
      
      return [...availablePopular, ...otherBrands]
    } catch (error) {
      return []
    }
  }

  /**
   * Get models with year ranges for a brand
   * @param {string} brand - Vehicle brand name
   * @returns {Promise<Array<Object>>} Models with year information
   */
  async getModelsYearRange(brand) {
    try {
      const models = await this.getVehicleModels(brand)
      
      // For now, return basic model info. In a real implementation,
      // this would fetch year ranges from the API
      return models.map(model => ({
        name: model,
        yearRange: '1990-2024', // Default range
        popular: false
      }))
    } catch (error) {
      return []
    }
  }

  /**
   * Batch decode multiple VINs
   * @param {Array<string>} vins - Array of VINs to decode
   * @returns {Promise<Array<Object>>} Array of decoded results
   */
  async batchDecodeVins(vins) {
    try {
      const results = []
      
      // Process VINs in batches to avoid overwhelming the API
      const batchSize = 5
      for (let i = 0; i < vins.length; i += batchSize) {
        const batch = vins.slice(i, i + batchSize)
        const batchPromises = batch.map(vin => 
          this.decodeVehicleVin(vin).catch(error => ({
            vin,
            error: error.message
          }))
        )
        
        const batchResults = await Promise.all(batchPromises)
        results.push(...batchResults)
      }
      
      return results
    } catch (error) {
      throw new Error('Failed to batch decode VINs')
    }
  }

  /**
   * Get vehicle specifications by make, model, and year
   * @param {string} make - Vehicle make
   * @param {string} model - Vehicle model
   * @param {number} year - Vehicle year
   * @returns {Promise<Object>} Vehicle specifications
   */
  async getVehicleSpecifications(make, model, year) {
    try {
      // This would typically call a specifications API
      // For now, return basic specifications based on common patterns
      const specs = {
        make,
        model,
        year,
        bodyType: this.guessBodyType(make, model),
        engineCapacity: this.guessEngineCapacity(make, model),
        fuelType: this.guessFuelType(make, model),
        transmission: 'Automatic',
        driveType: 'FWD'
      }
      
      return specs
    } catch (error) {
      throw new Error('Failed to get vehicle specifications')
    }
  }

  /**
   * Helper method to guess body type based on make and model
   * @param {string} make - Vehicle make
   * @param {string} model - Vehicle model
   * @returns {string} Guessed body type
   */
  guessBodyType(make, model) {
    const modelLower = model.toLowerCase()
    
    if (modelLower.includes('suv') || modelLower.includes('rav4') || modelLower.includes('highlander')) {
      return 'SUV'
    } else if (modelLower.includes('pickup') || modelLower.includes('hilux')) {
      return 'Pickup'
    } else if (modelLower.includes('van') || modelLower.includes('hiace')) {
      return 'Van'
    } else if (modelLower.includes('coupe') || modelLower.includes('86')) {
      return 'Coupe'
    } else if (modelLower.includes('hatchback') || modelLower.includes('yaris') || modelLower.includes('vitz')) {
      return 'Hatchback'
    } else {
      return 'Sedan'
    }
  }

  /**
   * Helper method to guess engine capacity based on make and model
   * @param {string} make - Vehicle make
   * @param {string} model - Vehicle model
   * @returns {number} Guessed engine capacity in CC
   */
  guessEngineCapacity(make, model) {
    const modelLower = model.toLowerCase()
    
    if (modelLower.includes('1.0') || modelLower.includes('1000')) {
      return 1000
    } else if (modelLower.includes('1.5') || modelLower.includes('1500')) {
      return 1500
    } else if (modelLower.includes('2.0') || modelLower.includes('2000')) {
      return 2000
    } else if (modelLower.includes('2.5') || modelLower.includes('2500')) {
      return 2500
    } else if (modelLower.includes('3.0') || modelLower.includes('3000')) {
      return 3000
    } else {
      return 2000 // Default
    }
  }

  /**
   * Helper method to guess fuel type based on make and model
   * @param {string} make - Vehicle make
   * @param {string} model - Vehicle model
   * @returns {string} Guessed fuel type
   */
  guessFuelType(make, model) {
    const modelLower = model.toLowerCase()
    const makeLower = make.toLowerCase()
    
    if (modelLower.includes('hybrid') || modelLower.includes('prius')) {
      return 'Hybrid'
    } else if (modelLower.includes('electric') || modelLower.includes('ev') || makeLower === 'tesla') {
      return 'Electric'
    } else if (modelLower.includes('diesel')) {
      return 'Diesel'
    } else {
      return 'Gasoline'
    }
  }
}

// Export singleton instance
const vehicleDataService = new VehicleDataService()

// Export individual functions for convenience
export const fetchVehicleBrands = () => vehicleDataService.getVehicleBrands()
export const fetchVehicleModels = (brand) => vehicleDataService.getVehicleModels(brand)
export const decodeVehicleVin = (vin) => vehicleDataService.decodeVehicleVin(vin)
export const fetchVehicleTypesForMake = (brand) => vehicleDataService.getVehicleTypesForMake(brand)
export const searchVehicles = (query) => vehicleDataService.searchVehicles(query)
export const validateVin = (vin) => vehicleDataService.validateVin(vin)
export const getPopularBrands = () => vehicleDataService.getPopularBrands()
export const getModelsYearRange = (brand) => vehicleDataService.getModelsYearRange(brand)
export const batchDecodeVins = (vins) => vehicleDataService.batchDecodeVins(vins)
export const getVehicleSpecifications = (make, model, year) => vehicleDataService.getVehicleSpecifications(make, model, year)

export default vehicleDataService
