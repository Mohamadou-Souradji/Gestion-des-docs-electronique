import { createRouter, createWebHistory } from 'vue-router'
import LoginView           from '../views/LoginView.vue'
import EspaceView          from '../views/EspaceView.vue'
import AdminView           from '../views/AdminView.vue'
import SuperAdminView      from '../views/SuperAdminView.vue'
import SuperAdminLoginView from '../views/SuperAdminLoginView.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/super-admin/login',
    name: 'super-admin-login',
    component: SuperAdminLoginView,
  },
  {
    path: '/:tenant([a-z0-9-]+)/login',
    name: 'login-tenant',
    component: LoginView,
    props: route => ({ tenantFromRoute: route.params.tenant }),
  },
  {
    path: '/espace',
    name: 'espace',
    component: EspaceView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/super-admin',
    name: 'super-admin',
    component: SuperAdminView,
    meta: { requiresAuth: true, requiresSuperAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
    return
  }

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))

      if (to.meta.requiresSuperAdmin && !payload.is_superuser) {
        next({ name: 'espace' })
        return
      }

      if (to.meta.requiresAdmin && payload.profil !== 'ADMIN') {
        next({ name: 'espace' })
        return
      }
    } catch {
      next({ name: 'login' })
      return
    }
  }

  next()
})

export default router