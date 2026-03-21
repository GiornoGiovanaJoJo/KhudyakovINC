/**
 * Lightweight API client for the KhudyakovINC backend.
 * In dev mode Vite proxies /api → localhost:8000.
 * In production (Capacitor) we use the full server URL.
 */

const API_BASE = import.meta.env.VITE_API_BASE || ''

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' }
  const token = localStorage.getItem('kh_token')
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function request(method, path, body = null) {
  const opts = { method, headers: getHeaders() }
  if (body) opts.body = JSON.stringify(body)

  const res = await fetch(`${API_BASE}${path}`, opts)

  if (res.status === 401) {
    localStorage.removeItem('kh_token')
    localStorage.removeItem('kh_user_type')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }

  // Handle empty responses (204 etc.)
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

export const api = {
  // Auth
  login: (username, password) =>
    request('POST', '/api/auth/login', { username, password }),

  // Leads
  getLeads: () => request('GET', '/api/leads'),
  updateLead: (id, data) => request('PATCH', `/api/leads/${id}`, data),
  getNewLeadsCount: () => request('GET', '/api/leads/count/new'),

  // Push
  registerPushToken: (token, platform) =>
    request('POST', '/api/push/register', { token, platform }),
}
