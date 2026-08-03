import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useParametres } from './useParametres'

export function useInactivite() {
  const router = useRouter()
  let minuterie = null
  let duree = 30

  async function init() {
    const p = await useParametres()
    duree = p.timeout_inactivite || 30
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
    const ev = ['mousemove','keydown','click','scroll','touchstart']
    ev.forEach(e => window.addEventListener(e, reinitialiser))
    reinitialiser()
  }

  function arreter() {
    clearTimeout(minuterie)
    const ev = ['mousemove','keydown','click','scroll','touchstart']
    ev.forEach(e => window.removeEventListener(e, reinitialiser))
  }

  onMounted(async () => { await init(); demarrer() })
  onUnmounted(() => arreter())
}
