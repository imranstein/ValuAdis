<template>
  <div class="review-panel">
    <div class="panel-header">
      <div class="header-icon-wrap">
        <i class="pi pi-shield text-2xl text-white" />
      </div>
      <div>
        <h3 class="panel-title">Valuation Review</h3>
        <p class="panel-subtitle">Reviewer approval & AI trust feedback</p>
      </div>
    </div>

    <div class="panel-body">
      <!-- AI Estimate Display -->
      <div v-if="aiEstimate" class="estimate-display">
        <div class="estimate-value">
          <span class="estimate-label">AI Estimated Value</span>
          <span class="estimate-amount">{{ formatETB(aiEstimate) }}</span>
        </div>
        <ValuationTrustBadge
          :score="trustScore"
          :total-reviews="totalReviews"
        />
      </div>
      <div v-else class="no-estimate">
        <i class="pi pi-info-circle text-slate-400" />
        <span>No AI estimate available for this property.</span>
      </div>

      <!-- Submitted State -->
      <div v-if="submitted" class="submitted-banner">
        <i class="pi pi-check-circle text-2xl" />
        <div>
          <strong>Review submitted!</strong>
          <p>New AI trust score: <strong class="font-mono">{{ newTrustScore?.toFixed(1) }}%</strong></p>
          <p v-if="deltaInfo" class="delta-info">{{ deltaInfo }}</p>
        </div>
      </div>

      <!-- Review Form (hidden after submit) -->
      <template v-else-if="aiEstimate">
        <!-- Mode Toggle -->
        <div class="mode-toggle">
          <button
            class="toggle-btn"
            :class="{ active: mode === 'approve' }"
            @click="mode = 'approve'"
          >
            <i class="pi pi-check-circle" />
            Approve As-Is
          </button>
          <button
            class="toggle-btn"
            :class="{ active: mode === 'modify' }"
            @click="mode = 'modify'"
          >
            <i class="pi pi-pencil" />
            Modify & Approve
          </button>
        </div>

        <!-- Approve mode: just a confirm message -->
        <div v-if="mode === 'approve'" class="approve-info">
          <i class="pi pi-info-circle text-emerald-600" />
          <span>Clicking <strong>Approve</strong> confirms the AI estimate is accurate. This increases the AI trust score.</span>
        </div>

        <!-- Modify mode: enter final value + comments -->
        <div v-if="mode === 'modify'" class="modify-form">
          <div class="field">
            <label class="field-label">Final Approved Value (ETB) <span class="req">*</span></label>
            <InputNumber
              v-model="finalValue"
              :min="1"
              :use-grouping="true"
              placeholder="Enter final value"
              class="w-full"
              :class="{ 'p-invalid': showErrors && !finalValue }"
            />
            <small v-if="showErrors && !finalValue" class="p-error">Final value is required</small>
          </div>

          <div class="field">
            <label class="field-label">Review Comments</label>
            <Textarea
              v-model="comments"
              rows="3"
              placeholder="Explain the adjustment — comparable sales, location factors, condition…"
              class="w-full"
            />
          </div>

          <div v-if="aiEstimate && finalValue" class="delta-preview">
            <span>Adjustment from AI estimate:</span>
            <strong :class="deltaClass">{{ deltaPreviewText }}</strong>
          </div>
        </div>

        <!-- Error banner -->
        <div v-if="submitError" class="error-banner">
          <i class="pi pi-exclamation-circle" /> {{ submitError }}
        </div>

        <!-- Submit button -->
        <div class="panel-actions">
          <Button
            :label="mode === 'approve' ? 'Approve Valuation' : 'Submit Modification'"
            :icon="submitting ? 'pi pi-spin pi-spinner' : (mode === 'approve' ? 'pi pi-check' : 'pi pi-send')"
            :severity="mode === 'approve' ? 'success' : 'info'"
            :loading="submitting"
            :disabled="submitting"
            @click="submitReview"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ValuationTrustBadge from '~/components/property/ValuationTrustBadge.vue'

const props = defineProps<{
  propertyId: number
  aiEstimate: number | null
  trustScore: number | null
  totalReviews?: number
}>()

const mode = ref<'approve' | 'modify'>('approve')
const finalValue = ref<number | null>(null)
const comments = ref('')
const submitting = ref(false)
const submitted = ref(false)
const submitError = ref('')
const showErrors = ref(false)
const newTrustScore = ref<number | null>(null)
const deltaInfo = ref('')

const deltaPreview = computed(() => {
  if (!props.aiEstimate || !finalValue.value) return null
  return ((finalValue.value - props.aiEstimate) / props.aiEstimate) * 100
})

const deltaPreviewText = computed(() => {
  const d = deltaPreview.value
  if (d === null) return ''
  const sign = d >= 0 ? '+' : ''
  return `${sign}${d.toFixed(1)}%`
})

const deltaClass = computed(() => {
  const d = deltaPreview.value
  if (d === null) return ''
  if (Math.abs(d) < 5) return 'text-emerald-600'
  if (Math.abs(d) < 15) return 'text-amber-600'
  return 'text-red-600'
})

function formatETB(value: number): string {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 0,
  }).format(value)
}

async function submitReview() {
  submitError.value = ''

  if (mode.value === 'modify' && !finalValue.value) {
    showErrors.value = true
    return
  }

  const approved = mode.value === 'approve'
  const resolvedFinal = approved ? props.aiEstimate! : finalValue.value!

  const token = localStorage.getItem('valuadis_token')
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'

  submitting.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/valuation-feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        property_id: props.propertyId,
        ai_estimate: props.aiEstimate,
        final_value: resolvedFinal,
        approved_without_change: approved,
        comments: comments.value || null,
      }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Server error ${res.status}`)
    }

    const data = await res.json()
    newTrustScore.value = data.trust_score ?? null
    if (!approved && deltaPreview.value !== null) {
      deltaInfo.value = `Adjustment: ${deltaPreviewText.value} from AI estimate`
    }
    submitted.value = true
  } catch (e: any) {
    submitError.value = e.message || 'Submission failed. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-panel {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  color: white;
}

.header-icon-wrap {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.panel-title { font-size: 1.05rem; font-weight: 700; margin: 0 0 0.15rem; }
.panel-subtitle { font-size: 0.8rem; opacity: 0.85; margin: 0; }

.panel-body {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.estimate-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.estimate-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: block;
}

.estimate-amount {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
}

.no-estimate {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.mode-toggle {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}

.toggle-btn:hover { border-color: #6366f1; color: #4f46e5; }
.toggle-btn.active { background: #eef2ff; border-color: #6366f1; color: #4f46e5; font-weight: 600; }

.approve-info {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #374151;
  padding: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
}

.modify-form { display: flex; flex-direction: column; gap: 0.75rem; }

.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: #475569; }
.req { color: #ef4444; }

.delta-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #64748b;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
}

.panel-actions { display: flex; justify-content: flex-end; }

.submitted-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  color: #166534;
}

.submitted-banner p {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
}

.delta-info { color: #64748b; font-size: 0.75rem; }

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
}

@media (max-width: 480px) {
  .panel-body { padding: 1rem; }
  .mode-toggle { flex-direction: column; }
}
</style>
