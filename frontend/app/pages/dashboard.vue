<template>
  <div class="dashboard-modern min-h-screen bg-[#f7f9fb] font-['Inter']">
    <!-- Sidebar -->
    <aside class="fixed left-0 top-0 h-full w-64 z-40 bg-slate-50/80 backdrop-blur-xl flex flex-col p-4 space-y-2 shadow-xl shadow-emerald-900/5">
      <div class="px-4 py-6 mb-4">
        <h1 class="font-['Syne'] font-extrabold text-emerald-800 text-2xl tracking-tight leading-tight">ValuAdis</h1>
        <p class="text-[10px] uppercase tracking-[0.2em] font-bold text-emerald-600/60 mt-1">Federal Valuation Dept</p>
      </div>
      <nav class="flex-1 space-y-1">
        <NuxtLink to="/dashboard" class="flex items-center gap-3 px-4 py-3 bg-emerald-100/50 text-emerald-700 rounded-xl font-bold transition-all duration-200 group">
          <Icon name="mdi:view-dashboard" class="w-5 h-5" />
          <span class="text-sm font-medium">Dashboard</span>
        </NuxtLink>
        <NuxtLink to="/properties" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:domain" class="w-5 h-5" />
          <span class="text-sm font-medium">Properties</span>
        </NuxtLink>
        <NuxtLink to="/vehicles" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:car" class="w-5 h-5" />
          <span class="text-sm font-medium">Vehicles</span>
        </NuxtLink>
        <NuxtLink to="/valuations" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:chart-line" class="w-5 h-5" />
          <span class="text-sm font-medium">Valuations</span>
        </NuxtLink>
        <NuxtLink to="/map" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:map" class="w-5 h-5" />
          <span class="text-sm font-medium">Maps</span>
        </NuxtLink>
        <NuxtLink to="/reports" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:file-document" class="w-5 h-5" />
          <span class="text-sm font-medium">Reports</span>
        </NuxtLink>
      </nav>
      <div class="pt-4 border-t border-emerald-900/5 mt-auto space-y-1">
        <NuxtLink to="/settings" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
          <Icon name="mdi:cog" class="w-5 h-5" />
          <span class="text-sm font-medium">Settings</span>
        </NuxtLink>
        <button @click="logout" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group w-full text-left">
          <Icon name="mdi:logout" class="w-5 h-5" />
          <span class="text-sm font-medium">Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="ml-64 p-8 min-h-screen">
      <!-- Header -->
      <header class="flex justify-between items-center mb-10">
        <div>
          <h2 class="font-['Syne'] font-extrabold text-4xl text-[#191c1e] tracking-tighter">Dashboard</h2>
          <p class="text-[#3d4a42] font-medium mt-1">Real-time asset valuation intelligence.</p>
        </div>
        <div class="flex gap-4">
          <button @click="router.push('/properties/create')" class="bg-[#e0e3e5] text-[#006948] px-6 py-3 rounded-3xl font-bold flex items-center gap-2 transition-all hover:bg-[#eceef0] active:scale-95 shadow-sm">
            <Icon name="mdi:home-plus" class="w-5 h-5" />
            New Property
          </button>
          <button @click="router.push('/valuations/quick')" class="bg-gradient-to-br from-[#006948] to-[#00855d] text-white px-6 py-3 rounded-3xl font-bold flex items-center gap-2 transition-all hover:shadow-lg active:scale-95">
            <Icon name="mdi:check-circle" class="w-5 h-5" />
            New Valuation
          </button>
        </div>
      </header>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-[#bccac0]/10 relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
          <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-[#006948]/10 to-transparent rounded-bl-full"></div>
          <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-[#00855d]/10 rounded-2xl text-[#006948]">
              <Icon name="mdi:office-building" class="w-8 h-8" />
            </div>
            <span class="text-xs font-bold text-[#006948] px-2 py-1 bg-[#006948]/10 rounded-lg flex items-center gap-1">
              <Icon name="mdi:trending-up" class="w-3 h-3" /> +12%
            </span>
          </div>
          <h3 class="text-[#3d4a42] text-xs font-bold uppercase tracking-widest">Total Properties</h3>
          <p class="text-3xl font-['Syne'] font-bold text-[#191c1e] mt-1">{{ stats.totalProperties || '1,482' }}</p>
        </div>

        <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-[#bccac0]/10 relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
          <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-[#4b41e1]/10 to-transparent rounded-bl-full"></div>
          <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-[#645efb]/10 rounded-2xl text-[#4b41e1]">
              <Icon name="mdi:car-multiple" class="w-8 h-8" />
            </div>
            <span class="text-xs font-bold text-[#4b41e1] px-2 py-1 bg-[#4b41e1]/10 rounded-lg flex items-center gap-1">
              <Icon name="mdi:trending-up" class="w-3 h-3" /> +5.4%
            </span>
          </div>
          <h3 class="text-[#3d4a42] text-xs font-bold uppercase tracking-widest">Fleet Assets</h3>
          <p class="text-3xl font-['Syne'] font-bold text-[#191c1e] mt-1">{{ vehicleStats.totalVehicles || '429' }}</p>
        </div>

        <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-[#bccac0]/10 relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
          <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-[#825100]/10 to-transparent rounded-bl-full"></div>
          <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-[#a36700]/10 rounded-2xl text-[#825100]">
              <Icon name="mdi:chart-bar" class="w-8 h-8" />
            </div>
            <span class="text-xs font-bold text-[#825100] px-2 py-1 bg-[#825100]/10 rounded-lg flex items-center gap-1">
              <Icon name="mdi:trending-flat" class="w-3 h-3" /> 0%
            </span>
          </div>
          <h3 class="text-[#3d4a42] text-xs font-bold uppercase tracking-widest">Valuations (MTD)</h3>
          <p class="text-3xl font-['Syne'] font-bold text-[#191c1e] mt-1">{{ stats.totalValuations || '84' }}</p>
        </div>

        <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-[#bccac0]/10 relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
          <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-emerald-600/10 to-transparent rounded-bl-full"></div>
          <div class="flex justify-between items-start mb-4">
            <div class="p-3 bg-emerald-500/10 rounded-2xl text-emerald-700">
              <Icon name="mdi:shield-check" class="w-8 h-8" />
            </div>
            <span class="text-xs font-bold text-emerald-700 px-2 py-1 bg-emerald-500/10 rounded-lg flex items-center gap-1">
              <Icon name="mdi:check-all" class="w-3 h-3" /> Valid
            </span>
          </div>
          <h3 class="text-[#3d4a42] text-xs font-bold uppercase tracking-widest">Compliance Score</h3>
          <p class="text-3xl font-['Syne'] font-bold text-[#191c1e] mt-1">{{ complianceRate || '98.2%' }}</p>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-12 gap-8 mb-10">
        <div class="col-span-12 lg:col-span-8 bg-white/70 backdrop-blur-xl p-8 rounded-3xl border border-[#bccac0]/10">
          <div class="flex justify-between items-center mb-8">
            <h4 class="font-['Syne'] font-bold text-xl text-[#191c1e]">Valuations Trend</h4>
            <select v-model="timeRange" class="bg-[#f2f4f6] border-none rounded-xl text-sm text-[#3d4a42] px-4 py-2">
              <option>Last 6 Months</option>
              <option>Last Year</option>
            </select>
          </div>
          <div class="h-64 flex items-end justify-between gap-4 px-2">
            <div v-for="(height, i) in chartData" :key="i" class="flex-1 bg-[#006948]/5 rounded-t-xl relative group transition-all hover:bg-[#006948]/10" :style="{ height: height + '%' }">
              <div class="absolute bottom-0 left-0 right-0 bg-[#006948] h-[4px] rounded-full"></div>
            </div>
          </div>
          <div class="flex justify-between mt-4 px-2">
            <span v-for="month in months" :key="month" class="text-[10px] font-bold text-[#3d4a42]">{{ month }}</span>
          </div>
        </div>

        <div class="col-span-12 lg:col-span-4 bg-white/70 backdrop-blur-xl p-8 rounded-3xl border border-[#bccac0]/10 flex flex-col items-center justify-center">
          <h4 class="font-['Syne'] font-bold text-xl text-[#191c1e] mb-6 w-full">Property Distribution</h4>
          <div class="relative w-48 h-48 mb-6">
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path class="text-[#00855d]" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="40, 100" stroke-width="6"></path>
              <path class="text-[#4b41e1]" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="30, 100" stroke-dashoffset="-40" stroke-width="6"></path>
              <path class="text-[#825100]" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="30, 100" stroke-dashoffset="-70" stroke-width="6"></path>
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-2xl font-['Syne'] font-bold">1.4k</span>
              <span class="text-[10px] text-[#3d4a42] uppercase font-bold tracking-tighter">Total</span>
            </div>
          </div>
          <div class="space-y-3 w-full">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#00855d]"></span>
                <span class="font-medium">Residential</span>
              </div>
              <span class="font-bold">40%</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#4b41e1]"></span>
                <span class="font-medium">Commercial</span>
              </div>
              <span class="font-bold">30%</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#825100]"></span>
                <span class="font-medium">Industrial</span>
              </div>
              <span class="font-bold">30%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <section class="bg-white/70 backdrop-blur-xl rounded-3xl overflow-hidden border border-[#bccac0]/10 shadow-sm">
        <div class="p-8 flex justify-between items-center bg-[#f2f4f6]/50">
          <h4 class="font-['Syne'] font-bold text-xl text-[#191c1e]">Recent Valuations</h4>
          <NuxtLink to="/valuations" class="text-[#006948] font-bold text-sm hover:underline">View All</NuxtLink>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-[#f2f4f6]/30">
                <th class="px-8 py-4 text-[10px] uppercase tracking-widest font-bold text-[#3d4a42]">ID</th>
                <th class="px-8 py-4 text-[10px] uppercase tracking-widest font-bold text-[#3d4a42]">Asset</th>
                <th class="px-8 py-4 text-[10px] uppercase tracking-widest font-bold text-[#3d4a42]">Type</th>
                <th class="px-8 py-4 text-[10px] uppercase tracking-widest font-bold text-[#3d4a42]">Status</th>
                <th class="px-8 py-4 text-[10px] uppercase tracking-widest font-bold text-[#3d4a42] text-right">Value</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#bccac0]/5">
              <tr v-for="valuation in recentValuations" :key="valuation.id" class="hover:bg-[#00855d]/5 transition-colors group">
                <td class="px-8 py-5 text-sm font-bold text-[#006948]">#{{ valuation.id }}</td>
                <td class="px-8 py-5">
                  <div class="font-medium text-[#191c1e]">{{ valuation.name }}</div>
                  <div class="text-xs text-[#3d4a42]">{{ valuation.location }}</div>
                </td>
                <td class="px-8 py-5 text-sm">{{ valuation.type }}</td>
                <td class="px-8 py-5">
                  <span :class="getStatusClass(valuation.status)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight">
                    {{ valuation.status }}
                  </span>
                </td>
                <td class="px-8 py-5 text-right font-['Syne'] font-bold text-[#191c1e]">{{ formatCurrency(valuation.value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const authStore = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8020'

const userName = computed(() => authStore.userName || authStore.user?.full_name || 'Admin')

const stats = ref({
  totalProperties: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0,
  propertyTrend: 0,
  valuationTrend: 0,
  marketValueTrend: 0
})

const vehicleStats = ref({
  totalVehicles: 0,
  totalValuations: 0,
  totalMarketValue: 0,
  pendingValuations: 0,
  trend: 0
})

const complianceRate = ref('98.2%')
const timeRange = ref('Last 6 Months')
const chartData = ref([40, 55, 45, 70, 85, 65])
const months = ref(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN'])

const recentValuations = ref([
  { id: 'VAL-88210', name: '22nd St. Bole, Addis Ababa', location: 'Kirkos Municipality', type: 'Commercial Hub', status: 'Completed', value: 2450000 },
  { id: 'VAL-88211', name: 'Lideta Condominiums, Block 12', location: 'Lideta Municipality', type: 'Residential Unit', status: 'In Progress', value: 820000 },
  { id: 'VAL-88212', name: 'Kaliti Industrial Zone A4', location: 'Akaki-Kality Municipality', type: 'Warehousing', status: 'Pending', value: 5600000 }
])

onMounted(async () => {
  await loadDashboardStats()
  await loadVehicleStats()
})

async function loadDashboardStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/analytics/dashboard?period=month`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const data = await response.json()
      stats.value = {
        totalProperties: data.properties?.total ?? 0,
        totalValuations: data.valuations?.total ?? 0,
        totalMarketValue: data.financials?.total_market_value ?? 0,
        pendingValuations: 0,
        propertyTrend: Math.round(data.properties?.growth_rate ?? 0),
        valuationTrend: Math.round(data.valuations?.growth_rate ?? 0),
        marketValueTrend: Math.round(data.financials?.market_value_growth ?? 0)
      }
      if (data.compliance) {
        complianceRate.value = Math.round(data.compliance.compliance_rate ?? 98.2) + '%'
      }
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
  }
}

async function loadVehicleStats() {
  try {
    const token = localStorage.getItem('valuadis_token')
    const response = await fetch(`${apiBase}/api/v1/vehicles/statistics/summary`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const data = await response.json()
      vehicleStats.value = {
        totalVehicles: data.total_vehicles ?? 0,
        totalValuations: data.total_valuations ?? 0,
        totalMarketValue: data.total_market_value ?? 0,
        pendingValuations: data.pending_valuations ?? 0,
        trend: 0
      }
    }
  } catch {
    vehicleStats.value = { totalVehicles: 0, totalValuations: 0, totalMarketValue: 0, pendingValuations: 0, trend: 0 }
  }
}

function formatCurrency(value) {
  if (value == null || isNaN(value)) return 'ETB 0'
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function getStatusClass(status) {
  const s = (status || '').toLowerCase()
  if (s === 'completed' || s === 'approved') return 'bg-emerald-100/50 text-emerald-700'
  if (s === 'in progress' || s === 'draft') return 'bg-[#645efb]/10 text-[#4b41e1]'
  return 'bg-slate-200 text-slate-600'
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
</style>
