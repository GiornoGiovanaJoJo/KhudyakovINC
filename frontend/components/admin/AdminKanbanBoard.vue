<template>
  <div class="admin-kanban-board">
    <div class="board-header mb-md flex-between">
      <div class="board-controls">
        <input v-model="searchQuery" class="form-input search-input" placeholder="Поиск задач..." />
      </div>
      <button v-if="canManage" class="btn btn-primary btn-sm" @click="startAddTask">+ Создать задачу</button>
    </div>

    <!-- Board Columns -->
    <div class="kanban-columns">
      <div 
        v-for="col in columns" :key="col.id" 
        class="kanban-column"
        @dragover.prevent
        @drop="onDrop($event, col.id)"
      >
        <div class="column-header">
          <h3>{{ col.title }} ({{ getTasksByStatus(col.id).length }})</h3>
        </div>
        <div class="column-body">
          <div 
            v-for="task in getTasksByStatus(col.id)" :key="task.id"
            class="kanban-card"
            :draggable="canDrag(task)"
            @dragstart="onDragStart($event, task)"
            @click="editTask(task)"
          >
            <div class="task-priority" :class="'priority-' + task.priority"></div>
            <h4>{{ task.title }}</h4>
            <p v-if="task.assignee_id" class="task-assignee">🛠️ Ассигнован: ID {{ task.assignee_id }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content" style="max-width: 500px">
          <button class="admin-modal-close" @click="showModal = false">&times;</button>
          <h2 class="mb-lg">{{ isEditing ? 'Задача' : 'Новая задача' }}</h2>

          <form @submit.prevent="saveTask" class="admin-form">
            <div class="form-group">
              <label class="form-label">Название</label>
              <input v-model="formData.title" type="text" class="form-input" required :disabled="!canManage" />
            </div>
            
            <div class="form-group">
              <label class="form-label">Описание</label>
              <textarea v-model="formData.description" class="form-input form-textarea" :disabled="!canManage"></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Статус</label>
              <select v-model="formData.status" class="form-input" :disabled="!canChangeStatus">
                <option value="todo">К выполнению (To Do)</option>
                <option value="in_progress">В работе (In Progress)</option>
                <option value="review">На проверке (Review)</option>
                <option value="done">Готово (Done)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Приоритет</label>
              <select v-model="formData.priority" class="form-input" :disabled="!canManage">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
                <option value="critical">Критический</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Ответственный (ID пользователя)</label>
              <input v-model="formData.assignee_id" type="number" class="form-input" :disabled="!canManage" />
            </div>

            <div class="admin-form__actions">
              <button v-if="isEditing && canManage" type="button" class="btn btn-outline" style="color:red; border-color:red" @click="deleteTask">Удалить</button>
              <div style="flex-grow: 1"></div>
              <button type="button" class="btn btn-outline" @click="showModal = false">Отмена</button>
              <button v-if="canManage || canChangeStatus" type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Сохранение...' : 'Сохранить' }}
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

const props = defineProps({
  project: Object,
  token: String,
  userRole: String,
  userId: [Number, String]
})

const columns = [
  { id: 'todo', title: 'К выполнению' },
  { id: 'in_progress', title: 'В работе' },
  { id: 'review', title: 'Проверка' },
  { id: 'done', title: 'Готово' }
]

const canManage = computed(() => ['admin', 'manager'].includes(props.userRole))

const tasks = ref([])
const searchQuery = ref('')
const showModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const formData = ref({ title: '', description: '', status: 'todo', priority: 'medium', assignee_id: null })
const editingId = ref(null)

const authHeaders = () => ({ Authorization: `Bearer ${props.token}` })

const loadTasks = async () => {
  try {
    tasks.value = await $fetch(`/api/tasks/?project_id=${props.project.id}`, { headers: authHeaders() })
  } catch (e) {
    alert('Ошибка загрузки задач: ' + (e.data?.detail || e.message))
  }
}

onMounted(() => {
  loadTasks()
})

const getTasksByStatus = (status) => {
  return tasks.value
    .filter(t => t.status === status)
    .filter(t => t.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
}

const canDrag = (task) => {
  if (canManage.value) return true
  // Employee can only drag their assigned tasks
  return task.assignee_id === props.userId
}

const canChangeStatus = computed(() => {
  if (canManage.value) return true
  if (isEditing.value && formData.value.assignee_id === props.userId) return true
  return false
})

const onDragStart = (e, task) => {
  e.dataTransfer.dropEffect = 'move'
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('taskId', task.id.toString())
}

const onDrop = async (e, toStatus) => {
  const taskId = e.dataTransfer.getData('taskId')
  if (!taskId) return
  
  const task = tasks.value.find(t => t.id.toString() === taskId)
  if (!task || task.status === toStatus) return
  
  if (!canDrag(task)) return

  const oldStatus = task.status
  task.status = toStatus // optimistic update

  try {
    await $fetch(`/api/tasks/${task.id}`, {
      method: 'PATCH',
      body: { status: toStatus },
      headers: authHeaders()
    })
  } catch (err) {
    task.status = oldStatus // revert
    alert('Ошибка изменения статуса: ' + (err.data?.detail || err.message))
  }
}

const startAddTask = () => {
  isEditing.value = false
  formData.value = { title: '', description: '', status: 'todo', priority: 'medium', assignee_id: '' }
  showModal.value = true
}

const editTask = (task) => {
  isEditing.value = true
  editingId.value = task.id
  formData.value = { ...task }
  showModal.value = true
}

const saveTask = async () => {
  loading.value = true
  try {
    const url = isEditing.value ? `/api/tasks/${editingId.value}` : `/api/tasks/`
    const method = isEditing.value ? 'PATCH' : 'POST'

    const payload = { ...formData.value }
    payload.project_id = props.project.id
    if (!payload.assignee_id) delete payload.assignee_id

    // Employees can only update status
    if (isEditing.value && !canManage.value) {
      await $fetch(url, {
        method,
        body: { status: payload.status },
        headers: authHeaders()
      })
    } else {
      await $fetch(url, {
        method,
        body: payload,
        headers: authHeaders()
      })
    }
    
    showModal.value = false
    loadTasks()
  } catch (e) {
    alert('Ошибка сохранения: ' + (e.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const deleteTask = async () => {
  if (!confirm('Удалить задачу?')) return
  try {
    await $fetch(`/api/tasks/${editingId.value}`, { method: 'DELETE', headers: authHeaders() })
    showModal.value = false
    loadTasks()
  } catch (e) {
    alert('Ошибка удаления: ' + (e.data?.detail || e.message))
  }
}
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.search-input { width: 300px; }

.kanban-columns {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  padding-bottom: var(--space-md);
  min-height: 500px;
}
.kanban-column {
  flex: 1;
  min-width: 250px;
  background: var(--c-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
}
.column-header {
  padding: var(--space-md);
  border-bottom: 1px solid var(--c-border);
}
.column-header h3 {
  font-size: 0.95rem;
  margin: 0;
  text-transform: uppercase;
  color: var(--c-text-secondary);
}
.column-body {
  padding: var(--space-sm);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.kanban-card {
  background: var(--c-bg-glass);
  border: 1px solid var(--c-border);
  padding: var(--space-md);
  border-radius: var(--radius-sm);
  cursor: grab;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kanban-card:active {
  cursor: grabbing;
}
.kanban-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.kanban-card h4 {
  margin: 0 0 var(--space-xs) 0;
  font-size: 0.95rem;
}
.task-assignee {
  font-size: 0.75rem;
  color: var(--c-text-muted);
  margin: 0;
}

.task-priority {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}
.priority-low { background: #3498db; }
.priority-medium { background: #f1c40f; }
.priority-high { background: #e67e22; }
.priority-critical { background: #e74c3c; }
</style>
