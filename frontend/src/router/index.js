/**
 * Routeur de l'application GED ESCEP-Niger.
 * Toutes les routes sont protégées — un utilisateur non connecté
 * est redirigé vers la page de connexion.
 */

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/dg',
      name: 'dg',
      component: () => import('../views/DGView.vue'),
      meta: { profil: 'DG' }
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: () => import('../views/AssistantView.vue'),
      meta: { profil: 'ASSIST' }
    },
    {
      path: '/bureau-ordre',
      name: 'bureau-ordre',
      component: () => import('../views/BureauOrdreView.vue'),
      meta: { profil: 'BO' }
    },
    {
      path: '/destinataire',
      name: 'destinataire',
      component: () => import('../views/DestinataireView.vue'),
      meta: { profil: 'DEST' }
    },
    {
      path: '/archiviste',
      name: 'archiviste',
      component: () => import('../views/ArchivisteView.vue'),
      meta: { profil: 'ARC' }
    },
    {
      path: '/admin-ged',
      name: 'admin-ged',
      component: () => import('../views/AdminView.vue'),
      meta: { profil: 'ADMIN' }
    },
  ]
})

/**
 * Garde de navigation.
 * Vérifie le token avant chaque changement de page.
 * Redirige vers la connexion si le token est absent ou expiré.
 */
router.beforeEach((to) => {
  if (to.name === 'login') return true

  const token = localStorage.getItem('access')
  if (!token) return { name: 'login' }

  // Vérifier l'expiration du token côté client
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const expiration = payload.exp * 1000
    if (Date.now() > expiration) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      return { name: 'login' }
    }
  } catch(e) {
    return { name: 'login' }
  }

  return true
})

export default router
