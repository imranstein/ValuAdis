<template>
  <section class="evidence-panel">
    <header class="evidence-head">
      <div>
        <p class="evidence-kicker">Market intelligence</p>
        <h3 class="evidence-title">Comparable listings</h3>
      </div>
      <span v-if="stats" class="evidence-count">{{ stats.count }} comparables</span>
    </header>

    <p v-if="loading" class="evidence-note">Loading market evidence…</p>

    <template v-else-if="stats">
      <div class="evidence-stats">
        <div class="evidence-stat">
          <span class="evidence-stat-label">Price / m² range</span>
          <span class="evidence-stat-value">
            ETB {{ fmt(stats.min_price_per_sqm) }} – {{ fmt(stats.max_price_per_sqm) }}
          </span>
        </div>
        <div class="evidence-stat">
          <span class="evidence-stat-label">Median price / m²</span>
          <span class="evidence-stat-value">ETB {{ fmt(stats.median_price_per_sqm) }}</span>
        </div>
        <div class="evidence-stat">
          <span class="evidence-stat-label">Implied value</span>
          <span class="evidence-stat-value accent">ETB {{ fmt(stats.implied_value_etb) }}</span>
        </div>
      </div>

      <table class="evidence-table">
        <thead>
          <tr><th>Listing</th><th>Area</th><th>Asking (ETB)</th><th>ETB / m²</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in comparables" :key="c.listing_url">
            <td class="evidence-listing">
              <a :href="c.listing_url" target="_blank" rel="noopener noreferrer">{{ c.title }}</a>
              <span class="evidence-sub">{{ c.location_subcity }}</span>
            </td>
            <td>{{ fmt(c.area_sqm) }} m²</td>
            <td>{{ fmt(c.asking_price_etb) }}</td>
            <td>{{ fmt(c.price_per_sqm) }}</td>
          </tr>
        </tbody>
      </table>
    </template>

    <p v-else class="evidence-empty">
      No comparable market listings yet for this property's area and sub-city.
      Comparables appear here once the market scraper has collected matching listings.
    </p>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAccessToken } from '~/utils/authToken'

const props = defineProps({
  propertyId: { type: [Number, String], required: true },
  apiBase: { type: String, required: true },
})

const loading = ref(true)
const comparables = ref([])
const stats = ref(null)

function fmt(n) {
  if (n === null || n === undefined) return '—'
  return Number(n).toLocaleString('en-US', { maximumFractionDigits: 0 })
}

onMounted(async () => {
  try {
    const res = await fetch(`${props.apiBase}/api/v1/properties/${props.propertyId}/market-evidence`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (res.ok) {
      const body = await res.json()
      comparables.value = body.data?.comparables ?? []
      stats.value = body.data?.statistics ?? null
    }
  } catch (err) {
    // Honest empty state on failure; no fabricated data.
    comparables.value = []
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.evidence-panel {
  margin-top: var(--space-6);
  padding: var(--space-5);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--surface);
}
.evidence-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.evidence-kicker {
  margin: 0;
  color: var(--gold);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.evidence-title {
  margin: var(--space-1) 0 0;
  color: var(--ink);
  font-size: 1.25rem;
}
.evidence-count {
  color: var(--muted);
  font-size: 0.8rem;
  font-family: var(--mono);
}
.evidence-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.evidence-stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-2);
}
.evidence-stat-label {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.evidence-stat-value {
  color: var(--ink);
  font-family: var(--mono);
  font-size: 0.95rem;
}
.evidence-stat-value.accent { color: var(--green); font-weight: 600; }
.evidence-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.evidence-table th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--line);
}
.evidence-table td {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--line);
  color: var(--ink);
  font-family: var(--mono);
}
.evidence-listing { display: flex; flex-direction: column; font-family: var(--sans); }
.evidence-listing a { color: var(--green); text-decoration: none; }
.evidence-listing a:hover { text-decoration: underline; }
.evidence-sub { color: var(--muted); font-size: 0.75rem; }
.evidence-note, .evidence-empty {
  margin: 0;
  color: var(--muted);
  font-size: 0.88rem;
  line-height: 1.5;
}
@media (max-width: 640px) {
  .evidence-stats { grid-template-columns: 1fr; }
}
</style>
