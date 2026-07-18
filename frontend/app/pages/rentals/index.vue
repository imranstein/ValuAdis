<template>
  <div class="page-shell rentals-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Rental registry operations</p>
        <h2 class="page-title">Officer review queue.</h2>
        <p class="page-subtitle">
          Verify owners, review suggested rent bands, and publish listings to the public registry.
          Every action is written to the audit ledger.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadQueue">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
        <NuxtLink to="/rent" class="btn-primary">
          <i class="pi pi-external-link" aria-hidden="true"></i>
          Public listings
        </NuxtLink>
      </div>
    </section>

    <section class="registry-toolbar panel">
      <div class="search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input v-model="searchQuery" type="search" placeholder="Search listing id, address, owner, or sub-city" />
      </div>
      <select v-model="queueStatus" class="filter-select" aria-label="Queue status" @change="loadQueue">
        <option value="pending_review">Pending review</option>
        <option value="published">Published</option>
        <option value="withdrawn">Withdrawn</option>
      </select>
      <button class="icon-button" type="button" aria-label="Reset filters" @click="resetFilters">
        <i class="pi pi-filter-slash" aria-hidden="true"></i>
      </button>
    </section>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-label">{{ metric.label }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">{{ queueTitle }}</h3>
          <p class="panel-subtitle">Showing {{ filteredListings.length }} of {{ total }} backend records</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>Review queue unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Listing</th>
              <th>Property</th>
              <th>Owner</th>
              <th class="text-right">Suggested rent</th>
              <th class="text-right">Band</th>
              <th>Flags</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7">Loading review queue…</td>
            </tr>
            <tr v-else-if="filteredListings.length === 0">
              <td colspan="7">No listings in this queue. Owner submissions appear here for review.</td>
            </tr>
            <tr v-for="listing in filteredListings" v-else :key="listing.public_id">
              <td class="record-id">{{ listing.public_id }}</td>
              <td>
                <strong>{{ listing.property_address || 'Address unavailable' }}</strong>
                <span>{{ listing.property_subcity || listing.property_municipality }} · {{ formatArea(listing.property_area_sqm) }} m²</span>
              </td>
              <td>
                <strong>{{ listing.owner_name || 'Owner' }}</strong>
                <span class="status-pill" :class="listing.owner_verified ? 'good' : 'warn'">
                  {{ listing.owner_verified ? 'Verified' : 'Unverified' }}
                </span>
              </td>
              <td class="text-right num">{{ formatEtb(listing.suggested_rent) }}</td>
              <td class="text-right num">{{ formatEtb(listing.band_min) }} – {{ formatEtb(listing.band_max) }}</td>
              <td>
                <span v-if="listing.requires_officer_review" class="status-pill warn">Band review required</span>
                <span v-else class="status-pill" :class="statusClass(listing.status)">{{ labelize(listing.status) }}</span>
              </td>
              <td class="text-right">
                <button class="icon-button inline" type="button" aria-label="Open listing" @click="openListing(listing)">
                  <i class="pi pi-eye" aria-hidden="true"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside v-if="selected" class="review-drawer" aria-label="Listing review">
      <div class="drawer-head">
        <div>
          <p class="record-id">{{ selected.public_id }}</p>
          <h3>{{ selected.property_address }}</h3>
        </div>
        <button class="icon-button" type="button" aria-label="Close" @click="closeDrawer">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </div>

      <dl class="drawer-facts">
        <div><dt>Status</dt><dd>{{ labelize(selected.status) }}</dd></div>
        <div><dt>Owner</dt><dd>{{ selected.owner_name || '—' }}</dd></div>
        <div>
          <dt>Owner verification</dt>
          <dd>
            <span class="status-pill" :class="selected.owner_verified ? 'good' : 'warn'">
              {{ selected.owner_verified ? 'Verified' : 'Unverified' }}
            </span>
          </dd>
        </div>
        <div><dt>Suggested rent</dt><dd class="num">{{ formatEtb(selected.suggested_rent) }}/mo</dd></div>
        <div><dt>Band</dt><dd class="num">{{ formatEtb(selected.band_min) }} – {{ formatEtb(selected.band_max) }}</dd></div>
        <div><dt>Valuation confidence</dt><dd class="num">{{ selected.confidence != null ? `${Math.round(selected.confidence * 100)}%` : '—' }}</dd></div>
        <div v-if="selected.review_reason"><dt>Note</dt><dd>{{ selected.review_reason }}</dd></div>
      </dl>

      <div v-if="actionError" class="state-panel error-state" role="alert">
        <strong>Action failed</strong>
        <span>{{ actionError }}</span>
      </div>
      <div v-if="actionNotice" class="drawer-notice" role="status">{{ actionNotice }}</div>

      <div v-if="selected.status === 'pending_review'" class="drawer-actions">
        <button
          v-if="!selected.owner_verified"
          class="btn-secondary"
          type="button"
          :disabled="acting"
          @click="verifyOwner"
        >
          <i class="pi pi-id-card" aria-hidden="true"></i>
          Verify owner
        </button>

        <button class="btn-primary" type="button" :disabled="acting || !selected.owner_verified" @click="publish">
          <i class="pi pi-check" aria-hidden="true"></i>
          Publish at band
        </button>

        <details class="adjust-panel">
          <summary>Adjust band (reason required)</summary>
          <div class="adjust-fields">
            <label>
              <span>Band min (ETB)</span>
              <input v-model.number="adjust.bandMin" type="number" min="1" />
            </label>
            <label>
              <span>Band max (ETB)</span>
              <input v-model.number="adjust.bandMax" type="number" min="1" />
            </label>
            <label class="adjust-reason">
              <span>Reason (mandatory, audited)</span>
              <textarea v-model="adjust.reason" rows="2" placeholder="Why is the suggested band being changed?"></textarea>
            </label>
            <button class="btn-secondary" type="button" :disabled="acting" @click="adjustBand">
              Apply band adjustment
            </button>
          </div>
        </details>

        <details class="adjust-panel">
          <summary>Reject listing (reason required)</summary>
          <div class="adjust-fields">
            <label class="adjust-reason">
              <span>Reason (mandatory, audited)</span>
              <textarea v-model="rejectReason" rows="2" placeholder="Why is this listing rejected?"></textarea>
            </label>
            <button class="btn-danger" type="button" :disabled="acting" @click="reject">
              Reject listing
            </button>
          </div>
        </details>
      </div>

      <div v-else-if="selected.status === 'published'" class="drawer-actions">
        <p class="drawer-note">
          The published band is frozen. To change it, withdraw the listing; the owner must
          re-submit for review.
        </p>
        <button class="btn-danger" type="button" :disabled="acting" @click="withdraw">
          <i class="pi pi-undo" aria-hidden="true"></i>
          Withdraw listing
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import rentalService, { type OfficerListing } from '~/services/rentalService'

definePageMeta({ middleware: 'auth' })

const searchQuery = ref('')
const queueStatus = ref('pending_review')
const loading = ref(true)
const errorMessage = ref('')
const listings = ref<OfficerListing[]>([])
const total = ref(0)

const selected = ref<OfficerListing | null>(null)
const acting = ref(false)
const actionError = ref('')
const actionNotice = ref('')
const adjust = reactive({ bandMin: 0, bandMax: 0, reason: '' })
const rejectReason = ref('')

const filteredListings = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return listings.value
  return listings.value.filter((listing) =>
    [listing.public_id, listing.property_address, listing.owner_name, listing.property_subcity]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(q)),
  )
})

const queueTitle = computed(() => {
  if (queueStatus.value === 'pending_review') return 'Pending review'
  return `${labelize(queueStatus.value)} listings`
})

const metrics = computed(() => [
  { label: 'In this queue', value: String(total.value), note: `Status: ${labelize(queueStatus.value)}` },
  {
    label: 'Band review flags',
    value: String(listings.value.filter((l) => l.requires_officer_review).length),
    note: 'Low-confidence valuations',
  },
  {
    label: 'Unverified owners',
    value: String(listings.value.filter((l) => !l.owner_verified).length),
    note: 'Verification required before publish',
  },
  {
    label: 'Median suggested rent',
    value: medianRent.value ? formatEtb(medianRent.value) : '—',
    note: 'Across loaded queue records',
  },
])

const medianRent = computed(() => {
  const rents = listings.value.map((l) => l.suggested_rent).sort((a, b) => a - b)
  if (!rents.length) return 0
  const mid = Math.floor(rents.length / 2)
  return rents.length % 2 ? rents[mid] : (rents[mid - 1] + rents[mid]) / 2
})

onMounted(loadQueue)

async function loadQueue() {
  loading.value = true
  errorMessage.value = ''
  closeDrawer()
  try {
    const result = await rentalService.reviewQueue(queueStatus.value)
    listings.value = result.data
    total.value = result.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load the review queue.'
    listings.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function openListing(listing: OfficerListing) {
  selected.value = listing
  actionError.value = ''
  actionNotice.value = ''
  adjust.bandMin = listing.band_min
  adjust.bandMax = listing.band_max
  adjust.reason = ''
  rejectReason.value = ''
}

function closeDrawer() {
  selected.value = null
  actionError.value = ''
  actionNotice.value = ''
}

async function verifyOwner() {
  if (!selected.value) return
  await runAction(async () => {
    await rentalService.verifyOwner(selected.value!.owner_user_id)
    selected.value!.owner_verified = true
    actionNotice.value = 'Owner verified. This action was audit-logged.'
  })
}

async function publish() {
  if (!selected.value) return
  await runAction(async () => {
    await rentalService.reviewListing(selected.value!.public_id, 'publish')
    actionNotice.value = 'Listing published at the frozen band.'
    await loadQueue()
  })
}

async function adjustBand() {
  if (!selected.value) return
  await runAction(async () => {
    const updated = await rentalService.reviewListing(selected.value!.public_id, 'adjust_band', {
      band_min: adjust.bandMin,
      band_max: adjust.bandMax,
      reason: adjust.reason,
    })
    selected.value = { ...selected.value!, ...updated }
    actionNotice.value = 'Band adjusted with reason. This action was audit-logged.'
  })
}

async function reject() {
  if (!selected.value) return
  await runAction(async () => {
    await rentalService.reviewListing(selected.value!.public_id, 'reject', { reason: rejectReason.value })
    actionNotice.value = 'Listing rejected.'
    await loadQueue()
  })
}

async function withdraw() {
  if (!selected.value) return
  await runAction(async () => {
    await rentalService.withdrawListing(selected.value!.public_id, 'Withdrawn by rental officer')
    actionNotice.value = 'Listing withdrawn.'
    await loadQueue()
  })
}

async function runAction(action: () => Promise<void>) {
  acting.value = true
  actionError.value = ''
  actionNotice.value = ''
  try {
    await action()
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : 'Action failed.'
  } finally {
    acting.value = false
  }
}

function resetFilters() {
  searchQuery.value = ''
  queueStatus.value = 'pending_review'
  loadQueue()
}

function statusClass(status: string) {
  if (status === 'published') return 'good'
  if (status === 'pending_review') return 'warn'
  if (status === 'withdrawn') return 'bad'
  return 'muted'
}

function labelize(value: string) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatArea(value?: number | null) {
  return Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })
}
</script>

<style scoped>
.registry-toolbar {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(180px, 240px) 40px;
  gap: 10px;
  align-items: center;
  padding: 14px;
}

.search-field {
  min-width: 0;
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 12px;
}

.search-field input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
}

.filter-select {
  min-height: 40px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink-soft);
  padding: 0 10px;
}

.review-drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 60;
  width: min(440px, 100vw);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  overflow-y: auto;
  border-left: 1px solid var(--line-strong);
  background: var(--surface);
  box-shadow: var(--shadow-lg);
  padding: var(--space-5);
}

.drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.drawer-head h3 {
  margin: var(--space-2) 0 0;
  font-family: var(--serif);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
}

.drawer-facts {
  display: grid;
  gap: 0;
  margin: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.drawer-facts div {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-bottom: 1px solid var(--line);
  padding: var(--space-3) var(--space-4);
}

.drawer-facts div:last-child {
  border-bottom: 0;
}

.drawer-facts dt {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.drawer-facts dd {
  margin: 0;
  color: var(--ink);
  text-align: right;
}

.drawer-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.drawer-note {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.drawer-notice {
  border: 1px solid var(--line);
  border-left: 3px solid var(--green);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 13px;
  padding: var(--space-3) var(--space-4);
}

.adjust-panel {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: var(--space-3) var(--space-4);
}

.adjust-panel summary {
  color: var(--ink-soft);
  font-weight: 600;
  cursor: pointer;
}

.adjust-fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.adjust-fields label {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.adjust-fields label span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.adjust-fields input,
.adjust-fields textarea {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink);
  padding: 8px 10px;
  font-family: inherit;
}

@media (max-width: 820px) {
  .registry-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
