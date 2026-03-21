<template>
  <div class="admin-projects-tab">
    <div v-if="!selectedProject">
      <div class="admin-section__header mb-md flex-between">
        <h2>Проекты</h2>
        <button v-if="canManage" class="btn btn-primary btn-sm" @click="startAdd">+ Создать Проект</button>
      </div>

      <div class="admin-projects-grid">
        <div v-for="project in projects" :key="project.id" class="project-card" @click="openProject(project)">
          <h3>{{ project.title }}</h3>
          <p class="project-desc">{{ project.description || 'Нет описания' }}</p>
          <div class="project-meta">
            <span class="status-badge" :class="'status-project-' + project.status">{{ project.status === 'active' ? 'Активный' : 'Завершен' }}</span>
            <span class="date" v-if="project.deadline">🔥 {{ formatDate(project.deadline) }}</span>
          </div>
          <div class="project-actions" v-if="canManage" @click.stop>
            <button class="btn btn-outline btn-sm action-btn" @click="startEdit(project)">✏️ Редактировать</button>
            <button class="btn btn-outline btn-sm action-btn" @click="deleteProject(project.id)" title="Удалить">🗑️</button>
          </div>
        </div>
      </div>
      <div v-if="projects.length === 0" class="empty-state">
        Нет доступных проектов.
      </div>
    </div>
    
    <div v-else>
      <div class="mb-md flex-between">
        <div>
          <button class="btn btn-outline btn-sm mb-md" @click="selectedProject = null">← Назад к проектам</button>
          <h2>Доска: {{ selectedProject.title }}</h2>
        </div>
      </div>
      <!-- Render Kanban Component -->
      <AdminKanbanBoard :project="selectedProject" :token="token" :userRole="userRole" :userId="userId" />
    </div>

    <!-- Edit/Add Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content" style="max-width: 500px">
          <button class="admin-modal-close" @click="showModal = false">&times;</button>
          <h2 class="mb-lg">{{ isEditing ? 'Редактировать проект' : 'Создать проект' }}</h2>

          <form @submit.prevent="saveProject" class="admin-form">
            <div class="form-group">
              <label class="form-label">Название</label>
              <input v-model="formData.title" type="text" class="form-input" required />
            </div>
            
            <div class="form-group">
              <label class="form-label">Описание</label>
              <textarea v-model="formData.description" class="form-input form-textarea"></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Статус</label>
              <select v-model="formData.status" class="form-input" required>
                <option value="active">Активный</option>
                <option value="completed">Завершенный</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Дедлайн (опционально)</label>
              <input v-model="formData.deadline" type="datetime-local" class="form-input" />
            </div>

            <div class="admin-form__actions">
              <button type="button" class="btn btn-outline" @click="showModal = false">Отмена</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Сохранение...' : (isEditing ? 'Сохранить' : 'Создать') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminKanbanBoard from './AdminKanbanBoard.vue'

const props = defineProps({
  token: String,
  userRole: String,
  userId: [Number, String]
})

const canManage = computed(() => ['admin', 'manager'].includes(props.userRole))

const projects = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const formData = ref({ title: '', description: '', status: 'active', deadline: '' })
const editingId = ref(null)
const selectedProject = ref(null)

const authHeaders = () => ({ Authorization: `Bearer ${props.token}` })

const loadProjects = async () => {
  try {
    projects.value = await $fetch('/api/projects/', { headers: authHeaders() })
  } catch (e) {
    alert('Ошибка загрузки проектов: ' + (e.data?.detail || e.message))
  }
}

onMounted(() => {
  loadProjects()
})

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  })
}

const startAdd = () => {
  isEditing.value = false
  formData.value = { title: '', description: '', status: 'active', deadline: '' }
  showModal.value = true
}

const startEdit = (project) => {
  isEditing.value = true
  editingId.value = project.id
  let d = ''
  if (project.deadline) {
    d = new Date(project.deadline).toISOString().slice(0, 16)
  }
  formData.value = { ...project, deadline: d }
  showModal.value = true
}

const openProject = (project) => {
  selectedProject.value = project
}

const saveProject = async () => {
  loading.value = true
  try {
    const url = isEditing.value ? `/api/projects/${editingId.value}` : `/api/projects/`
    const method = isEditing.value ? 'PATCH' : 'POST'
    
    const payload = { ...formData.value }
    if (!payload.deadline) delete payload.deadline

    await $fetch(url, {
      method,
      body: payload,
      headers: authHeaders()
    })
    
    showModal.value = false
    loadProjects()
  } catch (e) {
    alert('Ошибка сохранения: ' + (e.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const deleteProject = async (id) => {
  if (!confirm('Удалить проект? Все задачи внутри будут так же удалены.')) return
  try {
    await $fetch(`/api/projects/${id}`, { method: 'DELETE', headers: authHeaders() })
    loadProjects()
  } catch (e) {
    alert('Ошибка удаления: ' + (e.data?.detail || e.message))
  }
}
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.admin-projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-md);
}
.project-card {
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: var(--c-accent);
}
.project-desc {
  color: var(--c-text-secondary);
  font-size: 0.9rem;
  margin: var(--space-xs) 0 var(--space-md) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex-grow: 1;
}
.project-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  font-size: 0.8rem;
}
.status-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}
.status-project-active { background: rgba(46, 213, 115, 0.2); color: #2ed573; }
.status-project-completed { background: rgba(164, 176, 190, 0.2); color: #a4b0be; }

.project-actions {
  display: flex;
  gap: var(--space-xs);
  border-top: 1px solid var(--c-border);
  padding-top: var(--space-sm);
  margin-top: auto;
}
.action-btn { flex: 1; text-align: center; }
.empty-state { text-align: center; padding: 2rem; color: var(--c-text-muted); }
</style>
