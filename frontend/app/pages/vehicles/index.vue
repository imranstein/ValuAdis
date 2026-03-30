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
        <NuxtLink to="/vehicles" class="nav-item active">
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
          <p class="user-role">Federal Auditor</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" v-model="searchQuery" placeholder="Search vehicle VIN, owner or model..." />
      </div>
      <div class="header-right">
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new-val">
            <span class="material-symbols-outlined">add</span> New Valuation
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrap">

        <nav class="breadcrumb">
          <span>Home</span><span class="bc-sep">/</span><span class="bc-active">Vehicles</span>
        </nav>

        <div class="page-hd">
          <div>
            <h1 class="page-title">Vehicles Ledger</h1>
            <p class="page-desc">Official federal vehicle registration and valuation database.</p>
          </div>
          <div class="page-hd-actions">
            <button class="btn-outline-action"><span class="material-symbols-outlined">filter_list</span> Filter</button>
            <button class="btn-outline-action"><span class="material-symbols-outlined">download</span> Export</button>
          </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card glass-card" v-for="s in stats" :key="s.label">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">{{ s.icon }}</span></div>
            <p class="stat-label">{{ s.label }}</p>
            <div class="stat-val-row">
              <h3 class="stat-value">{{ s.value }}</h3>
              <span class="stat-badge" :class="s.badgeClass">{{ s.badge }}</span>
            </div>
            <div class="stat-bar"><div class="stat-bar-fill" :class="s.fillClass" :style="`width:${s.pct}%`"></div></div>
          </div>
        </div>

        <!-- Table -->
        <div class="ledger-card glass-card">
          <div class="ledger-header">
            <h2 class="ledger-title">Vehicle Registry</h2>
            <span class="ledger-count">Showing {{ vehicles.length }} of 142,890 entries</span>
          </div>
          <div class="table-wrap">
            <table class="ledger-table">
              <thead>
                <tr class="table-head-row">
                  <th>VIN</th><th>Model &amp; Year</th><th>Owner</th><th>Last Valuation</th><th>Status</th><th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" v-for="v in vehicles" :key="v.vin">
                  <td class="td-vin">{{ v.vin }}</td>
                  <td>
                    <p class="td-model">{{ v.model }}</p>
                    <p class="td-meta">{{ v.year }} • {{ v.type }}</p>
                  </td>
                  <td>
                    <div class="td-owner">
                      <div class="owner-avatar" :style="`background:${v.avatarBg};color:${v.avatarColor}`">{{ v.initials }}</div>
                      <span class="owner-name">{{ v.owner }}</span>
                    </div>
                  </td>
                  <td class="td-value">{{ v.valuation }}</td>
                  <td><span class="status-badge" :class="v.statusClass">{{ v.status }}</span></td>
                  <td class="td-actions">
                    <button class="action-btn"><span class="material-symbols-outlined">visibility</span></button>
                    <button class="action-btn"><span class="material-symbols-outlined">more_vert</span></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <div class="pag-btns">
              <button class="pag-btn"><span class="material-symbols-outlined">chevron_left</span></button>
              <button class="pag-btn pag-active">1</button>
              <button class="pag-btn">2</button>
              <button class="pag-btn">3</button>
              <button class="pag-btn"><span class="material-symbols-outlined">chevron_right</span></button>
            </div>
            <span class="pag-info">Showing page 1 of 14,289</span>
          </div>
        </div>

      </div>
    </main>

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
definePageMeta({ middleware: 'auth' })
const searchQuery = ref('')
const stats = [
  { label: 'Total Registered Assets', value: '142,890', badge: '↑ 12%', badgeClass: 'badge-primary', icon: 'directions_car', pct: 75, fillClass: 'fill-primary' },
  { label: 'Active Valuations', value: '3,204', badge: 'Active', badgeClass: 'badge-secondary', icon: 'analytics', pct: 50, fillClass: 'fill-secondary' },
  { label: 'Portfolio Valuation', value: 'ETB 2.4B', badge: '↑ ETB 12M', badgeClass: 'badge-tertiary', icon: 'account_balance_wallet', pct: 65, fillClass: 'fill-tertiary' },
]
const vehicles = [
  { vin: '1HGBH41JXMN021XXX', model: 'Tesla Model S Plaid', year: '2023', type: 'Electric', owner: 'Abebe Selassie', initials: 'AS', avatarBg: '#e0e7ff', avatarColor: '#4338ca', valuation: 'ETB 5,890,000', status: 'Completed', statusClass: 'status-done' },
  { vin: '2T3WFREV7JW14XXXX', model: 'Toyota RAV4 Hybrid', year: '2022', type: 'Hybrid', owner: 'Marta Kebede', initials: 'MK', avatarBg: '#d1fae5', avatarColor: '#065f46', valuation: 'ETB 1,975,000', status: 'In Progress', statusClass: 'status-progress' },
  { vin: '5UXWX9C57G0S2XXXX', model: 'BMW X5 xDrive40i', year: '2021', type: 'ICE', owner: 'Tewodros Zewde', initials: 'TZ', avatarBg: '#f1f5f9', avatarColor: '#475569', valuation: 'ETB 3,400,000', status: 'Pending', statusClass: 'status-pending' },
  { vin: 'WBA8E3C51KG6XXXXX', model: 'Mercedes-Benz G-Class', year: '2024', type: 'Luxury', owner: 'Yared Lemi', initials: 'YL', avatarBg: '#fef3c7', avatarColor: '#92400e', valuation: 'ETB 10,670,000', status: 'Completed', statusClass: 'status-done' },
  { vin: 'WDCGG8HB8AF4XXXXX', model: 'Land Cruiser 300', year: '2023', type: 'SUV', owner: 'Tigist Haile', initials: 'TH', avatarBg: '#fce7f3', avatarColor: '#9d174d', valuation: 'ETB 7,200,000', status: 'Completed', statusClass: 'status-done' },
]
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
.header-right { display: flex; align-items: center; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; }
.icon-btn { background: none; border: none; cursor: pointer; color: #64748b; padding: 0.5rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #f1f5f9; }
.btn-new-val { display: flex; align-items: center; gap: 0.35rem; background: #006948; color: #fff; border: none; border-radius: 9999px; padding: 0.5rem 1.25rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.btn-new-val .material-symbols-outlined { font-size: 1rem; }
.btn-new-val:hover { opacity: 0.9; }

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
.btn-outline-action { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; background: #fff; border: 1px solid rgba(188,202,192,0.3); border-radius: 0.75rem; font-size: 0.8rem; font-weight: 500; color: #3d4a42; cursor: pointer; transition: background 0.2s; }
.btn-outline-action .material-symbols-outlined { font-size: 1rem; }
.btn-outline-action:hover { background: #f2f4f6; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.glass-card { background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(188,202,192,0.2); }
.stat-card { padding: 1.5rem; border-radius: 1.5rem; position: relative; overflow: hidden; }
.stat-bg-icon { position: absolute; top: 0; right: 0; padding: 1rem; opacity: 0.1; }
.stat-bg-icon .material-symbols-outlined { font-size: 4rem; }
.stat-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; margin: 0 0 0.5rem; }
.stat-val-row { display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 1rem; }
.stat-value { font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 800; color: #191c1e; margin: 0; }
.stat-badge { font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; gap: 0.2rem; }
.badge-primary { color: #006948; }
.badge-secondary { color: #4b41e1; }
.badge-tertiary { color: #825100; }
.stat-bar { height: 0.25rem; background: #f1f5f9; border-radius: 9999px; overflow: hidden; }
.stat-bar-fill { height: 100%; border-radius: 9999px; }
.fill-primary { background: #006948; }
.fill-secondary { background: #4b41e1; }
.fill-tertiary { background: #825100; }

/* Table */
.ledger-card { border-radius: 1.5rem; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.ledger-header { padding: 1.5rem 2rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.ledger-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #191c1e; margin: 0; }
.ledger-count { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
.table-wrap { overflow-x: auto; }
.ledger-table { width: 100%; text-align: left; border-collapse: collapse; }
.table-head-row { background: rgba(248,250,252,0.5); }
.table-head-row th { padding: 1rem 1.5rem; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #64748b; }
.text-right { text-align: right; }
.table-row { border-top: 1px solid #f1f5f9; transition: background 0.15s; }
.table-row:hover { background: rgba(248,250,252,0.85); }
.table-row td { padding: 1.25rem 1.5rem; }
.td-vin { font-family: monospace; font-size: 0.8rem; color: #065f46; }
.td-model { font-size: 0.875rem; font-weight: 700; color: #191c1e; margin: 0 0 0.15rem; }
.td-meta { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.td-owner { display: flex; align-items: center; gap: 0.5rem; }
.owner-avatar { width: 1.75rem; height: 1.75rem; border-radius: 50%; font-size: 0.65rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.owner-name { font-size: 0.875rem; font-weight: 500; }
.td-value { font-size: 0.875rem; font-weight: 600; color: #191c1e; }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.status-done { background: #d1fae5; color: #065f46; }
.status-progress { background: #dbeafe; color: #1d4ed8; }
.status-pending { background: #f1f5f9; color: #64748b; }
.td-actions { text-align: right; }
.action-btn { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 0.4rem; border-radius: 0.5rem; transition: all 0.15s; }
.action-btn:hover { background: #fff; color: #006948; }
.action-btn .material-symbols-outlined { font-size: 1.25rem; }

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
