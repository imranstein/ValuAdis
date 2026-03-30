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
        <NuxtLink to="/map" class="nav-item active">
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
        <div class="user-avatar">AB</div>
        <div>
          <p class="user-name">Abebe Bikila</p>
          <p class="user-role">Regional Auditor</p>
        </div>
      </div>
    </aside>

    <!-- Top Header -->
    <header class="top-header">
      <div class="search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input class="search-input" type="text" placeholder="Search assets, coordinates..." />
      </div>
      <div class="header-right">
        <nav class="header-links">
          <NuxtLink to="/dashboard" class="hlink">Dashboard</NuxtLink>
          <a href="#" class="hlink">Market Insights</a>
        </nav>
        <div class="header-actions">
          <button class="icon-btn"><span class="material-symbols-outlined">notifications</span></button>
          <button class="icon-btn"><span class="material-symbols-outlined">help_outline</span></button>
          <button class="btn-new-val">New Valuation</button>
        </div>
      </div>
    </header>

    <!-- Map Area -->
    <main class="map-main">

      <!-- Breadcrumb overlay -->
      <div class="breadcrumb-overlay">
        <span>Home</span>
        <span class="material-symbols-outlined bc-chevron">chevron_right</span>
        <span class="bc-active">Maps</span>
      </div>

      <!-- Map canvas -->
      <div class="map-canvas">
        <!-- Pin 1 -->
        <div class="map-pin pin-1 group">
          <div class="pin-badge pin-primary">
            <span class="material-symbols-outlined pin-icon">home</span>
          </div>
          <div class="pin-tooltip">Bole Residential A2</div>
        </div>
        <!-- Pin 2 -->
        <div class="map-pin pin-2 group">
          <div class="pin-badge pin-secondary">
            <span class="material-symbols-outlined pin-icon">directions_car</span>
          </div>
          <div class="pin-tooltip">Logistics Unit #402</div>
        </div>

        <!-- Map Controls -->
        <div class="map-controls">
          <div class="zoom-btns">
            <button class="map-ctrl-btn border-b"><span class="material-symbols-outlined">add</span></button>
            <button class="map-ctrl-btn"><span class="material-symbols-outlined">remove</span></button>
          </div>
          <button class="map-ctrl-btn mt-2"><span class="material-symbols-outlined">layers</span></button>
          <button class="map-ctrl-btn mt-1"><span class="material-symbols-outlined">my_location</span></button>
        </div>

        <!-- PropertyMap Component (functional) -->
        <div class="leaflet-wrap">
          <PropertyMap
            ref="propertyMap"
            height="100%"
            :zoom="12"
            :center="[9.0116, 38.7616]"
            :properties="mapProperties"
            @property-selected="onPropertySelected"
            @property-view="onPropertyView"
          />
        </div>
      </div>

      <!-- Detail Panel -->
      <div class="detail-panel" :class="{ 'panel-visible': selectedProperty }">
        <div class="panel-header">
          <div>
            <span class="active-label">Active Selection</span>
            <button class="panel-close" @click="closeModal">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <h2 class="panel-title">{{ selectedProperty?.title || 'Bole Estate Sector 4' }}</h2>
          <p class="panel-id">Asset ID: {{ selectedProperty?.id || 'ETH-AA-77291-B' }}</p>
        </div>
        <div class="panel-body">
          <div class="panel-stats">
            <div class="ps-card ps-green">
              <p class="ps-label">Valuation</p>
              <p class="ps-val">{{ selectedProperty ? formatPrice(selectedProperty.price) : '12.4M ETB' }}</p>
            </div>
            <div class="ps-card ps-indigo">
              <p class="ps-label">Compliance</p>
              <div class="ps-compliance">
                <span class="material-symbols-outlined compliance-icon">verified</span>
                <p class="ps-val">High</p>
              </div>
            </div>
          </div>
          <div class="params-section">
            <h3 class="params-heading">Property Parameters</h3>
            <div class="param-list">
              <div class="param-row" v-for="p in propertyParams" :key="p.label">
                <span class="param-label">{{ p.label }}</span>
                <span class="param-value" :class="p.valueClass">{{ p.value }}</span>
              </div>
            </div>
          </div>
          <div class="insight-box">
            <h4 class="insight-title">Development Insight</h4>
            <p class="insight-body">This sector has seen a 14.2% value appreciation over the last 18 months due to proximity to the new diplomatic corridor.</p>
          </div>
          <div class="panel-actions">
            <button class="btn-update-val" @click="viewFullDetails">
              <span class="material-symbols-outlined">edit_document</span> Update Valuation
            </button>
            <button class="btn-view-hist">
              <span class="material-symbols-outlined">history</span> View History
            </button>
          </div>
        </div>
      </div>

      <!-- Default detail panel when nothing selected -->
      <div class="detail-panel" v-if="!selectedProperty">
        <div class="panel-header">
          <div class="panel-header-top">
            <span class="active-label">Active Selection</span>
          </div>
          <h2 class="panel-title">Bole Estate Sector 4</h2>
          <p class="panel-id">Asset ID: ETH-AA-77291-B</p>
        </div>
        <div class="panel-body">
          <div class="panel-stats">
            <div class="ps-card ps-green">
              <p class="ps-label">Valuation</p>
              <p class="ps-val">12.4M <span class="ps-unit">ETB</span></p>
            </div>
            <div class="ps-card ps-indigo">
              <p class="ps-label">Compliance</p>
              <div class="ps-compliance">
                <span class="material-symbols-outlined compliance-icon">verified</span>
                <p class="ps-val">High</p>
              </div>
            </div>
          </div>
          <div class="params-section">
            <h3 class="params-heading">Property Parameters</h3>
            <div class="param-list">
              <div class="param-row" v-for="p in propertyParams" :key="p.label">
                <span class="param-label">{{ p.label }}</span>
                <span class="param-value" :class="p.valueClass">{{ p.value }}</span>
              </div>
            </div>
          </div>
          <div class="insight-box">
            <h4 class="insight-title">Development Insight</h4>
            <p class="insight-body">This sector has seen a 14.2% value appreciation over the last 18 months due to proximity to the new diplomatic corridor.</p>
          </div>
          <div class="panel-actions">
            <button class="btn-update-val">
              <span class="material-symbols-outlined">edit_document</span> Update Valuation
            </button>
            <button class="btn-view-hist">
              <span class="material-symbols-outlined">history</span> View History
            </button>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PropertyMap from '~/components/map/PropertyMap.vue'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8020'

const selectedProperty = ref<any>(null)
const mapProperties = ref<any[]>([])

const propertyParams = [
  { label: 'Land Area', value: '1,250 m²', valueClass: '' },
  { label: 'Zoning', value: 'Residential-Mixed', valueClass: '' },
  { label: 'Tax Status', value: 'Current', valueClass: 'val-green' },
  { label: 'Owner', value: 'Private Heritage Fund', valueClass: '' },
]

onMounted(async () => {
  try {
    const token = localStorage.getItem('valuadis_token')
    const res = await fetch(`${apiBase}/api/v1/properties?limit=500`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      mapProperties.value = data.data || []
    }
  } catch {
    mapProperties.value = []
  }
})

const onPropertySelected = (property: any) => { selectedProperty.value = property }
const onPropertyView = () => { viewFullDetails() }
const closeModal = () => { selectedProperty.value = null }
const viewFullDetails = () => {
  if (selectedProperty.value) router.push(`/properties/${selectedProperty.value.id}`)
}

const formatPrice = (price: number) =>
  new Intl.NumberFormat('en-ET', { style: 'currency', currency: 'ETB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(price)

useHead({
  title: 'GIS Maps — ValuAdis',
  meta: [{ name: 'description', content: 'Interactive GIS map for asset valuation across Ethiopia.' }]
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
.btn-new-val { background: #006948; color: #fff; border: none; border-radius: 9999px; padding: 0.5rem 1.25rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
.btn-new-val:hover { opacity: 0.9; }

/* Map Main */
.map-main { margin-left: 16rem; margin-top: 4rem; flex: 1; position: relative; display: flex; height: calc(100vh - 4rem); overflow: hidden; }

/* Breadcrumb overlay */
.breadcrumb-overlay { position: absolute; top: 1.5rem; left: 2rem; z-index: 20; display: flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.92); backdrop-filter: blur(8px); padding: 0.35rem 1rem; border-radius: 9999px; border: 1px solid rgba(209,250,229,0.5); box-shadow: 0 1px 3px rgba(0,0,0,0.06); font-size: 0.75rem; font-weight: 500; color: #94a3b8; }
.bc-chevron { font-size: 0.875rem; color: #cbd5e1; }
.bc-active { color: #065f46; font-weight: 700; }

/* Map canvas */
.map-canvas { flex: 1; position: relative; background: #cbd5e1; overflow: hidden; }
.leaflet-wrap { position: absolute; inset: 0; z-index: 0; }

/* Pins */
.map-pin { position: absolute; display: flex; flex-direction: column; align-items: center; cursor: pointer; }
.pin-1 { top: 33%; left: 25%; }
.pin-2 { bottom: 33%; right: 50%; }
.pin-badge { background: #fff; padding: 0.25rem; border-radius: 0.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 2px solid #006948; }
.pin-badge.pin-secondary { border-color: #4b41e1; }
.pin-badge > span { display: flex; align-items: center; justify-content: center; background: #006948; color: #fff; padding: 0.35rem; border-radius: 0.4rem; font-size: 1.1rem; }
.pin-badge.pin-secondary > span { background: #4b41e1; }
.pin-tooltip { margin-top: 0.4rem; background: rgba(255,255,255,0.92); backdrop-filter: blur(8px); padding: 0.2rem 0.6rem; border-radius: 0.4rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border: 1px solid rgba(0,105,72,0.1); font-size: 0.65rem; font-weight: 700; color: #065f46; white-space: nowrap; opacity: 0; transition: opacity 0.2s; pointer-events: none; }
.map-pin:hover .pin-tooltip { opacity: 1; }

/* Map Controls */
.map-controls { position: absolute; right: 1.5rem; top: 5rem; z-index: 20; display: flex; flex-direction: column; gap: 0.5rem; }
.zoom-btns { display: flex; flex-direction: column; background: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-radius: 0.75rem; overflow: hidden; border: 1px solid rgba(226,232,240,0.5); }
.map-ctrl-btn { background: #fff; border: none; padding: 0.75rem; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #475569; transition: background 0.15s; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border-radius: 0.75rem; border: 1px solid rgba(226,232,240,0.5); }
.map-ctrl-btn:hover { background: #f1f5f9; }
.border-b { border-bottom: 1px solid #f1f5f9; border-radius: 0; }
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }

/* Detail Panel */
.detail-panel { width: 24rem; background: #fff; border-left: 1px solid rgba(226,232,240,0.5); z-index: 30; display: flex; flex-direction: column; overflow-y: auto; }
.panel-header { padding: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.panel-header-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.active-label { background: #d1fae5; color: #065f46; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; padding: 0.15rem 0.6rem; border-radius: 9999px; }
.panel-close { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 0.25rem; }
.panel-title { font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: #191c1e; margin: 0.5rem 0 0.2rem; }
.panel-id { font-size: 0.75rem; color: #94a3b8; margin: 0; }
.panel-body { flex: 1; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }
.panel-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.ps-card { padding: 1rem; border-radius: 1rem; background: #f2f4f6; }
.ps-green { border: 1px solid rgba(0,105,72,0.1); }
.ps-indigo { border: 1px solid rgba(75,65,225,0.1); }
.ps-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0 0 0.35rem; }
.ps-val { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #065f46; margin: 0; }
.ps-unit { font-size: 0.65rem; }
.ps-compliance { display: flex; align-items: center; gap: 0.35rem; }
.compliance-icon { font-size: 1rem; color: #006948; }
.params-heading { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; margin: 0 0 1rem; }
.param-list { display: flex; flex-direction: column; }
.param-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #f8fafc; }
.param-label { font-size: 0.875rem; color: #475569; }
.param-value { font-size: 0.875rem; font-weight: 600; color: #191c1e; }
.val-green { color: #006948; }
.insight-box { padding: 1.25rem; border-radius: 1rem; background: rgba(0,105,72,0.05); border: 1px solid rgba(0,105,72,0.12); position: relative; overflow: hidden; }
.insight-title { font-family: 'Syne', sans-serif; font-size: 0.875rem; font-weight: 700; color: #065f46; margin: 0 0 0.5rem; }
.insight-body { font-size: 0.8rem; color: rgba(4,47,34,0.8); line-height: 1.6; margin: 0; }
.panel-actions { display: flex; flex-direction: column; gap: 0.5rem; }
.btn-update-val { display: flex; align-items: center; justify-content: center; gap: 0.5rem; width: 100%; background: #006948; color: #fff; border: none; border-radius: 0.75rem; padding: 0.75rem; font-size: 0.875rem; font-weight: 700; cursor: pointer; transition: opacity 0.2s; }
.btn-update-val:hover { opacity: 0.9; }
.btn-view-hist { display: flex; align-items: center; justify-content: center; gap: 0.5rem; width: 100%; background: #fff; border: 1px solid #e2e8f0; color: #475569; border-radius: 0.75rem; padding: 0.75rem; font-size: 0.875rem; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-view-hist:hover { background: #f8fafc; }

/* Footer */
.app-footer { margin-left: 16rem; padding: 1.5rem 3rem; border-top: 1px solid rgba(226,232,240,0.15); background: #f8fafc; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; }
.footer-brand { font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; }
.footer-copy { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin: 0; }
.footer-links { display: flex; gap: 2rem; }
.footer-links a { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; text-decoration: none; }
.footer-links a:hover { color: #006948; }
</style>

