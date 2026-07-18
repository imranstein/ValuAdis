/**
 * Phase E — role-aware shell/routing composable. Thin reactive wrapper
 * around the pure derivation in utils/persona.ts; keep the actual logic
 * there so it stays unit-testable without a Pinia/Nuxt runtime.
 */

import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { derivePersona, isRouteAllowedForPersona, personaHomePath, type Persona } from '~/utils/persona'

export function usePersona() {
  const authStore = useAuthStore()

  const persona = computed<Persona>(() => derivePersona(authStore.user as any))
  const isStaff = computed(() => persona.value === 'staff')
  const isOfficer = computed(() => persona.value === 'officer')
  const isOwner = computed(() => persona.value === 'owner')
  const isRenter = computed(() => persona.value === 'renter')
  const isCitizen = computed(() => isOwner.value || isRenter.value)
  const homePath = computed(() => personaHomePath(persona.value))

  function isRouteAllowed(path: string): boolean {
    return isRouteAllowedForPersona(persona.value, path)
  }

  return {
    persona,
    isStaff,
    isOfficer,
    isOwner,
    isRenter,
    isCitizen,
    homePath,
    isRouteAllowed,
  }
}
