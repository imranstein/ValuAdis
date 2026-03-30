<template>
  <div class="app-shell">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-title">ValuAdis</span>
        <p class="brand-sub">Property Valuation</p>
      </div>
      <nav class="sidebar-nav">
        <NuxtLink to="/properties" class="nav-item">
          <span class="material-symbols-outlined">domain</span><span>Properties</span>
        </NuxtLink>
        <NuxtLink to="/vehicles" class="nav-item">
          <span class="material-symbols-outlined">directions_car</span><span>Vehicles</span>
        </NuxtLink>
        <NuxtLink to="/valuations" class="nav-item">
          <span class="material-symbols-outlined">assessment</span><span>Valuations</span>
        </NuxtLink>
        <NuxtLink to="/map" class="nav-item">
          <span class="material-symbols-outlined">map</span><span>Maps</span>
        </NuxtLink>
        <NuxtLink to="/reports" class="nav-item">
          <span class="material-symbols-outlined">analytics</span><span>Reports</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item">
          <span class="material-symbols-outlined">settings</span><span>Settings</span>
        </NuxtLink>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">SA</div>
        <div>
          <p class="user-name">Super Admin</p>
          <p class="user-role">System Administrator</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" v-model="searchQuery" placeholder="Search users by name, email or role..." />
      </div>
      <div class="header-right">
        <nav class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink">Market Insights</a>
        </nav>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new" @click="showAddUserModal = true">
            <span class="material-symbols-outlined">person_add</span> Add User
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrap">

        <!-- Breadcrumb -->
        <nav class="breadcrumb">
          <span>Home</span>
          <span class="bc-sep">/</span>
          <span class="bc-active">Users</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h1 class="page-title">User Management</h1>
            <p class="page-desc">Manage system users, roles and permissions.</p>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">group</span></div>
            <p class="stat-label">Total Users</p>
            <h3 class="stat-value">247</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">↑ 12</span>
              <span class="stat-sub">this month</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">admin_panel_settings</span></div>
            <p class="stat-label">Administrators</p>
            <h3 class="stat-value">18</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">7%</span>
              <span class="stat-sub">of users</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">person_check</span></div>
            <p class="stat-label">Active Now</p>
            <h3 class="stat-value">42</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">17%</span>
              <span class="stat-sub">online</span>
            </div>
          </div>
        </div>

        <!-- Users Table -->
        <div class="table-card glass-card">
          <div class="table-header">
            <h2 class="table-title">System Users</h2>
            <div class="table-filters">
              <select v-model="selectedRole" class="filter-select">
                <option value="">All Roles</option>
                <option value="admin">Administrator</option>
                <option value="auditor">Auditor</option>
                <option value="appraiser">Appraiser</option>
                <option value="viewer">Viewer</option>
              </select>
              <select v-model="selectedStatus" class="filter-select">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
              </select>
              <button class="btn-reset" @click="resetFilters">
                <span class="material-symbols-outlined">refresh</span>
              </button>
            </div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr class="table-head-row">
                  <th>User</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Last Active</th>
                  <th>Status</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" v-for="u in filteredUsers" :key="u.id">
                  <td>
                    <div class="td-user">
                      <div class="user-avatar-sm" :style="`background:${u.avatarBg}`">{{ u.initials }}</div>
                      <span class="user-name-text">{{ u.name }}</span>
                    </div>
                  </td>
                  <td><span class="td-email">{{ u.email }}</span></td>
                  <td>
                    <span class="role-badge" :class="u.roleClass">{{ u.role }}</span>
                  </td>
                  <td><span class="td-dept">{{ u.department }}</span></td>
                  <td><span class="td-time">{{ u.lastActive }}</span></td>
                  <td>
                    <span class="status-badge" :class="u.statusClass">{{ u.status }}</span>
                  </td>
                  <td class="td-actions text-right">
                    <button class="action-btn" @click="editUser(u)"><span class="material-symbols-outlined">edit</span></button>
                    <button class="action-btn" @click="deleteUser(u)"><span class="material-symbols-outlined">delete</span></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <span class="pag-info">Showing {{ filteredUsers.length }} of 247 users</span>
            <div class="pag-btns">
              <button class="pag-btn"><span class="material-symbols-outlined">chevron_left</span></button>
              <button class="pag-btn pag-active">1</button>
              <button class="pag-btn">2</button>
              <button class="pag-btn">3</button>
              <button class="pag-btn"><span class="material-symbols-outlined">chevron_right</span></button>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <span class="footer-brand">ValuAdis</span>
      <p class="footer-copy">© 2025 ValuAdis. All rights reserved.</p>
      <div class="footer-links">
        <a href="#">Privacy Policy</a><a href="#">Terms of Service</a><a href="#">Contact Support</a>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

definePageMeta({ middleware: 'auth' })

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')
const showAddUserModal = ref(false)

const allUsers = [
  { id: 1, name: 'John Doe', initials: 'JD', email: 'john.doe@valuadis.gov.et', role: 'Administrator', roleClass: 'role-admin', department: 'Federal Audit', lastActive: '2 mins ago', status: 'Active', statusClass: 'status-active', avatarBg: '#006948' },
  { id: 2, name: 'Martha Kebede', initials: 'MK', email: 'martha.k@valuadis.gov.et', role: 'Auditor', roleClass: 'role-auditor', department: 'Property Valuation', lastActive: '1 hour ago', status: 'Active', statusClass: 'status-active', avatarBg: '#4b41e1' },
  { id: 3, name: 'Abebe Bikila', initials: 'AB', email: 'abebe.b@valuadis.gov.et', role: 'Appraiser', roleClass: 'role-appraiser', department: 'Field Operations', lastActive: '3 hours ago', status: 'Active', statusClass: 'status-active', avatarBg: '#825100' },
  { id: 4, name: 'Selamawit K.', initials: 'SK', email: 'selamawit@valuadis.gov.et', role: 'Auditor', roleClass: 'role-auditor', department: 'Compliance', lastActive: 'Yesterday', status: 'Inactive', statusClass: 'status-inactive', avatarBg: '#e0e7ff' },
  { id: 5, name: 'Yonas Lemma', initials: 'YL', email: 'yonas.l@valuadis.gov.et', role: 'Viewer', roleClass: 'role-viewer', department: 'Records', lastActive: '2 days ago', status: 'Pending', statusClass: 'status-pending', avatarBg: '#fef3c7' },
]

const filteredUsers = computed(() => {
  let filtered = allUsers
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
  }
  if (selectedRole.value) {
    filtered = filtered.filter(u => u.roleClass === `role-${selectedRole.value}`)
  }
  if (selectedStatus.value) {
    filtered = filtered.filter(u => u.status.toLowerCase() === selectedStatus.value)
  }
  return filtered
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedRole.value = ''
  selectedStatus.value = ''
}

const editUser = (u: any) => console.log('Edit user:', u.name)
const deleteUser = (u: any) => confirm(`Delete user ${u.name}?`)

useHead({
  title: 'User Management — ValuAdis',
  meta: [{ name: 'description', content: 'Manage system users and permissions.' }]
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.app-shell { display: flex; min-height: 100vh; background: #f7f9fb; font-family: 'Inter', sans-serif; color: #191c1e; }

/* Sidebar */
.sidebar { position: fixed; left: 0; top: 0; height: 100%; width: 16rem; background: rgba(248,250,252,0.7); backdrop-filter: blur(20px); border-right: 1px solid rgba(226,232,240,0.2); display: flex; flex-direction: column; padding: 1.5rem 1rem; z-index: 50; }
.sidebar-brand { padding: 0 0.5rem; margin-bottom: 2.5rem; }
.brand-title { display: block; font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: #065f46; }
.brand-sub { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; margin-top: 0.2rem; }
.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
.nav-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.75rem; border-radius: 0.75rem; font-size: 0.875rem; color: #475569; text-decoration: none; transition: all 0.2s; }
.nav-item:hover { color: #006948; background: rgba(248,250,252,0.6); }
.nav-item.active { color: #005137; font-weight: 600; background: rgba(0,105,72,0.06); border-right: 3px solid #006948; }
.nav-item .material-symbols-outlined { font-size: 1.25rem; }
.sidebar-user { display: flex; align-items: center; gap: 0.75rem; padding: 1rem 0.5rem; border-top: 1px solid rgba(226,232,240,0.2); margin-top: auto; }
.user-avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; background: #00855d; color: #fff; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; }
.user-name { font-size: 0.8rem; font-weight: 700; margin: 0; }
.user-role { font-size: 0.7rem; color: #94a3b8; margin: 0; }

/* Header */
.top-header { position: fixed; top: 0; right: 0; width: calc(100% - 16rem); height: 4rem; z-index: 40; background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(226,232,240,0.2); display: flex; align-items: center; justify-content: space-between; padding: 0 2rem; }
.search-wrap { position: relative; flex: 1; max-width: 28rem; }
.search-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 1.1rem; }
.search-input { width: 100%; padding: 0.5rem 1rem 0.5rem 2.5rem; background: #f1f5f9; border: none; border-radius: 9999px; font-size: 0.875rem; outline: none; }
.header-right { display: flex; align-items: center; gap: 1.5rem; }
.header-links { display: flex; gap: 1rem; }
.hlink { font-size: 0.875rem; font-weight: 500; color: #64748b; text-decoration: none; transition: color 0.2s; }
.hlink:hover { color: #006948; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; }
.icon-btn { background: none; border: none; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #f1f5f9; }
.btn-new { display: flex; align-items: center; gap: 0.35rem; background: #006948; color: #fff; border: none; border-radius: 9999px; padding: 0.5rem 1.25rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.btn-new:hover { opacity: 0.9; }

/* Main */
.main-content { margin-left: 16rem; padding-top: 4rem; flex: 1; min-height: 100vh; }
.content-wrap { padding: 2.5rem 2rem; }

/* Breadcrumb */
.breadcrumb { display: flex; align-items: center; gap: 0.4rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; margin-bottom: 1.5rem; }
.bc-sep { margin: 0 0.2rem; }
.bc-active { color: #065f46; }

/* Page header */
.page-hd { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; gap: 1rem; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2.25rem; font-weight: 800; letter-spacing: -0.02em; color: #191c1e; margin: 0 0 0.4rem; }
.page-desc { font-size: 0.95rem; color: #3d4a42; margin: 0; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.glass-card { background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(188,202,192,0.2); }
.stat-card { padding: 1.5rem; border-radius: 1.5rem; position: relative; overflow: hidden; }
.stat-bg-icon { position: absolute; top: 0; right: 0; padding: 1rem; opacity: 0.1; }
.stat-bg-icon .material-symbols-outlined { font-size: 4rem; }
.stat-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; margin: 0 0 0.5rem; }
.stat-value { font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 800; color: #191c1e; margin: 0 0 1rem; }
.stat-badge-wrap { display: flex; align-items: center; gap: 0.5rem; }
.stat-badge { font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 9999px; }
.badge-green { background: #d1fae5; color: #065f46; }
.badge-indigo { background: #e0e7ff; color: #4b41e1; }
.badge-amber { background: #fef3c7; color: #92400e; }
.stat-sub { font-size: 0.7rem; color: #94a3b8; font-style: italic; }

/* Table */
.table-card { border-radius: 1.5rem; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.table-header { padding: 1.5rem 2rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.table-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #191c1e; margin: 0; }
.table-filters { display: flex; gap: 0.75rem; align-items: center; }
.filter-select { padding: 0.5rem 1rem; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 0.5rem; font-size: 0.8rem; color: #475569; }
.btn-reset { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 0.5rem; }
.btn-reset:hover { color: #006948; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; text-align: left; border-collapse: collapse; }
.table-head-row { background: rgba(248,250,252,0.5); }
.table-head-row th { padding: 1rem 1.5rem; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #64748b; }
.text-right { text-align: right; }
.table-row { border-top: 1px solid #f1f5f9; transition: background 0.15s; }
.table-row:hover { background: rgba(248,250,252,0.85); }
.table-row td { padding: 1.25rem 1.5rem; }
.td-user { display: flex; align-items: center; gap: 0.75rem; }
.user-avatar-sm { width: 2rem; height: 2rem; border-radius: 50%; color: #fff; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.user-name-text { font-weight: 600; color: #191c1e; }
.td-email { font-size: 0.875rem; color: #475569; }
.td-dept { font-size: 0.875rem; color: #64748b; }
.td-time { font-size: 0.875rem; color: #94a3b8; }
.role-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.role-admin { background: #fecaca; color: #dc2626; }
.role-auditor { background: #dbeafe; color: #1e40af; }
.role-appraiser { background: #d1fae5; color: #065f46; }
.role-viewer { background: #e2e8f0; color: #475569; }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.status-active { background: #d1fae5; color: #065f46; }
.status-inactive { background: #e2e8f0; color: #64748b; }
.status-pending { background: #fef3c7; color: #92400e; }
.td-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.action-btn { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 0.4rem; border-radius: 0.5rem; transition: all 0.15s; }
.action-btn:hover { background: #fff; color: #006948; }

/* Pagination */
.pagination { padding: 1.5rem 2rem; background: rgba(248,250,252,0.3); border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.pag-btns { display: flex; gap: 0.4rem; }
.pag-btn { width: 2rem; height: 2rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; background: #fff; font-size: 0.75rem; font-weight: 700; color: #475569; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.pag-btn:hover { color: #006948; border-color: #006948; }
.pag-btn.pag-active { background: #006948; color: #fff; border-color: #006948; }
.pag-btn .material-symbols-outlined { font-size: 0.9rem; }
.pag-info { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }

/* Footer */
.app-footer { margin-left: 16rem; padding: 2rem 3rem; border-top: 1px solid rgba(226,232,240,0.15); background: #f8fafc; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>
