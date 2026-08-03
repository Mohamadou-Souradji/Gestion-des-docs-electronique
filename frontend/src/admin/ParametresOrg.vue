<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-sliders"></i> Parametres de l'organisation
    </div>

    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
    </div>

    <div v-else>
      <!-- ONGLETS -->
      <div class="onglets" style="margin-bottom:20px">
        <button :class="['onglet', { actif: onglet === 'identite' }]" @click="onglet = 'identite'">
          <i class="fa-solid fa-id-card"></i> Identite
        </button>
        <button :class="['onglet', { actif: onglet === 'apparence' }]" @click="onglet = 'apparence'">
          <i class="fa-solid fa-palette"></i> Couleurs & Logo
        </button>
        <button :class="['onglet', { actif: onglet === 'typographie' }]" @click="onglet = 'typographie'">
          <i class="fa-solid fa-font"></i> Typographie
        </button>
      </div>

      <!-- ONGLET IDENTITE -->
      <div v-if="onglet === 'identite'" class="grille-form">
        <div class="champ champ-large">
          <label class="champ-obligatoire">Nom de l'organisation</label>
          <input v-model="form.nom_application" type="text" />
        </div>
        <div class="champ champ-large">
          <label>Slogan</label>
          <input v-model="form.slogan" type="text" placeholder="ex: Gelez vos documents efficacement" />
        </div>
        <div class="champ champ-large">
          <label>Texte du pied de page</label>
          <input v-model="form.texte_pied_page" type="text" />
        </div>
      </div>

      <!-- ONGLET COULEURS & LOGO -->
      <div v-if="onglet === 'apparence'" class="grille-form">
        <div class="champ">
          <label>Couleur principale</label>
          <div style="display:flex;gap:10px;align-items:center">
            <input v-model="form.couleur_principale" type="color"
              style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
            <input v-model="form.couleur_principale" type="text"
              style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
          </div>
        </div>
        <div class="champ">
          <label>Couleur accent</label>
          <div style="display:flex;gap:10px;align-items:center">
            <input v-model="form.couleur_accent" type="color"
              style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
            <input v-model="form.couleur_accent" type="text"
              style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
          </div>
        </div>

        <div class="champ champ-large">
          <label>Logo de l'organisation</label>
          <input type="file" accept=".png,.jpg,.jpeg,.svg" @change="e => { fichiers.logo = e.target.files[0]; logoLocalUrl = URL.createObjectURL(e.target.files[0]) }" />
          <div v-if="apercuLogo" style="display:flex;align-items:center;gap:12px;margin-top:10px;padding:10px;background:#f5f8ff;border-radius:6px">
            <img :src="apercuLogo" style="height:50px;object-fit:contain" />
            <button class="btn btn-danger" style="font-size:12px;padding:5px 12px" type="button" @click="supprimerLogo">
              <i class="fa-solid fa-trash"></i> Supprimer
            </button>
          </div>
        </div>

        <div class="champ champ-large">
          <label>Image de fond (page de connexion)</label>
          <input type="file" accept=".png,.jpg,.jpeg" @change="e => { fichiers.fond = e.target.files[0]; fondLocalUrl = URL.createObjectURL(e.target.files[0]) }" />
          <div class="controle-flou" style="display:flex;align-items:center;gap:12px;margin-top:10px">
            <label style="font-size:13px;white-space:nowrap">
              Intensite du flou : <strong>{{ form.flou_image_fond }} px</strong>
            </label>
            <input v-model.number="form.flou_image_fond" type="range" min="0" max="20" step="1"
              style="flex:1;cursor:pointer" />
          </div>
          <div v-if="apercuFond" style="margin-top:10px;border-radius:8px;overflow:hidden;position:relative;height:160px;background:#000">
            <img :src="apercuFond"
              style="width:100%;height:100%;object-fit:cover;display:block;transform:scale(1.08)"
              :style="{ filter: `blur(${form.flou_image_fond}px)` }" />
            <span style="position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.65);color:#fff;padding:4px 8px;border-radius:4px;font-size:11px">
              Apercu
            </span>
            <button class="btn btn-danger" style="position:absolute;top:8px;right:8px;font-size:12px;padding:5px 12px" type="button" @click="supprimerFond">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>

        <div class="champ champ-large">
          <label>Apercu du theme</label>
          <div style="display:flex;gap:12px;align-items:center;padding:12px;background:#fafafa;border:1px solid #eee;border-radius:6px">
            <div :style="{ background: form.couleur_principale, color:'#fff', padding:'8px 16px', borderRadius:'6px', fontSize:'13px', fontWeight:'600' }">
              Couleur principale
            </div>
            <div :style="{ background: form.couleur_accent, color:'#333', padding:'8px 16px', borderRadius:'6px', fontSize:'13px', fontWeight:'600' }">
              Couleur accent
            </div>
          </div>
        </div>
      </div>

      <!-- ONGLET TYPOGRAPHIE -->
      <div v-if="onglet === 'typographie'" class="grille-form">
        <div class="champ">
          <label>Police de caracteres</label>
          <select v-model="form.police">
            <option value="'Segoe UI', sans-serif">Segoe UI (defaut)</option>
            <option value="'Arial', sans-serif">Arial</option>
            <option value="'Roboto', sans-serif">Roboto</option>
            <option value="'Open Sans', sans-serif">Open Sans</option>
            <option value="'Lato', sans-serif">Lato</option>
            <option value="'Montserrat', sans-serif">Montserrat</option>
            <option value="'Georgia', serif">Georgia</option>
            <option value="'Times New Roman', serif">Times New Roman</option>
          </select>
        </div>
        <div class="champ">
          <label>Taille de base des textes</label>
          <select v-model="form.taille_texte_base">
            <option value="13px">Petit (13px)</option>
            <option value="14px">Normal (14px - defaut)</option>
            <option value="15px">Moyen (15px)</option>
            <option value="16px">Grand (16px)</option>
          </select>
        </div>
        <div class="champ">
          <label>Couleur du texte principal</label>
          <div style="display:flex;gap:10px;align-items:center">
            <input v-model="form.couleur_texte" type="color"
              style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
            <input v-model="form.couleur_texte" type="text"
              style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
          </div>
        </div>
        <div class="champ">
          <label>Couleur du texte secondaire</label>
          <div style="display:flex;gap:10px;align-items:center">
            <input v-model="form.couleur_texte_secondaire" type="color"
              style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
            <input v-model="form.couleur_texte_secondaire" type="text"
              style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
          </div>
        </div>
        <div class="champ">
          <label>Graisse des titres</label>
          <select v-model="form.graisse_titres">
            <option value="500">Normale (500)</option>
            <option value="600">Semi-gras (600)</option>
            <option value="700">Gras (700 - defaut)</option>
            <option value="800">Extra-gras (800)</option>
          </select>
        </div>
        <div class="champ">
          <label>Rayon des coins (boutons/cartes)</label>
          <select v-model="form.rayon_bord">
            <option value="0px">Carre (0px)</option>
            <option value="4px">Legerement arrondi (4px)</option>
            <option value="6px">Normal (6px - defaut)</option>
            <option value="10px">Arrondi (10px)</option>
            <option value="20px">Tres arrondi (20px)</option>
          </select>
        </div>

        <div class="champ champ-large">
          <label>Apercu typographie</label>
          <div :style="{
            fontFamily: form.police,
            fontSize: form.taille_texte_base,
            color: form.couleur_texte,
            padding: '16px',
            background: '#fafafa',
            border: '1px solid #eee',
            borderRadius: form.rayon_bord,
          }">
            <div :style="{ fontWeight: form.graisse_titres, fontSize: '18px', marginBottom: '8px' }">
              Titre de section - {{ form.nom_application || 'Organisation' }}
            </div>
            <div :style="{ color: form.couleur_texte_secondaire, fontSize: '13px', marginBottom: '10px' }">
              Texte secondaire : informations complementaires, descriptions, metadonnees.
            </div>
            <div style="display:flex;gap:8px">
              <div :style="{
                background: form.couleur_principale, color: '#fff',
                padding: '8px 16px', borderRadius: form.rayon_bord,
                fontSize: '13px', fontWeight: '600',
              }">Bouton principal</div>
              <div :style="{
                background: 'transparent', color: form.couleur_principale,
                border: `1.5px solid ${form.couleur_principale}`,
                padding: '8px 16px', borderRadius: form.rayon_bord,
                fontSize: '13px', fontWeight: '600',
              }">Bouton secondaire</div>
            </div>
          </div>
        </div>
      </div>

     
      <p v-if="msg" :class="estErreur ? 'msg-erreur' : 'msg-succes'" style="margin-top:12px">{{ msg }}</p>

      <div class="actions-form">
        <button class="btn btn-primary" @click="sauvegarder" :disabled="enEnvoi">
          <i class="fa-solid fa-floppy-disk"></i>
          {{ enEnvoi ? 'Enregistrement...' : 'Enregistrer et appliquer' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useParametres, appliquerCouleurs } from '../composables/useParametres'

const onglet     = ref('identite')
const enEnvoi    = ref(false)
const chargement = ref(false)
const msg        = ref('')
const estErreur  = ref(false)

const form = ref({
  nom_application: '',
  slogan: '',
  texte_pied_page: '',
  couleur_principale: '#1565C0',
  couleur_accent: '#FDD835',
  logo_url: null,
  image_fond_url: null,
  flou_image_fond: 5,
  plan: '',
  max_utilisateurs: 50,
  nb_utilisateurs: 0,
  police: "'Segoe UI', sans-serif",
  taille_texte_base: '14px',
  couleur_texte: '#222222',
  couleur_texte_secondaire: '#666666',
  graisse_titres: '700',
  rayon_bord: '6px'
})

const fichiers     = ref({ logo: null, fond: null, supprimer_logo: false, supprimer_fond: false })
const logoLocalUrl = ref(null)
const fondLocalUrl = ref(null)

const apercuLogo = computed(() => logoLocalUrl.value || form.value.logo_url)
const apercuFond = computed(() => fondLocalUrl.value || form.value.image_fond_url)

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
})

async function charger() {
  chargement.value = true
  try {
    const rep = await api.get('/organisation/parametres/')
    const data = rep.data
    form.value = {
      nom_application: data.nom_application || '',
      slogan: data.slogan || '',
      texte_pied_page: data.texte_pied_page || '',
      couleur_principale: data.couleur_principale || '#1565C0',
      couleur_accent: data.couleur_accent || '#FDD835',
      logo_url: data.logo_url || null,
      image_fond_url: data.image_fond_url || null,
      flou_image_fond: data.flou_image_fond || 5,
      plan: data.plan || '',
      max_utilisateurs: data.max_utilisateurs || 50,
      nb_utilisateurs: data.nb_utilisateurs || 0,
      police: data.police || "'Segoe UI', sans-serif",
      taille_texte_base: data.taille_texte_base || '14px',
      couleur_texte: data.couleur_texte || '#222222',
      couleur_texte_secondaire: data.couleur_texte_secondaire || '#666666',
      graisse_titres: data.graisse_titres || '700',
      rayon_bord: data.rayon_bord || '6px'
    }
  } catch(e) {
    afficherMsg('Erreur lors du chargement.', true)
  } finally { chargement.value = false }
}

function supprimerLogo() {
  form.value.logo_url = null
  logoLocalUrl.value = null
  fichiers.value.logo = null
  fichiers.value.supprimer_logo = true
}

function supprimerFond() {
  form.value.image_fond_url = null
  fondLocalUrl.value = null
  fichiers.value.fond = null
  fichiers.value.supprimer_fond = true
}

function afficherMsg(texte, erreur = false) {
  msg.value = texte
  estErreur.value = erreur
  setTimeout(() => { msg.value = '' }, 4000)
}

async function sauvegarder() {
  enEnvoi.value = true
  try {
    const fd = new FormData()
    const exclus = ['logo_url', 'image_fond_url', 'plan', 'max_utilisateurs', 'nb_utilisateurs']
    
    Object.entries(form.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined && !exclus.includes(k)) {
        fd.append(k, v)
      }
    })

    if (fichiers.value.logo) fd.append('logo', fichiers.value.logo)
    if (fichiers.value.fond) fd.append('image_fond_login', fichiers.value.fond)
    if (fichiers.value.supprimer_logo) fd.append('supprimer_logo', 'true')
    if (fichiers.value.supprimer_fond) fd.append('supprimer_fond', 'true')

    await api.patch('/organisation/parametres/', fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })

    appliquerStyles(form.value)
    await useParametres(true)

    afficherMsg('Parametres enregistres et appliques.')
    logoLocalUrl.value = null
    fondLocalUrl.value = null
    fichiers.value = { logo: null, fond: null, supprimer_logo: false, supprimer_fond: false }
    await charger()
  } catch(e) {
    console.error('Erreur:', e)
    afficherMsg("Erreur lors de l'enregistrement.", true)
  } finally { 
    enEnvoi.value = false 
  }
}

function appliquerStyles(p) {
  appliquerCouleurs(p)
  const root = document.documentElement
  if (p.police)                   root.style.setProperty('--police', p.police)
  if (p.taille_texte_base)        root.style.setProperty('--taille-texte', p.taille_texte_base)
  if (p.couleur_texte)            root.style.setProperty('--couleur-texte', p.couleur_texte)
  if (p.couleur_texte_secondaire) root.style.setProperty('--couleur-texte-sec', p.couleur_texte_secondaire)
  if (p.graisse_titres)           root.style.setProperty('--graisse-titres', p.graisse_titres)
  if (p.rayon_bord)               root.style.setProperty('--rayon-bord', p.rayon_bord)

  let style = document.getElementById('ged-typo-dynamique')
  if (!style) {
    style = document.createElement('style')
    style.id = 'ged-typo-dynamique'
    document.head.appendChild(style)
  }
  style.textContent = `
    body, .app-layout, .carte, .modal, .sidebar-nav {
      font-family: var(--police, 'Segoe UI', sans-serif) !important;
      font-size: var(--taille-texte, 14px);
      color: var(--couleur-texte, #222);
    }
    .carte-titre, .modal-titre, .topbar-titre, h1, h2, h3 {
      font-weight: var(--graisse-titres, 700) !important;
      color: var(--couleur-principale, #1565C0) !important;
    }
    .champ label, .meta-label, .stat-label,
    .sidebar-profil-role, .nav-section-titre {
      color: var(--couleur-texte-sec, #666) !important;
    }
    .btn, .btn-primary, .btn-connexion, .btn-success,
    .btn-danger, .btn-outline, .btn-ghost {
      border-radius: var(--rayon-bord, 6px) !important;
    }
    .carte, .modal, .stat-card, .courrier-card {
      border-radius: var(--rayon-bord, 6px) !important;
    }
  `
}

onMounted(async () => {
  await charger()
  applyOnLoad()
})

async function applyOnLoad() {
  try {
    const rep = await api.get('/organisation/parametres/')
    appliquerStyles(rep.data)
  } catch {}
}
</script>