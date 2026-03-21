<template>
  <div class="view-container">
    <header class="view-header flex-center">
      <button class="icon-btn" @click="$router.back()">←</button>
      <h2 style="flex-grow:1; text-align:center; font-size: 1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
        {{ project?.title || 'Загрузка...' }}
      </h2>
      <div style="width: 40px;"></div>
    </header>

    <div class="view-content">
      <div v-if="loading" class="text-center p-md">Загрузка задач...</div>
      
      <div v-else>
        <div class="status-tabs">
          <button 
            v-for="col in columns" 
            :key="col.id"
            class="status-tab" 
            :class="{ active: currentFilter === col.id }"
            @click="currentFilter = col.id"
          >
            {{ col.title }}
          </button>
        </div>

        <div class="task-list mt-md">
          <div v-if="filteredTasks.length === 0" class="text-center text-muted p-md">
            Нет задач в этой колонке.
          </div>
          <div 
            v-else 
            v-for="task in filteredTasks" 
            :key="task.id" 
            class="task-card"
            @click="openTaskModal(task)"
          >
            <div class="priority-stripe" :class="'p-' + task.priority"></div>
            <h4>{{ task.title }}</h4>
            <p v-if="task.assignee_id" class="task-assignee">Работник ID: {{ task.assignee_id }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Modal to Edit Status -->
    <Teleport to="body">
      <div v-if="selectedTask" class="modal-overlay" @click.self="selectedTask = null">
        <div class="modal-content">
          <button class="modal-close" @click="selectedTask = null">&times;</button>
          <h3 class="mb-sm">Управление задачей</h3>
          <p class="mb-md text-muted">{{ selectedTask.title }}</p>
          
          <select v-model="selectedTaskStatus" class="input-field w-100 mb-md">
             <option value="todo">К выполнению</option>
             <option value="in_progress">В работе</option>
             <option value="review">На проверке</option>
             <option value="done">Готово</option>
          </select>

          <button class="btn btn-primary w-100" @click="saveTaskStatus" :disabled="saving">
            {{ saving ? 'Сохранение...' : 'Обновить статус' }}
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api.js'

const route = useRoute()
const projectId = route.params.id

const project = ref(null)
const tasks = ref([])
const loading = ref(true)

const columns = [
  { id: 'todo', title: 'To Do' },
  { id: 'in_progress', title: 'Work' },
  { id: 'review', title: 'Review' },
  { id: 'done', title: 'Done' }
]

const currentFilter = ref('todo')

const filteredTasks = computed(() => {
  return tasks.value.filter(t => t.status === currentFilter.value)
})

const selectedTask = ref(null)
const selectedTaskStatus = ref('todo')
const saving = ref(false)

async function loadData() {
  loading.value = true
  try {
    project.value = await api.getProject(projectId)
    tasks.value = await api.getTasks(projectId)
  } catch (e) {
    alert('Ошибка загрузки: ' + e.message)
  } finally {
    loading.value = false
  }
}

function openTaskModal(task) {
  selectedTask.value = task
  selectedTaskStatus.value = task.status
}

async function saveTaskStatus() {
  saving.value = true
  try {
    await api.updateTask(selectedTask.value.id, { status: selectedTaskStatus.value })
    selectedTask.value.status = selectedTaskStatus.value
    selectedTask.value = null
  } catch (e) {
    alert('Ошибка сохранения: ' + e.message)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.flex-center {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.status-tabs {
  display: flex;
  background: var(--surface);
  border-radius: 8px;
  overflow: hidden;
}
.status-tab {
  flex: 1;
  background: none;
  border: none;
  padding: 0.8rem 0;
  color: var(--text);
  font-size: 0.85rem;
  font-weight: 500;
  opacity: 0.6;
}
.status-tab.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 2px solid var(--primary);
}
.task-card {
  background: var(--surface);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.8rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.priority-stripe {
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 4px;
}
.p-low { background: #3498db; }
.p-medium { background: #f1c40f; }
.p-high { background: #e67e22; }
.p-critical { background: #e74c3c; }

.task-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}
.task-assignee {
  margin: 0;
  font-size: 0.8rem;
  color: var(--primary);
}

.modal-content {
  background: var(--bg);
  padding: 1.5rem;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 10px; right: 10px;
  background: none; border: none;
  font-size: 1.5rem; color: var(--text);
}
.w-100 { width: 100%; }
.mt-md { margin-top: 1rem; }
.mb-md { margin-bottom: 1rem; }
.mb-sm { margin-bottom: 0.5rem; }
</style>
