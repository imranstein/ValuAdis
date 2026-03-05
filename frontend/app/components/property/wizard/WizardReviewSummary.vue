<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-clipboard text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Review & Submit</h2>
        <p class="step-subtitle">Confirm all details before submitting</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Property Ref Banner -->
      <div v-if="form.property_ref" class="ref-banner">
        <i class="pi pi-hashtag text-emerald-600" />
        <span>Property Reference: <strong class="font-mono">{{ form.property_ref }}</strong></span>
        <Tag v-if="store.isDraft" value="Draft" severity="warning" class="ml-auto" />
      </div>

      <!-- Basic Info Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-home text-emerald-600" /> Basic Information</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(1)" />
        </div>
        <div class="data-grid">
          <div class="data-item"><span>Type</span><strong>{{ ucfirst(form.property_type) }} {{ form.property_subtype ? `/ ${ucfirst(form.property_subtype)}` : '' }}</strong></div>
          <div class="data-item"><span>Address</span><strong>{{ form.address }}</strong></div>
          <div class="data-item"><span>Region</span><strong>{{ form.region || '—' }}</strong></div>
          <div class="data-item"><span>Municipality</span><strong>{{ form.municipality }}</strong></div>
          <div class="data-item" v-if="form.subcity"><span>Subcity</span><strong>{{ form.subcity }}</strong></div>
          <div class="data-item" v-if="form.woreda"><span>Woreda</span><strong>{{ form.woreda }}</strong></div>
          <div class="data-item" v-if="form.parcel_number"><span>Parcel #</span><strong>{{ form.parcel_number }}</strong></div>
          <div class="data-item" v-if="form.title_deed_number"><span>Title Deed</span><strong>{{ form.title_deed_number }}</strong></div>
        </div>
      </div>

      <!-- Location Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-map-marker text-blue-600" /> Location</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(2)" />
        </div>
        <div class="data-grid">
          <div class="data-item" v-if="form.latitude">
            <span>Coordinates</span>
            <strong class="font-mono">{{ form.latitude?.toFixed(5) }}, {{ form.longitude?.toFixed(5) }}</strong>
          </div>
          <div class="data-item" v-else>
            <span>Location</span><strong class="text-amber-600">Not pinned on map</strong>
          </div>
          <div class="data-item" v-if="form.boundaries.length > 0">
            <span>Boundary</span><strong>{{ form.boundaries.length }} coordinate polygon</strong>
          </div>
        </div>
      </div>

      <!-- Physical Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-th-large text-slate-600" /> Physical Details</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(3)" />
        </div>
        <div class="data-grid">
          <div class="data-item"><span>Land Area</span><strong>{{ form.area_sqm?.toLocaleString() }} m²</strong></div>
          <div class="data-item" v-if="form.building_area_sqm"><span>Building Area</span><strong>{{ form.building_area_sqm?.toLocaleString() }} m²</strong></div>
          <div class="data-item" v-if="form.number_of_floors"><span>Floors</span><strong>{{ form.number_of_floors }}</strong></div>
          <div class="data-item" v-if="form.number_of_bedrooms"><span>Bedrooms</span><strong>{{ form.number_of_bedrooms }}</strong></div>
          <div class="data-item" v-if="form.year_built"><span>Year Built</span><strong>{{ form.year_built }}</strong></div>
          <div class="data-item" v-if="form.condition"><span>Condition</span><strong>{{ ucfirst(form.condition) }}</strong></div>
          <div class="data-item" v-if="form.construction_material"><span>Construction</span><strong>{{ ucfirst(form.construction_material) }}</strong></div>
        </div>
      </div>

      <!-- Amenities Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-star text-purple-600" /> Amenities & Utilities</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(4)" />
        </div>
        <div class="data-grid">
          <div class="data-item">
            <span>Amenities</span>
            <strong>{{ amenityList || 'None selected' }}</strong>
          </div>
          <div class="data-item">
            <span>Utilities</span>
            <strong>{{ utilityList || 'None selected' }}</strong>
          </div>
        </div>
      </div>

      <!-- Valuation Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-calculator text-amber-600" /> Valuation</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(5)" />
        </div>
        <div class="data-grid">
          <div class="data-item" v-if="form.market_value">
            <span>Market Value</span>
            <strong class="text-lg text-emerald-700">{{ formatETB(form.market_value) }}</strong>
          </div>
          <div class="data-item" v-if="store.aiEstimate">
            <span>AI Estimate</span>
            <strong>{{ formatETB(store.aiEstimate.value) }}</strong>
          </div>
          <div class="data-item" v-if="form.valuation_method">
            <span>Method</span>
            <strong>{{ ucfirst(form.valuation_method) }}</strong>
          </div>
          <div class="data-item" v-if="form.valuer_name">
            <span>Valuer</span>
            <strong>{{ form.valuer_name }}</strong>
          </div>
        </div>
        <div v-if="store.aiEstimate" class="ai-summary">
          <ValuationTrustBadge
            :score="store.trustMetrics?.trust_score ?? null"
            :total-reviews="store.trustMetrics?.total_reviews"
          />
        </div>
      </div>

      <!-- Ownership Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-id-card text-indigo-600" /> Ownership</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(6)" />
        </div>
        <div class="data-grid">
          <div class="data-item" v-if="form.owner_name"><span>Owner</span><strong>{{ form.owner_name }}</strong></div>
          <div class="data-item" v-if="form.owner_phone"><span>Phone</span><strong>{{ form.owner_phone }}</strong></div>
          <div class="data-item" v-if="form.ownership_type"><span>Ownership</span><strong>{{ ucfirst(form.ownership_type) }}</strong></div>
          <div class="data-item" v-if="form.owner_id_type"><span>ID Type</span><strong>{{ ucfirst(form.owner_id_type.replace('_', ' ')) }}</strong></div>
        </div>
      </div>

      <!-- Documents Card -->
      <div class="review-card">
        <div class="card-header">
          <div class="card-title"><i class="pi pi-folder-open text-teal-600" /> Documents & Photos</div>
          <Button label="Edit" severity="secondary" size="small" text icon="pi pi-pencil" @click="store.goToStep(7)" />
        </div>
        <div class="data-grid">
          <div class="data-item"><span>Photos</span><strong>{{ form.photos.length }} uploaded</strong></div>
          <div class="data-item"><span>Documents</span><strong>{{ form.documents.length }} uploaded</strong></div>
        </div>
      </div>

      <!-- Submit Actions -->
      <div class="submit-section">
        <div v-if="submitError" class="error-banner">
          <i class="pi pi-exclamation-circle" /> {{ submitError }}
        </div>
        <div v-if="submitSuccess" class="success-banner">
          <i class="pi pi-check-circle" />
          Property submitted! Reference: <strong class="font-mono">{{ submittedRef }}</strong>
          <Button label="View Property" severity="success" size="small" class="ml-3" @click="goToProperty" />
        </div>

        <div class="action-row">
          <Button
            label="Save as Draft"
            icon="pi pi-save"
            severity="secondary"
            outlined
            :disabled="store.isSubmitting"
            @click="saveDraft"
          />
          <Button
            :label="store.editPropertyId ? 'Update Property' : 'Submit Property'"
            :icon="store.isSubmitting ? 'pi pi-spin pi-spinner' : 'pi pi-check'"
            severity="success"
            :loading="store.isSubmitting"
            :disabled="!canSubmit"
            @click="submit"
          />
        </div>
        <p class="submit-note">
          Required: property type, address, municipality, region, area, condition.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePropertyWizardStore } from '~/stores/propertyWizard'
import ValuationTrustBadge from '~/components/property/ValuationTrustBadge.vue'

const store = usePropertyWizardStore()
const form = store.formData
const router = useRouter()

const submitError = ref('')
const submitSuccess = ref(false)
const submittedId = ref<number | null>(null)
const submittedRef = ref('')

const canSubmit = computed(() => {
  const d = form
  return !!(d.address && d.municipality && d.property_type && d.region && d.area_sqm && d.condition)
})

const amenityList = computed(() =>
  Object.entries(form.amenities)
    .filter(([, v]) => v)
    .map(([k]) => ucfirst(k.replace('_', ' ')))
    .join(', ')
)

const utilityList = computed(() =>
  Object.entries(form.utilities)
    .filter(([, v]) => v)
    .map(([k]) => ucfirst(k.replace('_', ' ')))
    .join(', ')
)

function ucfirst(s: string): string {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function formatETB(value: number): string {
  return new Intl.NumberFormat('en-ET', { style: 'currency', currency: 'ETB', maximumFractionDigits: 0 }).format(value)
}

function saveDraft() {
  store.saveDraft()
}

async function submit() {
  submitError.value = ''
  const result = await store.submitProperty()
  if (result) {
    submitSuccess.value = true
    submittedId.value = result.id
    submittedRef.value = result.property_ref || String(result.id)
    store.clearWizard()
  } else {
    submitError.value = 'Submission failed. Please check all required fields and try again.'
  }
}

function goToProperty() {
  if (submittedId.value) router.push(`/properties/${submittedId.value}`)
}
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}
.step-icon-wrap {
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.2); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.2rem; }
.step-subtitle { font-size: 0.875rem; opacity: 0.85; margin: 0; }

.step-body { padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.25rem; }

.ref-banner {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px;
  font-size: 0.875rem; color: #166534;
}

.review-card {
  border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;
}
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 1.25rem;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.card-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.9rem; font-weight: 700; color: #334155;
}
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0; padding: 0.25rem 0;
}
.data-item {
  display: flex; flex-direction: column; gap: 0.2rem;
  padding: 0.6rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}
.data-item:last-child { border-bottom: none; }
.data-item span { font-size: 0.72rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; }
.data-item strong { font-size: 0.875rem; color: #1e293b; }
.ai-summary { padding: 0.75rem 1.25rem; border-top: 1px solid #f1f5f9; }

.submit-section { display: flex; flex-direction: column; gap: 0.75rem; }
.action-row { display: flex; align-items: center; justify-content: flex-end; gap: 0.75rem; flex-wrap: wrap; }
.submit-note { font-size: 0.75rem; color: #94a3b8; text-align: right; margin: 0; }

.error-banner {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
  color: #dc2626; font-size: 0.875rem;
}
.success-banner {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;
  color: #166534; font-size: 0.875rem; flex-wrap: wrap;
}

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .data-grid { grid-template-columns: 1fr; }
  .action-row { flex-direction: column; align-items: stretch; }
}
</style>
