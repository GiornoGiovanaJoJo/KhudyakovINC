<template>
  <div class="app-shell">
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta.transition || 'fade'" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>

    <!-- Bottom Tab Bar -->
    <nav v-if="showTabs" class="tab-bar">
      <router-link v-if="['admin', 'manager'].includes(userRole)" to="/ai" class="tab-item" :class="{ active: currentTab === 'ai' }">
        <span class="tab-icon">🤖</span>
        <span class="tab-label">AI</span>
      </router-link>
      <router-link to="/leads" class="tab-item" :class="{ active: currentTab === 'leads' }">
        <span class="tab-icon">📋</span>
        <span class="tab-label">CRM</span>
        <span v-if="newCount > 0" class="tab-badge">{{ newCount }}</span>
      </router-link>
      <router-link to="/projects" class="tab-item" :class="{ active: currentTab === 'projects' }">
        <span class="tab-icon">🗂️</span>
        <span class="tab-label">Проекты</span>
      </router-link>
      <router-link to="/settings" class="tab-item" :class="{ active: currentTab === 'settings' }">
        <span class="tab-icon">⚙️</span>
        <span class="tab-label">Ещё</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { authStore } from './stores/auth.js'
import { api } from './api.js'

const route = useRoute()
const newCount = ref(0)
const userRole = ref(authStore.userType === 'admin' ? 'admin' : 'employee')

const showTabs = computed(() => {
  return authStore.isAuthenticated && route.path !== '/login'
})

const currentTab = computed(() => route.meta?.tab || '')

async function fetchBadge() {
  if (!authStore.isAuthenticated) return
  try {
    const data = await api.getNewLeadsCount()
    newCount.value = data.count
  } catch (e) { /* ignore */ }
}

async function fetchRole() {
  if (!authStore.isAuthenticated) return
  try {
    const me = await api.getMe()
    userRole.value = me.role
  } catch (e) {
    if (e.message && e.message.includes('superadmin')) {
      userRole.value = 'admin'
    }
  }
}

watch(() => route.path, () => {
  fetchBadge()
  if (authStore.isAuthenticated && (userRole.value === 'employee' || !userRole.value)) {
    fetchRole()
  }
})

onMounted(() => {
  if (authStore.isAuthenticated) {
     fetchRole()
     fetchBadge()
     setInterval(fetchBadge, 30000)
  }
})
</script>
