<template>
  <div class="page-shell my-listings-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Rental registry</p>
        <h2 class="page-title">My rental listings.</h2>
        <p class="page-subtitle">
          Register a property for rent. The system suggests a rent band from its valuation; a
          rental officer verifies and publishes the listing to the public registry.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadAll">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
        <NuxtLink to="/properties/create" class="btn-primary">
          <i class="pi pi-plus" aria-hidden="true"></i>
          Register a property
        </NuxtLink>
      </div>
    </section>

    <section v-if="ownerUnverified" class="panel verification-banner" role="status">
      <i class="pi pi-id-card" aria-hidden="true"></i>
      <div>
        <strong>Owner verification pending.</strong>
        <span>
          You can draft listings now, but a rental officer must verify your account before any of
          your listings can be published.
        </span>
      </div>
    </section>

    <section class="panel create-panel">
      <div class="panel-head">
        <div>
          <h3 class="panel-title">List a property for rent</h3>
          <p class="panel-subtitle">
            Pick one of your registered properties. Use the property wizard first if it is not
            registered yet.
          </p>
        </div>
      </div>

      <div class="create-form">
        <select v-model="selectedPropertyId" class="filter-select" aria-label="Select property">
          <option value="">Select a registered property…</option>
          <option v-for="property in availableProperties" :key="property.id" :value="String(property.id)">
            {{ property.address }} · {{ property.municipality }} · {{ property.area_sqm }} m²
          </option>
        </select>
        <button class="btn-primary" type="button" :disabled="!selectedPropertyId || creating" @click="createListing">
          {{ creating ? 'Submitting…' : 'Submit for review' }}
        </button>
      </div>

      <p v-if="propertiesError" class="inline-error" role="alert">{{ propertiesError }}</p>
      <p v-else-if="properties.length === 0 && !loadingProperties" class="inline-muted">
        You have no registered properties yet. Register one with the property wizard first.
      </p>
      <p v-if="createError" class="inline-error" role="alert">{{ createError }}</p>
      <p v-if="createNotice" class="inline-notice" role="status">{{ createNotice }}</p>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">Listing records</h3>
          <p class="panel-subtitle">Showing {{ listings.length }} of {{ total }} backend records</p>
        </div>
      </div>

      <div v-if="listingsError" class="state-panel error-state" role="alert">
        <strong>Listings unavailable</strong>
        <span>{{ listingsError }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Listing</th>
              <th>Property</th>
              <th class="text-right">Suggested rent</th>
              <th class="text-right">Band</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingListings">
              <td colspan="6">Loading your listings…</td>
            </tr>
            <tr v-else-if="listings.length === 0">
              <td colspan="6">No rental listings yet. Submit a property above to start the review process.</td>
            </tr>
            <tr v-for="listing in listings" v-else :key="listing.public_id">
              <td class="record-id">{{ listing.public_id }}</td>
              <td><strong>{{ listing.property_address || `Property #${listing.property_id}` }}</strong></td>
              <td class="text-right num">{{ formatEtb(listing.suggested_rent) }}</td>
              <td class="text-right num">{{ formatEtb(listing.band_min) }} – {{ formatEtb(listing.band_max) }}</td>
              <td>
                <span class="status-pill" :class="statusClass(listing.status)">{{ labelize(listing.status) }}</span>
              </td>
              <td class="text-right">
                <NuxtLink
                  v-if="listing.status === 'published'"
                  :to="`/rent/${listing.public_id}`"
                  class="icon-button inline"
                  aria-label="View public listing"
                >
                  <i class="pi pi-external-link" aria-hidden="true"></i>
                </NuxtLink>
                <button
                  v-if="['pending_review', 'published'].includes(listing.status)"
                  class="icon-button inline"
                  type="button"
                  aria-label="Withdraw listing"
                  :disabled="acting"
                  @click="withdraw(listing)"
                >
                  <i class="pi pi-undo" aria-hidden="true"></i>
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
import { computed, onMounted, ref } from 'vue'
import rentalService, { type OwnerListing } from '~/services/rentalService'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const properties = ref<any[]>([])
const loadingProperties = ref(true)
const propertiesError = ref('')

const listings = ref<OwnerListing[]>([])
const total = ref(0)
const loadingListings = ref(true)
const listingsError = ref('')

const selectedPropertyId = ref('')
const creating = ref(false)
const createError = ref('')
const createNotice = ref('')
const acting = ref(false)
const ownerUnverified = ref(false)

const availableProperties = computed(() => {
  const activeIds = new Set(
    listings.value
      .filter((l) => ['draft', 'pending_review', 'published', 'rented'].includes(l.status))
      .map((l) => l.property_id),
  )
  return properties.value.filter((p) => !activeIds.has(p.id))
})

onMounted(loadAll)

async function loadAll() {
  await Promise.all([loadProperties(), loadListings()])
}

async function loadProperties() {
  loadingProperties.value = true
  propertiesError.value = ''
  try {
    const response = await fetch(`${apiBase}/api/v1/properties?limit=100`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) throw new Error(`Property request failed with ${response.status}`)
    const body = await response.json()
    properties.value = Array.isArray(body.data) ? body.data : []
  } catch (error) {
    propertiesError.value = error instanceof Error ? error.message : 'Could not load your properties.'
    properties.value = []
  } finally {
    loadingProperties.value = false
  }
}

async function loadListings() {
  loadingListings.value = true
  listingsError.value = ''
  try {
    const result = await rentalService.myListings()
    listings.value = result.data
    total.value = result.total
  } catch (error) {
    listingsError.value = error instanceof Error ? error.message : 'Could not load your listings.'
    listings.value = []
    total.value = 0
  } finally {
    loadingListings.value = false
  }
}

async function createListing() {
  if (!selectedPropertyId.value) return
  creating.value = true
  createError.value = ''
  createNotice.value = ''
  try {
    const listing = await rentalService.createListing(Number(selectedPropertyId.value))
    createNotice.value = `Listing ${listing.public_id} submitted for officer review with a suggested band of ${formatEtb(listing.band_min)} – ${formatEtb(listing.band_max)}.`
    selectedPropertyId.value = ''
    await loadListings()
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Could not create the listing.'
    createError.value = message
    if (message.toLowerCase().includes('property owners')) {
      ownerUnverified.value = true
    }
  } finally {
    creating.value = false
  }
}

async function withdraw(listing: OwnerListing) {
  acting.value = true
  try {
    await rentalService.withdrawListing(listing.public_id)
    await loadListings()
  } catch (error) {
    listingsError.value = error instanceof Error ? error.message : 'Could not withdraw the listing.'
  } finally {
    acting.value = false
  }
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
</script>

<style scoped>
.verification-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  border-left: 3px solid var(--gold-bright);
  padding: var(--space-4) var(--space-5);
}

.verification-banner i {
  color: var(--gold);
  font-size: 20px;
  margin-top: 2px;
}

.verification-banner strong {
  display: block;
  color: var(--ink);
}

.verification-banner span {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.create-panel {
  padding: var(--space-5);
}

.create-form {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) auto;
  gap: 10px;
  margin-top: var(--space-4);
}

.filter-select {
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink-soft);
  padding: 0 10px;
}

.inline-error {
  margin: var(--space-3) 0 0;
  color: var(--red, #9d3a28);
  font-weight: 600;
  font-size: 13px;
}

.inline-muted {
  margin: var(--space-3) 0 0;
  color: var(--muted);
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

@media (max-width: 720px) {
  .create-form {
    grid-template-columns: 1fr;
  }
}
</style>
