/**
 * Persona derivation (Phase E — role/permission matrix)
 *
 * Pure functions with no Nuxt/Pinia dependency so they can be unit tested
 * directly (see persona.spec.ts) and reused from both the composable
 * (usePersona.ts) and route middleware (global-auth.global.ts, guest.ts).
 *
 * Precedence mirrors the backend (backend/app/core/rbac.py): admin >
 * rental_officer > property_owner > renter > staff. A plain valuer account
 * (is_admin=false, no roles) is "staff" — the pre-rentals default — so
 * existing valuer accounts see no behavior change.
 */

export type Persona = 'staff' | 'officer' | 'owner' | 'renter'

const OFFICER_ROLE = 'rental_officer'
const OWNER_ROLE = 'property_owner'
const RENTER_ROLE = 'renter'

export interface PersonaUser {
  is_admin?: boolean
  roles?: string[] | null
}

export function derivePersona(user: PersonaUser | null | undefined): Persona {
  if (!user) return 'staff'
  if (user.is_admin) return 'staff'

  const roles = user.roles || []
  if (roles.includes(OFFICER_ROLE)) return 'officer'
  if (roles.includes(OWNER_ROLE)) return 'owner'
  if (roles.includes(RENTER_ROLE)) return 'renter'
  return 'staff'
}

export function personaHomePath(persona: Persona): string {
  switch (persona) {
    case 'officer':
      return '/rentals'
    case 'owner':
      return '/rentals/my-listings'
    case 'renter':
      return '/rentals/my-applications'
    default:
      return '/dashboard'
  }
}

// Routes every authenticated persona may reach regardless of role.
const COMMON_ALLOWED_PATHS = ['/profile']

// Staff keep the full pre-rentals app; the only surface reserved for
// citizens is self-registration (staff already have accounts).
const STAFF_DENIED_PATHS = new Set(['/rent/signup'])

// Citizen/officer shells are additive allow-lists — everything else in the
// staff app (dashboard, properties list, vehicles, scrapers, users,
// settings, audit, analytics, map, reports, valuations) is out of reach.
const OFFICER_ALLOWED_PATHS = new Set(['/rentals', '/rentals/contracts'])
const OWNER_ALLOWED_PATHS = new Set(['/rentals/my-listings', '/rentals/my-contracts', '/properties/create'])
const RENTER_ALLOWED_PATHS = new Set(['/rentals/my-applications', '/rentals/my-contracts'])

export function isRouteAllowedForPersona(persona: Persona, path: string): boolean {
  if (COMMON_ALLOWED_PATHS.includes(path)) return true

  switch (persona) {
    case 'staff':
      return !STAFF_DENIED_PATHS.has(path)
    case 'officer':
      return OFFICER_ALLOWED_PATHS.has(path)
    case 'owner':
      return OWNER_ALLOWED_PATHS.has(path)
    case 'renter':
      return RENTER_ALLOWED_PATHS.has(path)
    default:
      return false
  }
}
