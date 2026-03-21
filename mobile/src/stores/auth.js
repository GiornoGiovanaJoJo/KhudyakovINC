import { reactive } from 'vue'

export const authStore = reactive({
  token: localStorage.getItem('kh_token') || null,
  userType: localStorage.getItem('kh_user_type') || null,

  get isAuthenticated() {
    return !!this.token
  },

  get isAdmin() {
    return this.userType === 'admin'
  },

  setAuth(token, userType) {
    this.token = token
    this.userType = userType
    localStorage.setItem('kh_token', token)
    localStorage.setItem('kh_user_type', userType)
  },

  clear() {
    this.token = null
    this.userType = null
    localStorage.removeItem('kh_token')
    localStorage.removeItem('kh_user_type')
  },
})
