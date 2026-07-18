/**
 * Phase E — persona derivation unit tests
 */

import { describe, it, expect } from 'vitest'
import { derivePersona, isRouteAllowedForPersona, personaHomePath } from './persona'

describe('derivePersona', () => {
  it('returns staff for a null user', () => {
    expect(derivePersona(null)).toBe('staff')
  })

  it('returns staff for a plain valuer account with no roles', () => {
    expect(derivePersona({ is_admin: false, roles: [] })).toBe('staff')
  })

  it('returns staff for an admin account regardless of roles', () => {
    expect(derivePersona({ is_admin: true, roles: ['rental_officer'] })).toBe('staff')
  })

  it('returns officer for a rental_officer role', () => {
    expect(derivePersona({ is_admin: false, roles: ['rental_officer'] })).toBe('officer')
  })

  it('returns owner for a property_owner role', () => {
    expect(derivePersona({ is_admin: false, roles: ['property_owner'] })).toBe('owner')
  })

  it('returns renter for a renter role', () => {
    expect(derivePersona({ is_admin: false, roles: ['renter'] })).toBe('renter')
  })

  it('prioritizes officer over a citizen role on the same account', () => {
    expect(derivePersona({ is_admin: false, roles: ['property_owner', 'rental_officer'] })).toBe('officer')
  })
})

describe('personaHomePath', () => {
  it('maps each persona to its shell home route', () => {
    expect(personaHomePath('staff')).toBe('/dashboard')
    expect(personaHomePath('officer')).toBe('/rentals')
    expect(personaHomePath('owner')).toBe('/rentals/my-listings')
    expect(personaHomePath('renter')).toBe('/rentals/my-applications')
  })
})

describe('isRouteAllowedForPersona', () => {
  it('allows every persona to reach the common profile route', () => {
    expect(isRouteAllowedForPersona('staff', '/profile')).toBe(true)
    expect(isRouteAllowedForPersona('officer', '/profile')).toBe(true)
    expect(isRouteAllowedForPersona('owner', '/profile')).toBe(true)
    expect(isRouteAllowedForPersona('renter', '/profile')).toBe(true)
  })

  it('denies staff only the citizen self-registration page', () => {
    expect(isRouteAllowedForPersona('staff', '/rent/signup')).toBe(false)
    expect(isRouteAllowedForPersona('staff', '/dashboard')).toBe(true)
    expect(isRouteAllowedForPersona('staff', '/vehicles')).toBe(true)
  })

  it('scopes an officer to the review queue and contracts registry only', () => {
    expect(isRouteAllowedForPersona('officer', '/rentals')).toBe(true)
    expect(isRouteAllowedForPersona('officer', '/rentals/contracts')).toBe(true)
    expect(isRouteAllowedForPersona('officer', '/rentals/my-listings')).toBe(false)
    expect(isRouteAllowedForPersona('officer', '/dashboard')).toBe(false)
  })

  it('scopes a property owner to their listings, contracts, and property creation', () => {
    expect(isRouteAllowedForPersona('owner', '/rentals/my-listings')).toBe(true)
    expect(isRouteAllowedForPersona('owner', '/rentals/my-contracts')).toBe(true)
    expect(isRouteAllowedForPersona('owner', '/properties/create')).toBe(true)
    expect(isRouteAllowedForPersona('owner', '/properties')).toBe(false)
    expect(isRouteAllowedForPersona('owner', '/rentals')).toBe(false)
  })

  it('scopes a renter to their applications and contracts only', () => {
    expect(isRouteAllowedForPersona('renter', '/rentals/my-applications')).toBe(true)
    expect(isRouteAllowedForPersona('renter', '/rentals/my-contracts')).toBe(true)
    expect(isRouteAllowedForPersona('renter', '/rentals/my-listings')).toBe(false)
    expect(isRouteAllowedForPersona('renter', '/scrapers')).toBe(false)
  })
})
