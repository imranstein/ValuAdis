import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { PaginatedResponse, Property } from '~/types'

const getMock = vi.fn()
const postMock = vi.fn()
const putMock = vi.fn()
const deleteMock = vi.fn()

vi.mock('~/services/api', () => ({
  default: {
    get: getMock,
    post: postMock,
    put: putMock,
    delete: deleteMock,
  },
}))

vi.mock('~/utils/authToken', () => ({
  getAccessToken: () => 'test-access-token',
}))

vi.mock('#imports', () => ({
  useRuntimeConfig: () => ({ public: { apiBaseUrl: 'http://localhost:8020' } }),
}))


const property: Property = {
  id: 11,
  user_id: 1,
  address: '4 Kilo',
  municipality: 'Addis Ababa',
  region: 'AA',
  property_type: 'residential',
  area_sqm: 120,
  condition: 'good',
  boundaries: [],
  coordinates: [],
  amenities: {},
  utilities: {},
  photos: [],
  documents: [],
  status: 'draft',
  created_at: '2026-05-31T00:00:00Z',
  updated_at: '2026-05-31T00:00:00Z',
}

const paginated = { success: true, data: [property], pagination: { page: 1, per_page: 10, total: 1, pages: 1 } } as PaginatedResponse<Property>

describe('propertyService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.fetch = vi.fn()
  })

  it('loads property lists with parameters', async () => {
    getMock.mockResolvedValueOnce(paginated)
    const { propertyService } = await import('./propertyService')
    const result = await propertyService.getProperties({ page: 1, per_page: 20 })

    expect(getMock).toHaveBeenCalledWith('/api/v1/properties', { page: 1, per_page: 20 })
    expect(result.success).toBe(true)
    expect(result.pagination.total).toBe(1)
  })

  it('returns created property from createProperty', async () => {
    postMock.mockResolvedValueOnce({ success: true, data: property })
    const { propertyService } = await import('./propertyService')
    const created = await propertyService.createProperty({
      address: '4 Kilo',
      municipality: 'AA',
      region: 'AA',
      property_type: 'residential',
      area_sqm: 120,
      condition: 'good',
    })

    expect(postMock).toHaveBeenCalledWith('/api/v1/properties', {
      address: '4 Kilo',
      municipality: 'AA',
      region: 'AA',
      property_type: 'residential',
      area_sqm: 120,
      condition: 'good',
    })
    expect(created).toEqual(property)
  })

  it('throws when fetching property fails', async () => {
    getMock.mockResolvedValueOnce({ success: false, data: null, message: 'not found' })
    const { propertyService } = await import('./propertyService')
    await expect(propertyService.getProperty(999)).rejects.toThrow('Failed to get property')
  })

  it('throws when delete fails', async () => {
    deleteMock.mockResolvedValueOnce({ success: false })
    const { propertyService } = await import('./propertyService')
    await expect(propertyService.deleteProperty(11)).rejects.toThrow('Failed to delete property')
})

  it('imports properties with bulkImport', async () => {
    const response = {
      ok: true,
      json: vi.fn().mockResolvedValue({ success: true, imported_count: 2, data: [property] }),
    }
    globalThis.fetch = vi.fn().mockResolvedValue(response)

    const { propertyService } = await import('./propertyService')
    const file = new File(['id,address\\n1,4 Kilo'], 'properties.csv', { type: 'text/csv' })
    const result = await propertyService.bulkImport(file)

    expect(fetch).toHaveBeenCalledWith('http://localhost:8020/api/v1/properties/bulk-import', expect.any(Object))
    expect(result.imported_count).toBe(2)
  })

  it('throws on bulkImport failures with server detail', async () => {
    const response = {
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: vi.fn().mockResolvedValue({ detail: [{ message: 'validation error' }] }),
    }
    globalThis.fetch = vi.fn().mockResolvedValue(response)

    const { propertyService } = await import('./propertyService')
    const file = new File(['bad'], 'bad.csv', { type: 'text/csv' })
    await expect(propertyService.bulkImport(file)).rejects.toThrow('validation error')
  })
})
