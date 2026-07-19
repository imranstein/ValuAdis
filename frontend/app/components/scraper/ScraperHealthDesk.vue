<template>
  <section class="health-desk">
    <header class="health-head">
      <h2 class="health-title">Source health</h2>
      <button type="button" class="health-refresh" :disabled="loading" @click="load">
        <i class="pi pi-refresh" aria-hidden="true"></i> Refresh
      </button>
    </header>

    <p v-if="loading" class="health-note">Checking source health…</p>

    <div v-else-if="sources.length" class="health-grid">
      <article v-for="s in sources" :key="s.id" class="health-card" :data-status="statusOf(s)">
        <div class="health-card-top">
          <span class="health-domain">{{ s.domain }}</span>
          <span class="health-badge" :data-status="statusOf(s)">{{ statusLabel(s) }}</span>
        </div>
        <dl class="health-meta">
          <div><dt>Last run</dt><dd>{{ fmtDate(s.last_run) }}</dd></div>
          <div><dt>Listings</dt><dd class="mono">{{ s.total_listings ?? 0 }}</dd></div>
          <div v-if="s.consecutive_failures > 0">
            <dt>Consecutive failures</dt><dd class="mono danger">{{ s.consecutive_failures }}</dd>
          </div>
        </dl>
        <p v-if="s.last_error_message" class="health-error">{{ s.last_error_message }}</p>
      </article>
    </div>

    <p v-else class="health-empty">No scraper sources configured yet.</p>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAccessToken } from '~/utils/authToken'

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl
const loading = ref(true)
const sources = ref([])

function statusOf(s) {
  if (!s.enabled) return 'disabled'
  if (s.consecutive_failures >= 3) return 'critical'
  if (s.last_status === 'failed') return 'failing'
  if (s.last_status === 'success') return 'healthy'
  return 'idle'
}
function statusLabel(s) {
  return { disabled: 'Disabled', critical: 'Critical', failing: 'Failing', healthy: 'Healthy', idle: 'Idle' }[statusOf(s)]
}
function fmtDate(d) {
  if (!d) return 'Never'
  try { return new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' }) } catch { return d }
}

async function load() {
  loading.value = true
  try {
    const res = await fetch(`${apiBase}/api/v1/scrapers/health`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    sources.value = res.ok ? (await res.json()) : []
  } catch {
    sources.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.health-desk {
  margin-bottom: var(--space-5);
  padding: var(--space-5);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--surface);
}
.health-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-4); }
.health-title { margin: 0; color: var(--ink); font-size: 1.15rem; }
.health-refresh {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border: 1px solid var(--line-strong); border-radius: var(--radius);
  background: var(--surface-2); color: var(--ink-soft); font-size: 0.8rem; cursor: pointer;
}
.health-refresh:hover { border-color: var(--green); color: var(--green); }
.health-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-3); }
.health-card { padding: var(--space-4); border: 1px solid var(--line); border-left: 3px solid var(--muted); border-radius: var(--radius); background: var(--surface-2); }
.health-card[data-status="healthy"] { border-left-color: var(--green); }
.health-card[data-status="failing"] { border-left-color: var(--gold); }
.health-card[data-status="critical"] { border-left-color: var(--red); }
.health-card[data-status="disabled"] { border-left-color: var(--muted); opacity: 0.7; }
.health-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-3); }
.health-domain { color: var(--ink); font-weight: 600; font-size: 0.9rem; }
.health-badge {
  padding: 2px 8px; border-radius: var(--radius-full); font-size: 0.66rem; font-weight: 700;
  letter-spacing: 0.05em; text-transform: uppercase;
}
.health-badge[data-status="healthy"] { background: var(--green-soft); color: var(--green-dark); }
.health-badge[data-status="failing"] { background: var(--amber-soft); color: var(--gold); }
.health-badge[data-status="critical"] { background: var(--red-soft); color: var(--red); }
.health-badge[data-status="disabled"], .health-badge[data-status="idle"] { background: var(--surface-3); color: var(--muted); }
.health-meta { display: flex; flex-wrap: wrap; gap: var(--space-3); margin: 0; }
.health-meta dt { color: var(--muted); font-size: 0.66rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
.health-meta dd { margin: 2px 0 0; color: var(--ink); font-size: 0.85rem; }
.mono { font-family: var(--mono); }
.danger { color: var(--red); }
.health-error { margin: var(--space-3) 0 0; color: var(--red); font-size: 0.78rem; word-break: break-word; }
.health-note, .health-empty { margin: 0; color: var(--muted); font-size: 0.88rem; }
</style>
