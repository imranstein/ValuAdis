<template>
  <div class="settings-modern min-h-screen bg-[#f7f9fb] font-['Inter']">
    <!-- Sidebar -->
    <aside class="fixed left-0 top-0 h-full w-64 z-40 bg-slate-50/80 backdrop-blur-xl flex flex-col p-4 space-y-2 shadow-xl shadow-emerald-900/5">
      <div class="px-4 py-6 mb-4">
        <h1 class="font-['Syne'] font-extrabold text-emerald-800 text-2xl tracking-tight leading-tight">ValuAdis</h1>
        <p class="text-[10px] uppercase tracking-[0.2em] font-bold text-emerald-600/60 mt-1">Federal Valuation Dept</p>
      </div>
      <nav class="flex-1 space-y-1">
        <NuxtLink to="/dashboard" class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 rounded-xl transition-all duration-200 hover:translate-x-1 group">
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
        <NuxtLink to="/settings" class="flex items-center gap-3 px-4 py-3 bg-emerald-100/50 text-emerald-700 rounded-xl font-bold transition-all duration-200 group">
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
          <h2 class="font-['Syne'] font-extrabold text-4xl text-[#191c1e] tracking-tighter">System Settings</h2>
          <p class="text-[#3d4a42] font-medium mt-1">Manage your administrative profile and global system configurations.</p>
        </div>
      </header>

      <!-- Bento Grid Layout -->
      <div class="grid grid-cols-12 gap-6">
        <!-- Administrative Profile -->
        <section class="col-span-12 lg:col-span-8 bg-white/70 backdrop-blur-xl rounded-3xl p-8 border border-white/40 shadow-sm">
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700">
                <Icon name="mdi:account" class="w-6 h-6" />
              </div>
              <h3 class="text-xl font-bold font-['Syne']">Administrative Profile</h3>
            </div>
            <button class="text-sm font-semibold text-emerald-700 hover:underline">Edit Details</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Full Name</label>
              <p class="text-[#191c1e] font-medium border-b border-slate-100 pb-2">{{ userProfile.fullName }}</p>
            </div>
            <div class="space-y-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Email Address</label>
              <p class="text-[#191c1e] font-medium border-b border-slate-100 pb-2">{{ userProfile.email }}</p>
            </div>
            <div class="space-y-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Department</label>
              <p class="text-[#191c1e] font-medium border-b border-slate-100 pb-2">{{ userProfile.department }}</p>
            </div>
            <div class="space-y-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Role Access</label>
              <p class="text-[#191c1e] font-medium border-b border-slate-100 pb-2">{{ userProfile.role }}</p>
            </div>
          </div>
        </section>

        <!-- System Preferences -->
        <section class="col-span-12 lg:col-span-4 bg-white/70 backdrop-blur-xl rounded-3xl p-8 border border-white/40 shadow-sm flex flex-col">
          <div class="flex items-center gap-4 mb-8">
            <div class="w-12 h-12 rounded-2xl bg-indigo-100 flex items-center justify-center text-indigo-700">
              <Icon name="mdi:tune" class="w-6 h-6" />
            </div>
            <h3 class="text-xl font-bold font-['Syne']">System Preferences</h3>
          </div>
          <div class="space-y-6 flex-1">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-bold">Dark Mode</p>
                <p class="text-xs text-slate-500">Toggle system-wide theme</p>
              </div>
              <button @click="toggleDarkMode" :class="darkMode ? 'bg-emerald-600' : 'bg-slate-200'" class="w-12 h-6 rounded-full relative transition-colors p-1">
                <div :class="darkMode ? 'translate-x-6' : 'translate-x-0'" class="w-4 h-4 bg-white rounded-full shadow-sm transition-transform"></div>
              </button>
            </div>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-bold">Data Density</p>
                <p class="text-xs text-slate-500">Compact or Spacious UI</p>
              </div>
              <div class="flex bg-slate-100 p-1 rounded-lg">
                <button @click="dataDensity = 'compact'" :class="dataDensity === 'compact' ? 'bg-white shadow-sm' : 'text-slate-500'" class="px-3 py-1 text-[10px] font-bold rounded-md transition-all">Compact</button>
                <button @click="dataDensity = 'spacious'" :class="dataDensity === 'spacious' ? 'bg-white shadow-sm' : 'text-slate-500'" class="px-3 py-1 text-[10px] font-bold rounded-md transition-all">Spacious</button>
              </div>
            </div>
            <div class="space-y-2 pt-2">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">System Language</label>
              <select v-model="systemLanguage" class="w-full bg-slate-50 border-slate-200 rounded-xl text-sm py-2 px-3 border">
                <option>English (International)</option>
                <option>Amharic (አማርኛ)</option>
                <option>French</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Security & API Integration -->
        <section class="col-span-12 bg-white/70 backdrop-blur-xl rounded-3xl p-8 border border-white/40 shadow-sm">
          <div class="flex items-center gap-4 mb-10">
            <div class="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center text-amber-700">
              <Icon name="mdi:shield" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-xl font-bold font-['Syne']">Security & API Integration</h3>
              <p class="text-xs text-slate-500">Manage sensitive access tokens and authentication layers</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            <!-- Security -->
            <div class="space-y-6">
              <div class="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                <div class="flex items-start justify-between">
                  <div class="flex gap-4">
                    <Icon name="mdi:shield-check" class="w-6 h-6 text-emerald-600" />
                    <div>
                      <p class="font-bold text-sm">Two-Factor Authentication</p>
                      <p class="text-xs text-slate-500 mt-1">Status: <span class="text-emerald-600 font-bold uppercase">Active</span></p>
                    </div>
                  </div>
                  <button class="px-4 py-2 border border-slate-200 rounded-full text-[10px] font-bold uppercase tracking-wider hover:bg-white transition-all">Configure</button>
                </div>
              </div>
              <div class="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                <div class="flex items-start justify-between">
                  <div class="flex gap-4">
                    <Icon name="mdi:lock" class="w-6 h-6 text-slate-400" />
                    <div>
                      <p class="font-bold text-sm">Update Password</p>
                      <p class="text-xs text-slate-500 mt-1">Last updated {{ daysSincePasswordChange }} days ago</p>
                    </div>
                  </div>
                  <button class="px-4 py-2 border border-slate-200 rounded-full text-[10px] font-bold uppercase tracking-wider hover:bg-white transition-all">Update</button>
                </div>
              </div>
            </div>
            <!-- API Keys -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active API Keys</h4>
                <button class="text-[10px] font-bold text-emerald-700 flex items-center gap-1">
                  <Icon name="mdi:plus" class="w-4 h-4" /> GENERATE KEY
                </button>
              </div>
              <div class="space-y-2">
                <div v-for="key in apiKeys" :key="key.id" class="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                  <div>
                    <p class="text-xs font-bold">{{ key.name }}</p>
                    <p class="text-[10px] font-mono text-slate-400">{{ maskApiKey(key.key) }}</p>
                  </div>
                  <div class="flex gap-2">
                    <button @click="copyApiKey(key.key)" class="p-2 hover:bg-slate-50 rounded-lg text-slate-400 hover:text-emerald-600 transition-colors">
                      <Icon name="mdi:content-copy" class="w-4 h-4" />
                    </button>
                    <button @click="deleteApiKey(key.id)" class="p-2 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition-colors">
                      <Icon name="mdi:delete" class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'auth' })

const router = useRouter()
const authStore = useAuthStore()

const darkMode = ref(false)
const dataDensity = ref('compact')
const systemLanguage = ref('English (International)')
const daysSincePasswordChange = ref(42)

const userProfile = ref({
  fullName: 'Abebe Kebede',
  email: 'a.kebede@mof.gov.et',
  department: 'National Property Registry',
  role: 'System Administrator'
})

const apiKeys = ref([
  { id: 1, name: 'PROD_REGISTRY_V4', key: 'sk_live_xxxxxxxxxxxxxxxx4e21' },
  { id: 2, name: 'STAGING_VALUATION_SERVICE', key: 'sk_test_xxxxxxxxxxxxxxxx92a3' }
])

function toggleDarkMode() {
  darkMode.value = !darkMode.value
}

function maskApiKey(key) {
  return key.substring(0, 7) + '••••••••••••' + key.substring(key.length - 4)
}

function copyApiKey(key) {
  navigator.clipboard.writeText(key)
  // Could add toast notification here
}

function deleteApiKey(id) {
  apiKeys.value = apiKeys.value.filter(k => k.id !== id)
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
</style>
