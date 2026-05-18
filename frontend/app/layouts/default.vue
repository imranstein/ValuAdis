<template>
  <div class="app-layout">
    <aside class="app-sidebar" :class="{ 'sidebar-open': sidebarOpen }" aria-label="Primary navigation">
      <div class="brand-lockup">
        <div class="brand-mark" aria-hidden="true">V</div>
        <div>
          <p class="brand-title">ValuAdis</p>
          <p class="brand-subtitle">Civic valuation</p>
        </div>
      </div>

      <nav class="app-nav">
        <section v-for="group in visibleNavigation" :key="group.label" class="nav-group">
          <p class="nav-group-label">{{ group.label }}</p>
          <ul class="nav-list">
            <li v-for="item in group.items" :key="item.to">
              <NuxtLink
                :to="item.to"
                class="nav-link"
                :class="{ active: isActive(item) }"
                @click="sidebarOpen = false"
              >
                <i :class="item.icon" aria-hidden="true"></i>
                <span>{{ item.label }}</span>
              </NuxtLink>
            </li>
          </ul>
        </section>
      </nav>

      <div class="sidebar-account">
        <div class="account-card">
          <div class="account-avatar">{{ userInitials }}</div>
          <div>
            <p class="account-name">{{ userName || 'Signed-in user' }}</p>
            <p class="account-role">{{ userRole || 'Workspace access' }}</p>
          </div>
        </div>
        <button class="btn-danger" type="button" @click="handleLogout">
          <i class="pi pi-sign-out" aria-hidden="true"></i>
          Logout
        </button>
      </div>
    </aside>

    <div class="mobile-overlay" :class="{ active: sidebarOpen }" @click="sidebarOpen = false"></div>

    <main class="app-main" id="main-content">
      <header class="app-header">
        <div class="header-left">
          <button class="icon-button mobile-menu-toggle" type="button" aria-label="Open menu" @click="sidebarOpen = true">
            <i class="pi pi-bars" aria-hidden="true"></i>
          </button>
          <div class="header-title">
            <h1>{{ pageTitle }}</h1>
            <p>{{ pageSubtitle }}</p>
          </div>
        </div>

        <div class="header-actions">
          <button class="action-btn" type="button" aria-label="Search" @click="toggleSearch">
            <i class="pi pi-search" aria-hidden="true"></i>
          </button>
          <button class="action-btn" type="button" aria-label="Notifications" @click="toggleNotifications">
            <i class="pi pi-bell" aria-hidden="true"></i>
          </button>
          <button class="header-avatar" type="button" aria-label="Profile menu" @click="toggleProfileMenu">
            {{ userInitials }}
          </button>
        </div>

        <div v-if="showNotifications" class="dropdown-menu notifications-dropdown">
          <div class="dropdown-header">
            <h3>Notifications</h3>
            <button class="btn-ghost" type="button" @click="markAllAsRead">Mark read</button>
          </div>
          <div class="notifications-list">
            <div v-if="notifications.length === 0" class="empty-state">No notifications.</div>
            <div v-for="notification in notifications" :key="notification.id" class="notification-item">
              <span class="status-pill" :class="{ good: !notification.read }">{{ notification.read ? 'Read' : 'New' }}</span>
              <div>
                <p class="account-name">{{ notification.title }}</p>
                <p class="notification-message">{{ notification.message }}</p>
                <p class="notification-time">{{ notification.time }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showSearch" class="dropdown-menu search-dropdown">
          <div class="search-input-wrapper">
            <i class="pi pi-search" aria-hidden="true"></i>
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="Search properties, valuations, users"
              @input="debouncedSearch"
            />
          </div>
          <div class="search-results">
            <div v-if="searchQuery" class="empty-state">Search service is not connected yet.</div>
            <div v-else class="search-suggestions">
              <button class="suggestion-item" type="button" @click="navigateToQuickLink('/properties')">
                <i class="pi pi-building" aria-hidden="true"></i>
                All properties
              </button>
              <button class="suggestion-item" type="button" @click="navigateToQuickLink('/valuations')">
                <i class="pi pi-calculator" aria-hidden="true"></i>
                Valuations
              </button>
              <button class="suggestion-item" type="button" @click="navigateToQuickLink('/reports')">
                <i class="pi pi-file-pdf" aria-hidden="true"></i>
                Reports
              </button>
            </div>
          </div>
        </div>

        <div v-if="showProfileMenu" class="dropdown-menu profile-dropdown">
          <div class="profile-header">
            <div class="account-avatar">{{ userInitials }}</div>
            <div>
              <p class="profile-name">{{ userName || 'Signed-in user' }}</p>
              <p class="profile-email">{{ userEmail || 'Profile details unavailable' }}</p>
            </div>
          </div>
          <div class="profile-menu-items">
            <button class="menu-item" type="button" @click="navigateToQuickLink('/profile')">
              <i class="pi pi-user" aria-hidden="true"></i>
              My profile
            </button>
            <button class="menu-item" type="button" @click="navigateToQuickLink('/settings')">
              <i class="pi pi-cog" aria-hidden="true"></i>
              Settings
            </button>
            <button class="menu-item" type="button" @click="handleLogout">
              <i class="pi pi-sign-out" aria-hidden="true"></i>
              Logout
            </button>
          </div>
        </div>
      </header>

      <div class="page-content">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePermissions } from '~/composables/usePermissions.js'
import { clearAuthTokens, getAccessToken } from '~/utils/authToken'

const router = useRouter()
const route = useRoute()
const {
  canAccessAdmin,
  canManageScrapers,
  canManageUsers,
  hasPermission
} = usePermissions()

const sidebarOpen = ref(false)
const showNotifications = ref(false)
const showSearch = ref(false)
const showProfileMenu = ref(false)
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const userName = ref('')
const userRole = ref('')
const userEmail = ref('')

type NavigationItem = {
  label: string
  to: string
  icon: string
  visible?: boolean
}

type NavigationGroup = {
  label: string
  admin?: boolean
  items: NavigationItem[]
}

const navigation = computed<NavigationGroup[]>(() => [
  {
    label: 'Workspace',
    items: [
      { label: 'Dashboard', to: '/dashboard', icon: 'pi pi-home' },
      { label: 'Properties', to: '/properties', icon: 'pi pi-building' },
      { label: 'Vehicles', to: '/vehicles', icon: 'pi pi-car' },
      { label: 'Valuations', to: '/valuations', icon: 'pi pi-calculator' },
      { label: 'Quick Valuation', to: '/valuations/quick', icon: 'pi pi-bolt' }
    ]
  },
  {
    label: 'Intelligence',
    items: [
      { label: 'Analytics', to: '/analytics', icon: 'pi pi-chart-bar' },
      { label: 'Property Map', to: '/map', icon: 'pi pi-map' },
      { label: 'Reports', to: '/reports', icon: 'pi pi-file-pdf' }
    ]
  },
  {
    label: 'Administration',
    admin: true,
    items: [
      { label: 'Scrapers', to: '/scrapers', icon: 'pi pi-globe', visible: canManageScrapers.value },
      { label: 'Users', to: '/users', icon: 'pi pi-users', visible: canManageUsers.value },
      { label: 'Settings', to: '/settings', icon: 'pi pi-cog' },
      { label: 'Audit Log', to: '/audit', icon: 'pi pi-shield', visible: hasPermission('system:audit') }
    ]
  }
])

const visibleNavigation = computed(() => {
  return navigation.value
    .filter((group) => !group.admin || canAccessAdmin.value)
    .map((group) => ({
      ...group,
      items: group.items.filter((item) => item.visible !== false)
    }))
    .filter((group) => group.items.length > 0)
})

const pages: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Operating view for property and vehicle valuation work.' },
  '/properties': { title: 'Properties', subtitle: 'Registry records, locations, owners, and valuation readiness.' },
  '/vehicles': { title: 'Vehicles', subtitle: 'Fleet assets, registration state, and valuation records.' },
  '/valuations': { title: 'Valuations', subtitle: 'Pricing decisions, audit state, and valuation history.' },
  '/valuations/quick': { title: 'Quick Valuation', subtitle: 'Rapid estimate workflow for field and desk review.' },
  '/analytics': { title: 'Analytics', subtitle: 'Market movement, municipal coverage, and compliance signals.' },
  '/map': { title: 'Property Map', subtitle: 'Geographic review of registered assets and boundaries.' },
  '/reports': { title: 'Reports', subtitle: 'Generate civic records, valuation summaries, and exports.' },
  '/settings': { title: 'Settings', subtitle: 'Operational controls, system configuration, and preferences.' },
  '/users': { title: 'Users', subtitle: 'Manage access for valuation and administrative teams.' },
  '/scrapers': { title: 'Web Scrapers', subtitle: 'Monitor public-data collection jobs and source health.' },
  '/audit': { title: 'Audit Log', subtitle: 'Trace security, compliance, and record-change activity.' },
  '/profile': { title: 'Profile', subtitle: 'Account details and workspace preferences.' }
}

const pageTitle = computed(() => pages[route.path]?.title || 'ValuAdis')
const pageSubtitle = computed(() => pages[route.path]?.subtitle || 'Civic property valuation platform.')

const notifications = ref<Array<{ id: number; title: string; message: string; time: string; read: boolean }>>([])

const userInitials = computed(() => {
  if (!userName.value) return 'VA'
  return userName.value
    .split(' ')
    .map((name) => name[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

function loadUserData() {
  const token = getAccessToken()
  if (!token) return

  try {
    const payloadPart = token.split('.')[1]
    if (!payloadPart) throw new Error('Missing token payload')
    let base64Payload = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    while (base64Payload.length % 4) base64Payload += '='
    const payload = JSON.parse(atob(base64Payload))
    userName.value = payload.name || payload.full_name || ''
    userRole.value = payload.role || payload.user_type || ''
    userEmail.value = payload.email || payload.sub || ''
  } catch {
    userName.value = ''
    userRole.value = ''
    userEmail.value = ''
  }
}

async function loadCurrentUser() {
  const token = getAccessToken()
  if (!token) return

  try {
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBaseUrl}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) return

    const user = await response.json()
    userName.value = user.full_name || user.name || userName.value
    userRole.value = formatUserRole(user.role || user.user_type || userRole.value)
    userEmail.value = user.email || user.sub || userEmail.value
  } catch {
  }
}

function formatUserRole(role: string) {
  return role
    ? role.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
    : ''
}

function isActive(item: { to: string }) {
  return route.path === item.to || (item.to !== '/dashboard' && route.path.startsWith(`${item.to}/`))
}

function closeDropdowns() {
  showNotifications.value = false
  showSearch.value = false
  showProfileMenu.value = false
}

function toggleNotifications() {
  const next = !showNotifications.value
  closeDropdowns()
  showNotifications.value = next
}

function toggleSearch() {
  const next = !showSearch.value
  closeDropdowns()
  showSearch.value = next
  if (next) nextTick(() => searchInput.value?.focus())
}

function toggleProfileMenu() {
  const next = !showProfileMenu.value
  closeDropdowns()
  showProfileMenu.value = next
}

function markAllAsRead() {
  notifications.value.forEach((notification) => {
    notification.read = true
  })
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {}, 250)
}

function navigateToQuickLink(path: string) {
  closeDropdowns()
  router.push(path)
}

function handleLogout() {
  clearAuthTokens()
  router.push('/login')
}

onMounted(() => {
  loadUserData()
  loadCurrentUser()
})
onUnmounted(() => {
  if (searchTimeout) clearTimeout(searchTimeout)
})
</script>
