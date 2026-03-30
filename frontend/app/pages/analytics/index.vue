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
        <NuxtLink to="/analytics" class="nav-item active">
          <span class="material-symbols-outlined">monitoring</span><span>Analytics</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="nav-item">
          <span class="material-symbols-outlined">settings</span><span>Settings</span>
        </NuxtLink>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">DA</div>
        <div>
          <p class="user-name">Data Analyst</p>
          <p class="user-role">Analytics Team</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" placeholder="Search metrics..." />
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
          <span class="bc-active">Analytics</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h1 class="page-title">Analytics Dashboard</h1>
            <p class="page-desc">Deep insights into property valuations and market trends.</p>
          </div>
          <div class="page-hd-actions">
            <button class="btn-outline">
              <span class="material-symbols-outlined">download</span> Export Report
            </button>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">trending_up</span></div>
            <p class="stat-label">Market Growth</p>
            <h3 class="stat-value">+14.2%</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">YoY</span>
              <span class="stat-sub">vs last year</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">location_city</span></div>
            <p class="stat-label">Avg. Property Value</p>
            <h3 class="stat-value">ETB 4.2M</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">+5.8%</span>
              <span class="stat-sub">this quarter</span>
            </div>
          </div>
          <div class="stat-card glass-card">
            <div class="stat-bg-icon"><span class="material-symbols-outlined">speed</span></div>
            <p class="stat-label">Processing Time</p>
            <h3 class="stat-value">2.4 days</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">-18%</span>
              <span class="stat-sub">improvement</span>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
          <!-- Valuation Trends -->
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">Valuation Trends</h3>
              <select class="chart-filter">
                <option>Last 12 Months</option>
                <option>Last 6 Months</option>
                <option>Last 30 Days</option>
              </select>
            </div>
            <div class="chart-area">
              <div class="mock-chart">
                <div class="chart-bar" v-for="(bar, i) in trendData" :key="i" :style="`height:${bar.value}%`">
                  <span class="bar-label">{{ bar.month }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Property Types -->
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3 class="chart-title">Property Type Distribution</h3>
            </div>
            <div class="chart-area">
              <div class="donut-chart">
                <div class="donut-center">
                  <span class="donut-value">8,492</span>
                  <span class="donut-label">Total</span>
                </div>
              </div>
              <div class="chart-legend">
                <div class="legend-item" v-for="item in typeDistribution" :key="item.label">
                  <span class="legend-dot" :style="`background:${item.color}`"></span>
                  <span class="legend-label">{{ item.label }}</span>
                  <span class="legend-value">{{ item.value }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Regional Performance -->
          <div class="chart-card glass-card wide">
            <div class="chart-header">
              <h3 class="chart-title">Regional Performance</h3>
              <select class="chart-filter">
                <option>By Value</option>
                <option>By Volume</option>
              </select>
            </div>
            <div class="chart-area">
              <div class="region-list">
                <div class="region-item" v-for="region in regions" :key="region.name">
                  <div class="region-info">
                    <span class="region-name">{{ region.name }}</span>
                    <span class="region-value">{{ region.value }}</span>
                  </div>
                  <div class="region-bar">
                    <div class="region-fill" :style="`width:${region.pct}%`"></div>
                  </div>
                  <span class="region-pct">{{ region.pct }}%</span>
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
        <a href="#">Privacy Policy</a><a href="#">Terms of Service</a><a href="#">Contact Support</a>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const trendData = [
  { month: 'Jan', value: 45 },
  { month: 'Feb', value: 52 },
  { month: 'Mar', value: 48 },
  { month: 'Apr', value: 61 },
  { month: 'May', value: 55 },
  { month: 'Jun', value: 67 },
  { month: 'Jul', value: 72 },
  { month: 'Aug', value: 68 },
  { month: 'Sep', value: 75 },
  { month: 'Oct', value: 82 },
  { month: 'Nov', value: 78 },
  { month: 'Dec', value: 85 },
]

const typeDistribution = [
  { label: 'Residential', value: 58, color: '#006948' },
  { label: 'Commercial', value: 24, color: '#4b41e1' },
  { label: 'Industrial', value: 12, color: '#825100' },
  { label: 'Agricultural', value: 6, color: '#94a3b8' },
]

const regions = [
  { name: 'Addis Ababa', value: 'ETB 892M', pct: 42 },
  { name: 'Mekelle', value: 'ETB 234M', pct: 18 },
  { name: 'Dire Dawa', value: 'ETB 156M', pct: 15 },
  { name: 'Bahir Dar', value: 'ETB 128M', pct: 12 },
  { name: 'Hawassa', value: 'ETB 89M', pct: 8 },
  { name: 'Others', value: 'ETB 67M', pct: 5 },
]

useHead({
  title: 'Analytics — ValuAdis',
  meta: [{ name: 'description', content: 'Property valuation analytics and market insights.' }]
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

/* Charts Grid */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.chart-card { padding: 1.5rem; border-radius: 1.5rem; }
.chart-card.wide { grid-column: 1 / -1; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.chart-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #191c1e; margin: 0; }
.chart-filter { padding: 0.35rem 0.75rem; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 0.5rem; font-size: 0.75rem; color: #475569; }
.chart-area { min-height: 200px; }

/* Mock Bar Chart */
.mock-chart { display: flex; align-items: flex-end; justify-content: space-between; height: 180px; padding: 0 1rem; }
.chart-bar { flex: 1; background: linear-gradient(to top, #006948, #00855d); border-radius: 0.5rem 0.5rem 0 0; margin: 0 0.25rem; position: relative; min-height: 20px; }
.bar-label { position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); font-size: 0.65rem; color: #94a3b8; }

/* Donut Chart */
.donut-chart { width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(#006948 0% 58%, #4b41e1 58% 82%, #825100 82% 94%, #94a3b8 94% 100%); position: relative; margin: 0 auto 1.5rem; }
.donut-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80px; height: 80px; background: #fff; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.donut-value { font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: #191c1e; }
.donut-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; }
.chart-legend { display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 0.35rem; }
.legend-dot { width: 0.75rem; height: 0.75rem; border-radius: 50%; }
.legend-label { font-size: 0.75rem; color: #475569; }
.legend-value { font-size: 0.75rem; font-weight: 700; color: #191c1e; }

/* Region List */
.region-list { display: flex; flex-direction: column; gap: 1rem; }
.region-item { display: flex; align-items: center; gap: 1rem; }
.region-info { width: 180px; display: flex; justify-content: space-between; }
.region-name { font-size: 0.875rem; font-weight: 500; color: #191c1e; }
.region-value { font-size: 0.875rem; color: #64748b; }
.region-bar { flex: 1; height: 0.5rem; background: #f1f5f9; border-radius: 9999px; overflow: hidden; }
.region-fill { height: 100%; background: #006948; border-radius: 9999px; }
.region-pct { width: 40px; text-align: right; font-size: 0.875rem; font-weight: 600; color: #191c1e; }

/* Footer */
.app-footer { margin-left: 16rem; padding: 2rem 3rem; border-top: 1px solid rgba(226,232,240,0.15); background: #f8fafc; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>
