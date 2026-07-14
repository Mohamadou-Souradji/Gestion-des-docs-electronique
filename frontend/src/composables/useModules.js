/**
 * Gestion des modules actifs de l'utilisateur connecté.
 * Chargé depuis /api/moi/ au démarrage de chaque page.
 * Se rafraîchit toutes les 60 secondes pour refléter
 * les changements faits par l'admin en temps réel.
 */

import { ref } from 'vue'
import axios from 'axios'

let cache      = null
let lastLoad   = 0
const listeners = new Set()

function notifier() {
  listeners.forEach(fn => fn())
}

export function subscribeModules(fn) {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export function clearModulesCache() {
  cache    = null
  lastLoad = 0
  localStorage.removeItem('modules_cache')
  notifier()
}

export async function useModules(force = false) {
  const now = Date.now()
  // Retourner le cache si il a moins de 60 secondes et pas de forçage
  if (cache && !force && (now - lastLoad) < 60000) {
    return cache
  }

  try {
    const token = localStorage.getItem('access')
    if (!token) return []

    const rep = await axios.get('http://localhost:8000/api/moi/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    cache    = rep.data.modules || []
    lastLoad = now
    localStorage.setItem('modules_cache', JSON.stringify(cache))
    notifier()
  } catch(e) {
    // Utiliser le cache local si l'API échoue
    const local = localStorage.getItem('modules_cache')
    cache = local ? JSON.parse(local) : []
  }

  return cache
}
