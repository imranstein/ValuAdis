<template>
  <div class="page-shell settings-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">System controls</p>
        <h2 class="page-title">Operational settings.</h2>
          <p class="page-subtitle">
          Account context, workspace defaults, and API-key management, saved to the backend settings service.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="generateApiKey">
          <i class="pi pi-key" aria-hidden="true"></i>
          Create API key
        </button>
        <button class="btn-primary" type="button" @click="saveOperationalSettings">
          <i class="pi pi-save" aria-hidden="true"></i>
          Save settings
        </button>
      </div>
    </section>

    <section class="settings-grid">
      <article class="panel profile-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Administrative profile</h3>
            <p class="panel-subtitle">Authenticated account context from the backend session</p>
          </div>
          <span class="status-pill" :class="profileLoadError ? 'warn' : 'good'">
            {{ profileLoadError ? 'Session check needed' : 'Verified' }}
          </span>
        </div>
        <div class="field-grid">
          <div v-for="field in profileFields" :key="field.label" class="read-field">
            <span>{{ field.label }}</span>
            <strong>{{ field.value }}</strong>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Workspace behavior</h3>
            <p class="panel-subtitle">Interface defaults for repeated administrative work</p>
          </div>
        </div>
        <div class="control-list">
          <label class="control-row">
            <span>
              <strong>Dark mode</strong>
              <small>Reserved for low-light review sessions</small>
            </span>
            <input v-model="darkMode" type="checkbox" />
          </label>
          <div class="segmented-row">
            <span>
              <strong>Data density</strong>
              <small>Controls table and form spacing</small>
            </span>
            <div class="segmented-control">
              <button type="button" :class="{ active: dataDensity === 'compact' }" @click="dataDensity = 'compact'">Compact</button>
              <button type="button" :class="{ active: dataDensity === 'spacious' }" @click="dataDensity = 'spacious'">Spacious</button>
            </div>
          </div>
          <label class="field">
            <span>System language</span>
            <select v-model="systemLanguage" @change="applyLanguage">
              <option value="en">English (International)</option>
              <option value="am">Amharic (አማርኛ)</option>
            </select>
          </label>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Email delivery</h3>
            <p class="panel-subtitle">Outbound notifications for reports and approvals</p>
          </div>
          <span class="status-pill warn">
            {{ emailSettings.enabled ? 'Draft enabled' : 'Draft only' }}
          </span>
        </div>
        <div class="form-grid">
          <label class="field">
            <span>SMTP host</span>
            <input v-model="emailSettings.smtpHost" type="text" />
          </label>
          <label class="field">
            <span>SMTP port</span>
            <input v-model.number="emailSettings.smtpPort" type="number" />
          </label>
          <label class="field full">
            <span>Sender email</span>
            <input v-model="emailSettings.senderEmail" type="email" />
          </label>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">Security limits</h3>
            <p class="panel-subtitle">Request caps and credential posture</p>
          </div>
          <span class="status-pill warn">{{ passwordAgeLabel }}</span>
        </div>
        <div class="form-grid">
          <label class="field">
            <span>Requests per window</span>
            <input v-model.number="rateLimitSettings.requestsPerWindow" type="number" />
          </label>
          <label class="field">
            <span>Burst limit</span>
            <input v-model.number="rateLimitSettings.burst" type="number" />
          </label>
          <label class="field full">
            <span>Window</span>
            <select v-model="rateLimitSettings.window">
              <option>minute</option>
              <option>hour</option>
              <option>day</option>
            </select>
          </label>
        </div>
      </article>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">API keys</h3>
            <p class="panel-subtitle">{{ saveStatus }}</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Key</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="apiKeys.length === 0">
              <td colspan="3" class="empty-cell">No API keys yet. Create one to integrate external systems.</td>
            </tr>
            <tr v-for="key in apiKeys" :key="key.id" :class="{ revoked: key.revoked }">
              <td><strong>{{ key.name }}</strong></td>
              <td class="num">{{ maskApiKey(key) }}</td>
              <td class="text-right">
                <button class="icon-button inline" type="button" aria-label="Copy API key" @click="copyApiKey(key)">
                  <i class="pi pi-copy" aria-hidden="true"></i>
                </button>
                <button v-if="!key.revoked" class="icon-button inline danger" type="button" aria-label="Revoke API key" @click="deleteApiKey(key.id)">
                  <i class="pi pi-trash" aria-hidden="true"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import authService from '~/services/authService'
import { getAccessToken } from '~/utils/authToken'
import { useI18n } from '~/composables/useI18n'

definePageMeta({ middleware: ['auth', 'admin'] })

const { setLocale, locale } = useI18n()

function applyLanguage() {
  setLocale(systemLanguage.value === 'am' ? 'am' : 'en')
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

async function settingsFetch(path, options = {}) {
  return fetch(`${apiBase}/api/v1/settings${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getAccessToken()}`,
      ...(options.headers || {}),
    },
  })
}

const darkMode = ref(false)
const dataDensity = ref('compact')
const systemLanguage = ref(locale.value)
const daysSincePasswordChange = ref('unknown')
const saveStatus = ref('Loading…')
const profileLoadError = ref('')

const userProfile = ref({
  fullName: 'Signed-in user',
  email: 'Profile details unavailable',
  department: 'Not provided',
  role: 'Workspace access'
})

const apiKeys = ref([])

const emailSettings = ref({
  enabled: false,
  smtpHost: '',
  smtpPort: 587,
  senderEmail: ''
})

const rateLimitSettings = ref({
  requestsPerWindow: 900,
  window: 'hour',
  burst: 75
})

const profileFields = computed(() => [
  { label: 'Full name', value: userProfile.value.fullName },
  { label: 'Email address', value: userProfile.value.email },
  { label: 'Department', value: userProfile.value.department },
  { label: 'Role access', value: userProfile.value.role }
])

const passwordAgeLabel = computed(() => {
  return typeof daysSincePasswordChange.value === 'number'
    ? `${daysSincePasswordChange.value}d password age`
    : 'Password age unavailable'
})

onMounted(async () => {
  await Promise.all([loadSettings(), loadApiKeys(), loadCurrentUser()])
})

async function loadCurrentUser() {
  try {
    const user = await authService.getCurrentUser()
    userProfile.value = {
      fullName: user.full_name || 'Signed-in user',
      email: user.email || 'Profile details unavailable',
      department: user.municipality || 'Not provided',
      role: normalizeRole(user.role || (user.is_admin ? 'system_admin' : 'valuer'))
    }
    profileLoadError.value = ''
  } catch {
    profileLoadError.value = 'Unable to load authenticated profile'
  }
}

async function loadSettings() {
  try {
    const res = await settingsFetch('')
    if (!res.ok) throw new Error('load failed')
    const prefs = (await res.json()).preferences || {}
    emailSettings.value = { ...emailSettings.value, ...(prefs.email || {}) }
    rateLimitSettings.value = { ...rateLimitSettings.value, ...(prefs.rateLimits || {}) }
    saveStatus.value = 'Loaded from backend'
  } catch {
    saveStatus.value = 'Could not load settings'
  }
}

async function loadApiKeys() {
  try {
    const res = await settingsFetch('/api-keys')
    apiKeys.value = res.ok ? await res.json() : []
  } catch {
    apiKeys.value = []
  }
}

function normalizeRole(role) {
  return String(role || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase()) || 'Workspace access'
}

function maskApiKey(key) {
  // A freshly-created key carries the one-time plaintext; stored keys show a prefix.
  if (key.key) return `${key.key.substring(0, 7)}............${key.key.slice(-4)}`
  return `${key.key_prefix || '••••'}••••••••••••`
}

function copyApiKey(key) {
  if (!key.key) {
    saveStatus.value = 'Full key is only shown once at creation'
    return
  }
  navigator.clipboard?.writeText(key.key)
  saveStatus.value = 'Key copied'
}

async function deleteApiKey(id) {
  const res = await settingsFetch(`/api-keys/${id}`, { method: 'DELETE' })
  if (res.ok) {
    await loadApiKeys()
    saveStatus.value = 'Key revoked'
  } else {
    saveStatus.value = 'Could not revoke key'
  }
}

async function generateApiKey() {
  const name = (typeof window !== 'undefined' && window.prompt('Name this API key:', 'Integration key')) || ''
  if (!name.trim()) return
  const res = await settingsFetch('/api-keys', {
    method: 'POST',
    body: JSON.stringify({ name: name.trim() }),
  })
  if (!res.ok) {
    saveStatus.value = 'Could not create key'
    return
  }
  const created = await res.json()
  // Surface the one-time plaintext key at the top of the list for copying.
  await loadApiKeys()
  apiKeys.value = [created, ...apiKeys.value.filter((k) => k.id !== created.id)]
  saveStatus.value = 'Key created — copy it now, it is shown only once'
}

async function saveOperationalSettings() {
  const res = await settingsFetch('', {
    method: 'PUT',
    body: JSON.stringify({
      preferences: { email: emailSettings.value, rateLimits: rateLimitSettings.value },
    }),
  })
  saveStatus.value = res.ok ? 'Saved to backend' : 'Save failed'
}
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 14px;
}

.profile-panel {
  grid-row: span 2;
}

.field-grid,
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.read-field,
.field {
  display: grid;
  gap: 7px;
}

.read-field span,
.field span {
  color: var(--muted);
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.read-field strong {
  min-height: 42px;
  border-bottom: 1px solid var(--line);
  color: var(--ink-soft);
  font-weight: 750;
}

.field input,
.field select {
  min-height: 40px;
  width: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink);
  padding: 0 10px;
}

.field.full {
  grid-column: 1 / -1;
}

.control-list {
  display: grid;
  gap: 18px;
}

.control-row,
.segmented-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.control-row strong,
.segmented-row strong {
  display: block;
  color: var(--ink);
}

.control-row small,
.segmented-row small {
  display: block;
  margin-top: 2px;
  color: var(--muted);
}

.segmented-control {
  display: inline-flex;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface-2);
  padding: 3px;
}

.segmented-control button {
  min-height: 32px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-weight: 800;
  padding: 0 10px;
}

.segmented-control button.active {
  background: var(--surface);
  color: var(--green);
  box-shadow: var(--shadow-sm);
}

.table-head {
  margin: 0;
  padding: 20px 22px;
  border-bottom: 1px solid var(--line);
}

.icon-button.inline {
  display: inline-grid;
  margin-left: 6px;
}

.icon-button.danger {
  color: var(--red);
}

.empty-cell {
  color: var(--muted);
  padding: 24px;
  text-align: left;
}

@media (max-width: 1080px) {
  .settings-grid,
  .field-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .profile-panel {
    grid-row: auto;
  }
}
</style>
