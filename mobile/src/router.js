import LoginView from './views/LoginView.vue'
import LeadsView from './views/LeadsView.vue'
import LeadDetail from './views/LeadDetail.vue'
import DashboardView from './views/DashboardView.vue'
import SearchView from './views/SearchView.vue'
import SettingsView from './views/SettingsView.vue'
import ProjectsView from './views/ProjectsView.vue'
import ProjectDetail from './views/ProjectDetail.vue'
import AiManagerView from './views/AiManagerView.vue'

export const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, tab: 'dashboard' },
  },
  {
    path: '/leads',
    name: 'Leads',
    component: LeadsView,
    meta: { requiresAuth: true, tab: 'leads' },
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchView,
    meta: { requiresAuth: true, tab: 'search' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true, tab: 'settings' },
  },
  {
    path: '/lead/:id',
    name: 'LeadDetail',
    component: LeadDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/projects',
    name: 'Projects',
    component: ProjectsView,
    meta: { requiresAuth: true, tab: 'projects' },
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: ProjectDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/ai',
    name: 'AiManager',
    component: AiManagerView,
    meta: { requiresAuth: true, tab: 'ai' },
  },
]
