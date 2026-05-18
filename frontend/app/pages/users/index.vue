<template>
  <div class="page-shell users-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Access administration</p>
        <h2 class="page-title">User management.</h2>
        <p class="page-subtitle">
          Review platform access, valuer permissions, account status, and municipal assignment from the live user registry.
        </p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadUsers">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          Refresh
        </button>
      </div>
    </section>

    <section class="registry-toolbar panel">
      <div class="search-field">
        <i class="pi pi-search" aria-hidden="true"></i>
        <input v-model="searchQuery" type="search" placeholder="Search name, email, role, or municipality" />
      </div>
      <select v-model="selectedRole" class="filter-select" aria-label="Filter by role">
        <option value="">All roles</option>
        <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
      </select>
      <select v-model="selectedStatus" class="filter-select" aria-label="Filter by status">
        <option value="">All status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
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
          <h3 class="panel-title">System users</h3>
          <p class="panel-subtitle">Showing {{ filteredUsers.length }} of {{ users.length }} backend records</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>User registry unavailable</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Email</th>
              <th>Roles</th>
              <th>Municipality</th>
              <th>License</th>
              <th>Status</th>
              <th>Verified</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7">Loading user records...</td>
            </tr>
            <tr v-else-if="filteredUsers.length === 0">
              <td colspan="7">No user records match the current filters.</td>
            </tr>
            <tr v-for="user in filteredUsers" v-else :key="user.id">
              <td>
                <strong>{{ user.name }}</strong>
                <span class="record-id">ID {{ user.id }}</span>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span class="status-pill">{{ user.roleLabel }}</span>
              </td>
              <td>{{ user.municipality }}</td>
              <td class="num">{{ user.licenseNumber }}</td>
              <td>
                <span class="status-pill" :class="user.statusClass">{{ user.status }}</span>
              </td>
              <td>
                <span class="status-pill" :class="user.verifiedClass">{{ user.verified }}</span>
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
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: ['auth', 'admin'] })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')
const loading = ref(true)
const errorMessage = ref('')
const users = ref<any[]>([])

const filteredUsers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return users.value.filter((user) => {
    const matchesSearch = !q || [user.name, user.email, user.roleLabel, user.municipality].some((value) => value.toLowerCase().includes(q))
    const matchesRole = !selectedRole.value || user.roleNames.includes(selectedRole.value)
    const matchesStatus = !selectedStatus.value || user.status.toLowerCase() === selectedStatus.value
    return matchesSearch && matchesRole && matchesStatus
  })
})

const roles = computed(() => Array.from(new Set(users.value.flatMap((user) => user.roleNames))).filter(Boolean).sort())

const metrics = computed(() => [
  { label: 'Total users', value: String(users.value.length), note: 'Loaded from users API' },
  { label: 'Administrators', value: String(users.value.filter((user) => user.isAdmin).length), note: 'Admin permission accounts' },
  { label: 'Valuers', value: String(users.value.filter((user) => user.isValuer).length), note: 'Valuation-capable users' },
  { label: 'Verified', value: String(users.value.filter((user) => user.isVerified).length), note: 'Approved active identities' },
])

onMounted(loadUsers)

async function loadUsers() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(`${apiBase}/api/v1/users/`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })

    if (!response.ok) throw new Error(`User records request failed with ${response.status}`)

    const rows = await response.json()
    users.value = Array.isArray(rows) ? rows.map(normalizeUser) : []
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Could not load user records.'
    users.value = []
  } finally {
    loading.value = false
  }
}

function normalizeUser(user: any) {
  const roleNames = Array.isArray(user.roles) ? user.roles.map((role: any) => role.display_name || role.name).filter(Boolean) : []
  const isActive = Boolean(user.is_active)
  const isVerified = Boolean(user.is_verified)
  return {
    id: String(user.id),
    name: user.full_name || 'Unnamed user',
    email: user.email || 'Email pending',
    municipality: user.municipality || 'Unassigned',
    licenseNumber: user.license_number || 'Not recorded',
    roleNames,
    roleLabel: roleNames.length ? roleNames.join(', ') : roleFallback(user),
    status: isActive ? 'Active' : 'Inactive',
    statusClass: isActive ? 'good' : 'muted',
    verified: isVerified ? 'Verified' : 'Unverified',
    verifiedClass: isVerified ? 'good' : 'warn',
    isAdmin: Boolean(user.is_admin),
    isValuer: Boolean(user.is_valuer),
    isVerified,
  }
}

function roleFallback(user: any) {
  if (user.is_admin) return 'Administrator'
  if (user.is_valuer) return 'Valuer'
  return 'User'
}

function resetFilters() {
  searchQuery.value = ''
  selectedRole.value = ''
  selectedStatus.value = ''
}
</script>
