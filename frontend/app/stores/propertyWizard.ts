import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getAccessToken } from '~/utils/authToken'

export interface WizardFormData {
  // Step 1 - Basic Info
  property_ref: string
  parcel_number: string
  title_deed_number: string
  registration_date: string
  address: string
  municipality: string
  region: string
  subcity: string
  woreda: string
  kebele: string
  zone: string
  neighborhood: string
  property_type: string
  property_subtype: string

  // Step 2 - Location
  latitude: number | null
  longitude: number | null
  boundaries: number[][]

  // Step 3 - Physical
  area_sqm: number | null
  building_area_sqm: number | null
  number_of_floors: number | null
  number_of_rooms: number | null
  number_of_bedrooms: number | null
  number_of_bathrooms: number | null
  year_built: number | null
  construction_material: string
  roof_material: string
  floor_material: string
  construction_quality: string
  condition: string
  parking_spaces: number | null

  // Step 4 - Amenities
  amenities: Record<string, boolean>
  utilities: Record<string, boolean>
  additional_features: string

  // Step 5 - Valuation
  valuation_method: string
  land_value: number | null
  building_value: number | null
  market_value: number | null
  valuation_date: string
  valuer_name: string
  valuer_license_number: string
  valuer_phone: string
  comparable_properties: any[]
  valuation_notes: string

  // Step 6 - Ownership
  owner_name: string
  owner_phone: string
  owner_email: string
  owner_id_type: string
  owner_id_number: string
  ownership_type: string
  legal_description: string

  // Step 7 - Documents
  photos: File[]
  documents: File[]
}

const DRAFT_KEY = 'property_wizard_draft'
const TOTAL_STEPS = 7

const defaultForm = (): WizardFormData => ({
  property_ref: '', parcel_number: '', title_deed_number: '', registration_date: '',
  address: '', municipality: '', region: '', subcity: '', woreda: '', kebele: '',
  zone: '', neighborhood: '', property_type: '', property_subtype: '',
  latitude: null, longitude: null, boundaries: [],
  area_sqm: null, building_area_sqm: null, number_of_floors: null,
  number_of_rooms: null, number_of_bedrooms: null, number_of_bathrooms: null,
  year_built: null, construction_material: '', roof_material: '', floor_material: '',
  construction_quality: '', condition: '', parking_spaces: null,
  amenities: {}, utilities: {}, additional_features: '',
  valuation_method: '', land_value: null, building_value: null, market_value: null,
  valuation_date: '', valuer_name: '', valuer_license_number: '', valuer_phone: '',
  comparable_properties: [], valuation_notes: '',
  owner_name: '', owner_phone: '', owner_email: '', owner_id_type: '',
  owner_id_number: '', ownership_type: '', legal_description: '',
  photos: [], documents: [],
})

export const usePropertyWizardStore = defineStore('propertyWizard', () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBaseUrl
  const currentStep = ref(1)
  const completedSteps = ref<Set<number>>(new Set())
  const formData = ref<WizardFormData>(defaultForm())
  const stepErrors = ref<Record<number, Record<string, string>>>({})
  const isSubmitting = ref(false)
  const isDraft = ref(false)
  const editPropertyId = ref<number | null>(null)

  const aiEstimate = ref<{
    value: number
    confidence: number
    method: string
    breakdown: any
    land_value?: number
    building_value?: number
  } | null>(null)

  const trustMetrics = ref<{
    trust_score: number
    total_reviews: number
    avg_error_pct: number
    approved_unchanged: number
    modified_reviews: number
  } | null>(null)

  const progressPercent = computed(() =>
    Math.round((completedSteps.value.size / TOTAL_STEPS) * 100)
  )

  function validateStep(step: number): boolean {
    const errs: Record<string, string> = {}
    const d = formData.value

    if (step === 1) {
      if (!d.address?.trim()) errs.address = 'Address is required'
      if (!d.municipality) errs.municipality = 'Municipality is required'
      if (!d.property_type) errs.property_type = 'Property type is required'
      if (!d.region) errs.region = 'Region is required'
    }
    if (step === 2) {
      if (!d.latitude || !d.longitude) errs.location = 'Place a pin on the map to set the property location'
    }
    if (step === 3) {
      if (!d.area_sqm || d.area_sqm <= 0) errs.area_sqm = 'Land area must be greater than 0'
      if (!d.condition) errs.condition = 'Property condition is required'
    }

    stepErrors.value[step] = errs
    const valid = Object.keys(errs).length === 0
    if (valid) completedSteps.value.add(step)
    return valid
  }

  function nextStep() {
    // Allow advancing through all 7 steps + into the review summary (step 8)
    if (validateStep(currentStep.value) && currentStep.value <= TOTAL_STEPS) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 1) currentStep.value--
  }

  function goToStep(step: number) {
    currentStep.value = step
  }

  function markStepComplete(step: number) {
    completedSteps.value.add(step)
  }

  function saveDraft() {
    const serializable = { ...formData.value, photos: [], documents: [] }
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({ data: serializable, step: currentStep.value, editPropertyId: editPropertyId.value })
    )
    isDraft.value = true
  }

  function loadDraft(): boolean {
    try {
      const raw = localStorage.getItem(DRAFT_KEY)
      if (!raw) return false
      const parsed = JSON.parse(raw)
      formData.value = { ...defaultForm(), ...parsed.data }
      currentStep.value = parsed.step || 1
      editPropertyId.value = parsed.editPropertyId || null
      isDraft.value = true
      return true
    } catch {
      return false
    }
  }

  function loadFromProperty(property: Record<string, any>) {
    formData.value = {
      ...defaultForm(),
      ...property,
      boundaries: property.coordinates || [],
      photos: [],
      documents: [],
    }
    editPropertyId.value = property.id
    // Mark all steps complete when editing
    for (let i = 1; i <= TOTAL_STEPS; i++) completedSteps.value.add(i)
  }

  function clearWizard() {
    formData.value = defaultForm()
    currentStep.value = 1
    completedSteps.value.clear()
    stepErrors.value = {}
    isDraft.value = false
    aiEstimate.value = null
    editPropertyId.value = null
    localStorage.removeItem(DRAFT_KEY)
  }

  async function calculateAIValuation() {
    const token = getAccessToken()
    const d = formData.value

    const conditionMap: Record<string, number> = { excellent: 1, good: 2, fair: 3, poor: 4 }

    const res = await fetch(`${apiBase}/api/v1/valuations/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        property_type: d.property_type,
        municipality: d.municipality,
        area_sqm: d.area_sqm,
        condition_grade: conditionMap[d.condition] || 2,
        neighborhood_quality: 2,
      }),
    })

    if (res.ok) {
      const json = await res.json()
      aiEstimate.value = {
        value: json.market_value ?? json.estimated_value ?? 0,
        confidence: json.confidence ?? 0.75,
        method: d.valuation_method || 'comparative',
        breakdown: json,
        land_value: json.land_value,
        building_value: json.building_value,
      }
    }
  }

  async function fetchTrustMetrics() {
    try {
      const token = getAccessToken()
      const res = await fetch(`${apiBase}/api/v1/valuation-feedback/metrics`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (res.ok) trustMetrics.value = await res.json()
    } catch {
      // Non-critical; silently fail
    }
  }

  async function submitProperty(): Promise<{ id: number; property_ref: string } | null> {
    const token = getAccessToken()
    isSubmitting.value = true

    try {
      const d = formData.value

      // If user only dropped a pin (no polygon drawn), derive a point polygon
      // so the backend coordinates field is never empty.
      let resolvedCoordinates: number[][] = d.boundaries
      if (resolvedCoordinates.length === 0 && d.latitude !== null && d.longitude !== null) {
        const DELTA = 0.0002 // ~22 m bounding box at equator
        const lat = d.latitude!, lng = d.longitude!
        resolvedCoordinates = [
          [lng - DELTA, lat - DELTA],
          [lng + DELTA, lat - DELTA],
          [lng + DELTA, lat + DELTA],
          [lng - DELTA, lat + DELTA],
          [lng - DELTA, lat - DELTA], // closed ring
        ]
      }

      const payload = {
        ...d,
        coordinates: resolvedCoordinates,
        ai_estimated_value: aiEstimate.value?.value ?? null,
        ai_confidence_score: aiEstimate.value?.confidence ?? null,
        ai_trust_score_at_time: trustMetrics.value?.trust_score ?? null,
        photos: undefined,
        documents: undefined,
      }

      const url = editPropertyId.value
        ? `${apiBase}/api/v1/properties/${editPropertyId.value}`
        : `${apiBase}/api/v1/properties`
      const method = editPropertyId.value ? 'PUT' : 'POST'

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        const json = await res.json()
        localStorage.removeItem(DRAFT_KEY)
        return json.data || json
      }
      return null
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    currentStep, completedSteps, formData, stepErrors,
    isSubmitting, isDraft, editPropertyId,
    aiEstimate, trustMetrics, progressPercent,
    validateStep, nextStep, prevStep, goToStep, markStepComplete,
    saveDraft, loadDraft, loadFromProperty, clearWizard,
    calculateAIValuation, fetchTrustMetrics, submitProperty,
  }
})
