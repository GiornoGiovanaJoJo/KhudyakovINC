<template>
  <div class="login-page">
    <div class="login-logo">🔐</div>
    <h1 class="login-title">Khudyakov Leads</h1>
    <p class="login-subtitle">Вход для сотрудников</p>

    <form class="login-form" @submit.prevent="handleLogin">
      <div class="input-group">
        <label for="username">Логин</label>
        <input
          id="username"
          v-model="username"
          class="input"
          type="text"
          placeholder="admin"
          autocomplete="username"
          autocapitalize="none"
          required
        />
      </div>

      <div class="input-group">
        <label for="password">Пароль</label>
        <input
          id="password"
          v-model="password"
          class="input"
          type="password"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />
      </div>

      <div v-if="error" class="login-error">{{ error }}</div>

      <button
        class="btn btn-primary"
        type="submit"
        :disabled="loading"
        style="margin-top: 8px; width: 100%;"
      >
        <span v-if="loading" class="ptr-spinner" style="width:18px;height:18px;border-width:2px;"></span>
        <span v-else>Войти</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'
import { authStore } from '../stores/auth.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const data = await api.login(username.value, password.value)
    authStore.setAuth(data.access_token, data.user_type)
    router.push('/')
  } catch (e) {
    error.value = e.message || 'Неверный логин или пароль'
  } finally {
    loading.value = false
  }
}
</script>
