<template>
  <div class="page-shell my-contracts-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Rental registry</p>
        <h2 class="page-title">My tenancy contracts.</h2>
        <p class="page-subtitle">
          Registered contracts where you are the owner or renter party. A contract becomes active
          once the deposit receipt is recorded by a rental officer.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="load">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
      </div>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Contract records</h3>
          <p class="panel-subtitle">Showing {{ contracts.length }} of {{ total }} backend records</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>Contracts unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>
      <div v-if="downloadError" class="state-panel error-state" role="alert">
        <strong>Download failed</strong>
        <span>{{ downloadError }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Contract No.</th>
              <th>Listing</th>
              <th class="text-right">Monthly rent</th>
              <th class="text-right">Deposit</th>
              <th>Term</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7">Loading your contracts…</td>
            </tr>
            <tr v-else-if="contracts.length === 0">
              <td colspan="7">
                No registered contracts yet. Contracts appear here once a rental officer registers
                them from an accepted application.
              </td>
            </tr>
            <tr v-for="contract in contracts" v-else :key="contract.contract_no">
              <td class="record-id">{{ contract.contract_no }}</td>
              <td class="record-id">{{ contract.listing_public_id || '—' }}</td>
              <td class="text-right num">{{ formatEtb(contract.monthly_rent) }}</td>
              <td class="text-right num">
                {{ formatEtb(contract.deposit_amount) }}
                <span class="deposit-state" :class="contract.deposit_receipt_ref ? 'good' : 'warn'">
                  {{ contract.deposit_receipt_ref ? 'receipt recorded' : 'receipt pending' }}
                </span>
              </td>
              <td>{{ formatDate(contract.start_date) }} → {{ formatDate(contract.end_date) }}</td>
              <td>
                <span class="status-pill" :class="statusClass(contract.status)">{{ labelize(contract.status) }}</span>
              </td>
              <td class="text-right">
                <button
                  class="icon-button inline"
                  type="button"
                  aria-label="Download contract PDF"
                  :disabled="downloading === contract.contract_no"
                  @click="downloadPdf(contract.contract_no)"
                >
                  <i class="pi pi-file-pdf" aria-hidden="true"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import rentalService, { type TenancyContract } from '~/services/rentalService'

definePageMeta({ middleware: 'auth' })

const loading = ref(true)
const errorMessage = ref('')
const downloadError = ref('')
const downloading = ref('')
const contracts = ref<TenancyContract[]>([])
const total = ref(0)

onMounted(load)

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await rentalService.myContracts()
    contracts.value = result.data
    total.value = result.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load your contracts.'
    contracts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function downloadPdf(contractNo: string) {
  downloading.value = contractNo
  downloadError.value = ''
  try {
    const blob = await rentalService.downloadContractPdf(contractNo)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `ValuAdis_Contract_${contractNo}.pdf`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  } catch (error) {
    downloadError.value = error instanceof Error ? error.message : 'Could not download the contract.'
  } finally {
    downloading.value = ''
  }
}

function statusClass(status: string) {
  if (status === 'active') return 'good'
  if (status === 'draft') return 'warn'
  return 'bad'
}

function labelize(value: string) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-ET', { dateStyle: 'medium' }).format(date)
}
</script>

<style scoped>
.deposit-state {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.deposit-state.good {
  color: var(--green);
}

.deposit-state.warn {
  color: var(--gold);
}
</style>
