<template>
  <div class="login-page">
    <div class="container content-narrow">
      <div class="auth-card glass">
        <h1 class="auth-title">{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>
        <p class="auth-subtitle">
          {{ isLogin ? 'Войдите, чтобы отслеживать свои проекты' : 'Создайте аккаунт для доступа к личному кабинету' }}
        </p>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group" v-if="!isLogin">
            <label class="form-label">Имя</label>
            <input v-model="form.full_name" type="text" class="form-input" placeholder="Иван Иванов" required>
          </div>

          <div class="form-group">
            <label class="form-label">Номер телефона</label>
            <input v-model="form.phone" type="tel" class="form-input" placeholder="+7 (999) 000-00-00" autocomplete="username" required>
          </div>
|
          <div class="form-group">
            <label class="form-label">Пароль</label>
            <input v-model="form.password" type="password" class="form-input" placeholder="••••••••" autocomplete="current-password" required>
          </div>

          <div v-if="error" class="auth-error">{{ error }}</div>

          <button type="submit" class="chat-btn chat-btn--primary auth-submit" :disabled="loading">
            {{ loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Создать аккаунт') }}
          </button>
        </form>

        <div class="auth-switch">
          <button @click="isLogin = !isLogin" class="auth-switch-btn">
            {{ isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const form = reactive({
  phone: '',
  password: '',
  full_name: ''
})

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  const endpoint = isLogin.value ? '/api/auth/login' : '/api/auth/register'
  
  try {
    const payload = isLogin.value ? { username: form.phone, password: form.password } : { ...form }
    
    const { data, error: fetchError } = await useFetch(endpoint, {
      method: 'POST',
      body: payload
    })
    
    if (fetchError.value) {
      error.value = fetchError.value.data?.detail || 'Произошла ошибка'
      return
    }
    
    if (isLogin.value && data.value?.access_token) {
      localStorage.setItem('auth_token', data.value.access_token)
      navigateTo('/profile')
    } else if (!isLogin.value) {
      isLogin.value = true
      error.value = 'Регистрация успешна! Теперь вы можете войти.'
    }
  } catch (e) {
    error.value = 'Ошибка соединения с сервером'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  padding: var(--space-3xl) 0;
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
}

.auth-card {
  padding: var(--space-2xl);
  border-radius: var(--radius-2xl);
  text-align: center;
}

.auth-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: var(--space-xs);
  background: var(--c-gradient-1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.auth-subtitle {
  color: var(--c-text-secondary);
  margin-bottom: var(--space-2xl);
}

.auth-form {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--c-text-primary);
}

.form-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md) var(--space-lg);
  color: var(--c-text-primary);
  transition: all var(--duration-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--c-primary);
  background: rgba(255, 255, 255, 0.08);
}

.auth-submit {
  width: 100%;
  margin-top: var(--space-md);
  padding: var(--space-lg);
}

.auth-error {
  color: #ff4d4d;
  font-size: 0.9rem;
  background: rgba(255, 77, 77, 0.1);
  padding: var(--space-sm);
  border-radius: var(--radius-md);
}

.auth-switch {
  margin-top: var(--space-xl);
}

.auth-switch-btn {
  background: none;
  border: none;
  color: var(--c-text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  transition: color var(--duration-fast);
}

.auth-switch-btn:hover {
  color: var(--c-primary);
}
</style>
