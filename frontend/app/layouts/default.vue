<template>
  <div class="app-layout">
    <!-- Modern Sidebar -->
    <div class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">
            <i class="pi pi-building"></i>
          </div>
          <div class="logo-text">
            <h2>ValuAdis</h2>
            <p>Property Valuation Platform</p>
          </div>
        </div>
        <button class="sidebar-toggle" @click="toggleSidebar" aria-label="Toggle sidebar menu">
          <i class="pi pi-bars" aria-hidden="true"></i>
        </button>
      </div>

      <nav class="sidebar-nav" aria-label="Main navigation">
        <div class="nav-section">
          <h3>Main Menu</h3>
          <ul class="nav-list">
            <li class="nav-item" :class="{ active: $route.path === '/dashboard' }">
              <a href="/dashboard" @click.prevent="$router.push('/dashboard')" class="nav-link">
                <i class="pi pi-home"></i>
                <span>Dashboard</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path.startsWith('/properties') }">
              <a href="/properties" @click.prevent="$router.push('/properties')" class="nav-link">
                <i class="pi pi-building"></i>
                <span>Properties</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path === '/valuations' || $route.path.startsWith('/valuations/') && $route.path !== '/valuations/quick' }">
              <a href="/valuations" @click.prevent="$router.push('/valuations')" class="nav-link">
                <i class="pi pi-calculator"></i>
                <span>Valuations</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path === '/valuations/quick' }">
              <a href="/valuations/quick" @click.prevent="$router.push('/valuations/quick')" class="nav-link">
                <i class="pi pi-bolt"></i>
                <span>Quick Valuation</span>
              </a>
            </li>
          </ul>
        </div>

        <div class="nav-section">
          <h3>Analytics</h3>
          <ul class="nav-list">
            <li class="nav-item" :class="{ active: $route.path === '/analytics' }">
              <a href="/analytics" @click.prevent="$router.push('/analytics')" class="nav-link">
                <i class="pi pi-chart-bar"></i>
                <span>Analytics</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path === '/map' }">
              <a href="/map" @click.prevent="$router.push('/map')" class="nav-link">
                <i class="pi pi-map"></i>
                <span>Property Map</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path === '/reports' }">
              <a href="/reports" @click.prevent="$router.push('/reports')" class="nav-link">
                <i class="pi pi-file-pdf"></i>
                <span>Reports</span>
              </a>
            </li>
          </ul>
        </div>

        <div v-if="canAccessAdmin" class="nav-section">
          <h3>Admin</h3>
          <ul class="nav-list">
            <li v-if="canManageScrapers" class="nav-item" :class="{ active: $route.path === '/scrapers' }">
              <a href="/scrapers" @click.prevent="$router.push('/scrapers')" class="nav-link">
                <i class="pi pi-globe"></i>
                <span>Web Scrapers</span>
              </a>
            </li>
            <li v-if="canManageUsers" class="nav-item" :class="{ active: $route.path === '/users' }">
              <a href="/users" @click.prevent="$router.push('/users')" class="nav-link">
                <i class="pi pi-users"></i>
                <span>Users</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: $route.path === '/settings' }">
              <a href="/settings" @click.prevent="$router.push('/settings')" class="nav-link">
                <i class="pi pi-cog"></i>
                <span>Settings</span>
              </a>
            </li>
            <li v-if="hasPermission('system:audit')" class="nav-item" :class="{ active: $route.path === '/audit' }">
              <a href="/audit" @click.prevent="$router.push('/audit')" class="nav-link">
                <i class="pi pi-shield"></i>
                <span>Audit Log</span>
              </a>
            </li>
          </ul>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="user-avatar">
            <span>{{ userInitials }}</span>
          </div>
          <div class="user-info">
            <p class="user-name">{{ userName || 'Admin User' }}</p>
            <p class="user-role">{{ userRole || 'Administrator' }}</p>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" aria-label="Log out of your account">
          <i class="pi pi-sign-out" aria-hidden="true"></i>
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- Mobile Overlay -->
    <div class="mobile-overlay" :class="{ active: sidebarOpen }" @click="toggleSidebar"></div>

    <!-- Main Content Area -->
    <main class="main-content" role="main" id="main-content">
      <!-- Top Header -->
      <header class="top-header">
        <div class="header-left">
          <button class="mobile-menu-toggle" @click="toggleSidebar" aria-label="Open menu">
            <i class="pi pi-bars" aria-hidden="true"></i>
          </button>
          <div class="header-title">
            <h1>{{ pageTitle }}</h1>
            <p class="header-subtitle">{{ pageSubtitle }}</p>
          </div>
        </div>
        
        <div class="header-right">
          <div class="header-actions">
            <button class="action-btn" @click="toggleNotifications" title="Notifications" aria-label="View notifications">
              <i class="pi pi-bell" aria-hidden="true"></i>
              <span class="notification-badge" v-if="notificationCount > 0">{{ notificationCount }}</span>
            </button>
            <button class="action-btn" @click="toggleSearch" title="Search" aria-label="Search">
              <i class="pi pi-search" aria-hidden="true"></i>
            </button>
            <div class="user-menu" @click="toggleProfileMenu">
              <div class="user-avatar-small">
                <span>{{ userInitials }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Notifications Dropdown -->
        <div v-if="showNotifications" class="dropdown-menu notifications-dropdown">
          <div class="dropdown-header">
            <h3>Notifications</h3>
            <button @click="markAllAsRead" class="text-btn">Mark all as read</button>
          </div>
          <div class="notifications-list">
            <div v-if="notifications.length === 0" class="empty-state">
              <i class="pi pi-bell"></i>
              <p>No new notifications</p>
            </div>
            <div v-for="notification in notifications" :key="notification.id" class="notification-item" :class="{ unread: !notification.read }">
              <div class="notification-icon" :style="{ background: notification.color }">
                <i :class="notification.icon"></i>
              </div>
              <div class="notification-content">
                <p class="notification-title">{{ notification.title }}</p>
                <p class="notification-message">{{ notification.message }}</p>
                <span class="notification-time">{{ notification.time }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Search Dropdown -->
        <div v-if="showSearch" class="dropdown-menu search-dropdown">
          <div class="search-input-wrapper">
            <i class="pi pi-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search properties, valuations, users..."
              @input="debouncedSearch"
              ref="searchInput"
            />
          </div>
          <div class="search-results">
            <div v-if="searchQuery && searchResults.length === 0" class="empty-state">
              <i class="pi pi-search"></i>
              <p>No results found</p>
            </div>
            <div v-else-if="searchQuery" class="results-list">
              <div v-for="result in searchResults" :key="result.id" class="search-result-item" @click="navigateToResult(result)">
                <i :class="result.icon"></i>
                <div>
                  <p class="result-title">{{ result.title }}</p>
                  <span class="result-type">{{ result.type }}</span>
                </div>
              </div>
            </div>
            <div v-else class="search-suggestions">
              <p class="suggestions-title">Quick Links</p>
              <button @click="navigateToQuickLink('/properties')" class="suggestion-item">
                <i class="pi pi-building"></i>
                <span>All Properties</span>
              </button>
              <button @click="navigateToQuickLink('/valuations')" class="suggestion-item">
                <i class="pi pi-calculator"></i>
                <span>All Valuations</span>
              </button>
              <button @click="navigateToQuickLink('/reports')" class="suggestion-item">
                <i class="pi pi-file-pdf"></i>
                <span>Reports</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Profile Dropdown -->
        <div v-if="showProfileMenu" class="dropdown-menu profile-dropdown">
          <div class="profile-header">
            <div class="profile-avatar">
              <span>{{ userInitials }}</span>
            </div>
            <div>
              <p class="profile-name">{{ userName || 'Admin User' }}</p>
              <p class="profile-email">{{ userEmail || 'admin@valuadis.com' }}</p>
            </div>
          </div>
          <div class="profile-menu-items">
            <button @click="router.push('/profile')" class="menu-item">
              <i class="pi pi-user"></i>
              <span>My Profile</span>
            </button>
            <button @click="router.push('/settings')" class="menu-item">
              <i class="pi pi-cog"></i>
              <span>Settings</span>
            </button>
            <button @click="handleLogout" class="menu-item logout">
              <i class="pi pi-sign-out"></i>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="page-content">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { usePermissions } from '~/composables/usePermissions.js'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { 
  canAccessAdmin, 
  canManageUsers, 
  canManageScrapers, 
  hasPermission 
} = usePermissions()

const sidebarOpen = ref(false)
const showNotifications = ref(false)
const showSearch = ref(false)
const showProfileMenu = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searchInput = ref<HTMLInputElement | null>(null)

// User data from localStorage
const userName = ref('')
const userRole = ref('')
const userEmail = ref('')

// Load user data
const loadUserData = () => {
  const token = localStorage.getItem('valuadis_token')
  if (token) {
    // Decode JWT to get user info (simple decode, not verification)
    try {
      // Verify token has three parts
      const parts = token.split('.')
      if (parts.length !== 3) {
        throw new Error('Invalid token format')
      }
      
      // Guard against undefined payload
      const payloadPart = parts[1]
      if (!payloadPart) {
        throw new Error('Missing token payload')
      }
      
      // Convert base64url to standard base64
      let base64Payload = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
      // Add padding if needed
      while (base64Payload.length % 4) {
        base64Payload += '='
      }
      
      const payload = JSON.parse(atob(base64Payload))
      userName.value = payload.name || payload.full_name || 'Test User'
      userRole.value = payload.role || payload.user_type || 'Administrator'
      userEmail.value = payload.email || payload.sub || 'test@valuadis.com'
    } catch (e) {
      console.warn('Failed to decode JWT token:', e)
      userName.value = 'Test User'
      userRole.value = 'Administrator'
      userEmail.value = 'test@valuadis.com'
    }
  }
}

loadUserData()

// Notifications
const notifications = ref([
  {
    id: 1,
    title: 'New Valuation Request',
    message: 'Property at Bole Road requires valuation',
    time: '5 minutes ago',
    read: false,
    icon: 'pi pi-calculator',
    color: '#059669'
  },
  {
    id: 2,
    title: 'Report Generated',
    message: 'Monthly valuation report is ready',
    time: '1 hour ago',
    read: false,
    icon: 'pi pi-file-pdf',
    color: '#3b82f6'
  },
  {
    id: 3,
    title: 'System Update',
    message: 'New features available in settings',
    time: '3 hours ago',
    read: true,
    icon: 'pi pi-cog',
    color: '#8b5cf6'
  }
])

const notificationCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const userInitials = computed(() => {
  if (!userName.value) return 'U'
  const names = userName.value.split(' ')
  return names.map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/properties': 'Properties',
    '/valuations': 'Valuations',
    '/valuations/quick': 'Quick Valuation',
    '/analytics': 'Analytics',
    '/reports': 'Reports',
    '/users': 'Users',
    '/settings': 'Settings',
    '/audit': 'Audit Log'
  }
  return titles[route.path] || 'ValuAdis'
})

const pageSubtitle = computed(() => {
  const subtitles: Record<string, string> = {
    '/dashboard': 'Property valuation overview and statistics',
    '/properties': 'Manage and track property records',
    '/valuations': 'Property valuation history and reports',
    '/valuations/quick': 'Fast property valuation calculator',
    '/analytics': 'Data insights and market trends',
    '/reports': 'Generate and download reports',
    '/users': 'User management and permissions',
    '/settings': 'System configuration and preferences',
    '/audit': 'System activity and compliance logs'
  }
  return subtitles[route.path] || 'Ethiopian Property Valuation Platform'
})

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function toggleNotifications() {
  showNotifications.value = !showNotifications.value
  showSearch.value = false
  showProfileMenu.value = false
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  showNotifications.value = false
  showProfileMenu.value = false
  
  if (showSearch.value) {
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
  showNotifications.value = false
  showSearch.value = false
}

function markAllAsRead() {
  notifications.value.forEach(n => n.read = true)
}

// Debounced search function
let searchTimeout: NodeJS.Timeout | null = null

function handleSearch() {
  if (!searchQuery.value) {
    searchResults.value = []
    return
  }
  
  // In production, this would call the backend API search endpoint
  // For now, search results are empty until API is implemented
  searchResults.value = []
}

function debouncedSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    handleSearch()
  }, 300)
}

function navigateToResult(result: any) {
  router.push(result.path)
  showSearch.value = false
  searchQuery.value = ''
  searchResults.value = []
}

function navigateToQuickLink(path: string) {
  router.push(path)
  showSearch.value = false
  searchQuery.value = ''
  searchResults.value = []
}

function handleLogout() {
  localStorage.removeItem('valuadis_token')
  router.push('/login')
}

// Close dropdowns when clicking outside - using lifecycle hooks instead of watcher
function closeDropdowns(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.dropdown-menu') && !target.closest('.action-btn') && !target.closest('.user-menu')) {
    showNotifications.value = false
    showSearch.value = false
    showProfileMenu.value = false
  }
}

// Add lifecycle hooks for proper event listener management
onMounted(() => {
  document.addEventListener('click', closeDropdowns)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
/* Modern Layout Styles */
.app-layout {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Modern Sidebar */
.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 1000;
  transform: translateX(0);
  transition: transform 0.3s ease;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #059669, #047857);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.logo-text h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: white;
}

.logo-text p {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.sidebar-toggle {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Sidebar Navigation */
.sidebar-nav {
  padding: 1rem 0;
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

.nav-section {
  margin-bottom: 2rem;
  padding: 0 1rem;
}

.nav-section h3 {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
  margin: 0 0 1rem 0;
  letter-spacing: 0.05em;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active .nav-link {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.nav-link i {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Mobile Overlay */
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.mobile-overlay.active {
  display: block;
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Top Header */
.top-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-menu-toggle {
  display: none;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.mobile-menu-toggle:hover {
  background: #e2e8f0;
}

.header-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.header-subtitle {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  position: relative;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e2e8f0;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  padding: 2px 6px;
  border-radius: 999px;
  font-weight: 600;
}

.user-avatar-small {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
}

/* Dropdown Menus */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  z-index: 1000;
  min-width: 320px;
  max-width: 400px;
  max-height: 500px;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dropdown-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.text-btn {
  background: none;
  border: none;
  color: #059669;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.text-btn:hover {
  background: #f0fdf4;
}

/* Notifications Dropdown */
.notifications-dropdown {
  width: 380px;
}

.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #f0fdf4;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.notification-message {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0 0 0.25rem 0;
}

.notification-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Search Dropdown */
.search-dropdown {
  width: 450px;
}

.search-input-wrapper {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.search-input-wrapper i {
  color: #64748b;
}

.search-input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  color: #1e293b;
}

.search-input-wrapper input::placeholder {
  color: #94a3b8;
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
}

.results-list {
  padding: 0.5rem;
}

.search-result-item {
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.search-result-item:hover {
  background: #f8fafc;
}

.search-result-item i {
  color: #059669;
  font-size: 1.125rem;
}

.result-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.result-type {
  font-size: 0.75rem;
  color: #64748b;
}

.search-suggestions {
  padding: 1rem;
}

.suggestions-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
  margin: 0 0 0.75rem 0;
  letter-spacing: 0.05em;
}

.suggestion-item {
  width: 100%;
  padding: 0.75rem;
  border: none;
  background: none;
  text-align: left;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
  font-size: 0.875rem;
}

.suggestion-item:hover {
  background: #f8fafc;
  color: #059669;
}

.suggestion-item i {
  color: #94a3b8;
}

.suggestion-item:hover i {
  color: #059669;
}

/* Profile Dropdown */
.profile-dropdown {
  width: 280px;
}

.profile-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.profile-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.profile-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.profile-email {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.profile-menu-items {
  padding: 0.5rem;
}

.menu-item {
  width: 100%;
  padding: 0.75rem;
  border: none;
  background: none;
  text-align: left;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
}

.menu-item:hover {
  background: #f8fafc;
  color: #059669;
}

.menu-item.logout {
  color: #ef4444;
}

.menu-item.logout:hover {
  background: #fef2f2;
  color: #dc2626;
}

.menu-item i {
  width: 20px;
  text-align: center;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* Page Content */
.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .page-content {
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .top-header {
    padding: 1rem;
  }
  
  .header-title h1 {
    font-size: 1.25rem;
  }
  
  .header-subtitle {
    display: none;
  }
}
</style>
