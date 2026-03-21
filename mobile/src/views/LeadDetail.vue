<template>
  <div class="detail-page">
    <!-- Header -->
    <header class="detail-header">
      <button class="back-btn" @click="$router.back()">←</button>
      <div style="flex: 1;">
        <h1 style="font-size: 17px; font-weight: 600;">{{ lead?.name || 'Лид' }}</h1>
      </div>
      <span v-if="lead" class="status" :class="`status-${lead.status}`">
        <span class="status-dot"></span>
        {{ statusLabel(lead.status) }}
      </span>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="detail-body">
      <div class="skeleton" style="height: 80px;"></div>
      <div class="skeleton" style="height: 200px;"></div>
    </div>

    <!-- Content -->
    <div v-else-if="lead" class="detail-body">
      <!-- Contact info -->
      <div class="info-block">
        <h3>📞 Контактные данные</h3>
        <div class="info-row">
          <span class="label">Имя</span>
          <span class="value">{{ lead.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Контакт</span>
          <span class="value">
            <a :href="contactLink" style="color: var(--accent-light);">{{ lead.contact }}</a>
          </span>
        </div>
        <div class="info-row">
          <span class="label">Дата</span>
          <span class="value">{{ formatFullDate(lead.created_at) }}</span>
        </div>
        <div class="info-row">
          <span class="label">ID</span>
          <span class="value">#{{ lead.id }}</span>
        </div>
      </div>

      <!-- AI Summary -->
      <div v-if="lead.ai_summary" class="info-block">
        <h3>🤖 AI-анализ</h3>
        <p>{{ lead.ai_summary }}</p>
      </div>

      <!-- Status change -->
      <div class="info-block">
        <h3>📌 Изменить статус</h3>
        <div class="status-actions">
          <button
            v-for="s in statuses"
            :key="s.value"
            class="status-btn"
            :class="{ active: lead.status === s.value }"
            :data-status="s.value"
            @click="changeStatus(s.value)"
            :disabled="changingStatus"
          >
            <span class="icon">{{ s.emoji }}</span>
            {{ s.label }}
          </button>
        </div>
      </div>

      <!-- Chat history -->
      <div v-if="lead.chat_history" class="info-block">
        <h3>
          💬 История чата
          <button
            class="btn btn-ghost btn-sm"
            style="float: right; margin-top: -4px;"
            @click="chatExpanded = !chatExpanded"
          >
            {{ chatExpanded ? 'Свернуть' : 'Развернуть' }}
          </button>
        </h3>
        <pre v-if="chatExpanded" style="font-size: 13px; color: var(--text-secondary);">{{ lead.chat_history }}</pre>
        <p v-else style="color: var(--text-muted); font-size: 13px;">
          {{ lead.chat_history.slice(0, 200) }}{{ lead.chat_history.length > 200 ? '...' : '' }}
        </p>
      </div>

      <!-- Download PDF -->
      <button
        v-if="lead.ai_summary"
        class="btn btn-primary"
        style="width: 100%;"
        @click="downloadPdf"
      >
        📄 Скачать PDF-предложение
      </button>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast" class="toast" :class="`toast-${toast.type}`">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api.js'

const route = useRoute()
const lead = ref(null)
const loading = ref(true)
const changingStatus = ref(false)
const chatExpanded = ref(false)
const toast = ref(null)

const statuses = [
  { value: 'new', label: 'Новый', emoji: '🔵' },
  { value: 'in_progress', label: 'В работе', emoji: '🟡' },
  { value: 'completed', label: 'Готов', emoji: '🟢' },
  { value: 'rejected', label: 'Отказ', emoji: '🔴' },
]

function statusLabel(status) {
  const found = statuses.find(s => s.value === status)
  return found ? found.label : status
}

const contactLink = computed(() => {
  if (!lead.value) return '#'
  const c = lead.value.contact
  if (c.includes('@')) return `mailto:${c}`
  if (c.match(/^\+?\d/)) return `tel:${c}`
  if (c.startsWith('t.me/') || c.startsWith('@')) return `https://t.me/${c.replace(/^@/, '')}`
  return '#'
})

function formatFullDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

async function fetchLead() {
  try {
    const all = await api.getLeads()
    lead.value = all.find(l => l.id === Number(route.params.id)) || null
  } catch (e) {
    console.error('Failed to fetch lead:', e)
  } finally {
    loading.value = false
  }
}

async function changeStatus(newStatus) {
  if (lead.value.status === newStatus || changingStatus.value) return
  changingStatus.value = true

  try {
    const updated = await api.updateLead(lead.value.id, { status: newStatus })
    lead.value.status = updated.status
    showToast(`Статус изменён на «${statusLabel(newStatus)}»`)
  } catch (e) {
    showToast(e.message || 'Ошибка', 'error')
  } finally {
    changingStatus.value = false
  }
}

function downloadPdf() {
  const token = localStorage.getItem('kh_token')
  const base = import.meta.env.VITE_API_BASE || ''
  const url = `${base}/api/leads/${lead.value.id}/proposal`

  // Open in new tab with auth header via fetch + blob
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(res => {
      if (!res.ok) throw new Error('PDF download failed')
      return res.blob()
    })
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `Proposal_${lead.value.name.replace(/\s/g, '_')}.pdf`
      a.click()
      URL.revokeObjectURL(a.href)
      showToast('PDF скачан!')
    })
    .catch(() => showToast('Не удалось скачать PDF', 'error'))
}

onMounted(fetchLead)
</script>
