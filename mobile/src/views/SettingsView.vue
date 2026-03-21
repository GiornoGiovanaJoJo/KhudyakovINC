<template>
  <div class="settings-page">
    <header class="app-header">
      <h1>Настройки</h1>
    </header>

    <div class="detail-body" style="padding-bottom: 100px;">
      <!-- Profile card -->
      <div class="info-block">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div class="avatar">{{ initials }}</div>
          <div>
            <div style="font-size: 18px; font-weight: 700; color: var(--text-primary);">{{ displayName }}</div>
            <div style="font-size: 13px; color: var(--text-secondary);">Администратор</div>
          </div>
        </div>
      </div>

      <!-- App info -->
      <div class="info-block">
        <h3>📱 О приложении</h3>
        <div class="info-row">
          <span class="label">Версия</span>
          <span class="value">1.0.0</span>
        </div>
        <div class="info-row">
          <span class="label">Платформа</span>
          <span class="value">{{ platform }}</span>
        </div>
        <div class="info-row">
          <span class="label">Сервер</span>
          <span class="value" style="font-size: 12px; color: var(--text-muted);">khudyakov-inc.ru</span>
        </div>
      </div>

      <!-- Quick settings -->
      <div class="info-block">
        <h3>🔔 Настройки</h3>
        <div class="settings-row" @click="toggleAutoRefresh">
          <div>
            <div style="font-weight: 500;">Авто-обновление</div>
            <div style="font-size: 12px; color: var(--text-muted);">Обновлять лиды каждые 30 сек</div>
          </div>
          <div class="toggle" :class="{ on: autoRefresh }"></div>
        </div>
        <div class="settings-row" @click="toggleSound">
          <div>
            <div style="font-weight: 500;">Звук уведомлений</div>
            <div style="font-size: 12px; color: var(--text-muted);">Звуковой сигнал при новом лиде</div>
          </div>
          <div class="toggle" :class="{ on: soundOn }"></div>
        </div>
      </div>

      <!-- Data management -->
      <div class="info-block">
        <h3>🗂 Данные</h3>
        <button class="btn btn-ghost" style="width: 100%; justify-content: flex-start; padding: 14px 0; color: var(--text-primary);" @click="clearCache">
          🗑 Очистить кеш приложения
        </button>
        <button class="btn btn-ghost" style="width: 100%; justify-content: flex-start; padding: 14px 0; color: var(--text-primary);" @click="exportStats">
          📊 Экспорт статистики
        </button>
      </div>

      <!-- Danger zone -->
      <button class="btn btn-danger" style="width: 100%;" @click="handleLogout">
        🚪 Выйти из аккаунта
      </button>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast" class="toast toast-success">{{ toast }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../stores/auth.js'
import { api } from '../api.js'

const router = useRouter()
const toast = ref('')
const autoRefresh = ref(localStorage.getItem('kh_auto_refresh') !== 'false')
const soundOn = ref(localStorage.getItem('kh_sound') !== 'false')

const displayName = computed(() => {
  return authStore.userType === 'admin' ? 'Admin' : 'Сотрудник'
})

const initials = computed(() => {
  return displayName.value.slice(0, 2).toUpperCase()
})

const platform = computed(() => {
  const ua = navigator.userAgent
  if (/android/i.test(ua)) return 'Android'
  if (/iphone|ipad/i.test(ua)) return 'iOS'
  return 'Web Browser'
})

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  localStorage.setItem('kh_auto_refresh', autoRefresh.value)
  showToast(autoRefresh.value ? 'Авто-обновление включено' : 'Авто-обновление выключено')
}

function toggleSound() {
  soundOn.value = !soundOn.value
  localStorage.setItem('kh_sound', soundOn.value)
  showToast(soundOn.value ? 'Звук включён' : 'Звук выключен')
}

function clearCache() {
  showToast('Кеш очищен')
}

async function exportStats() {
  try {
    const data = await api.getStats()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `leads_stats_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(a.href)
    showToast('Статистика экспортирована')
  } catch (e) {
    showToast('Ошибка экспорта')
  }
}

function handleLogout() {
  authStore.clear()
  router.push('/login')
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 2500)
}
</script>
