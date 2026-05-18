const apiBaseUrl = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8020'
const frontendPort = Number(process.env.PORT || 3020)
const frontendHost = process.env.HOST || '127.0.0.1'
const enforceProductionConfig =
  process.env.VALUADIS_ENFORCE_PRODUCTION_CONFIG === 'true' ||
  process.env.ENVIRONMENT === 'production'
const allowLocalBrowserProof = process.env.VALUADIS_LOCAL_BROWSER_PROOF === 'true'

if (enforceProductionConfig) {
  if (!process.env.NUXT_PUBLIC_API_BASE_URL) {
    throw new Error('NUXT_PUBLIC_API_BASE_URL must be set in production')
  }

  if (!allowLocalBrowserProof && /localhost|127\.0\.0\.1/.test(apiBaseUrl)) {
    throw new Error('NUXT_PUBLIC_API_BASE_URL must point to the deployed API in production')
  }

  if (/\/api(\/v[0-9]+)?\/?$/.test(apiBaseUrl)) {
    throw new Error('NUXT_PUBLIC_API_BASE_URL must be the API origin only; the frontend appends /api/v1')
  }
}

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  ssr: false,
  
  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@400;500&display=swap' }
      ]
    }
  },
  
  // Port configuration
  devServer: {
    host: frontendHost,
    port: frontendPort
  },
  
  modules: [
    '@pinia/nuxt'
  ],

  css: [
    '~/assets/css/main.css'
  ],

  typescript: {
    strict: true,
    typeCheck: false
  },

  runtimeConfig: {
    public: {
      apiBaseUrl,
      mapDefaultLat: process.env.NUXT_PUBLIC_MAP_DEFAULT_LAT || '9.0320',
      mapDefaultLng: process.env.NUXT_PUBLIC_MAP_DEFAULT_LNG || '38.7578',
      defaultLanguage: process.env.NUXT_PUBLIC_DEFAULT_LANGUAGE || 'en',
      demoLoginEmail: process.env.NUXT_PUBLIC_DEMO_LOGIN_EMAIL || '',
      demoLoginPassword: process.env.NUXT_PUBLIC_DEMO_LOGIN_PASSWORD || ''
    }
  },

  vite: {
    server: {
      hmr: {
        protocol: 'ws',
        host: frontendHost,
        port: frontendPort,
        clientPort: frontendPort,
      },
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return undefined
            if (id.includes('/primevue/datatable') || id.includes('/primevue/column')) return 'primevue-table'
            if (id.includes('/primevue/chart')) return 'primevue-chart'
            if (id.includes('/primevue/dialog') || id.includes('/primevue/sidebar') || id.includes('/primevue/menu')) return 'primevue-overlay'
            if (id.includes('/primevue/') || id.includes('/primeicons/')) return 'primevue-core'
            if (id.includes('/chart.js/') || id.includes('/vue-chartjs/')) return 'charts'
            if (id.includes('/leaflet')) return 'maps'
            if (id.includes('/@vue/') || id.includes('/vue/') || id.includes('/vue-router/') || id.includes('/pinia/')) return 'vue-vendor'
            return undefined
          }
        }
      }
    },
    optimizeDeps: {
      include: ['leaflet', 'leaflet-draw']
    },
    resolve: {
      alias: {
        'form-data': 'form-data'
      }
    }
  },

  compatibilityDate: '2024-01-01'
})
