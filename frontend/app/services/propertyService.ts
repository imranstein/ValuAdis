import apiService from './api'
import type { Property, PropertyCreate, PaginatedResponse } from '~/types'
import { getAccessToken } from '~/utils/authToken'
import { useRuntimeConfig } from '#imports'

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

  async bulkImport(file: File): Promise<{ success: boolean; imported_count: number; data: Property[] }> {
    const config = useRuntimeConfig()
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${config.public.apiBaseUrl}/api/v1/properties/bulk-import`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getAccessToken()}`,
      },
      body: formData,
    })

    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(data.detail?.[0]?.message || data.detail || 'Failed to import properties')
    }
    return data
  }
}

export const propertyService = new PropertyService()
export default propertyService
