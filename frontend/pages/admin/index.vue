<template>
  <div class="admin-page section">
    <div class="container">
      <div class="admin-header">
        <h1 class="section__title" style="text-align: left">⚙️ Админ-панель</h1>
        <button class="btn btn-outline btn-sm" @click="logout">Выйти</button>
      </div>

      <!-- Tabs -->
      <div class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="admin-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <!-- Team Tab -->
      <div v-if="activeTab === 'team'" class="admin-section">
        <div class="admin-section__header">
          <h2>Команда</h2>
          <button class="btn btn-primary btn-sm" @click="startAdd('team')">+ Добавить</button>
        </div>

        <div class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Порядок</th>
                <th>Имя</th>
                <th>Должность</th>
                <th>Стек</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in teamList" :key="item.id">
                <td>{{ item.order }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.position }}</td>
                <td class="admin-table__stack">{{ item.stack }}</td>
                <td class="admin-table__actions">
                  <button class="btn btn-outline btn-sm" @click="startEdit('team', item)">✏️</button>
                  <button class="btn btn-outline btn-sm" @click="deleteItem('team', item.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Services Tab -->
      <div v-if="activeTab === 'services'" class="admin-section">
        <div class="admin-section__header">
          <h2>Услуги</h2>
          <button class="btn btn-primary btn-sm" @click="startAdd('services')">+ Добавить</button>
        </div>

        <div class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Порядок</th>
                <th>Иконка</th>
                <th>Название</th>
                <th>Описание</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in servicesList" :key="item.id">
                <td>{{ item.order }}</td>
                <td>{{ item.icon }}</td>
                <td>{{ item.title }}</td>
                <td class="admin-table__desc">{{ item.description }}</td>
                <td class="admin-table__actions">
                  <button class="btn btn-outline btn-sm" @click="startEdit('services', item)">✏️</button>
                  <button class="btn btn-outline btn-sm" @click="deleteItem('services', item.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Portfolio Tab -->
      <div v-if="activeTab === 'portfolio'" class="admin-section">
        <div class="admin-section__header">
          <h2>Портфолио</h2>
          <button class="btn btn-primary btn-sm" @click="startAdd('portfolio')">+ Добавить</button>
        </div>

        <div class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Порядок</th>
                <th>Название</th>
                <th>Slug</th>
                <th>Теги</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in portfolioList" :key="item.id">
                <td>{{ item.order }}</td>
                <td>{{ item.title }}</td>
                <td>{{ item.slug }}</td>
                <td>{{ item.tags }}</td>
                <td class="admin-table__actions">
                  <button class="btn btn-outline btn-sm" @click="startEdit('portfolio', item)">✏️</button>
                  <button class="btn btn-outline btn-sm" @click="deleteItem('portfolio', item.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Edit / Add Modal -->
      <Teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
          <div class="modal-content" style="max-width: 700px">
            <button class="admin-modal-close" @click="showModal = false">&times;</button>
            <h2 class="mb-lg">{{ isEditing ? 'Редактировать' : 'Добавить' }}</h2>

            <form @submit.prevent="saveItem" class="admin-form">
              <div v-for="field in currentFields" :key="field.key" class="form-group">
                <label class="form-label">{{ field.label }}</label>
                <textarea
                  v-if="field.type === 'textarea'"
                  v-model="formData[field.key]"
                  class="form-input form-textarea"
                  rows="4"
                ></textarea>
                <div v-else-if="field.key === 'photo_url' || field.key === 'image_url'" class="upload-field">
                  <input
                    v-model="formData[field.key]"
                    type="text"
                    class="form-input mb-2"
                    placeholder="URL или загрузите файл"
                  />
                  <div class="upload-control">
                    <input
                      type="file"
                      @change="handleFileUpload($event, field.key)"
                      accept="image/*"
                      class="hidden-input"
                      :id="'file-' + field.key"
                    />
                    <label :for="'file-' + field.key" class="btn btn-outline btn-sm">
                      📁 Загрузить файл
                    </label>
                    <span v-if="uploadingField === field.key" class="upload-status">Загрузка...</span>
                  </div>
                </div>
                <input
                  v-else
                  v-model="formData[field.key]"
                  :type="field.type || 'text'"
                  class="form-input"
                />
              </div>

              <div class="admin-form__actions">
                <button type="button" class="btn btn-outline" @click="showModal = false">Отмена</button>
                <button type="submit" class="btn btn-primary">
                  {{ isEditing ? 'Сохранить' : 'Создать' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
useHead({ title: 'Админ-панель — Khudyakov Inc.' })

const tabs = [
  { key: 'team', label: 'Команда', icon: '👥' },
  { key: 'services', label: 'Услуги', icon: '🛠️' },
  { key: 'portfolio', label: 'Портфолио', icon: '💼' },
]

const activeTab = ref('team')
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const editingType = ref('')
const formData = ref({})
const uploadingField = ref(null)

const teamList = ref([])
const servicesList = ref([])
const portfolioList = ref([])

// Auth check
const token = ref('')

onMounted(() => {
  if (typeof window !== 'undefined') {
    token.value = localStorage.getItem('admin_token') || ''
    if (!token.value) {
      navigateTo('/admin/login')
      return
    }
    loadAll()
  }
})

const authHeaders = () => ({
  Authorization: `Bearer ${token.value}`,
})

const loadAll = async () => {
  try {
    const [t, s, p] = await Promise.all([
      $fetch('/api/team/'),
      $fetch('/api/services/'),
      $fetch('/api/portfolio/'),
    ])
    teamList.value = t
    servicesList.value = s
    portfolioList.value = p
  } catch (e) {
    console.error('Ошибка загрузки данных:', e)
  }
}

// Field definitions
const fieldDefs = {
  team: [
    { key: 'name', label: 'Имя' },
    { key: 'position', label: 'Должность' },
    { key: 'stack', label: 'Стек (через запятую)' },
    { key: 'description', label: 'Описание опыта', type: 'textarea' },
    { key: 'photo_url', label: 'URL фото' },
    { key: 'order', label: 'Порядок', type: 'number' },
  ],
  services: [
    { key: 'title', label: 'Название' },
    { key: 'description', label: 'Описание', type: 'textarea' },
    { key: 'icon', label: 'Иконка (emoji)' },
    { key: 'order', label: 'Порядок', type: 'number' },
  ],
  portfolio: [
    { key: 'title', label: 'Название' },
    { key: 'slug', label: 'Slug (URL)' },
    { key: 'short_description', label: 'Краткое описание', type: 'textarea' },
    { key: 'full_description', label: 'Полное описание', type: 'textarea' },
    { key: 'image_url', label: 'URL изображения' },
    { key: 'tags', label: 'Теги (через запятую)' },
    { key: 'order', label: 'Порядок', type: 'number' },
  ],
}

const currentFields = computed(() => fieldDefs[editingType.value] || [])

const startAdd = (type) => {
  editingType.value = type
  isEditing.value = false
  editingId.value = null
  formData.value = {}
  showModal.value = true
}

const startEdit = (type, item) => {
  editingType.value = type
  isEditing.value = true
  editingId.value = item.id
  formData.value = { ...item }
  showModal.value = true
}

const handleFileUpload = async (event, fieldKey) => {
  const file = event.target.files[0]
  if (!file) return

  const formDataObj = new FormData()
  formDataObj.append('file', file)

  uploadingField.value = fieldKey
  try {
    const response = await $fetch('/api/upload/', {
      method: 'POST',
      body: formDataObj,
      headers: {
        Authorization: `Bearer ${token.value}`,
      }
    })
    formData.value[fieldKey] = response.url
  } catch (e) {
    alert('Ошибка загрузки: ' + (e.data?.detail || e.message))
  } finally {
    uploadingField.value = null
  }
}

const saveItem = async () => {
  const type = editingType.value
  const url = isEditing.value ? `/api/${type}/${editingId.value}` : `/api/${type}/`
  const method = isEditing.value ? 'PUT' : 'POST'

  try {
    await $fetch(url, {
      method,
      body: formData.value,
      headers: authHeaders(),
    })
    showModal.value = false
    await loadAll()
  } catch (e) {
    alert('Ошибка сохранения: ' + (e.data?.detail || e.message))
  }
}

const deleteItem = async (type, id) => {
  if (!confirm('Удалить элемент?')) return

  try {
    await $fetch(`/api/${type}/${id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    await loadAll()
  } catch (e) {
    alert('Ошибка удаления: ' + (e.data?.detail || e.message))
  }
}

const logout = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('admin_token')
  }
  navigateTo('/admin/login')
}
</script>

<style scoped>
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2xl);
}

.admin-header .section__title {
  margin-bottom: 0;
}

/* ── Tabs ────────────────────────────── */
.admin-tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-2xl);
  border-bottom: 1px solid var(--c-border);
  padding-bottom: var(--space-sm);
}

.admin-tab {
  padding: 0.6rem 1.2rem;
  background: none;
  border: none;
  color: var(--c-text-secondary);
  font-family: var(--font-main);
  font-size: 0.95rem;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);
}

.admin-tab:hover {
  background: var(--c-bg-glass);
  color: var(--c-text-primary);
}

.admin-tab.active {
  background: var(--c-bg-card);
  color: var(--c-accent-light);
  border: 1px solid var(--c-border);
}

/* ── Section ─────────────────────────── */
.admin-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.admin-section__header h2 {
  font-size: 1.2rem;
  font-weight: 600;
}

/* ── Table ────────────────────────────── */
.admin-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.admin-table th,
.admin-table td {
  padding: 0.8rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--c-border);
}

.admin-table th {
  color: var(--c-text-muted);
  font-weight: 500;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.admin-table td {
  color: var(--c-text-secondary);
}

.admin-table tbody tr:hover {
  background: var(--c-bg-glass);
}

.admin-table__stack,
.admin-table__desc {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-table__actions {
  display: flex;
  gap: var(--space-xs);
  white-space: nowrap;
}

/* ── Form ─────────────────────────────── */
.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--c-text-secondary);
  margin-bottom: var(--space-xs);
}

.form-input {
  width: 100%;
  padding: 0.7rem 1rem;
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-sm);
  color: var(--c-text-primary);
  font-family: var(--font-main);
  font-size: 0.95rem;
  outline: none;
  transition: border-color var(--duration-fast);
}

.form-input:focus {
  border-color: var(--c-accent);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.admin-form__actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
  margin-top: var(--space-xl);
}

.admin-modal-close {
  position: absolute;
  top: var(--space-lg);
  right: var(--space-lg);
  background: none;
  border: none;
  color: var(--c-text-secondary);
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);
}

.admin-modal-close:hover {
  color: var(--c-text-primary);
  background: var(--c-bg-glass);
}

@media (max-width: 768px) {
  .admin-tabs {
    flex-wrap: wrap;
  }
}

.upload-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hidden-input {
  display: none;
}

.upload-status {
  font-size: 0.8rem;
  color: var(--c-accent-light);
}

.mb-2 {
  margin-bottom: 0.5rem;
}
</style>
