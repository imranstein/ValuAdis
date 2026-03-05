<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-calculator text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Valuation Information</h2>
        <p class="step-subtitle">Set property values and get an AI-powered estimate</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Valuation Method -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-chart-bar text-amber-600" /> Valuation Method
        </h3>
        <div class="method-cards">
          <button
            v-for="m in methods"
            :key="m.value"
            class="method-card"
            :class="{ selected: form.valuation_method === m.value }"
            type="button"
            @click="form.valuation_method = m.value"
          >
            <i :class="m.icon" class="method-icon" />
            <strong>{{ m.label }}</strong>
            <span class="method-desc">{{ m.desc }}</span>
          </button>
        </div>
      </section>

      <!-- Values -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-dollar text-amber-600" /> Property Values (ETB)
        </h3>
        <div class="form-grid">
          <div class="field">
            <label>Land Value (ETB)</label>
            <InputNumber
              v-model="form.land_value"
              :min="0"
              :use-grouping="true"
              placeholder="e.g. 500,000"
              class="w-full"
              @update:model-value="updateTotal"
            />
          </div>
          <div class="field">
            <label>Building Value (ETB)</label>
            <InputNumber
              v-model="form.building_value"
              :min="0"
              :use-grouping="true"
              placeholder="e.g. 1,200,000"
              class="w-full"
              @update:model-value="updateTotal"
            />
          </div>
          <div class="field full-width">
            <label>Total Market Value (ETB) <span class="auto-tag">auto-calculated</span></label>
            <InputNumber
              v-model="form.market_value"
              :min="0"
              :use-grouping="true"
              placeholder="Sum of land + building, or manual entry"
              class="w-full"
            />
          </div>
        </div>
      </section>

      <!-- AI Estimate -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-sparkles text-amber-600" /> AI Valuation Estimate
        </h3>
        <div class="ai-section">
          <Button
            label="Calculate AI Estimate"
            icon="pi pi-sparkles"
            :loading="calculating"
            :disabled="!canCalculate"
            severity="warning"
            @click="runCalculation"
          />
          <span v-if="!canCalculate" class="ai-hint">
            Complete Steps 1–3 first (property type, municipality, area, condition)
          </span>

          <div v-if="store.aiEstimate" class="ai-result">
            <div class="ai-result-header">
              <div class="ai-value">
                <span class="ai-label">AI Estimated Value</span>
                <span class="ai-amount">{{ formatETB(store.aiEstimate.value) }}</span>
              </div>
              <ValuationTrustBadge
                :score="store.trustMetrics?.trust_score ?? null"
                :total-reviews="store.trustMetrics?.total_reviews"
              />
            </div>

            <div class="confidence-row">
              <span class="conf-label">Confidence:</span>
              <div class="conf-bar-track">
                <div
                  class="conf-bar-fill"
                  :style="{ width: (store.aiEstimate.confidence * 100).toFixed(0) + '%' }"
                  :class="confidenceClass"
                />
              </div>
              <span class="conf-pct">{{ (store.aiEstimate.confidence * 100).toFixed(0) }}%</span>
            </div>

            <div class="breakdown-grid" v-if="store.aiEstimate.breakdown">
              <div class="breakdown-item" v-if="store.aiEstimate.land_value">
                <span>Land component</span>
                <strong>{{ formatETB(store.aiEstimate.land_value) }}</strong>
              </div>
              <div class="breakdown-item" v-if="store.aiEstimate.building_value">
                <span>Building component</span>
                <strong>{{ formatETB(store.aiEstimate.building_value) }}</strong>
              </div>
              <div class="breakdown-item">
                <span>Method</span>
                <strong>{{ store.aiEstimate.method || 'Comparative' }}</strong>
              </div>
            </div>

            <Button
              label="Use AI Value"
              severity="secondary"
              size="small"
              icon="pi pi-check"
              class="mt-2"
              @click="useAIValue"
            />
          </div>
        </div>
      </section>

      <!-- Valuer Details -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-user text-amber-600" /> Valuer Details
        </h3>
        <div class="form-grid">
          <div class="field">
            <label>Valuation Date</label>
            <Calendar
              v-model="valuationDateObj"
              dateFormat="yy-mm-dd"
              placeholder="Select date"
              class="w-full"
              showIcon
              @date-select="onDateSelect"
            />
          </div>
          <div class="field">
            <label>Valuer Name</label>
            <InputText v-model="form.valuer_name" placeholder="Full name" class="w-full" />
          </div>
          <div class="field">
            <label>License Number</label>
            <InputText v-model="form.valuer_license_number" placeholder="e.g. ETH-VAL-001" class="w-full" />
          </div>
          <div class="field">
            <label>Valuer Phone</label>
            <InputText v-model="form.valuer_phone" placeholder="+251 9X XXX XXXX" class="w-full" />
          </div>
        </div>
      </section>

      <!-- Comparable Properties -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-list text-amber-600" /> Comparable Properties
        </h3>
        <div
          v-for="(comp, i) in form.comparable_properties"
          :key="i"
          class="comparable-row"
        >
          <InputText
            v-model="comp.address"
            placeholder="Address / Description"
            class="comp-addr"
          />
          <InputNumber
            v-model="comp.value"
            :use-grouping="true"
            placeholder="Value (ETB)"
            class="comp-val"
          />
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click="removeComp(i)"
          />
        </div>
        <Button
          label="Add Comparable"
          icon="pi pi-plus"
          severity="secondary"
          size="small"
          outlined
          @click="addComp"
        />
      </section>

      <!-- Notes -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-pencil text-amber-600" /> Valuation Notes
        </h3>
        <Textarea
          v-model="form.valuation_notes"
          :rows="4"
          placeholder="Any relevant observations, assumptions, or methodology notes..."
          class="w-full"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'
import ValuationTrustBadge from '~/components/property/ValuationTrustBadge.vue'

const store = usePropertyWizardStore()
const form = store.formData
const calculating = ref(false)

const valuationDateObj = ref<Date | null>(
  form.valuation_date ? new Date(form.valuation_date) : null
)

function onDateSelect(date: Date) {
  form.valuation_date = date.toISOString().split('T')[0]
}

const canCalculate = computed(() =>
  !!(form.property_type && form.municipality && form.area_sqm && form.area_sqm > 0 && form.condition)
)

const confidenceClass = computed(() => {
  const c = (store.aiEstimate?.confidence ?? 0) * 100
  if (c >= 75) return 'conf-high'
  if (c >= 50) return 'conf-moderate'
  return 'conf-low'
})

async function runCalculation() {
  calculating.value = true
  try {
    await store.calculateAIValuation()
  } finally {
    calculating.value = false
  }
}

function useAIValue() {
  if (store.aiEstimate) {
    form.market_value = store.aiEstimate.value
    if (store.aiEstimate.land_value) form.land_value = store.aiEstimate.land_value
    if (store.aiEstimate.building_value) form.building_value = store.aiEstimate.building_value
  }
}

function updateTotal() {
  const land = form.land_value ?? 0
  const building = form.building_value ?? 0
  if (land + building > 0) {
    form.market_value = land + building
  }
}

function addComp() {
  form.comparable_properties.push({ address: '', value: null })
}

function removeComp(i: number) {
  form.comparable_properties.splice(i, 1)
}

function formatETB(value: number): string {
  return new Intl.NumberFormat('en-ET', { style: 'currency', currency: 'ETB', maximumFractionDigits: 0 }).format(value)
}

const methods = [
  { value: 'comparative', label: 'Comparative', icon: 'pi pi-chart-line', desc: 'Based on similar sold properties' },
  { value: 'cost', label: 'Cost', icon: 'pi pi-home', desc: 'Land + depreciated building cost' },
  { value: 'income', label: 'Income', icon: 'pi pi-money-bill', desc: 'Capitalised rental income' },
]

onMounted(() => {
  store.fetchTrustMetrics()
})
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
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

.step-body { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }

.form-section { display: flex; flex-direction: column; gap: 1rem; }
.section-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.95rem; font-weight: 600; color: #334155;
  padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field.full-width { grid-column: 1 / -1; }
.field label { font-size: 0.8rem; font-weight: 600; color: #475569; }

.auto-tag {
  font-size: 0.7rem; font-weight: 400; color: #94a3b8;
  background: #f1f5f9; padding: 0.1rem 0.4rem; border-radius: 4px;
  margin-left: 0.4rem;
}

/* Method cards */
.method-cards { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.method-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 1rem 1.25rem; min-width: 140px;
  border: 2px solid #e2e8f0; border-radius: 12px;
  background: white; cursor: pointer; transition: all 0.2s;
  font-size: 0.8rem; color: #64748b; text-align: center;
}
.method-card:hover { border-color: #d97706; color: #d97706; }
.method-card.selected { border-color: #d97706; background: #fffbeb; color: #92400e; font-weight: 600; }
.method-icon { font-size: 1.5rem; }
.method-desc { font-size: 0.72rem; color: #94a3b8; font-weight: 400; }

/* AI section */
.ai-section { display: flex; flex-direction: column; gap: 1rem; }
.ai-hint { font-size: 0.8rem; color: #94a3b8; }

.ai-result {
  padding: 1.25rem;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1.5px solid #fcd34d; border-radius: 12px;
  display: flex; flex-direction: column; gap: 0.85rem;
}
.ai-result-header { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; }
.ai-value { display: flex; flex-direction: column; gap: 0.2rem; }
.ai-label { font-size: 0.75rem; color: #92400e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.ai-amount { font-size: 1.6rem; font-weight: 800; color: #78350f; }

.confidence-row { display: flex; align-items: center; gap: 0.6rem; }
.conf-label { font-size: 0.8rem; color: #92400e; font-weight: 600; white-space: nowrap; }
.conf-bar-track { flex: 1; height: 8px; background: #fde68a; border-radius: 4px; overflow: hidden; }
.conf-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.conf-high { background: #059669; }
.conf-moderate { background: #d97706; }
.conf-low { background: #dc2626; }
.conf-pct { font-size: 0.8rem; font-weight: 700; color: #92400e; min-width: 32px; text-align: right; }

.breakdown-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.5rem; }
.breakdown-item {
  display: flex; justify-content: space-between;
  padding: 0.4rem 0.6rem;
  background: rgba(255,255,255,0.6); border-radius: 6px;
  font-size: 0.8rem; color: #78350f;
}

/* Comparable rows */
.comparable-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.comp-addr { flex: 2; }
.comp-val { flex: 1; }

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .form-grid { grid-template-columns: 1fr; }
  .method-cards { gap: 0.5rem; }
  .method-card { min-width: 100px; padding: 0.75rem; }
  .ai-result-header { flex-direction: column; }
  .ai-amount { font-size: 1.25rem; }
}
</style>
