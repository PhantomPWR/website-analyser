// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: [['@nuxt/ui', { colorMode: false }]],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '',
    },
  },
  routeRules: {
    '/analyse/**': { proxy: 'http://backend:8000/analyse/**' },
    '/reports/**': { proxy: 'http://backend:8000/reports/**' },
    '/health': { proxy: 'http://backend:8000/health' },
  },
})
