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
    <div v-else-if="lead" class="detail-body" style="padding-bottom: 100px;">
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
        <!-- Quick contact actions -->
        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <a :href="contactLink" class="btn btn-sm btn-ghost" style="flex: 1; justify-content: center; border: 1px solid var(--border);">
            {{ contactIcon }} Связаться
          </a>
          <button class="btn btn-sm btn-ghost" style="flex: 1; border: 1px solid var(--border);" @click="copyContact">
            📋 Копировать
          </button>
        </div>
      </div>

      <!-- AI Summary -->
      <div v-if="lead.ai_summary" class="info-block">
        <h3>🤖 AI-анализ</h3>
        <p>{{ lead.ai_summary }}</p>
      </div>

      <!-- Priority -->
      <div class="info-block">
        <h3>🔥 Приоритет</h3>
        <div class="priority-select">
          <button
            v-for="p in priorities"
            :key="p.value"
            class="priority-chip"
            :class="{ active: lead.priority === p.value, [p.value]: true }"
            @click="changePriority(p.value)"
          >
            {{ p.emoji }} {{ p.label }}
          </button>
        </div>
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

      <!-- Notes -->
      <div class="info-block">
        <h3>📝 Заметки ({{ notes.length }})</h3>
        
        <!-- Add note -->
        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
          <input
            v-model="newNote"
            class="input"
            style="flex: 1; padding: 10px 14px; font-size: 14px;"
            placeholder="Добавить заметку..."
            @keyup.enter="addNote"
          />
          <button class="btn btn-primary btn-sm" @click="addNote" :disabled="!newNote.trim()">+</button>
        </div>
        
        <!-- Notes list -->
        <div v-if="notes.length" class="notes-list">
          <div v-for="note in notes" :key="note.id" class="note-item">
            <div class="note-content">
              <div class="note-text">{{ note.text }}</div>
              <div class="note-meta">
                {{ note.author }} · {{ formatDate(note.created_at) }}
              </div>
            </div>
            <button class="btn btn-ghost btn-sm" style="padding: 4px 8px; font-size: 12px;" @click="deleteNote(note.id)">✕</button>
          </div>
        </div>
        <p v-else style="color: var(--text-muted); font-size: 13px;">Пока нет заметок</p>
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

      <!-- Actions row -->
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <button
          v-if="lead.ai_summary"
          class="btn btn-primary"
          style="width: 100%;"
          @click="downloadPdf"
        >
          📄 Скачать PDF-предложение
        </button>
        
        <button
          class="btn btn-danger"
          style="width: 100%; opacity: 0.8;"
          @click="confirmDelete"
        >
          🗑 Удалить лид
        </button>
      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast" class="toast" :class="`toast-${toast.type}`">
        {{ toast.message }}
      </div>
    </transition>

    <!-- Delete confirmation modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal-content">
          <h3 style="margin-bottom: 12px; font-size: 18px;">Удалить лид?</h3>
          <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 20px;">
            Лид «{{ lead?.name }}» будет удалён навсегда. Это действие нельзя отменить.
          </p>
          <div style="display: flex; gap: 10px;">
            <button class="btn btn-ghost" style="flex: 1;" @click="showDeleteModal = false">Отмена</button>
            <button class="btn btn-danger" style="flex: 1;" @click="doDelete">Удалить</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api.js'

const route = useRoute()
const router = useRouter()
const lead = ref(null)
const loading = ref(true)
const changingStatus = ref(false)
const chatExpanded = ref(false)
const toast = ref(null)
const notes = ref([])
const newNote = ref('')
const showDeleteModal = ref(false)

const priorities = [
  { value: 'hot', label: 'Горячий', emoji: '🔥' },
  { value: 'warm', label: 'Тёплый', emoji: '🟡' },
  { value: 'cold', label: 'Холодный', emoji: '❄️' },
]

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

const contactIcon = computed(() => {
  if (!lead.value) return '📞'
  const c = lead.value.contact
  if (c.includes('@')) return '✉️'
  if (c.match(/^\+?\d/)) return '📞'
  return '💬'
})

function formatFullDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function formatDate(iso) {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 60) return `${diffMin} мин назад`
  const diffH = Math.floor(diffMs / 3600000)
  if (diffH < 24) return `${diffH} ч назад`
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

async function fetchLead() {
  try {
    const all = await api.getLeads()
    lead.value = all.find(l => l.id === Number(route.params.id)) || null
    if (lead.value) {
      notes.value = lead.value.notes || []
    }
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

async function changePriority(newPriority) {
  if (lead.value.priority === newPriority) return
  try {
    const updated = await api.updateLead(lead.value.id, { priority: newPriority })
    lead.value.priority = updated.priority || newPriority
    showToast(`Приоритет: ${priorities.find(p => p.value === newPriority)?.label}`)
  } catch (e) {
    showToast(e.message || 'Ошибка', 'error')
  }
}

async function addNote() {
  if (!newNote.value.trim()) return
  try {
    const note = await api.addNote(lead.value.id, newNote.value.trim())
    notes.value.unshift(note)
    newNote.value = ''
    showToast('Заметка добавлена')
  } catch (e) {
    showToast('Ошибка', 'error')
  }
}

async function deleteNote(noteId) {
  try {
    await api.deleteNote(lead.value.id, noteId)
    notes.value = notes.value.filter(n => n.id !== noteId)
    showToast('Заметка удалена')
  } catch (e) {
    showToast('Ошибка', 'error')
  }
}

function confirmDelete() {
  showDeleteModal.value = true
}

async function doDelete() {
  try {
    await api.deleteLead(lead.value.id)
    showToast('Лид удалён')
    setTimeout(() => router.push('/leads'), 1000)
  } catch (e) {
    showToast(e.message || 'Ошибка', 'error')
  }
  showDeleteModal.value = false
}

function copyContact() {
  navigator.clipboard.writeText(lead.value.contact)
    .then(() => showToast('Контакт скопирован'))
    .catch(() => showToast('Не удалось скопировать', 'error'))
}

function downloadPdf() {
  const token = localStorage.getItem('kh_token')
  const base = import.meta.env.VITE_API_BASE || ''
  const url = `${base}/api/leads/${lead.value.id}/proposal`
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
