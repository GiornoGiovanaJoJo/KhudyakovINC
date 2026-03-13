<template>
  <div class="profile-page">
    <div class="container">
      <div v-if="loading" class="text-center py-20">Загрузка...</div>
      
      <div v-else-if="user" class="profile-layout">
        <!-- Sidebar -->
        <aside class="profile-sidebar glass">
          <div class="user-info">
            <div class="user-avatar text-gradient">
              {{ user.full_name?.charAt(0) || '👤' }}
            </div>
            <h2 class="user-name">{{ user.full_name || 'Клиент' }}</h2>
            <p class="user-phone">{{ user.phone }}</p>
          </div>
          
          <nav class="profile-nav">
            <button class="nav-btn active">Мои проекты</button>
            <button @click="logout" class="nav-btn logout">Выйти</button>
          </nav>
        </aside>

        <!-- Main Content -->
        <main class="profile-content">
          <div class="content-header">
            <h1 class="content-title">История проектов</h1>
          </div>

          <div v-if="leads.length" class="leads-list">
            <div v-for="lead in leads" :key="lead.id" class="lead-card glass">
              <div class="lead-header">
                <div class="lead-info">
                  <h3 class="lead-name">{{ lead.name }}</h3>
                  <p class="lead-date">{{ formatDate(lead.created_at) }}</p>
                </div>
                <div class="lead-status" :class="lead.status">
                  {{ formatStatus(lead.status) }}
                </div>
              </div>

              <div class="lead-summary" v-if="lead.ai_summary">
                <h4 class="summary-title">Аналитика ИИ</h4>
                <p class="summary-text">{{ lead.ai_summary }}</p>
              </div>

              <div class="lead-actions" v-if="lead.status === 'completed'">
                <a :href="`/api/leads/${lead.id}/proposal`" class="chat-btn chat-btn--primary">
                  Скачать КП (PDF)
                </a>
              </div>
            </div>
          </div>

          <div v-else class="empty-state glass">
             <p>У вас пока нет активных проектов.</p>
             <NuxtLink to="/" class="chat-btn chat-btn--primary mt-md">Начать проект</NuxtLink>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
const user = ref(null)
const leads = ref([])
const loading = ref(true)

onMounted(async () => {
  const token = localStorage.getItem('auth_token')
  if (!token) {
    navigateTo('/auth/login')
    return
  }

  try {
    const [userRes, leadsRes] = await Promise.all([
      $fetch('/api/users/me', { headers: { Authorization: `Bearer ${token}` } }),
      $fetch('/api/users/my-leads', { headers: { Authorization: `Bearer ${token}` } })
    ])
    user.value = userRes
    leads.value = leadsRes
  } catch (e) {
    localStorage.removeItem('auth_token')
    navigateTo('/auth/login')
  } finally {
    loading.value = false
  }
})

function logout() {
  localStorage.removeItem('auth_token')
  window.location.href = '/'
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function formatStatus(status) {
  const statuses = {
    'new': 'Ожидание',
    'in_progress': 'В работе',
    'completed': 'Готов',
    'rejected': 'Отклонен'
  }
  return statuses[status] || status
}
</script>

<style scoped>
.profile-page {
  padding: var(--space-3xl) 0;
  background: var(--c-bg-secondary);
  min-height: calc(100vh - 80px);
}

.profile-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--space-2xl);
}

.profile-sidebar {
  padding: var(--space-xl);
  border-radius: var(--radius-2xl);
  height: fit-content;
  position: sticky;
  top: 100px;
}

.user-info {
  text-align: center;
  padding-bottom: var(--space-xl);
  border-bottom: 1px solid var(--c-border);
  margin-bottom: var(--space-xl);
}

.user-avatar {
  width: 80px;
  height: 80px;
  background: rgba(255,255,255,0.05);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto var(--space-md);
  box-shadow: 0 0 20px rgba(0,0,0,0.2);
}

.user-name {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
}

.user-phone {
  color: var(--c-text-muted);
  font-size: 0.9rem;
}

.profile-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.nav-btn {
  width: 100%;
  padding: var(--space-md);
  border: none;
  background: none;
  border-radius: var(--radius-lg);
  color: var(--c-text-secondary);
  text-align: left;
  cursor: pointer;
  transition: all var(--duration-fast);
  font-weight: 500;
}

.nav-btn.active, .nav-btn:hover {
  background: rgba(255,255,255,0.05);
  color: var(--c-text-primary);
}

.nav-btn.logout {
  color: #ff4d4d;
  margin-top: var(--space-xl);
}

.content-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: var(--space-xl);
}

.leads-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.lead-card {
  padding: var(--space-xl);
  border-radius: var(--radius-xl);
  transition: transform var(--duration-fast);
}

.lead-card:hover {
  transform: translateY(-2px);
}

.lead-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.lead-name {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.lead-date {
  font-size: 0.85rem;
  color: var(--c-text-muted);
}

.lead-status {
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(255,255,255,0.05);
}

.lead-status.new { color: var(--c-primary); background: rgba(var(--c-primary-rgb), 0.1); }
.lead-status.in_progress { color: #f39c12; background: rgba(243, 156, 18, 0.1); }
.lead-status.completed { color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
.lead-status.rejected { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }

.lead-summary {
  background: rgba(0,0,0,0.2);
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
}

.summary-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--c-text-secondary);
  margin-bottom: var(--space-sm);
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-title::before {
  content: '✦';
  color: var(--c-primary);
}

.summary-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--c-text-secondary);
}

.empty-state {
  padding: var(--space-3xl);
  text-align: center;
  border-radius: var(--radius-2xl);
  color: var(--c-text-muted);
}

@media (max-width: 900px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}
</style>
