<template>
  <div class="page-shell settings-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">System controls</p>
        <h2 class="page-title">Operational settings.</h2>
          <p class="page-subtitle">
          Review account context and prepare workspace defaults. Production notification and API-key controls require backend settings endpoints before deployment.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="generateApiKey">
          <i class="pi pi-key" aria-hidden="true"></i>
          Create draft key
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
            <select v-model="systemLanguage">
              <option>English (International)</option>
              <option>Amharic</option>
              <option>Afaan Oromo</option>
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
              <td colspan="3" class="empty-cell">No API keys are loaded. Backend key management is not connected yet.</td>
            </tr>
            <tr v-for="key in apiKeys" :key="key.id">
              <td><strong>{{ key.name }}</strong></td>
              <td class="num">{{ maskApiKey(key.key) }}</td>
              <td class="text-right">
                <button class="icon-button inline" type="button" aria-label="Copy API key" @click="copyApiKey(key.key)">
                  <i class="pi pi-copy" aria-hidden="true"></i>
                </button>
                <button class="icon-button inline danger" type="button" aria-label="Delete API key" @click="deleteApiKey(key.id)">
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

definePageMeta({ middleware: ['auth', 'admin'] })

const darkMode = ref(false)
const dataDensity = ref('compact')
const systemLanguage = ref('English (International)')
const daysSincePasswordChange = ref('unknown')
const saveStatus = ref('Local draft only')
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
  loadLocalSettings()
  await loadCurrentUser()
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

function loadLocalSettings() {
  const saved = localStorage.getItem('valuadis_operational_settings')
  if (!saved) return

  try {
    const parsed = JSON.parse(saved)
    emailSettings.value = { ...emailSettings.value, ...(parsed.email || {}) }
    rateLimitSettings.value = { ...rateLimitSettings.value, ...(parsed.rateLimits || {}) }
    apiKeys.value = Array.isArray(parsed.apiKeys) ? parsed.apiKeys : []
    saveStatus.value = 'Local draft loaded'
  } catch {
    saveStatus.value = 'Saved draft could not be read'
  }
}

function normalizeRole(role) {
  return String(role || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase()) || 'Workspace access'
}

function maskApiKey(key) {
  return `${key.substring(0, 7)}............${key.substring(key.length - 4)}`
}

function copyApiKey(key) {
  navigator.clipboard?.writeText(key)
  saveStatus.value = 'Key copied'
}

function deleteApiKey(id) {
  apiKeys.value = apiKeys.value.filter((key) => key.id !== id)
  saveStatus.value = 'Key removed'
}

function generateApiKey() {
  const nextId = Math.max(...apiKeys.value.map((key) => key.id), 0) + 1
  const randomPart = crypto.randomUUID?.() || `${Date.now()}`
  apiKeys.value.push({
    id: nextId,
    name: `LOCAL_DRAFT_KEY_${nextId}`,
    key: `local_draft_${randomPart.replace(/-/g, '').slice(0, 24)}`
  })
  saveStatus.value = 'Draft key created locally'
}

function saveOperationalSettings() {
  localStorage.setItem('valuadis_operational_settings', JSON.stringify({
    email: emailSettings.value,
    rateLimits: rateLimitSettings.value,
    apiKeys: apiKeys.value
  }))
  saveStatus.value = 'Local draft saved'
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
