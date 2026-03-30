<template>
  <div class="app-shell">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-title">ValuAdis</span>
        <p class="brand-sub">Property Valuation</p>
      </div>
      <nav class="sidebar-nav">
        <NuxtLink to="/properties" class="nav-item active">
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
        <div class="user-avatar">JD</div>
        <div>
          <p class="user-name">John Doe</p>
          <p class="user-role">Property Auditor</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" v-model="searchQuery" placeholder="Search properties by address, type or ID..." />
      </div>
      <div class="header-right">
        <nav class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink">Market Insights</a>
        </nav>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new" @click="router.push('/properties/create')">
            <span class="material-symbols-outlined">add</span> Create Property
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
          <span class="bc-active">Properties</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h1 class="page-title">Property Registry</h1>
            <p class="page-desc">Official federal property database. Manage land titles, buildings, and real estate assets.</p>
          </div>
          <div class="page-hd-actions">
            <button class="btn-outline" @click="exportProperties">
              <span class="material-symbols-outlined">download</span> Export
            </button>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">domain</span></div>
            <p class="stat-label">Total Properties</p>
            <h3 class="stat-value">8,492</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">↑ 4.2%</span>
              <span class="stat-sub">this quarter</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">location_city</span></div>
            <p class="stat-label">Commercial Assets</p>
            <h3 class="stat-value">3,204</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">38%</span>
              <span class="stat-sub">of portfolio</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">home</span></div>
            <p class="stat-label">Residential</p>
            <h3 class="stat-value">4,891</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">58%</span>
              <span class="stat-sub">of portfolio</span>
            </div>
          </div>
        </div>

        <!-- Properties Table -->
        <div class="table-card glass-card">
          <div class="table-header">
            <h2 class="table-title">Property Records</h2>
            <div class="table-filters">
              <select v-model="selectedMunicipality" class="filter-select">
                <option value="">All Municipalities</option>
                <option value="Addis Ababa">Addis Ababa</option>
                <option value="Mekelle">Mekelle</option>
                <option value="Dire Dawa">Dire Dawa</option>
                <option value="Bahir Dar">Bahir Dar</option>
              </select>
              <select v-model="selectedType" class="filter-select">
                <option value="">All Types</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="industrial">Industrial</option>
                <option value="agricultural">Agricultural</option>
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
                  <th>Property ID</th>
                  <th>Address</th>
                  <th>Type</th>
                  <th>Municipality</th>
                  <th class="text-right">Market Value</th>
                  <th>Status</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" v-for="p in filteredProperties" :key="p.id">
                  <td><span class="td-id">{{ p.id }}</span></td>
                  <td>
                    <div class="td-address">
                      <span class="material-symbols-outlined td-icon">location_on</span>
                      <span>{{ p.address }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="type-badge" :class="p.type">{{ p.typeLabel }}</span>
                  </td>
                  <td><span class="td-muni">{{ p.municipality }}</span></td>
                  <td class="text-right"><span class="td-value">{{ p.value }}</span></td>
                  <td>
                    <span class="status-badge" :class="p.statusClass">{{ p.status }}</span>
                  </td>
                  <td class="td-actions text-right">
                    <button class="action-btn" @click="viewProperty(p)"><span class="material-symbols-outlined">visibility</span></button>
                    <button class="action-btn" @click="editProperty(p)"><span class="material-symbols-outlined">edit</span></button>
                    <button class="action-btn"><span class="material-symbols-outlined">more_vert</span></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <span class="pag-info">Showing {{ filteredProperties.length }} of 8,492 properties</span>
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
import { useRouter } from 'vue-router'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const searchQuery = ref('')
const selectedMunicipality = ref('')
const selectedType = ref('')

const allProperties = [
  { id: 'PRP-2024-001', address: 'Bole Road, Block 47', type: 'commercial', typeLabel: 'Commercial', municipality: 'Addis Ababa', value: 'ETB 45,000,000', status: 'Active', statusClass: 'status-active' },
  { id: 'PRP-2024-002', address: 'Mekelle Stadium Area', type: 'residential', typeLabel: 'Residential', municipality: 'Mekelle', value: 'ETB 12,500,000', status: 'Active', statusClass: 'status-active' },
  { id: 'PRP-2024-003', address: 'Industrial Zone 4', type: 'industrial', typeLabel: 'Industrial', municipality: 'Dire Dawa', value: 'ETB 89,000,000', status: 'Pending', statusClass: 'status-pending' },
  { id: 'PRP-2024-004', address: 'Lake Tana Shore', type: 'agricultural', typeLabel: 'Agricultural', municipality: 'Bahir Dar', value: 'ETB 8,200,000', status: 'Active', statusClass: 'status-active' },
  { id: 'PRP-2024-005', address: 'Piassa Commercial Center', type: 'commercial', typeLabel: 'Commercial', municipality: 'Addis Ababa', value: 'ETB 120,000,000', status: 'Under Review', statusClass: 'status-review' },
]

const filteredProperties = computed(() => {
  let filtered = allProperties
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => p.address.toLowerCase().includes(q) || p.id.toLowerCase().includes(q))
  }
  if (selectedMunicipality.value) {
    filtered = filtered.filter(p => p.municipality === selectedMunicipality.value)
  }
  if (selectedType.value) {
    filtered = filtered.filter(p => p.type === selectedType.value)
  }
  return filtered
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedMunicipality.value = ''
  selectedType.value = ''
}

const viewProperty = (p: any) => router.push(`/properties/${p.id}`)
const editProperty = (p: any) => router.push(`/properties/edit/${p.id}`)
const exportProperties = () => console.log('Exporting...')

useHead({
  title: 'Property Registry — ValuAdis',
  meta: [{ name: 'description', content: 'Federal property database management.' }]
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
.page-hd-actions { display: flex; gap: 0.75rem; }
.btn-outline { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; background: #fff; border: 1px solid rgba(188,202,192,0.3); border-radius: 0.75rem; font-size: 0.8rem; font-weight: 500; color: #3d4a42; cursor: pointer; transition: background 0.2s; }
.btn-outline:hover { background: #f2f4f6; }

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
.td-id { font-family: monospace; font-weight: 700; color: #065f46; }
.td-address { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; }
.td-icon { font-size: 1rem; color: #94a3b8; }
.td-muni { font-size: 0.875rem; color: #475569; }
.td-value { font-weight: 700; color: #191c1e; }
.type-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.type-badge.commercial { background: #dbeafe; color: #1e40af; }
.type-badge.residential { background: #d1fae5; color: #065f46; }
.type-badge.industrial { background: #e9d5ff; color: #7c3aed; }
.type-badge.agricultural { background: #fef3c7; color: #92400e; }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.status-active { background: #d1fae5; color: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-review { background: #dbeafe; color: #1e40af; }
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
