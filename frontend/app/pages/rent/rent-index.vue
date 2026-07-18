<template>
  <main class="rent-page">
    <nav class="rent-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="rent-brand">
        <span class="rent-mark" aria-hidden="true">V</span>
        <span>ValuAdis Rentals</span>
      </NuxtLink>
      <div class="rent-nav-links">
        <NuxtLink to="/rent">Listings</NuxtLink>
        <NuxtLink to="/rent/index" class="active">Rent index</NuxtLink>
        <NuxtLink to="/rent/signup">Citizen signup</NuxtLink>
        <NuxtLink to="/login" class="rent-login">Workspace sign in</NuxtLink>
      </div>
    </nav>

    <header class="rent-hero">
      <p class="rent-kicker">Addis Ababa Housing Administration pilot &mdash; Bole &amp; Yeka</p>
      <h1>The public district rent index.</h1>
      <p class="rent-lede">
        Median monthly rent by sub-city, property type, and bedroom count, computed from
        registered tenancy contracts under Proclamation 1320/2024. A district only appears once
        enough contracts are registered to protect any single household's privacy — small
        samples are withheld, never estimated or fabricated.
      </p>
    </header>

    <section class="rent-toolbar" aria-label="Index filters">
      <div class="rent-search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input
          v-model="district"
          type="search"
          placeholder="Sub-city (e.g. Bole, Yeka)"
          @keyup.enter="loadIndex"
        />
      </div>
      <select v-model="propertySubtype" class="rent-filter-select" aria-label="Property type">
        <option value="">Any property type</option>
        <option value="apartment">Apartment</option>
        <option value="villa">Villa / house</option>
        <option value="condominium">Condominium</option>
      </select>
      <button class="rent-btn-primary" type="button" @click="loadIndex">Filter</button>
    </section>

    <section class="rent-results" aria-label="Rent index results">
      <div v-if="loading" class="rent-state">Loading the rent index…</div>

      <div v-else-if="errorMessage" class="rent-state rent-state-error" role="alert">
        <strong>Rent index unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div v-else-if="Object.keys(groupedByDistrict).length === 0" class="rent-state">
        <strong>Insufficient data{{ district ? ` for ${district}` : '' }} yet.</strong>
        <span>
          Not enough registered tenancy contracts exist in this district to publish a reliable
          median without risking any single household's privacy. Check back as more contracts
          register, or browse the listings directly.
        </span>
      </div>

      <div v-else class="index-groups">
        <article v-for="(rows, districtName) in groupedByDistrict" :key="districtName" class="index-card">
          <h2>{{ districtName }}</h2>
          <div class="index-table-wrap">
            <table class="index-table">
              <thead>
                <tr>
                  <th>Property type</th>
                  <th>Bedrooms</th>
                  <th class="text-right">Median rent</th>
                  <th class="text-right">Sample size</th>
                  <th>Period</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in rows" :key="i">
                  <td>{{ formatSubtype(row.property_subtype) }}</td>
                  <td>{{ row.bedrooms != null ? row.bedrooms : 'All' }}</td>
                  <td class="text-right num">{{ formatEtb(row.median_rent) }}/mo</td>
                  <td class="text-right num">{{ row.sample_size }} contracts</td>
                  <td>{{ row.period }}</td>
                  <td class="index-source">{{ formatSource(row.source) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>
    </section>

    <footer class="rent-footer">
      <span>ValuAdis &mdash; government-mediated rental registry</span>
      <NuxtLink to="/rent">Browse published listings</NuxtLink>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import rentalService, { type RentIndexRow } from '~/services/rentalService'

// Nuxt's file-based router builds a route's NAME by joining every path
// segment (including literal "index" segments), while only stripping
// "index" from the PATH. A sibling pages/rent/index.vue (route name
// "rent/index", path "/rent") therefore collides by name with a nested
// pages/rent/index/index.vue (also name "rent/index"), and the scanner
// silently nests the second file as a child of the first, breaking both
// routes. Keeping this file flat (no "index" segment at all) and setting an
// explicit path is what actually makes it reachable at /rent/index.
definePageMeta({ layout: 'landing', path: '/rent/index' })

const district = ref('')
const propertySubtype = ref('')
const loading = ref(true)
const errorMessage = ref('')
const rows = ref<RentIndexRow[]>([])

onMounted(loadIndex)

async function loadIndex() {
  loading.value = true
  errorMessage.value = ''
  try {
    rows.value = await rentalService.getRentIndex({
      district: district.value.trim() || undefined,
      property_subtype: propertySubtype.value || undefined,
    })
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load the rent index.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

const groupedByDistrict = computed(() => {
  const groups: Record<string, RentIndexRow[]> = {}
  for (const row of rows.value) {
    if (!groups[row.district]) groups[row.district] = []
    groups[row.district].push(row)
  }
  return groups
})

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatSubtype(value: string) {
  return String(value || '').replace(/_/g, ' ')
}

function formatSource(source: string) {
  if (source === 'contracts') return 'Registered contracts'
  if (source === 'listings') return 'Published listings'
  return 'Blended'
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

.rent-nav-links a:hover,
.rent-nav-links a.active {
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
  font-size: clamp(34px, 5vw, 56px);
  font-weight: 600;
  line-height: 1.04;
}

.rent-lede {
  max-width: 680px;
  margin: var(--space-5) 0 0;
  color: var(--ink-soft);
  font-size: 17px;
  line-height: 1.6;
}

.rent-toolbar {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(180px, 240px) auto;
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
  max-width: 620px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--muted);
  padding: var(--space-5);
}

.rent-state-error strong {
  color: var(--red, #9d3a28);
}

.index-groups {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.index-card {
  border: 1px solid var(--line);
  border-top: 2px solid var(--gold-bright);
  border-radius: var(--radius);
  background: var(--surface);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.index-card h2 {
  margin: 0 0 var(--space-4);
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
}

.index-table-wrap {
  overflow-x: auto;
}

.index-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.index-table th {
  text-align: left;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--line);
  padding: 8px 10px;
}

.index-table td {
  border-bottom: 1px solid var(--line);
  padding: 10px;
  color: var(--ink-soft);
}

.index-table .text-right {
  text-align: right;
}

.index-table .num {
  color: var(--green);
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
}

.index-source {
  color: var(--muted);
  font-size: 12px;
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
