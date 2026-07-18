<template>
  <div class="page-shell contracts-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Rental registry operations</p>
        <h2 class="page-title">Contracts registry.</h2>
        <p class="page-subtitle">
          Register tenancy contracts from accepted applications and record deposit receipts.
          A contract activates only when the recorded receipt matches the required deposit.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadContracts">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
        <NuxtLink to="/rentals" class="btn-primary">
          <i class="pi pi-inbox" aria-hidden="true"></i>
          Review queue
        </NuxtLink>
      </div>
    </section>

    <section class="panel create-panel">
      <div class="panel-head">
        <div>
          <h3 class="panel-title">Register a contract</h3>
          <p class="panel-subtitle">
            Look up a rented listing's accepted application, then set the tenancy term. Rent is
            captured from the accepted offer; the default deposit is two months' rent.
          </p>
        </div>
      </div>

      <div class="lookup-form">
        <input
          v-model="lookupPublicId"
          type="text"
          class="text-input"
          placeholder="Listing id, e.g. AA-LST-2026-000123"
          aria-label="Listing public id"
        />
        <button class="btn-secondary" type="button" :disabled="lookingUp || !lookupPublicId" @click="lookupApplications">
          {{ lookingUp ? 'Looking up…' : 'Find accepted application' }}
        </button>
      </div>
      <p v-if="lookupError" class="inline-error" role="alert">{{ lookupError }}</p>

      <form v-if="acceptedApplication" class="contract-form" @submit.prevent="registerContract">
        <div class="accepted-summary" role="status">
          Accepted application #{{ acceptedApplication.id }} — {{ acceptedApplication.renter_name || 'Renter' }}
          at {{ formatEtb(acceptedApplication.offered_rent) }}/mo.
          Default deposit: {{ formatEtb(acceptedApplication.offered_rent * 2) }}.
        </div>
        <div class="field-row">
          <label class="field">
            <span>Start date</span>
            <input v-model="contractForm.start_date" type="date" required class="text-input" />
          </label>
          <label class="field">
            <span>End date</span>
            <input v-model="contractForm.end_date" type="date" required class="text-input" />
          </label>
        </div>
        <details class="override-panel">
          <summary>Override deposit (reason required, audited)</summary>
          <div class="field-row">
            <label class="field">
              <span>Deposit amount (ETB)</span>
              <input v-model.number="contractForm.deposit_amount" type="number" min="1" class="text-input" />
            </label>
            <label class="field">
              <span>Reason</span>
              <input v-model="contractForm.deposit_reason" type="text" maxlength="1000" class="text-input" />
            </label>
          </div>
        </details>
        <p v-if="createError" class="inline-error" role="alert">{{ createError }}</p>
        <button class="btn-primary" type="submit" :disabled="creating">
          {{ creating ? 'Registering…' : 'Register contract' }}
        </button>
      </form>
      <p v-if="createNotice" class="inline-notice" role="status">{{ createNotice }}</p>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Registered contracts</h3>
          <p class="panel-subtitle">Showing {{ contracts.length }} of {{ total }} backend records</p>
        </div>
      </div>

      <div v-if="contractsError" class="state-panel error-state" role="alert">
        <strong>Contracts unavailable</strong>
        <span>{{ contractsError }}</span>
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
              <td colspan="7">Loading contracts…</td>
            </tr>
            <tr v-else-if="contracts.length === 0">
              <td colspan="7">No registered contracts yet.</td>
            </tr>
            <tr v-for="contract in contracts" v-else :key="contract.contract_no">
              <td class="record-id">{{ contract.contract_no }}</td>
              <td class="record-id">{{ contract.listing_public_id || '—' }}</td>
              <td class="text-right num">{{ formatEtb(contract.monthly_rent) }}</td>
              <td class="text-right num">
                {{ formatEtb(contract.deposit_amount) }}
                <span class="deposit-state" :class="contract.deposit_receipt_ref ? 'good' : 'warn'">
                  {{ contract.deposit_receipt_ref ? `ref ${contract.deposit_receipt_ref}` : 'receipt pending' }}
                </span>
              </td>
              <td>{{ formatDate(contract.start_date) }} → {{ formatDate(contract.end_date) }}</td>
              <td>
                <span class="status-pill" :class="statusClass(contract.status)">{{ labelize(contract.status) }}</span>
              </td>
              <td class="text-right">
                <button
                  v-if="contract.status === 'draft'"
                  class="btn-secondary btn-compact"
                  type="button"
                  @click="openDeposit(contract)"
                >
                  Record deposit
                </button>
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

    <section v-if="depositFor" class="panel deposit-panel" aria-label="Record deposit">
      <div class="panel-head">
        <div>
          <h3 class="panel-title">Record deposit — {{ depositFor.contract_no }}</h3>
          <p class="panel-subtitle">
            Required deposit: {{ formatEtb(depositFor.deposit_amount) }}. A mismatched receipt
            amount is rejected; a matching one activates the contract.
          </p>
        </div>
        <button class="icon-button" type="button" aria-label="Close" @click="depositFor = null">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </div>
      <form class="deposit-form" @submit.prevent="submitDeposit">
        <div class="field-row">
          <label class="field">
            <span>Receipt reference (Telebirr/CBE)</span>
            <input v-model="depositForm.ref" type="text" required minlength="3" class="text-input" />
          </label>
          <label class="field">
            <span>Amount (ETB)</span>
            <input v-model.number="depositForm.amount" type="number" required min="1" step="0.01" class="text-input" />
          </label>
          <label class="field">
            <span>Paid on</span>
            <input v-model="depositForm.paidOn" type="date" class="text-input" />
          </label>
        </div>
        <p v-if="depositError" class="inline-error" role="alert">{{ depositError }}</p>
        <p v-if="depositNotice" class="inline-notice" role="status">{{ depositNotice }}</p>
        <button class="btn-primary" type="submit" :disabled="recordingDeposit">
          {{ recordingDeposit ? 'Recording…' : 'Record receipt' }}
        </button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import rentalService, { type OwnerApplication, type TenancyContract } from '~/services/rentalService'

definePageMeta({ middleware: 'auth' })

const loading = ref(true)
const contractsError = ref('')
const contracts = ref<TenancyContract[]>([])
const total = ref(0)
const downloading = ref('')

const lookupPublicId = ref('')
const lookingUp = ref(false)
const lookupError = ref('')
const acceptedApplication = ref<OwnerApplication | null>(null)

const creating = ref(false)
const createError = ref('')
const createNotice = ref('')
const contractForm = reactive({
  start_date: '',
  end_date: '',
  deposit_amount: null as number | null,
  deposit_reason: '',
})

const depositFor = ref<TenancyContract | null>(null)
const recordingDeposit = ref(false)
const depositError = ref('')
const depositNotice = ref('')
const depositForm = reactive({ ref: '', amount: null as number | null, paidOn: '' })

onMounted(loadContracts)

async function loadContracts() {
  loading.value = true
  contractsError.value = ''
  try {
    const result = await rentalService.listContracts()
    contracts.value = result.data
    total.value = result.total
  } catch (error) {
    contractsError.value = error instanceof Error ? error.message : 'Could not load contracts.'
    contracts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function lookupApplications() {
  lookingUp.value = true
  lookupError.value = ''
  acceptedApplication.value = null
  createNotice.value = ''
  try {
    const applications = await rentalService.listingApplications(lookupPublicId.value.trim())
    const accepted = applications.find((app) => app.status === 'accepted')
    if (!accepted) {
      lookupError.value = 'No accepted application on this listing yet. The owner must accept an applicant first.'
    } else {
      acceptedApplication.value = accepted
    }
  } catch (error) {
    lookupError.value = error instanceof Error ? error.message : 'Lookup failed.'
  } finally {
    lookingUp.value = false
  }
}

async function registerContract() {
  if (!acceptedApplication.value) return
  creating.value = true
  createError.value = ''
  createNotice.value = ''
  try {
    const payload: Parameters<typeof rentalService.createContract>[0] = {
      application_id: acceptedApplication.value.id,
      start_date: contractForm.start_date,
      end_date: contractForm.end_date,
    }
    if (contractForm.deposit_amount != null && contractForm.deposit_amount > 0) {
      payload.deposit_amount = contractForm.deposit_amount
      payload.deposit_reason = contractForm.deposit_reason
    }
    const contract = await rentalService.createContract(payload)
    createNotice.value = `Contract ${contract.contract_no} registered as draft. Record the deposit receipt to activate it.`
    acceptedApplication.value = null
    lookupPublicId.value = ''
    contractForm.start_date = ''
    contractForm.end_date = ''
    contractForm.deposit_amount = null
    contractForm.deposit_reason = ''
    await loadContracts()
  } catch (error) {
    createError.value = error instanceof Error ? error.message : 'Contract registration failed.'
  } finally {
    creating.value = false
  }
}

function openDeposit(contract: TenancyContract) {
  depositFor.value = contract
  depositError.value = ''
  depositNotice.value = ''
  depositForm.ref = ''
  depositForm.amount = contract.deposit_amount
  depositForm.paidOn = ''
}

async function submitDeposit() {
  if (!depositFor.value || depositForm.amount == null) return
  recordingDeposit.value = true
  depositError.value = ''
  depositNotice.value = ''
  try {
    const updated = await rentalService.recordDeposit(
      depositFor.value.contract_no,
      depositForm.ref,
      depositForm.amount,
      depositForm.paidOn || undefined,
    )
    depositNotice.value = `Deposit recorded. Contract ${updated.contract_no} is now ${updated.status}.`
    await loadContracts()
  } catch (error) {
    depositError.value = error instanceof Error ? error.message : 'Deposit recording failed.'
  } finally {
    recordingDeposit.value = false
  }
}

async function downloadPdf(contractNo: string) {
  downloading.value = contractNo
  contractsError.value = ''
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
    contractsError.value = error instanceof Error ? error.message : 'Could not download the contract.'
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
.create-panel,
.deposit-panel {
  padding: var(--space-5);
}

.lookup-form {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) auto;
  gap: 10px;
  margin-top: var(--space-4);
}

.text-input {
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink);
  padding: 0 12px;
  font-family: inherit;
}

.text-input:focus {
  outline: none;
  border-color: var(--green);
}

.contract-form,
.deposit-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.accepted-summary {
  border: 1px solid var(--line);
  border-left: 3px solid var(--green);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 14px;
  padding: var(--space-3) var(--space-4);
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.field span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.override-panel {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: var(--space-3) var(--space-4);
}

.override-panel summary {
  color: var(--ink-soft);
  font-weight: 600;
  cursor: pointer;
}

.override-panel .field-row {
  margin-top: var(--space-3);
}

.inline-error {
  margin: var(--space-3) 0 0;
  color: var(--red, #9d3a28);
  font-weight: 600;
  font-size: 13px;
}

.inline-notice {
  margin: var(--space-3) 0 0;
  border: 1px solid var(--line);
  border-left: 3px solid var(--green);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 13px;
  padding: var(--space-3) var(--space-4);
}

.btn-compact {
  min-height: 32px;
  padding: 0 12px;
  font-size: 13px;
  margin-right: 8px;
}

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

@media (max-width: 720px) {
  .lookup-form {
    grid-template-columns: 1fr;
  }
}
</style>
