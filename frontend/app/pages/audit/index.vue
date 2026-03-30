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
        <NuxtLink to="/audit" class="nav-item active">
          <span class="material-symbols-outlined">fact_check</span><span>Audit</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item">
          <span class="material-symbols-outlined">settings</span><span>Settings</span>
        </NuxtLink>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">AO</div>
        <div>
          <p class="user-name">Audit Officer</p>
          <p class="user-role">Compliance Team</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" placeholder="Search audit logs..." />
      </div>
      <div class="header-right">
        <nav class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink">Market Insights</a>
        </nav>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new">New Valuation</button>
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
          <span class="bc-active">Audit Log</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h1 class="page-title">Audit Log</h1>
            <p class="page-desc">System activity tracking and compliance monitoring.</p>
          </div>
          <div class="page-hd-actions">
            <button class="btn-outline">
              <span class="material-symbols-outlined">download</span> Export
            </button>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">fact_check</span></div>
            <p class="stat-label">Total Events</p>
            <h3 class="stat-value">24,892</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">↑ 8.2%</span>
              <span class="stat-sub">this month</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">warning</span></div>
            <p class="stat-label">Alerts</p>
            <h3 class="stat-value">14</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">3 urgent</span>
              <span class="stat-sub">requires attention</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">verified</span></div>
            <p class="stat-label">Compliance Rate</p>
            <h3 class="stat-value">99.4%</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">OPTIMAL</span>
              <span class="stat-sub">within thresholds</span>
            </div>
          </div>
        </div>

        <!-- Audit Log Table -->
        <div class="table-card glass-card">
          <div class="table-header">
            <h2 class="table-title">Activity Log</h2>
            <div class="table-filters">
              <select class="filter-select">
                <option>All Events</option>
                <option>CREATE</option>
                <option>UPDATE</option>
                <option>DELETE</option>
                <option>LOGIN</option>
              </select>
              <button class="btn-reset"><span class="material-symbols-outlined">refresh</span></button>
            </div>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr class="table-head-row">
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Details</th>
                  <th>IP Address</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr class="table-row" v-for="log in auditLogs" :key="log.id">
                  <td><span class="td-time">{{ log.timestamp }}</span></td>
                  <td>
                    <div class="td-user">
                      <div class="user-avatar-sm">{{ log.initials }}</div>
                      <span>{{ log.user }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="action-badge" :class="log.actionClass">{{ log.action }}</span>
                  </td>
                  <td><span class="td-resource">{{ log.resource }}</span></td>
                  <td><span class="td-details">{{ log.details }}</span></td>
                  <td><span class="td-ip">{{ log.ip }}</span></td>
                  <td>
                    <span class="status-badge" :class="log.statusClass">{{ log.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <span class="pag-info">Showing 6 of 24,892 events</span>
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
definePageMeta({ middleware: 'auth' })

const auditLogs = [
  { id: 1, timestamp: '2024-11-20 14:32:15', user: 'John Doe', initials: 'JD', action: 'CREATE', actionClass: 'act-create', resource: 'Property', details: 'Created PRP-2024-0891', ip: '192.168.1.45', status: 'Success', statusClass: 'status-success' },
  { id: 2, timestamp: '2024-11-20 14:28:03', user: 'Martha Kebede', initials: 'MK', action: 'UPDATE', actionClass: 'act-update', resource: 'Valuation', details: 'Modified SP-2024-0042', ip: '192.168.1.52', status: 'Success', statusClass: 'status-success' },
  { id: 3, timestamp: '2024-11-20 14:15:47', user: 'Abebe B.', initials: 'AB', action: 'LOGIN', actionClass: 'act-login', resource: 'System', details: 'User authentication', ip: '192.168.1.38', status: 'Success', statusClass: 'status-success' },
  { id: 4, timestamp: '2024-11-20 13:58:22', user: 'System', initials: 'SY', action: 'DELETE', actionClass: 'act-delete', resource: 'Draft', details: 'Auto-cleared expired draft', ip: '127.0.0.1', status: 'Success', statusClass: 'status-success' },
  { id: 5, timestamp: '2024-11-20 13:45:11', user: 'Selamawit K.', initials: 'SK', action: 'EXPORT', actionClass: 'act-export', resource: 'Report', details: 'Downloaded Q3-2024 report', ip: '192.168.1.61', status: 'Success', statusClass: 'status-success' },
  { id: 6, timestamp: '2024-11-20 13:30:55', user: 'Yonas L.', initials: 'YL', action: 'UPDATE', actionClass: 'act-update', resource: 'Profile', details: 'Changed password', ip: '192.168.1.49', status: 'Warning', statusClass: 'status-warning' },
]

useHead({
  title: 'Audit Log — ValuAdis',
  meta: [{ name: 'description', content: 'System audit log and compliance monitoring.' }]
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
.btn-new { background: #006948; color: #fff; border: none; border-radius: 9999px; padding: 0.5rem 1.25rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
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
.table-row { border-top: 1px solid #f1f5f9; transition: background 0.15s; }
.table-row:hover { background: rgba(248,250,252,0.85); }
.table-row td { padding: 1.25rem 1.5rem; }
.td-time { font-family: monospace; font-size: 0.8rem; color: #475569; }
.td-user { display: flex; align-items: center; gap: 0.75rem; font-weight: 600; }
.user-avatar-sm { width: 2rem; height: 2rem; border-radius: 50%; background: #e2e8f0; color: #475569; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.action-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.act-create { background: #d1fae5; color: #065f46; }
.act-update { background: #dbeafe; color: #1e40af; }
.act-delete { background: #fecaca; color: #dc2626; }
.act-login { background: #f1f5f9; color: #64748b; }
.act-export { background: #e9d5ff; color: #7c3aed; }
.td-resource { font-size: 0.875rem; color: #191c1e; font-weight: 500; }
.td-details { font-size: 0.875rem; color: #64748b; }
.td-ip { font-family: monospace; font-size: 0.8rem; color: #94a3b8; }
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.status-success { background: #d1fae5; color: #065f46; }
.status-warning { background: #fef3c7; color: #92400e; }

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
