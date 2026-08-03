import { ref } from 'vue'
import { usersApi } from '../services/api'

const modules      = ref([])
const profil       = ref('')
const nom          = ref('')
const prenom       = ref('')
const direction    = ref('')
const workflow_type = ref('CLASSIQUE')  // ← AJOUTER
let   loaded       = false

export async function useModules(force = false) {
  if (loaded && !force) {
    return {
      modules:       modules.value,
      profil:        profil.value,
      nom:           nom.value,
      prenom:        prenom.value,
      direction:     direction.value,
      workflow_type: workflow_type.value,  // ← CORRIGER (data n'existe pas)
    }
  }
  try {
    const rep          = await usersApi.monProfil()
    modules.value      = rep.data.modules       || []
    profil.value       = rep.data.profil        || ''
    nom.value          = rep.data.nom           || ''
    prenom.value       = rep.data.prenom        || ''
    direction.value    = rep.data.direction     || ''
    workflow_type.value = rep.data.workflow_type || 'CLASSIQUE'  // ← AJOUTER
    loaded             = true
    localStorage.setItem('ged_modules', JSON.stringify(modules.value))
  } catch(e) {
    const cached = localStorage.getItem('ged_modules')
    if (cached) modules.value = JSON.parse(cached)
    const token = localStorage.getItem('access')
    if (token) {
      try {
        const p = JSON.parse(atob(token.split('.')[1]))
        profil.value       = p.profil        || ''
        nom.value          = p.nom           || ''
        prenom.value       = p.prenom        || ''
        workflow_type.value = p.workflow_type || 'CLASSIQUE'  // ← AJOUTER
      } catch(e2) {}
    }
  }
  return {
    modules:       modules.value,
    profil:        profil.value,
    nom:           nom.value,
    prenom:        prenom.value,
    direction:     direction.value,
    workflow_type: workflow_type.value,  // ← AJOUTER
  }
}

export function clearModulesCache() {
  loaded = false
  modules.value       = []
  profil.value        = ''
  nom.value           = ''
  prenom.value        = ''
  direction.value     = ''
  workflow_type.value = 'CLASSIQUE'  // ← AJOUTER
  localStorage.removeItem('ged_modules')
}

export function hasModule(code) {
  return modules.value.includes(code)
}