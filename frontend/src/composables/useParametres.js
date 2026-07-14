/**
 * Charge et met en cache les paramètres publics de l'application.
 * Applique les couleurs dynamiquement via injection CSS.
 * Recharge automatiquement tous les 60 secondes pour refléter les changements de l'admin.
 */

import { ref } from 'vue'
import axios from 'axios'

const cache = ref(null)
let lastLoadTime = 0
const POLLING_INTERVAL = 60000 // 60 secondes

export async function useParametres(forceReload = false) {
  const now = Date.now()
  
  // Si forceReload=true ou si le cache a plus de 60 secondes, recharger
  if ((cache.value && !forceReload && (now - lastLoadTime < POLLING_INTERVAL))) {
    return cache.value
  }

  try {
    const rep   = await axios.get('http://localhost:8000/api/parametres/publics/')
    cache.value = rep.data
    lastLoadTime = now
    appliquerCouleurs(rep.data)
  } catch(e) {
    cache.value = {
      nom_application:    'GED ESCEP-Niger',
      slogan:             'Gestion Électronique des Documents',
      texte_pied_page:    '© ESCEP-Niger',
      couleur_principale: '#1565C0',
      couleur_accent:     '#FDD835',
      couleur_danger:     '#D32F2F',
      logo_url:           null,
      image_fond_url:     null,
      timeout_inactivite: 30,
    }
  }
  return cache.value
}


export function appliquerCouleurs(params) {
  const c = params.couleur_principale || '#1565C0'
  const a = params.couleur_accent     || '#FDD835'
  const d = params.couleur_danger     || '#D32F2F'

  // Variables CSS
  const root = document.documentElement
  root.style.setProperty('--c-principal', c)
  root.style.setProperty('--c-accent',    a)
  root.style.setProperty('--c-danger',    d)

  // Injection CSS dynamique couvrant toutes les classes
  let style = document.getElementById('ged-couleurs-dynamiques')
  if (!style) {
    style    = document.createElement('style')
    style.id = 'ged-couleurs-dynamiques'
    document.head.appendChild(style)
  }
  style.textContent = `
    .sidebar                             { background-color: ${c} !important; }
    .pied-page                           { background-color: ${c} !important; }
    .topbar-titre                        { color: ${c} !important; }
    .login-titre                         { color: ${c} !important; }
    .login-box                           { border-top-color: ${a} !important; }
    .carte-titre                         { color: ${c} !important; border-bottom-color: ${a} !important; }
    .stat-valeur                         { color: ${c} !important; }
    .tableau th                          { background-color: ${c} !important; }
    .nav-item.actif                      { border-left-color: ${a} !important; }
    .nav-sous-item.actif                 { color: ${a} !important; }
    .sidebar-profil-role                 { color: ${a} !important; }
    .entete-titre                        { color: ${a} !important; }
    .btn-primary, .btn-connexion         { background-color: ${c} !important; }
    .btn-primary:hover:not(:disabled),
    .btn-connexion:hover:not(:disabled)  { background-color: ${c}cc !important; }
    .btn-outline                         { color: ${c} !important; border-color: ${c} !important; }
    .btn-outline:hover                   { background-color: ${c}11 !important; }
    .btn-danger, .btn-rejeter            { background-color: ${d} !important; }
    .badge-saisi                         { color: ${c} !important; }
    .onglet.actif                        { color: ${c} !important; border-bottom-color: ${c} !important; }
    .champ input:focus,
    .champ select:focus,
    .champ textarea:focus                { border-color: ${c} !important; }
    .modal-titre                         { color: ${c} !important; }
    .carte-titre                         { color: ${c} !important; }
  `
}
