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
        <NuxtLink to="/valuations" class="nav-item active">
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
        <div class="user-avatar">AP</div>
        <div>
          <p class="user-name">Admin Panel</p>
          <p class="user-role">Verified Officer</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" v-model="searchQuery" placeholder="Search valuations, assets, or IDs..." />
      </div>
      <div class="header-right">
        <nav class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink hlink-active">Market Insights</a>
        </nav>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new-val" @click="router.push('/valuations/quick')">
            <span class="material-symbols-outlined">add</span> New Valuation
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
          <span class="material-symbols-outlined bc-chevron">chevron_right</span>
          <span class="bc-active">Valuations</span>
        </nav>

        <!-- Hero Section -->
        <div class="hero-section">
          <div class="hero-text">
            <h1 class="page-title">Valuations Hub</h1>
            <p class="page-desc">The definitive digital ledger for national asset appraisals. Monitoring ETB 1.4B in active market valuations across all government sectors.</p>
          </div>
          <div class="hero-actions">
            <button class="btn-export" @click="exportValuations">
              <span class="material-symbols-outlined">download</span> Export Ledger
            </button>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">account_balance</span></div>
            <p class="stat-label">Total Market Value</p>
            <h3 class="stat-value">ETB 1.48B</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">↑ 12.4%</span>
              <span class="stat-sub">from last quarter</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">verified</span></div>
            <p class="stat-label">Compliance Rate</p>
            <h3 class="stat-value">98.4%</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">OPTIMAL</span>
              <span class="stat-sub">against national benchmarks</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">schedule</span></div>
            <p class="stat-label">Pending Appraisals</p>
            <h3 class="stat-value">142</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">ATTENTION</span>
              <span class="stat-sub">avg. 48h resolution time</span>
            </div>
          </div>
        </div>

        <!-- Valuations Table -->
        <div class="valuations-card">
          <div class="valuations-header">
            <h2 class="valuations-title">Appraisal History</h2>
            <div class="valuations-actions">
              <button class="icon-btn-round"><span class="material-symbols-outlined">filter_list</span></button>
              <button class="icon-btn-round"><span class="material-symbols-outlined">sort</span></button>
            </div>
          </div>
          <div class="table-wrap">
            <table class="valuations-table">
              <thead>
                <tr class="table-head-row">
                  <th>Valuation ID</th>
                  <th>Asset Type</th>
                  <th>Location</th>
                  <th class="text-right">Market Value</th>
                  <th class="text-center">Compliance Status</th>
                  <th>Validator</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" v-for="v in valuations" :key="v.id">
                  <td><span class="td-id">{{ v.id }}</span></td>
                  <td>
                    <div class="td-type">
                      <span class="material-symbols-outlined td-icon">{{ v.icon }}</span>
                      <span>{{ v.type }}</span>
                    </div>
                  </td>
                  <td><span class="td-location">{{ v.location }}</span></td>
                  <td class="text-right"><span class="td-value">{{ v.value }}</span></td>
                  <td class="text-center">
                    <span class="compliance-badge" :class="v.statusClass">
                      <span class="dot"></span>{{ v.status }}
                    </span>
                  </td>
                  <td>
                    <div class="td-validator">
                      <div class="validator-avatar" :style="`background:${v.avatarBg}`">{{ v.initials }}</div>
                      <span class="validator-name">{{ v.validator }}</span>
                    </div>
                  </td>
                  <td>
                    <button class="action-btn" @click="viewValuation(v)"><span class="material-symbols-outlined">more_vert</span></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <span class="pag-info">Showing 1 to 4 of 1,248 active appraisals</span>
            <div class="pag-btns">
              <button class="pag-btn"><span class="material-symbols-outlined">chevron_left</span></button>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const searchQuery = ref('')

const valuations = [
  { id: 'SP-2024-001', type: 'Commercial Land', icon: 'domain', location: 'Addis Ababa, Piazza', value: '$4,200,000', status: 'Certified', statusClass: 'status-certified', validator: 'Dr. Selamawit K.', initials: 'SK', avatarBg: '#e0e7ff' },
  { id: 'SP-2024-002', type: 'Industrial Plant', icon: 'factory', location: 'Bole Lemi Zone', value: '$12,850,000', status: 'Pending', statusClass: 'status-pending', validator: 'Abebe B.', initials: 'AB', avatarBg: '#d1fae5' },
  { id: 'SP-2024-003', type: 'Govt HQ', icon: 'apartment', location: 'Arat Kilo District', value: '$25,000,000', status: 'Flagged', statusClass: 'status-flagged', validator: 'Hanna M.', initials: 'HM', avatarBg: '#fce7f3' },
  { id: 'SP-2024-004', type: 'Fleet Cluster A', icon: 'directions_car', location: 'National Logistics Hub', value: '$1,120,000', status: 'Certified', statusClass: 'status-certified', validator: 'Yonas L.', initials: 'YL', avatarBg: '#fef3c7' },
]

const viewValuation = (v: any) => {
  router.push(`/valuations/${v.id}`)
}

const exportValuations = () => {
  console.log('Exporting valuations...')
}

useHead({
  title: 'Valuations Hub — ValuAdis',
  meta: [{ name: 'description', content: 'National asset appraisals and valuations hub.' }]
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
.hlink-active { color: #065f46; font-weight: 700; border-bottom: 2px solid #006948; padding-bottom: 0.1rem; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; }
.icon-btn { background: none; border: none; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #f1f5f9; }
.btn-new-val { display: flex; align-items: center; gap: 0.35rem; background: #006948; color: #fff; border: none; border-radius: 9999px; padding: 0.5rem 1.25rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.btn-new-val .material-symbols-outlined { font-size: 1rem; }
.btn-new-val:hover { opacity: 0.9; }

/* Main */
.main-content { margin-left: 16rem; padding-top: 4rem; flex: 1; min-height: 100vh; }
.content-wrap { padding: 2.5rem 3rem; max-width: 1600px; }

/* Breadcrumb */
.breadcrumb { display: flex; align-items: center; gap: 0.4rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; margin-bottom: 2rem; }
.bc-chevron { font-size: 0.875rem; color: #cbd5e1; }
.bc-active { color: #065f46; }

/* Hero Section */
.hero-section { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2.5rem; gap: 1.5rem; }
.hero-text { max-width: 40rem; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2.25rem; font-weight: 800; color: #191c1e; margin: 0 0 0.75rem; }
.page-desc { font-size: 1.125rem; color: #3d4a42; line-height: 1.6; margin: 0; }
.hero-actions { display: flex; gap: 0.75rem; }
.btn-export { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: 1px solid #bccac0; background: #fff; color: #006948; border-radius: 0.75rem; font-size: 0.875rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-export:hover { background: #f2f4f6; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2.5rem; }
.glass-card { background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(188,202,192,0.2); }
.stat-card { padding: 2rem; border-radius: 1.5rem; position: relative; overflow: hidden; transition: all 0.2s; }
.stat-card:hover { transform: scale(1.02); }
.stat-bg-icon { position: absolute; top: 0; right: 0; width: 6rem; height: 6rem; background: linear-gradient(135deg, rgba(0,105,72,0.05) 0%, transparent 70%); border-bottom-left-radius: 100%; display: flex; align-items: center; justify-content: center; }
.stat-bg-icon .material-symbols-outlined { font-size: 2rem; color: rgba(0,105,72,0.2); }
.stat-label { font-size: 0.875rem; font-weight: 500; color: #64748b; margin: 0 0 0.5rem; }
.stat-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #065f46; margin: 0 0 1rem; }
.stat-badge-wrap { display: flex; align-items: center; gap: 0.75rem; }
.stat-badge { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; padding: 0.15rem 0.5rem; border-radius: 9999px; }
.badge-green { background: #d1fae5; color: #065f46; }
.badge-indigo { background: #e0e7ff; color: #4b41e1; }
.badge-amber { background: #fef3c7; color: #92400e; }
.stat-sub { font-size: 0.75rem; color: #94a3b8; font-style: italic; }

/* Valuations Table Card */
.valuations-card { background: rgba(255,255,255,0.5); backdrop-filter: blur(8px); border-radius: 2rem; border: 1px solid rgba(226,232,240,0.5); box-shadow: 0 1px 4px rgba(0,0,0,0.04); overflow: hidden; }
.valuations-header { padding: 2rem 2rem 1.5rem; border-bottom: 1px solid rgba(226,232,240,0.5); display: flex; justify-content: space-between; align-items: center; }
.valuations-title { font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; color: #191c1e; margin: 0; }
.valuations-actions { display: flex; gap: 0.5rem; }
.icon-btn-round { width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; background: #fff; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.icon-btn-round:hover { border-color: #006948; color: #006948; }
.table-wrap { overflow-x: auto; }
.valuations-table { width: 100%; text-align: left; border-collapse: collapse; }
.table-head-row { background: rgba(248,250,252,0.5); }
.table-head-row th { padding: 1.25rem 2rem; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #64748b; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.table-row { border-top: 1px solid #f1f5f9; transition: background 0.15s; }
.table-row:hover { background: rgba(255,255,255,0.85); }
.table-row td { padding: 1.5rem 2rem; }
.td-id { font-family: monospace; font-weight: 700; color: #065f46; }
.td-type { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; }
.td-icon { font-size: 1.1rem; color: #94a3b8; }
.td-location { font-size: 0.875rem; color: #475569; }
.td-value { font-weight: 700; color: #191c1e; }
.compliance-badge { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.compliance-badge .dot { width: 0.375rem; height: 0.375rem; border-radius: 50%; }
.status-certified { background: #d1fae5; color: #065f46; }
.status-certified .dot { background: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-pending .dot { background: #92400e; }
.status-flagged { background: #fecaca; color: #dc2626; }
.status-flagged .dot { background: #dc2626; }
.td-validator { display: flex; align-items: center; gap: 0.5rem; }
.validator-avatar { width: 1.5rem; height: 1.5rem; border-radius: 50%; font-size: 0.6rem; font-weight: 700; color: #475569; display: flex; align-items: center; justify-content: center; }
.validator-name { font-size: 0.8rem; color: #475569; }
.action-btn { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 0.25rem; }
.action-btn:hover { color: #006948; }

/* Pagination */
.pagination { padding: 1.5rem 2rem; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: rgba(248,250,252,0.3); }
.pag-info { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
.pag-btns { display: flex; gap: 0.5rem; }
.pag-btn { width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; background: #fff; color: #475569; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.pag-btn:hover { border-color: #006948; color: #006948; }

/* Footer */
.app-footer { margin-left: 16rem; padding: 2rem 3rem; border-top: 1px solid rgba(226,232,240,0.15); background: #f8fafc; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>
