/**
 * useParametres.js — Paramètres visuels + typographie par organisation.
 * Utilise le tenant_code sauvegardé en localStorage.
 */
import axios from 'axios'

let cache = null

function getTenantCode() {
  try {
    const token = localStorage.getItem('access')
    if (token) {
      const p = JSON.parse(atob(token.split('.')[1]))
      if (p.tenant_code) return p.tenant_code
    }
  } catch (e) {}
  return localStorage.getItem('tenant_code') || ''
}

export async function useParametres(force = false) {
  if (cache && !force) return cache

  const code = getTenantCode()

  try {
    const BASE = import.meta.env.VITE_API_URL || 'https://gestion-des-docs-electronique.onrender.com/api'
      const url = code
      ? `${BASE}/parametres/publics/?tenant=${code}`
      : `${BASE}/parametres/publics/`t:8000/api/parametres/publics/'

    const rep = await axios.get(url)

    if (rep.data) {
      cache = rep.data
      if (cache.code_tenant) localStorage.setItem('tenant_code', cache.code_tenant)
      appliquerStyles(cache)
      appliquerFavicon(cache)
      return cache
    }
  } catch (error) {
    console.error('Erreur chargement parametres:', error)
  }

  cache = {
    nom_application:          'GED',
    slogan:                   'Gestion Electronique des Documents',
    texte_pied_page:          '© GED SaaS',
    couleur_principale:       '#1565C0',
    couleur_accent:           '#FDD835',
    couleur_danger:           '#D32F2F',
    logo_url:                 null,
    favicon_url:              null,
    image_fond_url:           null,
    flou_image_fond:          5,
    timeout_inactivite:       30,
    double_auth_active:       false,
    code_tenant:              code || '',
    police:                   "'Segoe UI', sans-serif",
    taille_texte_base:        '14px',
    couleur_texte:            '#222222',
    couleur_texte_secondaire: '#666666',
    graisse_titres:           '700',
    rayon_bord:               '6px',
  }

  appliquerStyles(cache)
  return cache
}

export function appliquerFavicon(p) {
  // Favicon dynamique selon l'organisation
  const iconUrl = p.favicon_url || p.logo_url
  if (iconUrl) {
    let link = document.querySelector("link[rel~='icon']")
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.head.appendChild(link)
    }
    link.href = iconUrl
  }

  // Titre de l'onglet
  if (p.nom_application) document.title = p.nom_application
}

export function appliquerStyles(p) {
  appliquerCouleurs(p)
  appliquerTypographie(p)
}

export function appliquerCouleurs(p) {
  const c = p.couleur_principale || '#1565C0'
  const a = p.couleur_accent     || '#FDD835'
  const d = p.couleur_danger     || '#D32F2F'

  const root = document.documentElement
  root.style.setProperty('--couleur-principale', c)
  root.style.setProperty('--couleur-accent', a)
  root.style.setProperty('--couleur-danger', d)

  let style = document.getElementById('ged-couleurs-dynamiques')
  if (!style) {
    style = document.createElement('style')
    style.id = 'ged-couleurs-dynamiques'
    document.head.appendChild(style)
  }

  style.textContent = `
    .sidebar {
      background: linear-gradient(180deg,
        var(--couleur-principale,${c}) 0%,
        color-mix(in srgb, var(--couleur-principale,${c}) 95%, black) 100%
      ) !important;
    }
    .nav-item { color: #fff !important; }
    .nav-item:hover { background: rgba(255,255,255,0.15) !important; }
    .nav-item.actif { border-left-color: var(--couleur-accent,${a}) !important; background: rgba(255,255,255,0.1) !important; }
    .nav-sous-item.actif { color: var(--couleur-accent,${a}) !important; font-weight:600 !important; }
    .sidebar-profil-role { color: var(--couleur-accent,${a}) !important; }
    .topbar-titre { color: var(--couleur-principale,${c}) !important; }
    .login-titre { color: var(--couleur-principale,${c}) !important; }
    .login-box { border-top-color: var(--couleur-accent,${a}) !important; }
    .carte-titre { color: var(--couleur-principale,${c}) !important; border-bottom-color: var(--couleur-accent,${a}) !important; }
    .stat-valeur { color: var(--couleur-principale,${c}) !important; }
    .tableau th { background: var(--couleur-principale,${c}) !important; }
    .btn-primary, .btn-connexion { background: var(--couleur-principale,${c}) !important; color:#fff !important; }
    .btn-primary:hover:not(:disabled), .btn-connexion:hover:not(:disabled) {
      background: color-mix(in srgb, var(--couleur-principale,${c}) 80%, black) !important;
    }
    .btn-outline { color: var(--couleur-principale,${c}) !important; border-color: var(--couleur-principale,${c}) !important; }
    .btn-danger { background: var(--couleur-danger,${d}) !important; }
    .modal-titre { color: var(--couleur-principale,${c}) !important; }
    .champ input:focus, .champ select:focus, .champ textarea:focus {
      border-color: var(--couleur-principale,${c}) !important;
    }
    .onglet.actif { color: var(--couleur-principale,${c}) !important; border-bottom-color: var(--couleur-principale,${c}) !important; }
    .pied-page { background: var(--couleur-principale,${c}) !important; }
    .checklist input[type="checkbox"] { accent-color: var(--couleur-principale,${c}) !important; }
  `
}

export function appliquerTypographie(p) {
  const police   = p.police                   || "'Segoe UI', sans-serif"
  const taille   = p.taille_texte_base        || '14px'
  const txtPrinc = p.couleur_texte            || '#222222'
  const txtSec   = p.couleur_texte_secondaire || '#666666'
  const graisse  = p.graisse_titres           || '700'
  const rayon    = p.rayon_bord               || '6px'

  const root = document.documentElement
  root.style.setProperty('--police',            police)
  root.style.setProperty('--taille-texte',      taille)
  root.style.setProperty('--couleur-texte',     txtPrinc)
  root.style.setProperty('--couleur-texte-sec', txtSec)
  root.style.setProperty('--graisse-titres',    graisse)
  root.style.setProperty('--rayon-bord',        rayon)

  let style = document.getElementById('ged-typo-dynamique')
  if (!style) {
    style = document.createElement('style')
    style.id = 'ged-typo-dynamique'
    document.head.appendChild(style)
  }

  style.textContent = `
    body, .app-layout, .carte, .modal, .sidebar-nav, .champ, .tableau {
      font-family: var(--police) !important;
      font-size: var(--taille-texte);
    }
    p, span, label, td, li, input, select, textarea, button {
      font-family: var(--police) !important;
    }
    .carte-titre, .modal-titre, .topbar-titre, h1, h2, h3, h4 {
      font-weight: var(--graisse-titres) !important;
    }
    .champ label, .meta-label, .stat-label,
    .sidebar-profil-role, .nav-section-titre, .courrier-card-exp {
      color: var(--couleur-texte-sec) !important;
    }
    .btn, .btn-primary, .btn-connexion, .btn-success,
    .btn-danger, .btn-outline, .btn-ghost {
      border-radius: var(--rayon-bord) !important;
    }
    .carte, .stat-card, .courrier-card, .kpi-card {
      border-radius: var(--rayon-bord) !important;
    }
    .modal { border-radius: calc(var(--rayon-bord) * 1.5) !important; }
    input, select, textarea { border-radius: var(--rayon-bord) !important; }
    .app-layout .sidebar .nav-item,
    .app-layout .sidebar .nav-sous-item,
    .app-layout .sidebar . {
      color: var(--couleur-texte, #fff) !important;
    }
    .app-layout  {
      color: var(--couleur-texte, #fff) !important;
    } 
  `
}

export function getCachedParametres() { return cache }
export function clearParametresCache() { cache = null }
