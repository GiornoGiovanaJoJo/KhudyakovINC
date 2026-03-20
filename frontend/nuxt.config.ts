// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: process.env.NODE_ENV === 'development' },

  app: {
    head: {
      title: 'Khudyakov Inc. — Веб-разработка, дизайн и IT-решения',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Khudyakov Inc. — команда профессионалов: веб-разработка, UI/UX дизайн, DevOps и IT-консалтинг.',
        },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/images/logo.png' },
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    apiBase: process.env.NUXT_API_BASE || 'http://localhost:8000',
  },

  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8000/api',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000/static',
        changeOrigin: true,
      },
    },
    routeRules: {
      '/api/**': {
        proxy: (process.env.NUXT_API_BASE || 'http://localhost:8000') + '/api/**',
      },
      '/static/**': {
        proxy: (process.env.NUXT_API_BASE || 'http://localhost:8000') + '/static/**',
      },
    },
  },

  compatibilityDate: '2024-11-01',
})
