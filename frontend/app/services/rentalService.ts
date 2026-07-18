import { getAccessToken } from '~/utils/authToken'
import { useRuntimeConfig } from '#imports'

export interface PublicListingProperty {
  address: string
  municipality: string
  subcity?: string | null
  property_type: string
  property_subtype?: string | null
  area_sqm: number
  building_area_sqm?: number | null
  number_of_bedrooms?: number | null
  number_of_bathrooms?: number | null
  number_of_floors?: number | null
  year_built?: number | null
  condition?: string | null
  latitude?: number | null
  longitude?: number | null
}

export interface PublicListing {
  public_id: string
  suggested_rent: number
  band_min: number
  band_max: number
  published_at?: string | null
  has_valuation_certificate: boolean
  property: PublicListingProperty
}

export interface OwnerListing {
  public_id: string
  property_id: number
  property_address?: string | null
  suggested_rent: number
  band_min: number
  band_max: number
  confidence?: number | null
  requires_officer_review: boolean
  status: string
  review_reason?: string | null
  published_at?: string | null
  created_at?: string | null
}

export interface OfficerListing extends OwnerListing {
  valuation_id: number
  owner_user_id: number
  owner_name?: string | null
  owner_verified: boolean
  property_municipality?: string | null
  property_subcity?: string | null
  property_type?: string | null
  property_area_sqm?: number | null
}

export interface ListingSearchFilters {
  district?: string
  property_subtype?: string
  bedrooms?: number
  band_min?: number
  band_max?: number
  skip?: number
  limit?: number
}

interface ListEnvelope<T> {
  success: boolean
  data: T[]
  total: number
  skip: number
  limit: number
}

class RentalService {
  private base(): string {
    const config = useRuntimeConfig()
    return `${config.public.apiBaseUrl}/api/v1/rentals`
  }

  private authHeaders(): Record<string, string> {
    const token = getAccessToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  private async parse(response: Response) {
    const body = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(body.detail || body.message || `Request failed with ${response.status}`)
    }
    return body
  }

  async searchPublished(filters: ListingSearchFilters = {}): Promise<ListEnvelope<PublicListing>> {
    const params = new URLSearchParams()
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null && value !== '') params.set(key, String(value))
    }
    const query = params.toString()
    const response = await fetch(`${this.base()}/listings${query ? `?${query}` : ''}`)
    return this.parse(response)
  }

  async getPublicListing(publicId: string): Promise<PublicListing> {
    const response = await fetch(`${this.base()}/listings/${encodeURIComponent(publicId)}`)
    const body = await this.parse(response)
    return body.data
  }

  async createListing(propertyId: number, notes?: string): Promise<OwnerListing> {
    const response = await fetch(`${this.base()}/listings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ property_id: propertyId, notes: notes || null }),
    })
    const body = await this.parse(response)
    return body.data
  }

  async myListings(skip = 0, limit = 50): Promise<ListEnvelope<OwnerListing>> {
    const response = await fetch(`${this.base()}/my-listings?skip=${skip}&limit=${limit}`, {
      headers: this.authHeaders(),
    })
    return this.parse(response)
  }

  async reviewQueue(status = 'pending_review', skip = 0, limit = 50): Promise<ListEnvelope<OfficerListing>> {
    const response = await fetch(
      `${this.base()}/listings?status=${encodeURIComponent(status)}&skip=${skip}&limit=${limit}`,
      { headers: this.authHeaders() },
    )
    return this.parse(response)
  }

  async reviewListing(
    publicId: string,
    action: 'publish' | 'adjust_band' | 'reject',
    options: { band_min?: number; band_max?: number; reason?: string } = {},
  ): Promise<OfficerListing> {
    const response = await fetch(`${this.base()}/listings/${encodeURIComponent(publicId)}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ action, ...options }),
    })
    const body = await this.parse(response)
    return body.data
  }

  async withdrawListing(publicId: string, reason?: string): Promise<OwnerListing> {
    const response = await fetch(`${this.base()}/listings/${encodeURIComponent(publicId)}/withdraw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ reason: reason || null }),
    })
    const body = await this.parse(response)
    return body.data
  }

  async verifyOwner(userId: number): Promise<{ user_id: number; owner_verified: boolean }> {
    const response = await fetch(`${this.base()}/owners/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ user_id: userId }),
    })
    const body = await this.parse(response)
    return body.data
  }

  async citizenSignup(payload: {
    email: string
    full_name: string
    phone: string
    password: string
    municipality: string
    fayda_id_number: string
    account_type: 'renter' | 'property_owner'
  }): Promise<{ access_token: string; account_type: string; owner_verified: boolean }> {
    const response = await fetch(`${this.base()}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    })
    const body = await this.parse(response)
    return body.data
  }
}

export const rentalService = new RentalService()
export default rentalService
