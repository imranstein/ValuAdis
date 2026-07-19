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

  it('lists photos via apiService.get', async () => {
    getMock.mockResolvedValueOnce({ success: true, data: [{ id: 1, url: '/api/v1/properties/11/photos/1/file', position: 0 }] })
    const { propertyService } = await import('./propertyService')
    const photos = await propertyService.listPhotos(11)

    expect(getMock).toHaveBeenCalledWith('/api/v1/properties/11/photos')
    expect(photos).toHaveLength(1)
    expect(photos[0].id).toBe(1)
  })

  it('uploads a photo with the multipart body', async () => {
    const response = {
      ok: true,
      json: vi.fn().mockResolvedValue({ success: true, data: { id: 2, url: '/api/v1/properties/11/photos/2/file', position: 1 } }),
    }
    globalThis.fetch = vi.fn().mockResolvedValue(response)

    const { propertyService } = await import('./propertyService')
    const file = new File(['img'], 'photo.png', { type: 'image/png' })
    const photo = await propertyService.uploadPhoto(11, file)

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8020/api/v1/properties/11/photos',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(photo.id).toBe(2)
  })

  it('throws when photo upload is rejected with a server detail', async () => {
    const response = {
      ok: false,
      json: vi.fn().mockResolvedValue({ detail: 'File is not a valid JPEG, PNG, or WEBP image.' }),
    }
    globalThis.fetch = vi.fn().mockResolvedValue(response)

    const { propertyService } = await import('./propertyService')
    const file = new File(['not an image'], 'fake.jpg', { type: 'image/jpeg' })
    await expect(propertyService.uploadPhoto(11, file)).rejects.toThrow('not a valid JPEG')
  })

  it('deletes a photo', async () => {
    const response = { ok: true, json: vi.fn().mockResolvedValue({ success: true }) }
    globalThis.fetch = vi.fn().mockResolvedValue(response)

    const { propertyService } = await import('./propertyService')
    await propertyService.deletePhoto(11, 2)

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8020/api/v1/properties/11/photos/2',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('resolves a host-relative photo url against the api base', async () => {
    const { propertyService } = await import('./propertyService')
    expect(propertyService.resolvePhotoUrl('/api/v1/properties/11/photos/2/file')).toBe(
      'http://localhost:8020/api/v1/properties/11/photos/2/file',
    )
  })

  it('leaves an already-absolute photo url untouched', async () => {
    const { propertyService } = await import('./propertyService')
    expect(propertyService.resolvePhotoUrl('https://cdn.example.com/photo.jpg')).toBe(
      'https://cdn.example.com/photo.jpg',
    )
  })
})
