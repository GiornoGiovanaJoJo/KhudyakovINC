import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { routes } from './router.js'
import './assets/styles.css'

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

/* ── Auth guard ── */
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('kh_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
