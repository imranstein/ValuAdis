import apiService from './api'
import type { Property, PropertyCreate, PaginatedResponse } from '~/types'
import { getAccessToken } from '~/utils/authToken'
import { useRuntimeConfig } from '#imports'

export interface PropertyPhoto {
  id: number
  url: string
  position: number
  created_at?: string | null
}

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

  async listPhotos(propertyId: number): Promise<PropertyPhoto[]> {
    const response = await apiService.get<PropertyPhoto[]>(`/api/v1/properties/${propertyId}/photos`)
    return (response as any).data || []
  }

  async uploadPhoto(propertyId: number, file: File): Promise<PropertyPhoto> {
    const config = useRuntimeConfig()
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${config.public.apiBaseUrl}/api/v1/properties/${propertyId}/photos`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getAccessToken()}` },
      body: formData,
    })

    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to upload photo')
    }
    return data.data
  }

  async deletePhoto(propertyId: number, photoId: number): Promise<void> {
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBaseUrl}/api/v1/properties/${propertyId}/photos/${photoId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || 'Failed to delete photo')
    }
  }

  /** Photo `url` values from the API are host-relative (opaque, no filesystem
   * path); resolve them against the configured API origin for <img src>. */
  resolvePhotoUrl(url: string): string {
    if (/^https?:\/\//i.test(url)) return url
    const config = useRuntimeConfig()
    return `${config.public.apiBaseUrl}${url}`
  }
}

export const propertyService = new PropertyService()
export default propertyService
