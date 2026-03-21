<template>
  <div class="dashboard-page">
    <header class="app-header">
      <div>
        <h1>Дашборд</h1>
        <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">{{ todayStr }}</p>
      </div>
      <div class="header-actions">
        <span v-if="stats.today > 0" class="badge">+{{ stats.today }}</span>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="detail-body">
      <div class="skeleton" style="height: 100px;"></div>
      <div class="skeleton" style="height: 140px;"></div>
      <div class="skeleton" style="height: 200px;"></div>
    </div>

    <div v-else class="detail-body" style="padding-bottom: 100px;">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-value">{{ stats.total }}</span>
          <span class="kpi-label">Всего лидов</span>
        </div>
        <div class="kpi-card kpi-accent">
          <span class="kpi-value">{{ stats.today }}</span>
          <span class="kpi-label">Сегодня</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-value">{{ stats.week }}</span>
          <span class="kpi-label">За неделю</span>
        </div>
        <div class="kpi-card kpi-success">
          <span class="kpi-value">{{ stats.conversion }}%</span>
          <span class="kpi-label">Конверсия</span>
        </div>
      </div>

      <!-- Status breakdown -->
      <div class="info-block">
        <h3>📊 По статусам</h3>
        <div class="bar-chart">
          <div v-for="s in statusBars" :key="s.key" class="bar-row">
            <div class="bar-label">
              <span class="bar-emoji">{{ s.emoji }}</span>
              <span>{{ s.name }}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: s.pct + '%', background: s.color }"></div>
            </div>
            <span class="bar-count">{{ s.count }}</span>
          </div>
        </div>
      </div>

      <!-- Priority breakdown -->
      <div class="info-block">
        <h3>🔥 По приоритету</h3>
        <div class="priority-pills">
          <div class="priority-pill hot">
            <span class="pp-icon">🔥</span>
            <span class="pp-count">{{ stats.by_priority?.hot || 0 }}</span>
            <span class="pp-label">Горячие</span>
          </div>
          <div class="priority-pill warm">
            <span class="pp-icon">🟡</span>
            <span class="pp-count">{{ stats.by_priority?.warm || 0 }}</span>
            <span class="pp-label">Тёплые</span>
          </div>
          <div class="priority-pill cold">
            <span class="pp-icon">❄️</span>
            <span class="pp-count">{{ stats.by_priority?.cold || 0 }}</span>
            <span class="pp-label">Холодные</span>
          </div>
        </div>
      </div>

      <!-- Weekly chart -->
      <div v-if="Object.keys(stats.daily || {}).length > 0" class="info-block">
        <h3>📈 Активность за неделю</h3>
        <div class="week-chart">
          <div v-for="(count, day) in stats.daily" :key="day" class="week-bar-col">
            <div class="week-bar" :style="{ height: weekBarHeight(count) + 'px' }">
              <span class="week-bar-val">{{ count }}</span>
            </div>
            <span class="week-bar-label">{{ day }}</span>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="info-block">
        <h3>⚡ Быстрые действия</h3>
        <div class="quick-actions">
          <router-link to="/leads" class="quick-btn">
            <span>📋</span> Все лиды
          </router-link>
          <router-link to="/search" class="quick-btn">
            <span>🔍</span> Поиск
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'

const stats = ref({
  total: 0, today: 0, week: 0, conversion: 0,
  by_status: {}, by_priority: {}, daily: {},
})
const loading = ref(true)

const todayStr = new Date().toLocaleDateString('ru-RU', {
  weekday: 'long', day: 'numeric', month: 'long',
})

const statusBars = computed(() => {
  const s = stats.value.by_status || {}
  const total = stats.value.total || 1
  return [
    { key: 'new', name: 'Новые', emoji: '🔵', color: '#3b82f6', count: s.new || 0, pct: ((s.new || 0) / total * 100) },
    { key: 'in_progress', name: 'В работе', emoji: '🟡', color: '#ffaa00', count: s.in_progress || 0, pct: ((s.in_progress || 0) / total * 100) },
    { key: 'completed', name: 'Готовые', emoji: '🟢', color: '#00d68f', count: s.completed || 0, pct: ((s.completed || 0) / total * 100) },
    { key: 'rejected', name: 'Отказ', emoji: '🔴', color: '#ff4757', count: s.rejected || 0, pct: ((s.rejected || 0) / total * 100) },
  ]
})

function weekBarHeight(count) {
  const daily = stats.value.daily || {}
  const max = Math.max(...Object.values(daily), 1)
  return Math.max(20, (count / max) * 100)
}

onMounted(async () => {
  try {
    stats.value = await api.getStats()
  } catch (e) {
    console.error('Failed to load stats:', e)
  } finally {
    loading.value = false
  }
})
</script>
