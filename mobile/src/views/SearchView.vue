<template>
  <div class="search-page">
    <header class="app-header">
      <h1>Поиск</h1>
    </header>

    <!-- Search input -->
    <div style="padding: 12px 20px;">
      <div style="position: relative;">
        <input
          v-model="query"
          class="input"
          type="search"
          placeholder="Имя, контакт или описание..."
          style="padding-left: 44px;"
          @input="onSearch"
        />
        <span style="position: absolute; left: 16px; top: 50%; transform: translateY(-50%); font-size: 18px;">🔍</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="searching" style="padding: 20px; text-align: center;">
      <div class="ptr-spinner" style="margin: 0 auto;"></div>
    </div>

    <!-- Results -->
    <div v-else-if="results.length" class="leads-list">
      <router-link
        v-for="lead in results"
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
            {{ statusMap[lead.status] || lead.status }}
          </span>
        </div>
        <div v-if="lead.ai_summary" class="lead-summary">
          {{ highlightText(lead.ai_summary) }}
        </div>
        <div class="lead-footer">
          <span class="lead-date">{{ formatDate(lead.created_at) }}</span>
          <span class="lead-arrow">›</span>
        </div>
      </router-link>
    </div>

    <!-- Empty state -->
    <div v-else-if="query && searched" class="empty-state">
      <div class="emoji">🔎</div>
      <h3>Ничего не найдено</h3>
      <p>Попробуйте другой запрос</p>
    </div>

    <!-- Initial state -->
    <div v-else-if="!query" class="empty-state">
      <div class="emoji">🔍</div>
      <h3>Найдите лид</h3>
      <p>Поиск по имени, контакту или содержимому</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../api.js'

const query = ref('')
const results = ref([])
const searching = ref(false)
const searched = ref(false)
let timeout = null

const statusMap = {
  new: 'Новый',
  in_progress: 'В работе',
  completed: 'Готов',
  rejected: 'Отказ',
}

function onSearch() {
  clearTimeout(timeout)
  if (!query.value.trim()) {
    results.value = []
    searched.value = false
    return
  }
  timeout = setTimeout(doSearch, 400)
}

async function doSearch() {
  searching.value = true
  searched.value = true
  try {
    results.value = await api.searchLeads(query.value.trim())
  } catch (e) {
    console.error('Search failed:', e)
    results.value = []
  } finally {
    searching.value = false
  }
}

function highlightText(text) {
  return text?.slice(0, 150) + (text?.length > 150 ? '...' : '')
}

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}
</script>
