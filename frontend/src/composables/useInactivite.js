/**
 * Gestion du timeout d'inactivité.
 * Déconnecte l'utilisateur après N minutes sans activité.
 */

import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export function useInactivite() {
  const router  = useRouter()
  let minuterie = null
  let duree     = 30

  async function chargerDuree() {
    try {
      const rep = await axios.get('http://localhost:8000/api/parametres/publics/')
      duree = rep.data.timeout_inactivite || 30
    } catch(e) {}
  }

  function reinitialiser() {
    clearTimeout(minuterie)
    minuterie = setTimeout(() => {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      router.push('/?timeout=1')
    }, duree * 60 * 1000)
  }

  function demarrer() {
    const evenements = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']
    evenements.forEach(e => window.addEventListener(e, reinitialiser))
    reinitialiser()
  }

  function arreter() {
    clearTimeout(minuterie)
    const evenements = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']
    evenements.forEach(e => window.removeEventListener(e, reinitialiser))
  }

  onMounted(async () => {
    await chargerDuree()
    demarrer()
  })

  onUnmounted(() => arreter())
}
