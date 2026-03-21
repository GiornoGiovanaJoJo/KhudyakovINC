/**
 * Lightweight API client for the KhudyakovINC backend.
 * In dev mode Vite proxies /api → localhost:8000.
 * In production (Capacitor) we use the full server URL.
 */

// In development, we use '' to let Vite proxy /api to localhost:8000.
// In production (Capacitor APK), we must use the full URL of the server.
const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? '' : 'http://leads.khudyakov-inc.ru')

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
  deleteLead: (id) => request('DELETE', `/api/leads/${id}`),
  getNewLeadsCount: () => request('GET', '/api/leads/count/new'),
  searchLeads: (q) => request('GET', `/api/leads/search?q=${encodeURIComponent(q)}`),

  // Stats
  getStats: () => request('GET', '/api/leads/stats'),

  // Notes
  getNotes: (leadId) => request('GET', `/api/leads/${leadId}/notes`),
  addNote: (leadId, text) => request('POST', `/api/leads/${leadId}/notes`, { text }),
  deleteNote: (leadId, noteId) => request('DELETE', `/api/leads/${leadId}/notes/${noteId}`),

  // Push
  registerPushToken: (token, platform) =>
    request('POST', '/api/push/register', { token, platform }),

  // Users
  getMe: () => request('GET', '/api/users/me'),

  // Agile Projects
  getProjects: () => request('GET', '/api/projects/'),
  getProject: (id) => request('GET', `/api/projects/${id}`),

  // Tasks
  getTasks: (projectId) => request('GET', `/api/tasks/?project_id=${projectId}`),
  updateTask: (id, data) => request('PATCH', `/api/tasks/${id}`, data),

  // AI Manager
  evaluateOrder: (text) => request('POST', '/api/ai/evaluate', { text }),
  askAiQuestion: (text) => request('POST', '/api/ai/ask', { text })
}
