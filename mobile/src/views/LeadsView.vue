<template>
  <div class="leads-page">
    <!-- Header -->
    <header class="app-header">
      <div>
        <h1>Лиды</h1>
      </div>
      <div class="header-actions">
        <span v-if="newCount > 0" class="badge">{{ newCount }}</span>
        <button class="btn btn-ghost btn-icon" @click="handleLogout" title="Выйти">🚪</button>
      </div>
    </header>

    <!-- Filter chips -->
    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        class="filter-chip"
        :class="{ active: activeFilter === f.value }"
        @click="activeFilter = f.value"
      >
        {{ f.emoji }} {{ f.label }}
      </button>
    </div>

    <!-- Pull to refresh indicator -->
    <div class="ptr-indicator" :class="{ active: refreshing }">
      <div class="ptr-spinner"></div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading && !leads.length" class="leads-list">
      <div v-for="i in 5" :key="i" class="card" style="height: 100px;">
        <div class="skeleton" style="width: 60%; height: 16px; margin-bottom: 8px;"></div>
        <div class="skeleton" style="width: 40%; height: 14px; margin-bottom: 12px;"></div>
        <div class="skeleton" style="width: 100%; height: 14px;"></div>
      </div>
    </div>

    <!-- Leads list -->
    <div v-else-if="filteredLeads.length" class="leads-list" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
      <router-link
        v-for="lead in filteredLeads"
        :key="lead.id"
        :to="`/lead/${lead.id}`"
        class="card lead-card"
      >
        <div class="lead-card-header">
          <div>
            <div class="lead-name">{{ lead.name }}</div>
            <div class="lead-contact">{{ lead.contact }}</div>
          </div>
          <span class="status" :class="`status-${lead.status}`">
            <span class="status-dot"></span>
            {{ statusLabel(lead.status) }}
          </span>
        </div>
        <div v-if="lead.ai_summary" class="lead-summary">
          {{ lead.ai_summary }}
        </div>
        <div class="lead-footer">
          <span class="lead-date">{{ formatDate(lead.created_at) }}</span>
          <span class="lead-arrow">›</span>
        </div>
      </router-link>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <div class="emoji">📭</div>
      <h3>Нет лидов</h3>
      <p v-if="activeFilter !== 'all'">Попробуйте сменить фильтр</p>
      <p v-else>Новые заявки появятся здесь</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'
import { authStore } from '../stores/auth.js'

const router = useRouter()
const leads = ref([])
const loading = ref(true)
const refreshing = ref(false)
const newCount = ref(0)
const activeFilter = ref('all')

const filters = [
  { value: 'all', label: 'Все', emoji: '📋' },
  { value: 'new', label: 'Новые', emoji: '🔵' },
  { value: 'in_progress', label: 'В работе', emoji: '🟡' },
  { value: 'completed', label: 'Готовые', emoji: '🟢' },
  { value: 'rejected', label: 'Отказ', emoji: '🔴' },
]

const filteredLeads = computed(() => {
  if (activeFilter.value === 'all') return leads.value
  return leads.value.filter(l => l.status === activeFilter.value)
})

function statusLabel(status) {
  const map = {
    new: 'Новый',
    in_progress: 'В работе',
    completed: 'Готов',
    rejected: 'Отказ',
  }
  return map[status] || status
}

function formatDate(iso) {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return 'Только что'
  if (diffMin < 60) return `${diffMin} мин назад`
  if (diffHours < 24) return `${diffHours} ч назад`
  if (diffDays < 7) return `${diffDays} дн назад`

  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

async function fetchLeads() {
  try {
    leads.value = await api.getLeads()
    newCount.value = leads.value.filter(l => l.status === 'new').length
  } catch (e) {
    console.error('Failed to fetch leads:', e)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function handleLogout() {
  authStore.clear()
  router.push('/login')
}

/* ── Pull-to-refresh via touch ── */
let startY = 0

function onTouchStart(e) {
  if (window.scrollY === 0) {
    startY = e.touches[0].clientY
  }
}

function onTouchMove(e) {
  if (window.scrollY === 0) {
    const diff = e.touches[0].clientY - startY
    if (diff > 80 && !refreshing.value) {
      refreshing.value = true
    }
  }
}

function onTouchEnd() {
  if (refreshing.value) {
    fetchLeads()
  }
}

/* ── Auto-refresh every 30s ── */
let interval
onMounted(() => {
  fetchLeads()
  interval = setInterval(fetchLeads, 30000)
})

/* Не используем onUnmounted для setInterval ради простоты —
   при уходе со страницы Vue размонтирует компонент */
</script>
