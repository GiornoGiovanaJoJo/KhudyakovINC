import LoginView from './views/LoginView.vue'
import LeadsView from './views/LeadsView.vue'
import LeadDetail from './views/LeadDetail.vue'

export const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/',
    name: 'Leads',
    component: LeadsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/lead/:id',
    name: 'LeadDetail',
    component: LeadDetail,
    meta: { requiresAuth: true },
  },
]
