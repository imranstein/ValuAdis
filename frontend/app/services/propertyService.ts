import apiService from './api'
import type { Property, PropertyCreate, ApiResponse, PaginatedResponse } from '~/types'

class PropertyService {
  async getProperties(params?: any): Promise<PaginatedResponse<Property>> {
    const response = await apiService.get<Property[]>('/api/v1/properties', params)
    return response as any
  }

  async getProperty(id: number): Promise<Property> {
    const response = await apiService.get<Property>(`/api/v1/properties/${id}`)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to get property')
  }

  async createProperty(data: PropertyCreate): Promise<Property> {
    const response = await apiService.post<Property>('/api/v1/properties', data)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to create property')
  }

  async updateProperty(id: number, data: Partial<PropertyCreate>): Promise<Property> {
    const response = await apiService.put<Property>(`/api/v1/properties/${id}`, data)
    if (response.success && response.data) {
      return response.data
    }
    throw new Error('Failed to update property')
  }

  async deleteProperty(id: number): Promise<void> {
    const response = await apiService.delete<void>(`/api/v1/properties/${id}`)
    if (!response.success) {
      throw new Error('Failed to delete property')
    }
  }
}

export const propertyService = new PropertyService()
export default propertyService
