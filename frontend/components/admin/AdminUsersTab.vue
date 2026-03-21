<template>
  <div class="admin-users-tab">
    <div class="admin-section__header mb-md flex-between">
      <h2>Сотрудники CRM</h2>
      <button class="btn btn-primary btn-sm" @click="startAdd">+ Добавить</button>
    </div>

    <div class="admin-table-wrapper">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Telegram</th>
            <th>Роль</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.full_name || '—' }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ user.email || '—' }}</td>
            <td>{{ user.telegram || '—' }}</td>
            <td>
              <span class="role-badge" :class="'role-' + user.role">{{ user.role }}</span>
            </td>
            <td class="admin-table__actions">
              <button class="btn btn-outline btn-sm" @click="startEdit(user)">✏️</button>
              <button class="btn btn-outline btn-sm" @click="deleteUser(user.id)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit/Add Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content" style="max-width: 500px">
          <button class="admin-modal-close" @click="showModal = false">&times;</button>
          <h2 class="mb-lg">{{ isEditing ? 'Редактировать сотрудника' : 'Добавить сотрудника' }}</h2>

          <form @submit.prevent="saveUser" class="admin-form">
            <div class="form-group">
              <label class="form-label">Телефон (логин)</label>
              <input v-model="formData.phone" type="text" class="form-input" required :disabled="isEditing" />
            </div>
            
            <div class="form-group" v-if="!isEditing || formData.password">
              <label class="form-label">{{ isEditing ? 'Новый пароль (опционально)' : 'Пароль' }}</label>
              <input v-model="formData.password" type="password" class="form-input" :required="!isEditing" />
            </div>

            <div class="form-group">
              <label class="form-label">ФИО</label>
              <input v-model="formData.full_name" type="text" class="form-input" />
            </div>

            <div class="form-group">
              <label class="form-label">Роль</label>
              <select v-model="formData.role" class="form-input" required>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="employee">Employee</option>
              </select>
            </div>

            <div class="admin-form__actions">
              <button type="button" class="btn btn-outline" @click="showModal = false">Отмена</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Загрузка...' : (isEditing ? 'Сохранить' : 'Создать') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  token: String
})

const users = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const formData = ref({ phone: '', password: '', full_name: '', role: 'employee' })
const editingId = ref(null)

const authHeaders = () => ({ Authorization: `Bearer ${props.token}` })

const loadUsers = async () => {
  try {
    users.value = await $fetch('/api/users/', { headers: authHeaders() })
  } catch (e) {
    alert('Ошибка загрузки пользователей: ' + (e.data?.detail || e.message))
  }
}

onMounted(() => {
  loadUsers()
})

const startAdd = () => {
  isEditing.value = false
  formData.value = { phone: '', password: '', full_name: '', role: 'employee' }
  showModal.value = true
}

const startEdit = (user) => {
  isEditing.value = true
  editingId.value = user.id
  formData.value = { ...user, password: '' }
  showModal.value = true
}

const saveUser = async () => {
  loading.value = true
  try {
    const url = isEditing.value ? `/api/users/${editingId.value}` : `/api/users/`
    const method = isEditing.value ? 'PATCH' : 'POST'
    
    const payload = { ...formData.value }
    if (isEditing.value && !payload.password) {
      delete payload.password
    }

    await $fetch(url, {
      method,
      body: payload,
      headers: authHeaders()
    })
    
    showModal.value = false
    loadUsers()
  } catch (e) {
    alert('Ошибка сохранения: ' + (e.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const deleteUser = async (id) => {
  if (!confirm('Точно удалить сотрудника?')) return
  try {
    await $fetch(`/api/users/${id}`, { method: 'DELETE', headers: authHeaders() })
    loadUsers()
  } catch (e) {
    alert('Ошибка удаления: ' + (e.data?.detail || e.message))
  }
}
</script>

<style scoped>
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.role-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}
.role-admin { background: #ff4757; color: white; }
.role-manager { background: #ffa502; color: white; }
.role-employee { background: #2ed573; color: white; }
</style>
