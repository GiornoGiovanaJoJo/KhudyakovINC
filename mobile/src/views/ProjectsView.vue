<template>
  <div class="view-container">
    <header class="view-header">
      <h2>🗂️ Проекты (Agile)</h2>
    </header>
    
    <div class="view-content list-view">
      <div v-if="loading" class="text-center p-md">Загрузка...</div>
      
      <div v-else-if="projects.length === 0" class="text-center p-md text-muted">
        Проектов не найдено.
      </div>

      <div 
        v-else 
        v-for="project in projects" 
        :key="project.id" 
        class="card clickable"
        @click="$router.push(`/project/${project.id}`)"
      >
        <div class="card-header">
          <h3 class="card-title">{{ project.title }}</h3>
          <span class="status-badge" :class="'bg-' + project.status">
            {{ project.status === 'active' ? 'Активный' : 'Завершен' }}
          </span>
        </div>
        <p class="card-desc">{{ project.description || 'Нет описания' }}</p>
        <div v-if="project.deadline" class="card-meta">
          Дедлайн: {{ new Date(project.deadline).toLocaleDateString('ru-RU') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'

const projects = ref([])
const loading = ref(true)

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await api.getProjects()
  } catch (e) {
    alert('Ошибка загрузки проектов: ' + e.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.card {
  background: var(--surface);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.clickable {
  cursor: pointer;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-title {
  margin: 0;
  font-size: 1.1rem;
}
.card-desc {
  color: #bbb;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  font-size: 0.8rem;
  color: #888;
}
.status-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}
.bg-active { background: #2ed573; color: #fff; }
.bg-completed { background: #747d8c; color: #fff; }
</style>
