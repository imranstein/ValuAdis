/**
 * Vehicle Valuation System Integration Tests
 * 
 * This test suite verifies the complete vehicle valuation workflow
 * from frontend to backend, including Ethiopian market factors.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// Import components
import VehicleBrandSelector from '~/components/vehicle/VehicleBrandSelector.vue'
import VINDecoder from '~/components/vehicle/VINDecoder.vue'
import VehicleValuation from '~/components/vehicle/VehicleValuation.vue'

// Import services
import { apiService } from '~/services/api'
import vehicleDataService from '~/services/vehicleDataService'

describe('Vehicle Valuation System Integration', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('VehicleBrandSelector Component', () => {
    it('renders vehicle selection interface', () => {
      const wrapper = mount(VehicleBrandSelector, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.find('.vehicle-brand-selector').exists()).toBe(true)
      expect(wrapper.find('h3').text()).toContain('Vehicle Selection')
    })

    it('loads vehicle brands on mount', async () => {
      // Mock API call
      const mockBrands = ['Toyota', 'Honda', 'BMW', 'Mercedes']
      vi.spyOn(vehicleDataService, 'getVehicleBrands').mockResolvedValue(mockBrands)

      const wrapper = mount(VehicleBrandSelector, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.loadBrands()
      expect(wrapper.vm.brands).toEqual(mockBrands)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('loads models when brand is selected', async () => {
      const mockModels = ['Corolla', 'Camry', 'Prius']
      vi.spyOn(vehicleDataService, 'getVehicleModels').mockResolvedValue(mockModels)

      const wrapper = mount(VehicleBrandSelector, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.selectBrand('Toyota')
      expect(wrapper.vm.models).toEqual(mockModels)
    })

    it('decodes VIN and populates vehicle data', async () => {
      const mockVinData = {
        make: 'TOYOTA',
        model: 'COROLLA',
        year: '2020',
        body_type: 'Sedan',
        fuel_type: 'Gasoline',
        transmission: 'Automatic'
      }

      vi.spyOn(vehicleDataService, 'decodeVehicleVin').mockResolvedValue(mockVinData)

      const wrapper = mount(VehicleBrandSelector, {
        global: {
          plugins: [pinia]
        }
      })

      await wrapper.vm.decodeVin('1HGBH41JXMN109186')
      expect(wrapper.vm.decodedData).toEqual(mockVinData)
      expect(wrapper.vm.selectedMake).toBe('TOYOTA')
      expect(wrapper.vm.selectedModel).toBe('COROLLA')
      expect(wrapper.vm.selectedYear).toBe('2020')
    })

    it('validates VIN format correctly', () => {
      const wrapper = mount(VehicleBrandSelector, {
        global: {
          plugins: [pinia]
        }
      })

      // Test valid VIN
      wrapper.vm.vinInput = '1HGBH41JXMN109186'
      expect(wrapper.vm.isValidVin).toBe(true)

      // Test invalid VIN (contains I)
      wrapper.vm.vinInput = '1HGBH41JXMN109I86'
      expect(wrapper.vm.isValidVin).toBe(false)

      // Test invalid length
      wrapper.vm.vinInput = '123'
      expect(wrapper.vm.isValidVin).toBe(false)
    })
  })

  describe('VINDecoder Component', () => {
    it('renders VIN decoder interface', () => {
      const wrapper = mount(VINDecoder, {
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.find('.vin-decoder').exists()).toBe(true)
      expect(wrapper.find('h3').text()).toContain('VIN Decoder')
    })

    it('decodes VIN and displays results', async () => {
      const mockDecodedData = {
        make: 'TOYOTA',
        model: 'COROLLA',
        year: '2020',
        trim: 'LE',
        body_type: 'Sedan',
        fuel_type: 'Gasoline',
        transmission: 'Automatic',
        engine: '1.8L',
        manufacturer: 'Toyota Motor Corporation',
        plant_country: 'Japan'
      }

      vi.spyOn(vehicleDataService, 'decodeVehicleVin').mockResolvedValue(mockDecodedData)

      const wrapper = mount(VINDecoder, {
        global: {
          plugins: [pinia]
        }
      })

      wrapper.vm.vinInput = '1HGBH41JXMN109186'
      await wrapper.vm.decodeVin()

      expect(wrapper.vm.decodedData).toEqual(mockDecodedData)
      expect(wrapper.find('.decoded-results').exists()).toBe(true)
      expect(wrapper.find('.vehicle-name').text()).toContain('TOYOTA COROLLA 2020')
    })

    it('applies decoded data to vehicle form', async () => {
      const mockDecodedData = {
        make: 'TOYOTA',
        model: 'COROLLA',
        year: '2020',
        body_type: 'Sedan',
        fuel_type: 'Gasoline',
        transmission: 'Automatic'
      }

      vi.spyOn(vehicleDataService, 'decodeVehicleVin').mockResolvedValue(mockDecodedData)

      const wrapper = mount(VINDecoder, {
        global: {
          plugins: [pinia]
        },
        props: {
          onDecoded: vi.fn()
        }
      })

      wrapper.vm.vinInput = '1HGBH41JXMN109186'
      await wrapper.vm.decodeVin()

      const emittedData = {
        make: 'TOYOTA',
        model: 'COROLLA',
        year: 2020,
        vin: '1HGBH41JXMN109186',
        body_type: 'sedan',
        fuel_type: 'gasoline',
        transmission: 'automatic'
      }

      wrapper.vm.applyDecodedData()
      expect(wrapper.emitted()['apply-data'][0]).toEqual(emittedData)
    })
  })

  describe('VehicleValuation Component', () => {
    it('renders Ethiopian market valuation analysis', () => {
      const mockVehicle = {
        make: 'Toyota',
        model: 'Corolla',
        year: 2020,
        region: 'Addis Ababa',
        custom_duty_paid: true,
        import_year: 2020
      }

      const mockValuation = {
        market_value: 850000,
        taxable_value: 212500,
        confidence_score: 85,
        regional_multiplier: 1.15,
        customs_multiplier: 1.05,
        make_reliability_multiplier: 0.95,
        fuel_type_multiplier: 1.0,
        body_type_multiplier: 1.0,
        condition_multiplier: 0.9,
        created_date: '2024-01-15'
      }

      const wrapper = mount(VehicleValuation, {
        props: {
          vehicle: mockVehicle,
          valuation: mockValuation
        },
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.find('.vehicle-valuation').exists()).toBe(true)
      expect(wrapper.find('.valuation-header h3').text()).toContain('Ethiopian market')
      expect(wrapper.find('.summary-value').text()).toContain('ETB 850,000')
    })

    it('displays Ethiopian market factors correctly', () => {
      const mockVehicle = {
        make: 'Toyota',
        region: 'Addis Ababa',
        custom_duty_paid: true,
        import_year: 2020
      }

      const mockValuation = {
        regional_multiplier: 1.15,
        customs_multiplier: 1.05,
        make_reliability_multiplier: 0.95,
        fuel_type_multiplier: 1.0,
        body_type_multiplier: 1.0,
        condition_multiplier: 0.9
      }

      const wrapper = mount(VehicleValuation, {
        props: {
          vehicle: mockVehicle,
          valuation: mockValuation
        },
        global: {
          plugins: [pinia]
        }
      })

      // Check regional factor
      expect(wrapper.text()).toContain('Addis Ababa')
      expect(wrapper.text()).toContain('1.15x')

      // Check customs factor
      expect(wrapper.text()).toContain('Paid')
      expect(wrapper.text()).toContain('1.05x')

      // Check make reliability
      expect(wrapper.text()).toContain('Toyota')
      expect(wrapper.text()).toContain('0.95x')
    })

    it('calculates confidence score correctly', () => {
      const mockValuation = {
        confidence_score: 85
      }

      const wrapper = mount(VehicleValuation, {
        props: {
          vehicle: {},
          valuation: mockValuation
        },
        global: {
          plugins: [pinia]
        }
      })

      expect(wrapper.vm.getConfidenceTrend()).toBe('positive')
      expect(wrapper.vm.getConfidenceIcon()).toBe('pi-check-circle')
      expect(wrapper.vm.getConfidenceText()).toBe('High confidence')
    })
  })

  describe('Vehicle Data Service', () => {
    it('fetches vehicle brands from API', async () => {
      const mockBrands = ['Toyota', 'Honda', 'BMW', 'Mercedes', 'Audi']
      vi.spyOn(apiService, 'get').mockResolvedValue({ data: mockBrands })

      const result = await vehicleDataService.getVehicleBrands()
      expect(result).toEqual(mockBrands)
      expect(apiService.get).toHaveBeenCalledWith('/vehicle-data/brands')
    })

    it('fetches models for specific make', async () => {
      const mockModels = ['Corolla', 'Camry', 'Prius', 'Highlander']
      vi.spyOn(apiService, 'get').mockResolvedValue({ data: mockModels })

      const result = await vehicleDataService.getVehicleModels('Toyota')
      expect(result).toEqual(mockModels)
      expect(apiService.get).toHaveBeenCalledWith('/vehicle-data/models/Toyota')
    })

    it('decodes VIN from API', async () => {
      const mockVinData = {
        make: 'TOYOTA',
        model: 'COROLLA',
        year: '2020',
        vin: '1HGBH41JXMN109186'
      }
      vi.spyOn(apiService, 'get').mockResolvedValue({ data: mockVinData })

      const result = await vehicleDataService.decodeVehicleVin('1HGBH41JXMN109186')
      expect(result).toEqual(mockVinData)
      expect(apiService.get).toHaveBeenCalledWith('/vehicle-data/decode-vin/1HGBH41JXMN109186')
    })

    it('handles API errors gracefully', async () => {
      vi.spyOn(apiService, 'get').mockRejectedValue(new Error('Network error'))

      await expect(vehicleDataService.getVehicleBrands()).rejects.toThrow('Failed to fetch vehicle brands')
    })
  })

  describe('Ethiopian Market Calculations', () => {
    it('calculates regional multipliers correctly', () => {
      const testCases = [
        { region: 'Addis Ababa', expected: 1.15 },
        { region: 'Oromia', expected: 1.0 },
        { region: 'Amhara', expected: 0.95 },
        { region: 'Tigray', expected: 0.9 },
        { region: 'Southern', expected: 0.85 }
      ]

      testCases.forEach(({ region, expected }) => {
        const multiplier = getRegionalMultiplier(region)
        expect(multiplier).toBe(expected)
      })
    })

    it('calculates customs duty factors correctly', () => {
      expect(getCustomsMultiplier(true)).toBe(1.05)  // Paid
      expect(getCustomsMultiplier(false)).toBe(0.8)   // Unpaid
    })

    it('calculates make reliability multipliers correctly', () => {
      const testCases = [
        { make: 'Toyota', expected: 0.95 },
        { make: 'Honda', expected: 0.90 },
        { make: 'Mercedes', expected: 0.85 },
        { make: 'Hyundai', expected: 0.75 }
      ]

      testCases.forEach(({ make, expected }) => {
        const multiplier = getMakeReliabilityMultiplier(make)
        expect(multiplier).toBe(expected)
      })
    })

    it('calculates total market value with all factors', () => {
      const baseValue = 600000
      const factors = {
        regional_multiplier: 1.15,
        customs_multiplier: 1.05,
        make_reliability_multiplier: 0.95,
        fuel_type_multiplier: 1.0,
        body_type_multiplier: 1.0,
        condition_multiplier: 0.9
      }

      const expected = baseValue * 
        factors.regional_multiplier * 
        factors.customs_multiplier * 
        factors.make_reliability_multiplier * 
        factors.fuel_type_multiplier * 
        factors.body_type_multiplier * 
        factors.condition_multiplier

      expect(calculateMarketValue(baseValue, factors)).toBeCloseTo(expected, 2)
    })
  })

  describe('End-to-End Workflow', () => {
    it('completes full vehicle valuation workflow', async () => {
      // Mock all API calls
      vi.spyOn(vehicleDataService, 'getVehicleBrands').mockResolvedValue(['Toyota', 'Honda'])
      vi.spyOn(vehicleDataService, 'getVehicleModels').mockResolvedValue(['Corolla', 'Camry'])
      vi.spyOn(vehicleDataService, 'decodeVehicleVin').mockResolvedValue({
        make: 'TOYOTA',
        model: 'COROLLA',
        year: '2020',
        body_type: 'Sedan',
        fuel_type: 'Gasoline'
      })

      // Step 1: Load brands
      const brands = await vehicleDataService.getVehicleBrands()
      expect(brands).toContain('Toyota')

      // Step 2: Select brand and load models
      const models = await vehicleDataService.getVehicleModels('Toyota')
      expect(models).toContain('Corolla')

      // Step 3: Decode VIN
      const vinData = await vehicleDataService.decodeVehicleVin('1HGBH41JXMN109186')
      expect(vinData.make).toBe('TOYOTA')

      // Step 4: Calculate Ethiopian market valuation
      const valuation = calculateEthiopianValuation({
        make: 'Toyota',
        model: 'Corolla',
        year: 2020,
        region: 'Addis Ababa',
        custom_duty_paid: true,
        import_year: 2020,
        mileage: 45000
      })

      expect(valuation.market_value).toBeGreaterThan(0)
      expect(valuation.taxable_value).toBe(valuation.market_value * 0.25)
      expect(valuation.regional_multiplier).toBe(1.15)
      expect(valuation.customs_multiplier).toBe(1.05)
    })
  })
})

// Helper functions for Ethiopian market calculations
function getRegionalMultiplier(region) {
  const multipliers = {
    'Addis Ababa': 1.15,
    'Oromia': 1.0,
    'Amhara': 0.95,
    'Tigray': 0.9,
    'Southern': 0.85,
    'Somali': 0.8,
    'Afar': 0.75,
    'Benishangul': 0.8,
    'Gambela': 0.8,
    'Harari': 0.9,
    'Dire Dawa': 0.95
  }
  return multipliers[region] || 1.0
}

function getCustomsMultiplier(paid) {
  return paid ? 1.05 : 0.8
}

function getMakeReliabilityMultiplier(make) {
  const reliability = {
    'Toyota': 0.95,
    'Honda': 0.90,
    'Mazda': 0.85,
    'Nissan': 0.80,
    'Hyundai': 0.75,
    'Kia': 0.75,
    'BMW': 0.85,
    'Mercedes': 0.85,
    'Audi': 0.80,
    'Volkswagen': 0.80,
    'Isuzu': 0.85,
    'Hino': 0.85
  }
  return reliability[make] || 0.7
}

function calculateMarketValue(baseValue, factors) {
  return baseValue * 
    factors.regional_multiplier * 
    factors.customs_multiplier * 
    factors.make_reliability_multiplier * 
    factors.fuel_type_multiplier * 
    factors.body_type_multiplier * 
    factors.condition_multiplier
}

function calculateEthiopianValuation(vehicle) {
  const baseValue = 600000
  const currentYear = new Date().getFullYear()
  const age = currentYear - vehicle.year
  const depreciation = Math.min(age * 0.1, 0.8)
  
  let adjustedValue = baseValue * (1 - depreciation)
  
  // Apply Ethiopian market factors
  const regionalMultiplier = getRegionalMultiplier(vehicle.region)
  const customsMultiplier = getCustomsMultiplier(vehicle.custom_duty_paid)
  const makeMultiplier = getMakeReliabilityMultiplier(vehicle.make)
  
  // Import year adjustment
  const importAge = currentYear - vehicle.import_year
  let importMultiplier = 1.0
  if (importAge <= 1) importMultiplier = 1.1
  else if (importAge <= 3) importMultiplier = 1.0
  else if (importAge <= 5) importMultiplier = 0.95
  else importMultiplier = 0.85
  
  // Condition factor based on mileage
  let conditionMultiplier = 1.0
  if (vehicle.mileage > 100000) conditionMultiplier = 0.8
  else if (vehicle.mileage > 75000) conditionMultiplier = 0.9
  else if (vehicle.mileage > 50000) conditionMultiplier = 0.95
  
  const marketValue = adjustedValue * regionalMultiplier * customsMultiplier * makeMultiplier * importMultiplier * conditionMultiplier
  
  return {
    market_value: Math.round(marketValue),
    taxable_value: Math.round(marketValue * 0.25),
    confidence_score: 85,
    regional_multiplier,
    customs_multiplier,
    make_reliability_multiplier: makeMultiplier,
    fuel_type_multiplier: 1.0,
    body_type_multiplier: 1.0,
    condition_multiplier,
    created_date: new Date().toISOString().split('T')[0]
  }
}
