import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import propertyService from '~/services/propertyService'
import type { Property, PropertyCreate } from '~/types'

export const usePropertiesStore = defineStore('properties', () => {
  // State
  const properties = ref<Property[]>([])
  const currentProperty = ref<Property | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  })

  // Getters
  const totalProperties = computed(() => properties.value.length)
  const recentProperties = computed(() => properties.value.slice(0, 5))

  // Actions
  async function fetchProperties(params?: any) {
    loading.value = true
    error.value = null
    try {
      const response = await propertyService.getProperties(params)
      properties.value = response.data
      if (response.pagination) {
        pagination.value = response.pagination
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch properties'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchProperty(id: number) {
    loading.value = true
    error.value = null
    try {
      currentProperty.value = await propertyService.getProperty(id)
      return currentProperty.value
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch property'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createProperty(data: PropertyCreate) {
    loading.value = true
    error.value = null
    try {
      const property = await propertyService.createProperty(data)
      properties.value.unshift(property)
      return property
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create property'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProperty(id: number, data: Partial<PropertyCreate>) {
    loading.value = true
    error.value = null
    try {
      const property = await propertyService.updateProperty(id, data)
      const index = properties.value.findIndex(p => p.id === id)
      if (index !== -1) {
        properties.value[index] = property
      }
      if (currentProperty.value?.id === id) {
        currentProperty.value = property
      }
      return property
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update property'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteProperty(id: number) {
    loading.value = true
    error.value = null
    try {
      await propertyService.deleteProperty(id)
      properties.value = properties.value.filter(p => p.id !== id)
      if (currentProperty.value?.id === id) {
        currentProperty.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete property'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    properties,
    currentProperty,
    loading,
    error,
    pagination,
    // Getters
    totalProperties,
    recentProperties,
    // Actions
    fetchProperties,
    fetchProperty,
    createProperty,
    updateProperty,
    deleteProperty
  }
})
