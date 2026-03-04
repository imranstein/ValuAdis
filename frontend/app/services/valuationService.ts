import apiService from './api'
import type { Valuation, ValuationCalculate, ValuationCreate, PaginatedResponse } from '~/types'

class ValuationService {
  async getValuations(params?: any): Promise<PaginatedResponse<Valuation>> {
    const response = await apiService.get<Valuation[]>('/api/v1/valuations/', params)
    return response as any
  }

  async getValuation(id: number): Promise<Valuation> {
    const response = await apiService.get<Valuation>(`/api/v1/valuations/${id}`)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to get valuation')
  }

  async calculateValuation(data: ValuationCalculate): Promise<any> {
    const response = await apiService.post<any>('/api/v1/valuations/calculate', data)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to calculate valuation')
  }

  async createValuation(data: ValuationCreate): Promise<Valuation> {
    const response = await apiService.post<Valuation>('/api/v1/valuations/', data)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to create valuation')
  }

  async updateValuation(id: number, data: Partial<ValuationCreate>): Promise<Valuation> {
    const response = await apiService.put<Valuation>(`/api/v1/valuations/${id}`, data)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to update valuation')
  }

  async deleteValuation(id: number): Promise<void> {
    const response = await apiService.delete<void>(`/api/v1/valuations/${id}`)
    if (!response.success) {
      throw new Error('Failed to delete valuation')
    }
  }
}

export const valuationService = new ValuationService()
export default valuationService
