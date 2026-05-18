<template>
  <div class="page-shell compliance-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Regulatory reporting</p>
        <h2 class="page-title">Compliance report.</h2>
        <p class="page-subtitle">
          Track Ethiopian Proclamation 1365/2025 taxable-value compliance from live valuation records.
        </p>
      </div>
      <div class="page-actions">
        <NuxtLink to="/reports" class="btn-secondary">
          <i class="pi pi-file-export" aria-hidden="true"></i>
          Export center
        </NuxtLink>
        <button class="btn-secondary" type="button" @click="loadCompliance">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
      </div>
    </section>

    <div v-if="errorMessage" class="state-panel error-state" role="alert">
      <strong>Compliance report unavailable</strong>
      <span>{{ errorMessage }}</span>
    </div>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="profile-detail-grid">
      <article class="table-panel">
        <div class="panel-head table-head">
          <div>
            <h3 class="panel-title">Municipality compliance</h3>
            <p class="panel-subtitle">Grouped by valuation municipality from the backend report.</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Municipality</th>
                <th>Total</th>
                <th>Compliant</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="4">Loading municipality compliance...</td>
              </tr>
              <tr v-else-if="municipalityRows.length === 0">
                <td colspan="4">No municipality compliance records are available yet.</td>
              </tr>
              <tr v-for="row in municipalityRows" v-else :key="row.name">
                <td>{{ row.name }}</td>
                <td class="num">{{ row.total }}</td>
                <td class="num">{{ row.compliant }}</td>
                <td>
                  <span class="status-pill" :class="rateClass(row.rate)">{{ formatPercent(row.rate) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="table-panel">
        <div class="panel-head table-head">
          <div>
            <h3 class="panel-title">Property-type compliance</h3>
            <p class="panel-subtitle">Taxable-value compliance by asset class.</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Property type</th>
                <th>Total</th>
                <th>Compliant</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="4">Loading property-type compliance...</td>
              </tr>
              <tr v-else-if="propertyTypeRows.length === 0">
                <td colspan="4">No property-type compliance records are available yet.</td>
              </tr>
              <tr v-for="row in propertyTypeRows" v-else :key="row.name">
                <td>{{ row.name }}</td>
                <td class="num">{{ row.total }}</td>
                <td class="num">{{ row.compliant }}</td>
                <td>
                  <span class="status-pill" :class="rateClass(row.rate)">{{ formatPercent(row.rate) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Compliance exceptions</h3>
          <p class="panel-subtitle">Valuations where taxable value does not match the 25% rule.</p>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Valuation</th>
              <th>Municipality</th>
              <th>Market value</th>
              <th>Taxable value</th>
              <th>Expected</th>
              <th>Deviation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6">Loading compliance exceptions...</td>
            </tr>
            <tr v-else-if="violations.length === 0">
              <td colspan="6">No taxable-value exceptions are reported.</td>
            </tr>
            <tr v-for="violation in violations" v-else :key="violation.valuation_id">
              <td>
                <strong>#{{ violation.valuation_id }}</strong>
                <span class="record-id">{{ violation.property_type }}</span>
              </td>
              <td>{{ violation.municipality }}</td>
              <td class="num">{{ formatCurrency(violation.market_value) }}</td>
              <td class="num">{{ formatCurrency(violation.taxable_value) }}</td>
              <td class="num">{{ formatCurrency(violation.expected_taxable) }}</td>
              <td class="num">{{ formatCurrency(violation.deviation) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const loading = ref(true)
const errorMessage = ref('')
const report = ref<any>(null)

const rule = computed(() => report.value?.proclamation_1365_2025_compliance || {})
const violations = computed(() => Array.isArray(report.value?.compliance_details) ? report.value.compliance_details : [])

const metrics = computed(() => [
  { label: 'Compliance rate', value: formatPercent(rule.value.compliance_rate || 0), note: rule.value.rule || '25% taxable value rule' },
  { label: 'Analyzed valuations', value: String(report.value?.total_valuations_analyzed || 0), note: 'Backend valuation records' },
  { label: 'Compliant', value: String(rule.value.compliant_valuations || 0), note: 'Within tolerance' },
  { label: 'Exceptions', value: String(rule.value.non_compliant_valuations || 0), note: 'Need review' },
])

const municipalityRows = computed(() => normalizeGroupedRows(report.value?.municipality_analysis))
const propertyTypeRows = computed(() => normalizeGroupedRows(report.value?.property_type_analysis))

onMounted(loadCompliance)

async function loadCompliance() {
  loading.value = true
  errorMessage.value = ''

  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}/api/v1/audit/compliance`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!response.ok) throw new Error(`Compliance report request failed with ${response.status}`)
    const payload = await response.json()
    report.value = payload.compliance_report || null
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load compliance report.'
    report.value = null
  } finally {
    loading.value = false
  }
}

function normalizeGroupedRows(grouped: Record<string, any> | undefined) {
  if (!grouped) return []
  return Object.entries(grouped).map(([name, value]) => ({
    name,
    total: Number(value.total || 0),
    compliant: Number(value.compliant || 0),
    rate: Number(value.compliance_rate || 0),
  })).sort((a, b) => b.total - a.total)
}

function rateClass(rate: number) {
  if (rate >= 95) return 'good'
  if (rate >= 80) return 'warn'
  return 'bad'
}

function formatPercent(value: number) {
  return `${Number(value || 0).toFixed(1)}%`
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}
</script>

<style scoped>
.profile-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.table-panel {
  min-width: 0;
}

@media (max-width: 980px) {
  .profile-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
