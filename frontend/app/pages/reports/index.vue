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
          <span class="material-symbols-outlined">domain</span>
          <span>Properties</span>
        </NuxtLink>
        <NuxtLink to="/vehicles" class="nav-item">
          <span class="material-symbols-outlined">directions_car</span>
          <span>Vehicles</span>
        </NuxtLink>
        <NuxtLink to="/valuations" class="nav-item">
          <span class="material-symbols-outlined">assessment</span>
          <span>Valuations</span>
        </NuxtLink>
        <NuxtLink to="/map" class="nav-item">
          <span class="material-symbols-outlined">map</span>
          <span>Maps</span>
        </NuxtLink>
        <NuxtLink to="/reports" class="nav-item active">
          <span class="material-symbols-outlined">analytics</span>
          <span>Reports</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item">
          <span class="material-symbols-outlined">settings</span>
          <span>Settings</span>
        </NuxtLink>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">JD</div>
        <div>
          <p class="user-name">John Doe</p>
          <p class="user-role">Chief Appraiser</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" placeholder="Search analytics..." />
      </div>
      <div class="header-right">
        <div class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink hlink-active">Market Insights</a>
        </div>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new-val">New Valuation</button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrap">
        <!-- Breadcrumb -->
        <nav class="breadcrumb">
          <NuxtLink to="/dashboard">Home</NuxtLink>
          <span class="material-symbols-outlined">chevron_right</span>
          <span class="bc-active">Reports</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h2 class="page-title">Analytics Engine</h2>
            <p class="page-desc">Advanced real estate valuation metrics and regional market distribution for current fiscal year data.</p>
          </div>
          <div class="page-hd-actions">
            <button class="btn-filter">
              <span class="material-symbols-outlined">calendar_today</span>
              Last 30 Days
            </button>
            <button class="btn-export">
              <span class="material-symbols-outlined">download</span>
              Export Data
            </button>
          </div>
        </div>

        <!-- Bento Grid -->
        <div class="bento-grid">

          <!-- Main Chart: Valuation Volume -->
          <div class="chart-main card">
            <div class="chart-header">
              <div>
                <h3 class="card-title">Valuation Volume</h3>
                <p class="card-sub">Growth of assets processed across all districts</p>
              </div>
              <div class="chart-legend">
                <span class="legend-item"><span class="dot dot-primary"></span> Current</span>
                <span class="legend-item"><span class="dot dot-secondary"></span> Projected</span>
              </div>
            </div>
            <div class="chart-area">
              <svg class="chart-svg" viewBox="0 0 800 200" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#006948" stop-opacity="0.12"/>
                    <stop offset="100%" stop-color="#006948" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path d="M0,180 Q100,160 200,140 T400,100 T600,60 T800,20" fill="url(#grad1)" stroke="none"/>
                <path d="M0,180 Q100,160 200,140 T400,100 T600,60 T800,20" fill="none" stroke="#006948" stroke-width="3" stroke-linecap="round"/>
                <path d="M0,180 Q100,170 200,165 T400,150 T600,145 T800,130" fill="none" stroke="#c3c0ff" stroke-dasharray="8 4" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
              <div class="chart-grid">
                <div class="v-line" v-for="n in 6" :key="n"></div>
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="m in ['Jan','Mar','May','Jul','Sep','Nov']" :key="m">{{ m }}</span>
            </div>
          </div>

          <!-- Regional Distribution -->
          <div class="chart-donut card">
            <h3 class="card-title">Regional Distribution</h3>
            <p class="card-sub">Asset concentration by administrative zones</p>
            <div class="donut-wrap">
              <svg class="donut-svg" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#f2f4f6" stroke-width="4"/>
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#006948" stroke-dasharray="45 55" stroke-dashoffset="25" stroke-width="4"/>
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#4b41e1" stroke-dasharray="30 70" stroke-dashoffset="80" stroke-width="4"/>
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#825100" stroke-dasharray="25 75" stroke-dashoffset="110" stroke-width="4"/>
              </svg>
              <div class="donut-center">
                <span class="donut-val">1.2k</span>
                <span class="donut-lbl">Total Assets</span>
              </div>
            </div>
            <div class="region-list">
              <div class="region-row" v-for="r in regions" :key="r.name">
                <div class="region-info">
                  <span class="region-dot" :style="`background:${r.color}`"></span>
                  <span class="region-name">{{ r.name }}</span>
                </div>
                <span class="region-pct">{{ r.pct }}</span>
              </div>
            </div>
          </div>

          <!-- Compliance Gauge -->
          <div class="chart-gauge card">
            <div>
              <h3 class="card-title">Compliance Accuracy</h3>
              <p class="card-sub">Verification score against national standards</p>
            </div>
            <div class="gauge-area">
              <div class="gauge-ring"></div>
              <div class="gauge-arc"></div>
              <div class="gauge-text">
                <span class="gauge-val">98.4%</span>
                <p class="gauge-status">EXCELLENT STATUS</p>
              </div>
            </div>
            <div class="audit-notice">
              <span class="material-symbols-outlined audit-icon">verified_user</span>
              <div>
                <p class="audit-title">Automated Audit Successful</p>
                <p class="audit-desc">Last checked: 2 hours ago. No discrepancies found in the property registry.</p>
              </div>
            </div>
          </div>

          <!-- Recent Exports -->
          <div class="exports-card card">
            <div class="exports-header">
              <h3 class="card-title">Recent Exports</h3>
              <button class="view-all-btn">View All History</button>
            </div>
            <div class="export-list">
              <div class="export-item" v-for="exp in exports" :key="exp.name">
                <div class="export-left">
                  <div class="export-icon" :class="exp.iconClass">
                    <span class="material-symbols-outlined">{{ exp.icon }}</span>
                  </div>
                  <div>
                    <p class="export-name">{{ exp.name }}</p>
                    <p class="export-meta">{{ exp.meta }}</p>
                  </div>
                </div>
                <div class="export-right">
                  <span class="export-date">{{ exp.date }}</span>
                  <button class="dl-btn"><span class="material-symbols-outlined">download</span></button>
                </div>
              </div>
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
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="#">Contact Support</a>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

definePageMeta({ middleware: 'auth' })

const regions = [
  { name: 'Addis Ababa', pct: '45%', color: '#006948' },
  { name: 'Oromia', pct: '30%', color: '#4b41e1' },
  { name: 'Amhara', pct: '25%', color: '#825100' },
]

const exports = [
  { name: 'Q3_Property_Valuation_Report.pdf', meta: 'Generated by John Doe • 2.4 MB', date: 'Oct 12, 2024', icon: 'description', iconClass: 'icon-pdf' },
  { name: 'Residential_Market_Data_2024.xlsx', meta: 'System Automated • 1.1 MB', date: 'Oct 10, 2024', icon: 'table_view', iconClass: 'icon-xls' },
  { name: 'Regional_Growth_Forecast.pdf', meta: 'Requested by Board • 4.8 MB', date: 'Oct 08, 2024', icon: 'insights', iconClass: 'icon-insight' },
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

/* ── TOKENS ── */
:root {
  --primary: #006948;
  --primary-cont: #00855d;
  --secondary: #4b41e1;
  --tertiary: #825100;
  --surface: #f7f9fb;
  --on-surface: #191c1e;
  --on-surface-variant: #3d4a42;
  --outline-variant: #bccac0;
  --surface-container-low: #f2f4f6;
  --surface-container-high: #e6e8ea;
}

/* ── SHELL ── */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--surface);
  font-family: 'Inter', sans-serif;
  color: var(--on-surface);
}

/* ── SIDEBAR ── */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100%;
  width: 16rem;
  background: rgba(248, 250, 252, 0.7);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(226, 232, 240, 0.2);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  z-index: 50;
}
.sidebar-brand { padding: 0 0.5rem; margin-bottom: 2.5rem; }
.brand-title { display: block; font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: #065f46; }
.brand-sub { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; margin-top: 0.2rem; }

.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #475569;
  text-decoration: none;
  transition: all 0.2s;
}
.nav-item:hover { color: #006948; background: rgba(248, 250, 252, 0.6); }
.nav-item.active {
  color: #005137;
  font-weight: 600;
  background: rgba(0, 105, 72, 0.06);
  border-right: 3px solid #006948;
}
.nav-item .material-symbols-outlined { font-size: 1.25rem; }

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 0.5rem;
  border-top: 1px solid rgba(226, 232, 240, 0.2);
  margin-top: auto;
}
.user-avatar {
  width: 2.5rem; height: 2.5rem;
  border-radius: 50%;
  background: #00855d;
  color: #fff;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 0.8rem;
  display: flex; align-items: center; justify-content: center;
}
.user-name { font-size: 0.8rem; font-weight: 700; }
.user-role { font-size: 0.7rem; color: #94a3b8; }

/* ── TOP HEADER ── */
.top-header {
  position: fixed;
  top: 0; right: 0;
  width: calc(100% - 16rem);
  height: 4rem;
  z-index: 40;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
}
.search-wrap { position: relative; flex: 1; max-width: 28rem; }
.search-icon {
  position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%);
  color: #94a3b8; font-size: 1.1rem;
}
.search-input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  background: var(--surface-container-high);
  border: none;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  outline: none;
}
.header-right { display: flex; align-items: center; gap: 1.5rem; }
.header-links { display: flex; gap: 1rem; }
.hlink { font-size: 0.875rem; font-weight: 500; color: #64748b; text-decoration: none; transition: color 0.2s; }
.hlink:hover { color: #006948; }
.hlink-active { color: #065f46; font-weight: 700; border-bottom: 2px solid #006948; padding-bottom: 0.1rem; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; padding-left: 1rem; border-left: 1px solid #e2e8f0; }
.icon-btn { background: none; border: none; cursor: pointer; color: #64748b; padding: 0.4rem; border-radius: 50%; transition: background 0.2s; }
.icon-btn:hover { background: #f1f5f9; }
.btn-new-val {
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 9999px;
  padding: 0.5rem 1.25rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-new-val:hover { opacity: 0.9; }

/* ── MAIN CONTENT ── */
.main-content {
  margin-left: 16rem;
  padding-top: 4rem;
  flex: 1;
  min-height: 100vh;
}
.content-wrap { max-width: 80rem; margin: 0 auto; padding: 2.5rem 2rem; }

/* ── BREADCRUMB ── */
.breadcrumb {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.8rem; font-weight: 500; color: var(--on-surface-variant);
  margin-bottom: 2rem;
}
.breadcrumb a { color: inherit; text-decoration: none; }
.breadcrumb a:hover { color: var(--primary); }
.breadcrumb .material-symbols-outlined { font-size: 1rem; }
.bc-active { color: var(--on-surface); font-weight: 700; }

/* ── PAGE HEADER ── */
.page-hd { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 3rem; gap: 1rem; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2.75rem; font-weight: 800; letter-spacing: -0.02em; color: var(--on-surface); margin: 0 0 0.75rem; }
.page-desc { font-size: 1.05rem; color: var(--on-surface-variant); line-height: 1.65; margin: 0; max-width: 36rem; }
.page-hd-actions { display: flex; gap: 0.75rem; flex-shrink: 0; }
.btn-filter {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fff;
  border: 1px solid var(--outline-variant);
  border-radius: 0.75rem;
  font-size: 0.8rem; font-weight: 600;
  cursor: pointer; color: var(--on-surface-variant);
  transition: background 0.2s;
}
.btn-filter:hover { background: var(--surface-container-low); }
.btn-export {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: var(--secondary);
  color: #fff;
  border: none;
  border-radius: 9999px;
  font-size: 0.8rem; font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-export:hover { opacity: 0.9; }

/* ── BENTO GRID ── */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}
.card {
  background: #fff;
  border-radius: 1rem;
  border: 1px solid rgba(188, 202, 192, 0.15);
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  padding: 2rem;
}
.card-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--on-surface); margin: 0 0 0.25rem; }
.card-sub { font-size: 0.8rem; color: var(--on-surface-variant); margin: 0 0 1.5rem; }

/* Chart Main */
.chart-main { grid-column: span 8; }
.chart-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; }
.chart-legend { display: flex; gap: 1rem; }
.legend-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; font-weight: 600; }
.dot { width: 0.65rem; height: 0.65rem; border-radius: 50%; }
.dot-primary { background: var(--primary); }
.dot-secondary { background: #c3c0ff; }
.chart-area { height: 10rem; position: relative; }
.chart-svg { width: 100%; height: 100%; }
.chart-grid { position: absolute; inset: 0; display: flex; justify-content: space-between; pointer-events: none; opacity: 0.08; }
.v-line { width: 1px; height: 100%; background: var(--on-surface); }
.chart-labels { display: flex; justify-content: space-between; margin-top: 1rem; padding: 0 0.5rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--on-surface-variant); }

/* Donut */
.chart-donut { grid-column: span 4; }
.donut-wrap { position: relative; width: 10rem; height: 10rem; margin: 0 auto 1.5rem; }
.donut-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.donut-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.donut-val { font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 800; }
.donut-lbl { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: var(--on-surface-variant); }
.region-list { display: flex; flex-direction: column; gap: 0.75rem; }
.region-row { display: flex; justify-content: space-between; align-items: center; }
.region-info { display: flex; align-items: center; gap: 0.5rem; }
.region-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; }
.region-name { font-size: 0.875rem; }
.region-pct { font-size: 0.875rem; font-weight: 700; }

/* Gauge */
.chart-gauge { grid-column: span 5; display: flex; flex-direction: column; justify-content: space-between; }
.gauge-area { position: relative; height: 8rem; display: flex; align-items: flex-end; justify-content: center; overflow: hidden; }
.gauge-ring {
  position: absolute;
  bottom: 0; left: 50%; transform: translateX(-50%);
  width: 14rem; height: 14rem;
  border-radius: 50%;
  border: 1rem solid var(--surface-container-low);
}
.gauge-arc {
  position: absolute;
  bottom: 0; left: 50%; transform: translateX(-50%) rotate(45deg);
  width: 14rem; height: 14rem;
  border-radius: 50%;
  border: 1rem solid transparent;
  border-top-color: var(--primary);
  border-right-color: var(--primary);
}
.gauge-text { position: absolute; bottom: 1rem; left: 50%; transform: translateX(-50%); text-align: center; white-space: nowrap; }
.gauge-val { display: block; font-family: 'Syne', sans-serif; font-size: 2.5rem; font-weight: 800; color: var(--primary); }
.gauge-status { font-size: 0.65rem; font-weight: 700; color: var(--primary-cont); letter-spacing: 0.1em; margin: 0; }
.audit-notice {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 1rem;
  background: var(--surface-container-low);
  border: 1px solid var(--outline-variant);
  border-radius: 0.75rem;
  margin-top: 1.5rem;
}
.audit-icon { font-size: 1.25rem; color: var(--primary); }
.audit-title { font-size: 0.875rem; font-weight: 700; margin: 0 0 0.2rem; }
.audit-desc { font-size: 0.75rem; color: var(--on-surface-variant); margin: 0; line-height: 1.4; }

/* Exports */
.exports-card { grid-column: span 7; }
.exports-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.view-all-btn { background: none; border: none; font-size: 0.8rem; font-weight: 700; color: var(--secondary); cursor: pointer; }
.export-list { display: flex; flex-direction: column; gap: 0.25rem; }
.export-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid transparent;
  transition: all 0.15s;
}
.export-item:hover { background: var(--surface-container-low); border-color: var(--outline-variant); }
.export-left { display: flex; align-items: center; gap: 1rem; }
.export-icon {
  width: 2.5rem; height: 2.5rem;
  border-radius: 0.5rem;
  display: flex; align-items: center; justify-content: center;
}
.icon-pdf { background: #fef2f2; color: #dc2626; }
.icon-xls { background: #f0fdf4; color: #16a34a; }
.icon-insight { background: #eff6ff; color: #2563eb; }
.export-icon .material-symbols-outlined { font-size: 1.25rem; }
.export-name { font-size: 0.875rem; font-weight: 700; color: var(--on-surface); margin: 0 0 0.1rem; }
.export-meta { font-size: 0.75rem; color: var(--on-surface-variant); margin: 0; }
.export-right { display: flex; align-items: center; gap: 0.75rem; }
.export-date { font-size: 0.75rem; font-weight: 600; color: var(--on-surface-variant); }
.dl-btn {
  width: 2rem; height: 2rem;
  border-radius: 50%;
  border: none;
  background: var(--surface-container-high);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--on-surface);
  transition: all 0.2s;
}
.dl-btn:hover { background: var(--primary); color: #fff; }
.dl-btn .material-symbols-outlined { font-size: 1rem; }

/* ── FOOTER ── */
.app-footer {
  margin-left: 16rem;
  padding: 2rem 3rem;
  border-top: 1px solid rgba(226, 232, 240, 0.15);
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>
