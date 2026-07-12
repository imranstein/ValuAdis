<template>
  <div class="page-shell import-page">
    <nav class="breadcrumb">
      <span>Home</span>
      <span class="bc-sep">/</span>
      <NuxtLink to="/properties">Properties</NuxtLink>
      <span class="bc-sep">/</span>
      <span class="bc-active">Import</span>
    </nav>

    <div class="page-hd">
      <div>
        <h1 class="page-title">Bulk Property Import</h1>
        <p class="page-desc">Upload CSV property records, review mapped fields, and confirm compliant rows.</p>
      </div>
      <button class="btn-outline" type="button" @click="router.push('/properties')">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Registry
      </button>
    </div>

    <section class="upload-panel">
      <div class="upload-zone" data-testid="property-import-dropzone">
        <i class="pi pi-upload upload-icon" aria-hidden="true"></i>
        <div>
          <h2>CSV Upload</h2>
          <p>Required fields: address, municipality, property_type, latitude, longitude, market_value.</p>
        </div>
        <label class="btn-primary">
          Select CSV
          <input data-testid="property-import-file-input" type="file" accept=".csv,text/csv" @change="handleFileChange" />
        </label>
      </div>
      <div v-if="selectedFile" class="file-strip" data-testid="property-import-selected-file">
        <i class="pi pi-file" aria-hidden="true"></i>
        <span>{{ selectedFile.name }}</span>
        <span>{{ previewRows.length }} rows parsed</span>
      </div>
    </section>

        <section v-if="headers.length" class="grid-two">
          <div class="panel">
            <div class="panel-hd">
              <h2>Field Mapping</h2>
              <span>{{ mappedRequiredCount }}/{{ requiredFields.length }} required</span>
            </div>
            <table class="mapping-table" data-testid="property-import-mapping-table">
              <thead>
                <tr>
                  <th>Required field</th>
                  <th>CSV column</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="field in requiredFields" :key="field">
                  <td>{{ field }}</td>
                  <td>{{ fieldMap[field] || 'Not mapped' }}</td>
                  <td>
                    <span class="status-pill" :class="fieldMap[field] ? 'ok' : 'error'">
                      {{ fieldMap[field] ? 'Mapped' : 'Missing' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="panel">
            <div class="panel-hd">
              <h2>Validation</h2>
              <span :class="validationErrors.length ? 'count-error' : 'count-ok'">
                {{ validationErrors.length ? `${validationErrors.length} blocked` : 'Ready' }}
              </span>
            </div>
            <div class="validation-list" data-testid="property-import-validation-preview">
              <div v-if="!validationErrors.length" class="validation-ok">
                <i class="pi pi-check-circle" aria-hidden="true"></i>
                <span>All preview rows satisfy required fields and the 25% taxable value rule.</span>
              </div>
              <div v-for="error in validationErrors" v-else :key="`${error.row}-${error.message}`" class="validation-error">
                <span>Row {{ error.row }}</span>
                <p>{{ error.message }}</p>
              </div>
            </div>
          </div>
        </section>

        <section v-if="previewRows.length" class="panel">
          <div class="panel-hd">
            <h2>Validation Preview</h2>
            <span>{{ previewRows.length }} rows</span>
          </div>
          <div class="preview-table-wrap">
            <table class="preview-table" data-testid="property-import-preview-table">
              <thead>
                <tr>
                  <th>Address</th>
                  <th>Municipality</th>
                  <th>Type</th>
                  <th class="num">Market Value</th>
                  <th class="num">Taxable Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in previewRows" :key="index">
                  <td>{{ row.address }}</td>
                  <td>{{ row.municipality }}</td>
                  <td>{{ row.property_type }}</td>
                  <td class="num">{{ formatNumber(row.market_value) }}</td>
                  <td class="num">{{ formatNumber(row.taxable_value) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <div v-if="headers.length" class="action-bar">
          <div>
            <strong>{{ importStatus }}</strong>
            <p>{{ validationErrors.length ? 'Resolve blocked rows before import.' : 'Rows are ready for upload.' }}</p>
          </div>
          <button
            class="btn-primary"
            data-testid="property-import-confirm"
            :disabled="!canImport || importing"
            @click="confirmImport"
          >
            <i class="pi pi-cloud-upload" aria-hidden="true"></i>
            {{ importing ? 'Importing' : 'Confirm Import' }}
          </button>
        </div>
  </div>
</template>

<script setup lang="ts">
import propertyService from '~/services/propertyService'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const selectedFile = ref<File | null>(null)
const headers = ref<string[]>([])
const rows = ref<Record<string, string>[]>([])
const importing = ref(false)
const importStatus = ref('No file selected')

const requiredFields = ['address', 'municipality', 'property_type', 'latitude', 'longitude', 'market_value']

type PreviewRow = Record<string, string | number> & {
  address: string
  municipality: string
  property_type: string
  market_value: number
  taxable_value: number
}

const fieldMap = computed(() => {
  const normalizedHeaders = new Map(headers.value.map(header => [normalizeHeader(header), header]))
  return requiredFields.reduce<Record<string, string>>((map, field) => {
    map[field] = normalizedHeaders.get(field) || ''
    return map
  }, {})
})

const mappedRequiredCount = computed(() => requiredFields.filter(field => fieldMap.value[field]).length)

const previewRows = computed<PreviewRow[]>(() => rows.value.map(row => {
  const normalized = normalizeRow(row)
  const marketValue = Number(normalized.market_value || 0)
  const taxableValue = normalized.taxable_value ? Number(normalized.taxable_value) : marketValue * 0.25
  return {
    ...normalized,
    address: String(normalized.address || ''),
    municipality: String(normalized.municipality || ''),
    property_type: String(normalized.property_type || ''),
    market_value: marketValue,
    taxable_value: taxableValue,
  }
}))

const validationErrors = computed(() => {
  const errors: Array<{ row: number; message: string }> = []
  previewRows.value.forEach((row, index) => {
    requiredFields.forEach(field => {
      if (!row[field]) errors.push({ row: index + 2, message: `${field} is required` })
    })
    if (row.taxable_value && Math.round(row.taxable_value * 100) !== Math.round(row.market_value * 25)) {
      errors.push({ row: index + 2, message: 'Taxable value must be exactly 25% of market value' })
    }
  })
  return errors
})

const canImport = computed(() => selectedFile.value && rows.value.length > 0 && validationErrors.value.length === 0)

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  selectedFile.value = file
  const text = await file.text()
  const parsed = parseCsv(text)
  headers.value = parsed.headers
  rows.value = parsed.rows
  importStatus.value = `${parsed.rows.length} rows parsed`
}

async function confirmImport() {
  if (!selectedFile.value || !canImport.value) return

  importing.value = true
  importStatus.value = 'Uploading rows'
  try {
    const result = await propertyService.bulkImport(selectedFile.value)
    importStatus.value = `${result.imported_count} properties imported`
  } catch (error: any) {
    importStatus.value = error.message || 'Import failed'
  } finally {
    importing.value = false
  }
}

function parseCsv(text: string) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean)
  const csvHeaders = splitCsvLine(lines[0] || '')
  const csvRows = lines.slice(1).map(line => {
    const values = splitCsvLine(line)
    return csvHeaders.reduce<Record<string, string>>((row, header, index) => {
      row[header] = values[index] || ''
      return row
    }, {})
  })
  return { headers: csvHeaders, rows: csvRows }
}

function splitCsvLine(line: string) {
  return line.split(',').map(value => value.trim().replace(/^"|"$/g, ''))
}

function normalizeHeader(header: string) {
  return header.trim().toLowerCase().replace(/\s+/g, '_')
}

function normalizeRow(row: Record<string, string>) {
  return Object.entries(row).reduce<Record<string, any>>((normalized, [key, value]) => {
    normalized[normalizeHeader(key)] = value.trim()
    return normalized
  }, {})
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-ET', { maximumFractionDigits: 0 }).format(Number(value || 0))
}

useHead({
  title: 'Bulk Property Import - ValuAdis',
  meta: [{ name: 'description', content: 'Bulk import property records from CSV.' }],
})
</script>

<style scoped>
.import-page { max-width: 1180px; }
.breadcrumb { display: flex; align-items: center; gap: 0.4rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--muted); margin-bottom: 1.5rem; }
.breadcrumb a { color: var(--muted); text-decoration: none; }
.bc-active { color: var(--green-dark); }
.page-hd { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; gap: 1rem; }
.page-title { font-family: var(--display); font-size: clamp(32px, 4vw, 48px); font-weight: 600; color: var(--ink); margin: 0 0 0.4rem; }
.page-desc { font-size: 0.95rem; color: var(--ink-soft); margin: 0; }
.btn-outline, .btn-primary { display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem; min-height: 2.5rem; border-radius: 0.5rem; font-size: 0.82rem; font-weight: 700; cursor: pointer; transition: opacity 0.2s, background 0.2s; }
.btn-outline { padding: 0.55rem 1rem; background: #fff; border: 1px solid rgba(188,202,192,0.42); color: var(--ink-soft); }
.btn-primary { padding: 0.6rem 1.1rem; background: var(--green); border: 1px solid var(--green); color: #fff; }
.btn-primary input { display: none; }
.btn-primary:disabled { cursor: not-allowed; opacity: 0.55; }
.upload-panel, .panel, .action-bar { background: rgba(255,255,255,0.84); border: 1px solid rgba(188,202,192,0.24); border-radius: 0.5rem; box-shadow: 0 10px 26px rgba(15,23,42,0.04); }
.upload-panel { padding: 1rem; margin-bottom: 1.25rem; }
.upload-zone { display: flex; align-items: center; gap: 1rem; padding: 1.5rem; border: 1px dashed rgba(7,129,96,0.42); border-radius: 0.5rem; background: rgba(7,129,96,0.035); }
.upload-zone h2, .panel h2 { margin: 0; font-family: 'Syne', sans-serif; font-size: 1rem; color: var(--ink-soft); }
.upload-zone p, .action-bar p { margin: 0.25rem 0 0; color: var(--muted); font-size: 0.82rem; }
.upload-icon { font-size: 2.2rem; color: var(--green); }
.upload-zone > div { flex: 1; }
.file-strip { display: flex; align-items: center; gap: 0.75rem; padding: 0.8rem 1rem 0 1rem; color: var(--muted); font-size: 0.82rem; }
.grid-two { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }
.panel { padding: 1.25rem; margin-bottom: 1.25rem; }
.panel-hd { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; color: var(--muted); font-size: 0.8rem; }
.mapping-table, .preview-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
.mapping-table th, .preview-table th { text-align: left; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); border-bottom: 1px solid var(--line); padding: 0.7rem; }
.mapping-table td, .preview-table td { border-bottom: 1px solid var(--line); padding: 0.7rem; color: var(--ink-soft); }
.status-pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 0.15rem 0.55rem; font-size: 0.7rem; font-weight: 700; }
.status-pill.ok, .count-ok { color: var(--green-dark); background: var(--green-soft); }
.status-pill.error, .count-error { color: var(--red); background: var(--red-soft); }
.count-ok, .count-error { padding: 0.2rem 0.55rem; border-radius: 999px; font-weight: 700; }
.validation-list { display: flex; flex-direction: column; gap: 0.65rem; }
.validation-ok { display: flex; align-items: center; gap: 0.6rem; color: var(--green-dark); font-size: 0.86rem; }
.validation-error { border-left: 3px solid var(--red); padding: 0.45rem 0.75rem; background: var(--red-soft); border-radius: 0.4rem; }
.validation-error span { font-size: 0.72rem; font-weight: 800; color: var(--red); text-transform: uppercase; }
.validation-error p { margin: 0.2rem 0 0; color: var(--red); font-size: 0.82rem; }
.preview-table-wrap { overflow-x: auto; }
.num { text-align: right; font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace; }
.action-bar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1rem 1.25rem; position: sticky; bottom: 1rem; }
.action-bar strong { color: var(--ink-soft); }

@media (max-width: 900px) {
  .grid-two, .page-hd, .upload-zone, .action-bar { grid-template-columns: 1fr; flex-direction: column; align-items: stretch; }
}
</style>
