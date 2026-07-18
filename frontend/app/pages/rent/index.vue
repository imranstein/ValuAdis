<template>
  <main class="rent-page">
    <nav class="rent-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="rent-brand">
        <span class="rent-mark" aria-hidden="true">V</span>
        <span>ValuAdis Rentals</span>
      </NuxtLink>
      <div class="rent-nav-links">
        <NuxtLink to="/rent">Listings</NuxtLink>
        <NuxtLink to="/rent/signup">Citizen signup</NuxtLink>
        <NuxtLink to="/login" class="rent-login">Workspace sign in</NuxtLink>
      </div>
    </nav>

    <header class="rent-hero">
      <p class="rent-kicker">Addis Ababa Housing Administration pilot &mdash; Bole &amp; Yeka</p>
      <h1>Registered rental listings at honest, published prices.</h1>
      <p class="rent-lede">
        Every listing is verified by a rental officer and published inside a valuation-backed
        rent band under Proclamation 1320/2024. No brokers, no key money.
      </p>
    </header>

    <section class="rent-toolbar" aria-label="Listing filters">
      <div class="rent-search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input
          v-model="district"
          type="search"
          placeholder="Sub-city (e.g. Bole, Yeka)"
          @keyup.enter="loadListings"
        />
      </div>
      <select v-model="bedrooms" class="rent-filter-select" aria-label="Bedrooms">
        <option value="">Any bedrooms</option>
        <option v-for="n in 5" :key="n" :value="String(n)">{{ n }} bedroom{{ n > 1 ? 's' : '' }}</option>
      </select>
      <input
        v-model="maxRent"
        type="number"
        min="0"
        class="rent-filter-select"
        placeholder="Max monthly rent (ETB)"
        aria-label="Maximum monthly rent"
      />
      <button class="rent-btn-primary" type="button" @click="loadListings">Search</button>
    </section>

    <section class="rent-results" aria-label="Search results">
      <div v-if="loading" class="rent-state">Loading published listings…</div>

      <div v-else-if="errorMessage" class="rent-state rent-state-error" role="alert">
        <strong>Listings unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div v-else-if="listings.length === 0" class="rent-state">
        <strong>No published listings match these filters.</strong>
        <span>
          Listings appear here after a rental officer verifies and publishes them.
          Check back soon or widen your filters.
        </span>
      </div>

      <div v-else class="rent-grid">
        <NuxtLink
          v-for="listing in listings"
          :key="listing.public_id"
          :to="`/rent/${listing.public_id}`"
          class="rent-card"
        >
          <div class="rent-card-head">
            <span class="rent-card-id">{{ listing.public_id }}</span>
            <span class="rent-cert-badge" title="Backed by an approved rent valuation">
              <i class="pi pi-verified" aria-hidden="true"></i>
              Valuation certified
            </span>
          </div>
          <h2>{{ listing.property.address }}</h2>
          <p class="rent-card-location">
            {{ listing.property.subcity || listing.property.municipality }}
            · {{ formatSubtype(listing.property) }}
            · {{ formatArea(listing.property.area_sqm) }} m²
            <template v-if="listing.property.number_of_bedrooms">
              · {{ listing.property.number_of_bedrooms }} bd
            </template>
          </p>
          <div class="rent-card-band">
            <div>
              <span>Suggested rent</span>
              <strong>{{ formatEtb(listing.suggested_rent) }}/mo</strong>
            </div>
            <div>
              <span>Published band</span>
              <strong>{{ formatEtb(listing.band_min) }} – {{ formatEtb(listing.band_max) }}</strong>
            </div>
          </div>
        </NuxtLink>
      </div>

      <p v-if="!loading && !errorMessage" class="rent-count">
        {{ total }} published listing{{ total === 1 ? '' : 's' }} from the registry.
      </p>
    </section>

    <footer class="rent-footer">
      <span>ValuAdis &mdash; government-mediated rental registry</span>
      <NuxtLink to="/rent/signup">Register as owner or renter</NuxtLink>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import rentalService, { type PublicListing } from '~/services/rentalService'

definePageMeta({ layout: 'landing' })

const district = ref('')
const bedrooms = ref('')
const maxRent = ref('')
const loading = ref(true)
const errorMessage = ref('')
const listings = ref<PublicListing[]>([])
const total = ref(0)

onMounted(loadListings)

async function loadListings() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await rentalService.searchPublished({
      district: district.value.trim() || undefined,
      bedrooms: bedrooms.value ? Number(bedrooms.value) : undefined,
      band_max: maxRent.value ? Number(maxRent.value) : undefined,
    })
    listings.value = result.data
    total.value = result.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load listings.'
    listings.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatSubtype(property: PublicListing['property']) {
  const subtype = property.property_subtype || property.property_type
  return String(subtype).replace(/_/g, ' ')
}

function formatArea(value: number) {
  return Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })
}
</script>

<style scoped>
.rent-page {
  min-height: 100vh;
  background: var(--canvas);
  color: var(--ink);
}

.rent-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  height: 72px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  padding: 0 clamp(18px, 5vw, 64px);
}

.rent-brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
  text-decoration: none;
}

.rent-mark {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-size: 18px;
}

.rent-nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-5);
}

.rent-nav-links a {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
}

.rent-nav-links a:hover {
  color: var(--ink);
}

.rent-login {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 var(--space-4);
}

.rent-hero {
  max-width: 880px;
  padding: clamp(40px, 7vw, 88px) clamp(18px, 5vw, 64px) var(--space-6);
}

.rent-kicker {
  margin: 0 0 var(--space-4);
  color: var(--gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.rent-hero h1 {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(38px, 5.5vw, 64px);
  font-weight: 600;
  line-height: 1.04;
}

.rent-lede {
  max-width: 640px;
  margin: var(--space-5) 0 0;
  color: var(--ink-soft);
  font-size: 17px;
  line-height: 1.6;
}

.rent-toolbar {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(150px, 200px) minmax(180px, 220px) auto;
  gap: 10px;
  align-items: center;
  margin: 0 clamp(18px, 5vw, 64px);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 14px;
}

.rent-search-field {
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  padding: 0 12px;
}

.rent-search-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
}

.rent-filter-select {
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  padding: 0 10px;
}

.rent-btn-primary {
  min-height: 42px;
  border: 0;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-weight: 700;
  padding: 0 var(--space-5);
  cursor: pointer;
}

.rent-btn-primary:hover {
  background: var(--green-dark);
}

.rent-results {
  padding: var(--space-6) clamp(18px, 5vw, 64px);
}

.rent-state {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 560px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--muted);
  padding: var(--space-5);
}

.rent-state-error strong {
  color: var(--red, #9d3a28);
}

.rent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}

.rent-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  border: 1px solid var(--line);
  border-top: 2px solid var(--gold-bright);
  border-radius: var(--radius);
  background: var(--surface);
  padding: var(--space-5);
  color: var(--ink);
  text-decoration: none;
  box-shadow: var(--shadow-sm);
  transition: transform var(--duration-fast) var(--ease), box-shadow var(--duration-normal) var(--ease);
}

.rent-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.rent-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.rent-card-id {
  color: var(--muted);
  font-family: var(--mono);
  font-size: 12px;
}

.rent-cert-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--green);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.rent-card h2 {
  margin: 0;
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
  line-height: 1.2;
}

.rent-card-location {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.rent-card-band {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  border-top: 1px solid var(--line);
  padding-top: var(--space-3);
}

.rent-card-band span {
  display: block;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.rent-card-band strong {
  display: block;
  margin-top: 4px;
  color: var(--green);
  font-family: var(--mono);
  font-size: 15px;
  font-variant-numeric: tabular-nums;
}

.rent-count {
  margin: var(--space-5) 0 0;
  color: var(--muted);
  font-size: 13px;
}

.rent-footer {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-top: 1px solid var(--line);
  margin-top: var(--space-6);
  padding: var(--space-6) clamp(18px, 5vw, 64px);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.rent-footer a {
  color: var(--green);
  text-decoration: none;
}

@media (max-width: 860px) {
  .rent-toolbar {
    grid-template-columns: 1fr;
  }

  .rent-nav-links {
    gap: var(--space-3);
  }
}
</style>
