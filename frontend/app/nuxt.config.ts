// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,
  
  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap' }
      ]
    }
  },
  
  // Port configuration
  devServer: {
    port: 3020
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
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8020',
      mapDefaultLat: process.env.NUXT_PUBLIC_MAP_DEFAULT_LAT || '9.0320',
      mapDefaultLng: process.env.NUXT_PUBLIC_MAP_DEFAULT_LNG || '38.7578',
      defaultLanguage: process.env.NUXT_PUBLIC_DEFAULT_LANGUAGE || 'en'
    }
  },

  vite: {
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
