<template>
  <div class="page-shell reports-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Report desk</p>
        <h2 class="page-title">Export verified valuation evidence.</h2>
        <p class="page-subtitle">
          Generate compliance, valuation, certificate, and property registry exports from backend records.
        </p>
      </div>
      <div class="page-actions">
        <NuxtLink to="/reports/compliance" class="btn-secondary">
          <i class="pi pi-shield" aria-hidden="true"></i>
          Compliance
        </NuxtLink>
        <button class="btn-primary" type="button" :disabled="!canDownload || downloading" @click="downloadReport">
          <i class="pi pi-download" aria-hidden="true"></i>
          {{ downloading ? 'Generating' : 'Download' }}
        </button>
      </div>
    </section>

    <section class="metric-grid" aria-label="Report metrics">
      <article class="metric-card">
        <p class="metric-label">Total properties</p>
        <p class="metric-value">{{ dashboard.properties }}</p>
        <p class="metric-note">Backend registry records</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Total valuations</p>
        <p class="metric-value">{{ dashboard.valuations }}</p>
        <p class="metric-note">Exportable valuation records</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Taxable value</p>
        <p class="metric-value">{{ formatCurrency(dashboard.taxableValue) }}</p>
        <p class="metric-note">Current dashboard period</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Compliance</p>
        <p class="metric-value">{{ dashboard.complianceRate }}%</p>
        <p class="metric-note">Backend compliance rate</p>
      </article>
    </section>

    <section class="report-grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Report parameters</h3>
            <p class="panel-subtitle">Choose the export surface and scope before generating the file.</p>
          </div>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>Report type</span>
            <select v-model="form.reportType" data-testid="report-type-select">
              <option value="valuation_certificate">Valuation certificate PDF</option>
              <option value="valuations_csv">Valuations CSV</option>
              <option value="properties_csv">Properties CSV</option>
              <option value="audit_compliance">Compliance audit JSON</option>
            </select>
          </label>

          <label class="field">
            <span>Municipality</span>
            <select v-model="form.municipality" data-testid="report-municipality-select">
              <option value="">All municipalities</option>
              <option>Addis Ababa</option>
              <option>Dire Dawa</option>
              <option>Bahir Dar</option>
              <option>Hawassa</option>
              <option>Mekelle</option>
            </select>
          </label>

          <label class="field">
            <span>Start date</span>
            <input v-model="form.startDate" data-testid="report-start-date" type="date" />
          </label>

          <label class="field">
            <span>End date</span>
            <input v-model="form.endDate" data-testid="report-end-date" type="date" />
          </label>

          <label v-if="form.reportType === 'valuation_certificate'" class="field full">
            <span>Approved valuation ID</span>
            <input v-model="form.valuationId" data-testid="report-valuation-id" inputmode="numeric" />
          </label>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Download summary</h3>
            <p class="panel-subtitle">Exports use selected filters where the backend surface supports them.</p>
          </div>
          <span class="status-pill" :class="canDownload ? 'good' : 'warn'">{{ canDownload ? 'Ready' : 'Needs input' }}</span>
        </div>

        <dl class="summary-list">
          <div>
            <dt>Type</dt>
            <dd>{{ selectedReportLabel }}</dd>
          </div>
          <div>
            <dt>Period</dt>
            <dd>{{ form.startDate }} to {{ form.endDate }}</dd>
          </div>
          <div>
            <dt>Municipality</dt>
            <dd>{{ form.municipality || 'All municipalities' }}</dd>
          </div>
          <div>
            <dt>Endpoint</dt>
            <dd>{{ downloadEndpoint }}</dd>
          </div>
        </dl>

        <p class="status" data-testid="report-download-status">{{ downloadStatus }}</p>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const form = reactive({
  reportType: 'valuations_csv',
  municipality: '',
  startDate: '2026-01-01',
  endDate: '2026-03-31',
  valuationId: '',
})

const downloading = ref(false)
const downloadStatus = ref('Ready to generate')
const dashboard = ref({
  properties: 0,
  valuations: 0,
  taxableValue: 0,
  complianceRate: 0,
})

const reportLabels: Record<string, string> = {
  valuation_certificate: 'Valuation certificate PDF',
  valuations_csv: 'Valuations CSV',
  properties_csv: 'Properties CSV',
  audit_compliance: 'Compliance audit JSON',
}

const selectedReportLabel = computed(() => reportLabels[form.reportType])

const downloadEndpoint = computed(() => {
  const params = new URLSearchParams()
  if (form.startDate) params.set('start_date', form.startDate)
  if (form.endDate) params.set('end_date', form.endDate)
  if (form.municipality) params.set('municipality', form.municipality)

  if (form.reportType === 'valuation_certificate') {
    return `/api/v1/valuations/${form.valuationId}/certificate`
  }
  if (form.reportType === 'valuations_csv') {
    return '/api/v1/valuations/export?format=csv'
  }
  if (form.reportType === 'properties_csv') {
    return '/api/v1/properties/export?format=csv'
  }
  return `/api/v1/audit/export/compliance?format=json&${params.toString()}`
})

const canDownload = computed(() => {
  if (!form.startDate || !form.endDate) return false
  if (form.reportType === 'valuation_certificate') return Boolean(form.valuationId.trim())
  return true
})

onMounted(loadDashboard)

async function loadDashboard() {
  const token = getAccessToken()
  const response = await fetch(`${apiBase}/api/v1/analytics/dashboard?period=month`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) return
  const data = await response.json()
  dashboard.value = {
    properties: data.properties?.total ?? 0,
    valuations: data.valuations?.total ?? 0,
    taxableValue: data.financials?.total_taxable_value ?? 0,
    complianceRate: Math.round(data.compliance?.compliance_rate ?? 0),
  }
}

async function downloadReport() {
  if (!canDownload.value) return

  downloading.value = true
  downloadStatus.value = 'Generating report'
  try {
    const token = getAccessToken()
    const response = await fetch(`${apiBase}${downloadEndpoint.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) throw new Error('Report generation failed')

    const blob = await response.blob()
    const filename = getFilename(response.headers.get('Content-Disposition'))
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
    downloadStatus.value = `${filename} downloaded`
  } catch (error: any) {
    downloadStatus.value = error.message || 'Report generation failed'
  } finally {
    downloading.value = false
  }
}

function getFilename(disposition: string | null) {
  const match = disposition?.match(/filename="?([^"]+)"?/)
  if (match?.[1]) return match[1]
  if (form.reportType === 'valuation_certificate') return `ValuAdis_Certificate_${form.valuationId}.pdf`
  return `${form.reportType}_${form.startDate}_${form.endDate}.csv`
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

useHead({
  title: 'Reports - ValuAdis',
  meta: [{ name: 'description', content: 'Generate ValuAdis valuation and compliance reports.' }],
})
</script>

<style scoped>
.report-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.field {
  display: grid;
  gap: 7px;
}

.field span {
  color: var(--muted);
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.field input,
.field select {
  min-height: 40px;
  width: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink);
  padding: 0 10px;
}

.field.full {
  grid-column: 1 / -1;
}

.summary-list {
  display: grid;
  gap: 10px;
  margin: 0;
}

.summary-list div {
  display: grid;
  grid-template-columns: 7.5rem 1fr;
  gap: 12px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 10px;
}

dt {
  color: var(--muted);
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

dd {
  margin: 0;
  color: var(--ink-soft);
  font-size: 13px;
  overflow-wrap: anywhere;
}

.status {
  min-height: 1.3rem;
  margin: 14px 0 0;
  color: var(--green);
  font-size: 13px;
  font-weight: 750;
}

@media (max-width: 980px) {
  .report-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
