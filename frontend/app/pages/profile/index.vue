<template>
  <div class="page-shell profile-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Account identity</p>
        <h2 class="page-title">My profile.</h2>
        <p class="page-subtitle">
          Review the authenticated user record, municipal assignment, and recent backend activity tied to the current session.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadProfile">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
      </div>
    </section>

    <div v-if="errorMessage" class="state-panel error-state" role="alert">
      <strong>Profile unavailable</strong>
      <span>{{ errorMessage }}</span>
    </div>

    <section class="profile-grid">
      <article class="profile-card panel">
        <div class="profile-header">
          <div class="profile-avatar" aria-hidden="true">{{ initials }}</div>
          <div>
            <p class="profile-label">Signed-in account</p>
            <h3 class="profile-name">{{ profile.fullName }}</h3>
            <p class="profile-role">{{ roleLabel }}</p>
          </div>
        </div>
        <div class="profile-status-row">
          <span class="status-pill" :class="profile.isAdmin ? 'good' : 'muted'">{{ profile.isAdmin ? 'Administrator' : 'Standard user' }}</span>
          <span class="status-pill" :class="profile.isVerified ? 'good' : 'warn'">{{ profile.isVerified ? 'Verified' : 'Unverified' }}</span>
          <span class="status-pill" :class="profile.isValuer ? 'good' : 'muted'">{{ profile.isValuer ? 'Valuer' : 'No valuation role' }}</span>
        </div>
      </article>

      <article class="metric-card">
        <p class="metric-label">User ID</p>
        <p class="metric-value">{{ profile.id }}</p>
        <p class="metric-note">Backend identity</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Roles</p>
        <p class="metric-value">{{ profile.roles.length || (profile.role ? 1 : 0) }}</p>
        <p class="metric-note">{{ roleLabel }}</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Recent activity</p>
        <p class="metric-value">{{ activityLog.length }}</p>
        <p class="metric-note">Loaded from audit API</p>
      </article>
    </section>

    <section class="profile-detail-grid">
      <article class="panel info-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Contact and assignment</h3>
            <p class="panel-subtitle">Values returned by the authenticated current-user endpoint.</p>
          </div>
        </div>
        <dl class="profile-list">
          <div>
            <dt>Email</dt>
            <dd>{{ profile.email }}</dd>
          </div>
          <div>
            <dt>Phone</dt>
            <dd>{{ profile.phone }}</dd>
          </div>
          <div>
            <dt>Municipality</dt>
            <dd>{{ profile.municipality }}</dd>
          </div>
          <div>
            <dt>License number</dt>
            <dd class="num">{{ profile.licenseNumber }}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd class="num">{{ profile.createdAt }}</dd>
          </div>
        </dl>
      </article>

      <article class="panel activity-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Recent activity</h3>
            <p class="panel-subtitle">Most recent audit records available for this account.</p>
          </div>
        </div>
        <div v-if="loading" class="state-panel">Loading profile records...</div>
        <div v-else-if="activityLog.length === 0" class="state-panel">
          No audit activity is recorded for this account yet.
        </div>
        <div v-else class="activity-list">
          <div v-for="activity in activityLog" :key="activity.id" class="activity-item">
            <span class="status-pill" :class="activity.actionClass">{{ activity.action }}</span>
            <div>
              <strong>{{ activity.description }}</strong>
              <span class="record-id">{{ activity.timestamp }}</span>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const loading = ref(true)
const errorMessage = ref('')
const activityLog = ref<any[]>([])
const profile = reactive({
  id: 'Loading',
  fullName: 'Loading profile',
  email: 'Loading',
  phone: 'Loading',
  municipality: 'Loading',
  licenseNumber: 'Loading',
  role: '',
  roles: [] as string[],
  isAdmin: false,
  isValuer: false,
  isVerified: false,
  createdAt: 'Loading',
})

const initials = computed(() => profile.fullName.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'VA')
const roleLabel = computed(() => {
  if (profile.roles.length) return profile.roles.join(', ')
  if (profile.role) return humanize(profile.role)
  if (profile.isAdmin) return 'System administrator'
  if (profile.isValuer) return 'Valuer'
  return 'User'
})

onMounted(loadProfile)

async function loadProfile() {
  loading.value = true
  errorMessage.value = ''

  try {
    const token = getAccessToken()
    const [profileResponse, activityResponse] = await Promise.all([
      fetch(`${apiBase}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } }),
      fetch(`${apiBase}/api/v1/audit/logs?limit=10`, { headers: { Authorization: `Bearer ${token}` } }),
    ])

    if (!profileResponse.ok) throw new Error(`Profile request failed with ${profileResponse.status}`)
    if (!activityResponse.ok) throw new Error(`Activity request failed with ${activityResponse.status}`)

    setProfile(await profileResponse.json())
    const activityPayload = await activityResponse.json()
    activityLog.value = Array.isArray(activityPayload.data) ? activityPayload.data.map(normalizeActivity) : []
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load profile.'
    activityLog.value = []
  } finally {
    loading.value = false
  }
}

function setProfile(user: any) {
  profile.id = user.id ? String(user.id) : 'Not recorded'
  profile.fullName = user.full_name || 'Unnamed user'
  profile.email = user.email || 'Not recorded'
  profile.phone = user.phone || 'Not recorded'
  profile.municipality = user.municipality || 'Unassigned'
  profile.licenseNumber = user.license_number || 'Not recorded'
  profile.role = user.role || ''
  profile.roles = Array.isArray(user.roles) ? user.roles.filter(Boolean).map(humanize) : []
  profile.isAdmin = Boolean(user.is_admin)
  profile.isValuer = Boolean(user.is_valuer || user.role === 'valuer')
  profile.isVerified = Boolean(user.is_verified || user.is_admin)
  profile.createdAt = formatTimestamp(user.created_at)
}

function normalizeActivity(row: any) {
  const action = String(row.action_type || 'view').toUpperCase()
  return {
    id: String(row.id),
    action,
    actionClass: actionClass(action),
    description: row.description || `${action} on ${row.module || 'record'}`,
    timestamp: formatTimestamp(row.timestamp),
  }
}

function formatTimestamp(value: string | null) {
  if (!value) return 'Not recorded'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-ET', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function humanize(value: string) {
  return value.replace(/[_-]/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function actionClass(action: string) {
  if (action === 'DELETE') return 'bad'
  if (['CREATE', 'INSERT'].includes(action)) return 'good'
  if (['UPDATE', 'LOGIN'].includes(action)) return 'warn'
  return 'muted'
}
</script>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: minmax(280px, 2fr) repeat(3, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.profile-card,
.info-panel,
.activity-panel {
  padding: 1.25rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.profile-avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--green-dark);
  color: var(--shell-ink);
  font-weight: 800;
  letter-spacing: 0.04em;
}

.profile-label,
.metric-label,
.profile-list dt {
  margin: 0;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.profile-name {
  margin: 0.2rem 0;
  font-size: 1.35rem;
}

.profile-role {
  margin: 0;
  color: var(--ink-soft);
}

.profile-status-row,
.activity-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.profile-detail-grid {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(320px, 1fr);
  gap: 1rem;
}

.profile-list {
  display: grid;
  gap: 1rem;
  margin: 0;
}

.profile-list div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid rgba(15, 61, 53, 0.1);
}

.profile-list dd {
  margin: 0;
  text-align: right;
  color: var(--ink);
  font-weight: 650;
}

.activity-list {
  display: grid;
  gap: 0.9rem;
}

.activity-item {
  justify-content: flex-start;
  padding-bottom: 0.9rem;
  border-bottom: 1px solid rgba(15, 61, 53, 0.1);
}

.activity-item strong,
.activity-item span {
  display: block;
}

@media (max-width: 1100px) {
  .profile-grid,
  .profile-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
