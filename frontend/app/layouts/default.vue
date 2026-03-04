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
        <button class="sidebar-toggle" @click="toggleSidebar">
          <i class="pi pi-bars"></i>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <h3>Main Menu</h3>
          <ul class="nav-list">
            <li class="nav-item" :class="{ active: $route.path === '/' }">
              <a href="/" @click.prevent="$router.push('/')" class="nav-link">
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
            <li class="nav-item" :class="{ active: $route.path === '/reports' }">
              <a href="/reports" @click.prevent="$router.push('/reports')" class="nav-link">
                <i class="pi pi-file-pdf"></i>
                <span>Reports</span>
              </a>
            </li>
          </ul>
        </div>

        <div class="nav-section">
          <h3>Admin</h3>
          <ul class="nav-list">
            <li class="nav-item" :class="{ active: $route.path === '/users' }">
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
            <li class="nav-item" :class="{ active: $route.path === '/audit' }">
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
        <button class="logout-btn" @click="handleLogout">
          <i class="pi pi-sign-out"></i>
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- Mobile Overlay -->
    <div class="mobile-overlay" :class="{ active: sidebarOpen }" @click="toggleSidebar"></div>

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Top Header -->
      <header class="top-header">
        <div class="header-left">
          <button class="mobile-menu-toggle" @click="toggleSidebar">
            <i class="pi pi-bars"></i>
          </button>
          <div class="header-title">
            <h1>{{ pageTitle }}</h1>
            <p class="header-subtitle">{{ pageSubtitle }}</p>
          </div>
        </div>
        
        <div class="header-right">
          <div class="header-actions">
            <button class="action-btn">
              <i class="pi pi-bell"></i>
              <span class="notification-badge">3</span>
            </button>
            <button class="action-btn">
              <i class="pi pi-search"></i>
            </button>
            <div class="user-menu">
              <div class="user-avatar-small">
                <span>{{ userInitials }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { userName, userRole } = storeToRefs(authStore)

const sidebarOpen = ref(false)

const userInitials = computed(() => {
  if (!userName.value) return 'U'
  const names = userName.value.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/': 'Dashboard',
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
    '/': 'Property valuation overview and statistics',
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

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
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
