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
        <div class="user-avatar">JD</div>
        <div>
          <p class="user-name">John Doe</p>
          <p class="user-role">Senior Auditor</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" placeholder="Search..." />
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
          <span class="bc-active">Profile</span>
        </nav>

        <!-- Page Header -->
        <div class="page-hd">
          <div>
            <h1 class="page-title">My Profile</h1>
            <p class="page-desc">Manage your account settings and preferences.</p>
          </div>
        </div>

        <!-- Profile Grid -->
        <div class="profile-grid">
          
          <!-- Profile Card -->
          <div class="profile-card glass-card">
            <div class="profile-header">
              <div class="avatar-wrap">
                <div class="profile-avatar">JD</div>
                <button class="avatar-edit"><span class="material-symbols-outlined">photo_camera</span></button>
              </div>
              <div class="profile-info">
                <h2 class="profile-name">John Doe</h2>
                <p class="profile-role">Senior Property Auditor</p>
                <span class="profile-badge">Verified Officer</span>
              </div>
            </div>
            <div class="profile-stats">
              <div class="pstat">
                <span class="pstat-value">1,247</span>
                <span class="pstat-label">Valuations</span>
              </div>
              <div class="pstat">
                <span class="pstat-value">98.4%</span>
                <span class="pstat-label">Accuracy</span>
              </div>
              <div class="pstat">
                <span class="pstat-value">4.9</span>
                <span class="pstat-label">Rating</span>
              </div>
            </div>
          </div>

          <!-- Contact Info -->
          <div class="info-card glass-card">
            <h3 class="card-title">Contact Information</h3>
            <div class="info-list">
              <div class="info-item">
                <span class="material-symbols-outlined info-icon">email</span>
                <div class="info-text">
                  <span class="info-label">Email</span>
                  <span class="info-value">john.doe@valuadis.gov.et</span>
                </div>
              </div>
              <div class="info-item">
                <span class="material-symbols-outlined info-icon">phone</span>
                <div class="info-text">
                  <span class="info-label">Phone</span>
                  <span class="info-value">+251 911 234 567</span>
                </div>
              </div>
              <div class="info-item">
                <span class="material-symbols-outlined info-icon">location_on</span>
                <div class="info-text">
                  <span class="info-label">Office</span>
                  <span class="info-value">Addis Ababa, Federal Building 3</span>
                </div>
              </div>
              <div class="info-item">
                <span class="material-symbols-outlined info-icon">badge</span>
                <div class="info-text">
                  <span class="info-label">Employee ID</span>
                  <span class="info-value">FED-2021-0042</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Security Settings -->
          <div class="security-card glass-card">
            <h3 class="card-title">Security</h3>
            <div class="security-list">
              <div class="sec-item">
                <div class="sec-info">
                  <span class="sec-name">Two-Factor Authentication</span>
                  <span class="sec-desc">Add an extra layer of security</span>
                </div>
                <label class="toggle">
                  <input type="checkbox" checked />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="sec-item">
                <div class="sec-info">
                  <span class="sec-name">Biometric Login</span>
                  <span class="sec-desc">Use fingerprint or face recognition</span>
                </div>
                <label class="toggle">
                  <input type="checkbox" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="sec-item">
                <div class="sec-info">
                  <span class="sec-name">Session Notifications</span>
                  <span class="sec-desc">Alert on new device login</span>
                </div>
                <label class="toggle">
                  <input type="checkbox" checked />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <button class="btn-change-pw">Change Password</button>
          </div>

          <!-- Activity Log -->
          <div class="activity-card glass-card">
            <h3 class="card-title">Recent Activity</h3>
            <div class="activity-list">
              <div class="act-item" v-for="(act, i) in activityLog" :key="i">
                <div class="act-icon" :class="act.iconClass">
                  <span class="material-symbols-outlined">{{ act.icon }}</span>
                </div>
                <div class="act-info">
                  <span class="act-text">{{ act.text }}</span>
                  <span class="act-time">{{ act.time }}</span>
                </div>
              </div>
            </div>
            <button class="btn-view-all">View All Activity</button>
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

const activityLog = [
  { icon: 'check_circle', iconClass: 'act-green', text: 'Approved valuation #SP-2024-0892', time: '2 hours ago' },
  { icon: 'edit', iconClass: 'act-blue', text: 'Updated property #PRP-2024-0034', time: '5 hours ago' },
  { icon: 'login', iconClass: 'act-gray', text: 'Logged in from Chrome on macOS', time: 'Today, 08:23 AM' },
  { icon: 'download', iconClass: 'act-purple', text: 'Exported quarterly report Q3-2024', time: 'Yesterday' },
  { icon: 'person_add', iconClass: 'act-orange', text: 'Added new user: Martha Kebede', time: '2 days ago' },
]

useHead({
  title: 'My Profile — ValuAdis',
  meta: [{ name: 'description', content: 'User profile and account settings.' }]
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
.page-hd { margin-bottom: 2rem; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2.25rem; font-weight: 800; letter-spacing: -0.02em; color: #191c1e; margin: 0 0 0.4rem; }
.page-desc { font-size: 0.95rem; color: #3d4a42; margin: 0; }

/* Profile Grid */
.profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.glass-card { background: rgba(255,255,255,0.8); backdrop-filter: blur(12px); border: 1px solid rgba(188,202,192,0.2); border-radius: 1.5rem; padding: 2rem; }

/* Profile Card */
.profile-card { grid-column: 1 / -1; display: flex; align-items: center; gap: 2rem; }
.profile-header { display: flex; align-items: center; gap: 1.5rem; flex: 1; }
.avatar-wrap { position: relative; }
.profile-avatar { width: 6rem; height: 6rem; border-radius: 50%; background: linear-gradient(135deg, #006948, #00855d); color: #fff; font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.avatar-edit { position: absolute; bottom: 0; right: 0; width: 2rem; height: 2rem; border-radius: 50%; background: #fff; border: 1px solid #e2e8f0; color: #475569; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.avatar-edit .material-symbols-outlined { font-size: 1rem; }
.profile-name { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700; color: #191c1e; margin: 0 0 0.25rem; }
.profile-role { font-size: 0.875rem; color: #64748b; margin: 0 0 0.75rem; }
.profile-badge { display: inline-block; padding: 0.25rem 0.75rem; background: #d1fae5; color: #065f46; border-radius: 9999px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.profile-stats { display: flex; gap: 3rem; padding-left: 2rem; border-left: 1px solid #e2e8f0; }
.pstat { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.pstat-value { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; color: #065f46; }
.pstat-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }

/* Cards */
.card-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #191c1e; margin: 0 0 1.5rem; }

/* Info Card */
.info-list { display: flex; flex-direction: column; gap: 1.25rem; }
.info-item { display: flex; align-items: center; gap: 1rem; }
.info-icon { font-size: 1.25rem; color: #006948; width: 2.5rem; height: 2.5rem; background: rgba(0,105,72,0.1); border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; }
.info-text { display: flex; flex-direction: column; }
.info-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }
.info-value { font-size: 0.875rem; font-weight: 600; color: #191c1e; }

/* Security Card */
.security-list { display: flex; flex-direction: column; gap: 1.25rem; margin-bottom: 1.5rem; }
.sec-item { display: flex; align-items: center; justify-content: space-between; }
.sec-info { display: flex; flex-direction: column; }
.sec-name { font-size: 0.875rem; font-weight: 600; color: #191c1e; }
.sec-desc { font-size: 0.75rem; color: #94a3b8; }
.toggle { position: relative; width: 3rem; height: 1.5rem; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: #e2e8f0; border-radius: 9999px; transition: 0.3s; cursor: pointer; }
.toggle-slider:before { content: ''; position: absolute; height: 1.25rem; width: 1.25rem; left: 0.125rem; bottom: 0.125rem; background: white; border-radius: 50%; transition: 0.3s; }
input:checked + .toggle-slider { background: #006948; }
input:checked + .toggle-slider:before { transform: translateX(1.5rem); }
.btn-change-pw { width: 100%; padding: 0.75rem; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 0.75rem; font-size: 0.875rem; font-weight: 600; color: #475569; cursor: pointer; transition: all 0.2s; }
.btn-change-pw:hover { background: #e2e8f0; }

/* Activity Card */
.activity-list { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }
.act-item { display: flex; align-items: center; gap: 1rem; }
.act-icon { width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; }
.act-icon span { font-size: 1.25rem; }
.act-green { background: #d1fae5; color: #065f46; }
.act-blue { background: #dbeafe; color: #1e40af; }
.act-gray { background: #f1f5f9; color: #64748b; }
.act-purple { background: #e9d5ff; color: #7c3aed; }
.act-orange { background: #fef3c7; color: #92400e; }
.act-info { display: flex; flex-direction: column; }
.act-text { font-size: 0.875rem; color: #191c1e; }
.act-time { font-size: 0.75rem; color: #94a3b8; }
.btn-view-all { width: 100%; padding: 0.75rem; background: none; border: 1px solid #e2e8f0; border-radius: 0.75rem; font-size: 0.875rem; font-weight: 600; color: #006948; cursor: pointer; transition: all 0.2s; }
.btn-view-all:hover { background: rgba(0,105,72,0.05); }

/* Footer */
.app-footer { margin-left: 16rem; padding: 2rem 3rem; border-top: 1px solid rgba(226,232,240,0.15); background: #f8fafc; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>
