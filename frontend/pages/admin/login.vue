<template>
  <div class="login-page">
    <div class="login-card card">
      <h1 class="login-title">🔐 Вход в админку</h1>
      <p class="login-subtitle">Khudyakov Inc. CMS</p>

      <form @submit.prevent="doLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">Логин</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            placeholder="admin"
            required
            id="login-username"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Пароль</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            placeholder="••••••••"
            required
            id="login-password"
          />
        </div>

        <p v-if="error" class="login-error">{{ error }}</p>

        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
useHead({ title: 'Вход — Админка Khudyakov Inc.' })

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const doLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const res = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { username: username.value, password: password.value },
    })

    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_token', res.access_token)
    }

    navigateTo('/admin')
  } catch (e) {
    error.value = 'Неверный логин или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--space-3xl);
  text-align: center;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-xs);
}

.login-subtitle {
  color: var(--c-text-muted);
  font-size: 0.9rem;
  margin-bottom: var(--space-2xl);
}

.login-form {
  text-align: left;
}

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

.form-input::placeholder {
  color: var(--c-text-muted);
}

.login-error {
  color: var(--c-error);
  font-size: 0.85rem;
  margin-bottom: var(--space-md);
  text-align: center;
}

.login-btn {
  width: 100%;
}
</style>
