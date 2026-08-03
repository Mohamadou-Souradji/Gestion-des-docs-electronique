<template>
  <div class="login-page">
    <!-- Fond dynamique -->
    <div v-if="parametres.image_fond_url" class="fond-image"
      :style="{ backgroundImage: `url(${parametres.image_fond_url})`, filter: `blur(${parametres.flou_image_fond}px)` }">
    </div>
    <div v-else class="fond-defaut" :style="{ backgroundColor: parametres.couleur_principale || '#1565C0' }"></div>
    <div class="login-overlay"></div>

    <div class="login-box">
      <!-- Logo dynamique -->
      <img v-if="parametres.logo_url" :src="parametres.logo_url" alt="Logo" class="logo" />
      <div v-else class="logo-placeholder">
        <i class="fa-solid fa-file-lines"></i>
      </div>

      <h1 class="login-titre">{{ parametres.nom_application || 'GED' }}</h1>
      <p class="login-slogan">{{ parametres.slogan }}</p>

      <!-- ═══ ÉTAPE 1 : Code organisation ═══ -->
      <!-- Visible UNIQUEMENT si aucun tenant mémorisé -->
      <div v-if="!tenantValide" class="tenant-selector">
        <div class="tenant-selector-titre">
          <i class="fa-solid fa-building"></i> Entrez le code de votre organisation
        </div>
        <input
          v-model="tenantSaisi"
          type="text"
          placeholder="Code organisation (ex: escep, ministere...)"
          @keyup.enter="validerTenant"
          :class="{ 'input-error': erreurTenant }"
          autofocus
        />
        <p v-if="erreurTenant" class="erreur">
          <i class="fa-solid fa-triangle-exclamation"></i> {{ erreurTenant }}
        </p>
        <button class="btn-connexion" @click="validerTenant"
          :disabled="!tenantSaisi.trim() || rechercheEnCours">
          <span v-if="rechercheEnCours">
            <i class="fa-solid fa-spinner fa-spin"></i> Vérification...
          </span>
          <span v-else>Continuer <i class="fa-solid fa-arrow-right"></i></span>
        </button>
      </div>

      <!-- ═══ ÉTAPE 2 : Connexion ═══ -->
      <!-- Visible seulement si tenant validé en localStorage -->
      <div v-else>
        <!-- Badge organisation — PAS de bouton "Changer" visible par défaut
             Il n'apparaît QUE si l'utilisateur est sur un poste partagé
             et clique sur "Changer d'organisation" -->
        <div class="org-badge">
          <div class="org-badge-info">
            <img v-if="parametres.logo_url" :src="parametres.logo_url" class="org-badge-logo" />
            <i v-else class="fa-solid fa-building"></i>
            <span>{{ parametres.nom_application }}</span>
          </div>
          <!-- Le bouton "Changer" est discret, en bas de la box -->
        </div>

        <div v-if="timeoutAlert" class="alerte-info">
          <i class="fa-solid fa-clock"></i>
          Vous avez été déconnecté automatiquement.
        </div>

        <!-- Connexion normale -->
        <div v-if="!etape2fa">
          <div class="champ">
            <label>Identifiant</label>
            <input v-model="form.identifiant" type="text" placeholder="Votre identifiant"
              @keyup.enter="seConnecter" autocomplete="username" autofocus />
          </div>
          <div class="champ">
            <label>Mot de passe</label>
            <div style="position:relative">
              <input v-model="form.password" :type="afficherMdp ? 'text' : 'password'"
                placeholder="Votre mot de passe" @keyup.enter="seConnecter"
                autocomplete="current-password" style="padding-right:50px" />
              <button type="button" @click="afficherMdp = !afficherMdp"
                style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:#666;font-size:13px">
                {{ afficherMdp ? 'Cacher' : 'Voir' }}
              </button>
            </div>
          </div>
          <p v-if="erreur" class="erreur">
            <i class="fa-solid fa-triangle-exclamation"></i> {{ erreur }}
          </p>
          <button class="btn-connexion" @click="seConnecter" :disabled="enChargement">
            {{ enChargement ? 'Connexion...' : 'Se connecter' }}
          </button>

          <!-- Lien discret tout en bas pour changer d'organisation -->
          <div style="text-align:center;margin-top:16px">
            <button @click="demanderChangementOrg" class="btn-lien" style="font-size:11px;color:#bbb">
              <i class="fa-solid fa-rotate" style="font-size:10px"></i> Changer d'organisation
            </button>
          </div>
        </div>

        <!-- 2FA -->
        <div v-else>
          <div class="alerte-info">
            <i class="fa-solid fa-envelope"></i> {{ message2fa }}
          </div>
          <div class="champ">
            <label>Code de vérification (6 chiffres)</label>
            <input v-model="code2fa" type="text" maxlength="6" placeholder="000000"
              @keyup.enter="verifier2fa"
              style="letter-spacing:8px;font-size:20px;text-align:center" autofocus />
          </div>
          <p v-if="erreur" class="erreur">{{ erreur }}</p>
          <button class="btn-connexion" @click="verifier2fa" :disabled="enChargement">
            {{ enChargement ? 'Vérification...' : 'Valider le code' }}
          </button>
          <button class="btn-lien" @click="renvoyer2fa">Renvoyer le code</button>
          <button class="btn-lien" @click="etape2fa = false">Retour</button>
        </div>
      </div>
    </div>

    <!-- Confirmation changement d'organisation -->
    <div v-if="modalChangement" class="confirm-modal-fond">
      <div class="confirm-modal">
        <div style="font-size:18px;font-weight:700;color:#333;margin-bottom:10px">
          <i class="fa-solid fa-rotate" style="color:#1565C0"></i>
          Changer d'organisation ?
        </div>
        <p style="font-size:14px;color:#555;margin-bottom:20px">
          Cela effacera l'organisation mémorisée sur ce poste.
          Vous devrez ressaisir un code organisation.
        </p>
        <!-- Vérification mot de passe avant changement (sécurité) -->
        <div class="champ" style="margin-bottom:12px">
          <label style="font-size:13px;font-weight:600;color:#444">
            Confirmez avec votre identifiant
          </label>
          <input v-model="confirmIdentifiant" type="text"
            placeholder="Votre identifiant actuel"
            style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <p v-if="erreurConfirm" class="erreur" style="font-size:12px">{{ erreurConfirm }}</p>
        <div style="display:flex;gap:10px;justify-content:flex-end">
          <button @click="modalChangement = false; confirmIdentifiant = ''; erreurConfirm = ''"
            style="padding:9px 18px;background:#f5f5f5;border:1px solid #ddd;border-radius:6px;cursor:pointer;font-size:14px">
            Annuler
          </button>
          <button @click="confirmerChangementOrg"
            style="padding:9px 18px;background:#D32F2F;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600">
            <i class="fa-solid fa-rotate"></i> Changer
          </button>
        </div>
      </div>
    </div>

    <p class="login-pied">{{ parametres.texte_pied_page || '© GED SaaS' }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useParametres, clearParametresCache } from '../composables/useParametres'
import { clearModulesCache } from '../composables/useModules'

const router = useRouter()
const route  = useRoute()

const parametres = ref({
  nom_application: 'GED', slogan: 'Gestion Électronique des Documents',
  texte_pied_page: '© GED SaaS', couleur_principale: '#1565C0',
  logo_url: null, image_fond_url: null, flou_image_fond: 5,
})

const form            = ref({ identifiant: '', password: '' })
const erreur          = ref('')
const enChargement    = ref(false)
const afficherMdp     = ref(false)
const etape2fa        = ref(false)
const code2fa         = ref('')
const message2fa      = ref('')
const timeoutAlert    = ref(false)
const tenantSaisi     = ref('')
const erreurTenant    = ref('')
const rechercheEnCours = ref(false)

// Modal confirmation changement
const modalChangement   = ref(false)
const confirmIdentifiant = ref('')
const erreurConfirm     = ref('')

// tenantValide = true si tenant_code dans localStorage
// PERSISTE après déconnexion et redémarrage PC
const tenantValide = computed(() => !!localStorage.getItem('tenant_code'))

async function chargerParametresTenant(code) {
  try {
    const rep = await axios.get(`http://localhost:8000/api/parametres/publics/?tenant=${code}`)
    if (rep.data?.couleur_principale) {
      parametres.value = rep.data
      // Mettre à jour le titre de l'onglet
      if (rep.data.nom_application) {
        document.title = rep.data.nom_application
      }
    }
  } catch {}
}

async function validerTenant() {
  erreurTenant.value = ''
  const code = tenantSaisi.value.trim().toLowerCase()
  if (!code) return

  rechercheEnCours.value = true
  try {
    const rep = await axios.get(`http://localhost:8000/api/parametres/publics/?tenant=${code}`)
    if (rep.data?.code_tenant) {
      // Sauvegarder DÉFINITIVEMENT — reste même après déconnexion / redémarrage
      localStorage.setItem('tenant_code', rep.data.code_tenant)
      parametres.value = rep.data
      if (rep.data.nom_application) document.title = rep.data.nom_application
    } else {
      erreurTenant.value = 'Code organisation introuvable. Vérifiez avec votre administrateur.'
    }
  } catch {
    erreurTenant.value = 'Code organisation invalide ou organisation inactive.'
  } finally {
    rechercheEnCours.value = false
  }
}

// Demander le changement — ouvre modal de confirmation
function demanderChangementOrg() {
  confirmIdentifiant.value = ''
  erreurConfirm.value = ''
  modalChangement.value = true
}

// Confirmer le changement — vérifie que l'identifiant saisi correspond
// à un utilisateur existant (pour éviter qu'un inconnu change l'org)
async function confirmerChangementOrg() {
  erreurConfirm.value = ''
  const id = confirmIdentifiant.value.trim()

  if (!id) {
    erreurConfirm.value = "Saisissez votre identifiant pour confirmer."
    return
  }

  // Vérifier que cet identifiant existe réellement dans cette organisation
  try {
    const tenant = localStorage.getItem('tenant_code')
    const rep = await axios.post('http://localhost:8000/api/verifier-identifiant/', {
      identifiant: id,
      tenant_code: tenant,
    })
    if (rep.data?.existe) {
      // L'identifiant est reconnu — autoriser le changement
      localStorage.removeItem('tenant_code')
      clearParametresCache()
      modalChangement.value = false
      tenantSaisi.value = ''
      erreurTenant.value = ''
      parametres.value = {
        nom_application: 'GED', slogan: 'Gestion Électronique des Documents',
        texte_pied_page: '© GED SaaS', couleur_principale: '#1565C0',
        logo_url: null, image_fond_url: null, flou_image_fond: 5,
      }
      document.title = 'GED'
    } else {
      erreurConfirm.value = "Identifiant non reconnu dans cette organisation."
    }
  } catch {
    erreurConfirm.value = "Identifiant non reconnu dans cette organisation."
  }
}

async function seConnecter() {
  erreur.value = ''
  enChargement.value = true
  const tenant = localStorage.getItem('tenant_code')
  try {
    const rep = await axios.post('http://localhost:8000/api/connexion/', {
      identifiant: form.value.identifiant,
      password:    form.value.password,
      tenant_code: tenant,
    })
    traiterConnexion(rep.data)
  } catch(e) {
    const data = e.response?.data
    if (data?.requires_2fa) {
      etape2fa.value   = true
      message2fa.value = data.detail || 'Code envoyé par email.'
    } else {
      erreur.value = data?.detail || 'Identifiant ou mot de passe incorrect.'
    }
  } finally { enChargement.value = false }
}

async function verifier2fa() {
  erreur.value = ''
  enChargement.value = true
  try {
    const rep = await axios.post('http://localhost:8000/api/2fa/verifier/', {
      identifiant: form.value.identifiant, code: code2fa.value,
    })
    traiterConnexion(rep.data)
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Code incorrect.'
  } finally { enChargement.value = false }
}

async function renvoyer2fa() {
  try {
    await axios.post('http://localhost:8000/api/2fa/renvoyer/', { identifiant: form.value.identifiant })
    message2fa.value = 'Nouveau code envoyé.'
  } catch { erreur.value = 'Erreur lors du renvoi.' }
}

function traiterConnexion(data) {
  localStorage.setItem('access',  data.access)
  localStorage.setItem('refresh', data.refresh)
  clearModulesCache()

  if (data.mdp_expire) localStorage.setItem('mdp_expire', '1')

  const payload = JSON.parse(atob(data.access.split('.')[1]))

  if (payload.tenant_code) {
    localStorage.setItem('tenant_code', payload.tenant_code)
  }

  // Redirection selon profil
  if (payload.is_superuser) {
    router.push('/super-admin')
  } else if (payload.profil === 'ADMIN') {
    router.push('/admin')
  } else {
    router.push('/espace')
  }
}

onMounted(async () => {
  timeoutAlert.value = route.query.timeout === '1'
  const savedTenant = localStorage.getItem('tenant_code')
  if (savedTenant) {
    await chargerParametresTenant(savedTenant)
  }
})
</script>

<style scoped>
@import "../assets/login.css";

.login-page {
  position: relative; width: 100vw; height: 100vh;
  overflow: hidden; display: flex; align-items: center;
  justify-content: center; flex-direction: column;
}
.fond-image {
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
  background-size: cover; background-position: center;
  z-index: 0; transform: scale(1.08);
}
.fond-defaut {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0;
}
.login-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.45); z-index: 1;
}
.login-box {
  position: relative; z-index: 2; background: #fff;
  padding: 40px; border-radius: 10px;
  width: 100%; max-width: 420px;
  border-top: 5px solid #FDD835;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}
.logo {
  display: block; margin: 0 auto 16px;
  max-width: 140px; max-height: 70px; object-fit: contain;
}
.logo-placeholder {
  display: flex; align-items: center; justify-content: center;
  width: 60px; height: 60px; margin: 0 auto 16px;
  background: #e3f2fd; border-radius: 12px; font-size: 28px; color: #1565C0;
}
.login-titre {
  text-align: center; font-size: 20px; font-weight: 700;
  margin-bottom: 4px; color: #1565C0;
}
.login-slogan { text-align: center; color: #666; font-size: 13px; margin-bottom: 20px; }

/* Sélecteur tenant */
.tenant-selector { margin-top: 4px; }
.tenant-selector-titre {
  font-size: 13px; font-weight: 600; color: #333;
  margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; background: #f5f8ff; border-radius: 8px;
}
.tenant-selector input {
  width: 100%; padding: 11px 14px;
  border: 2px solid #D0D0D0; border-radius: 8px;
  font-size: 14px; box-sizing: border-box;
  margin-bottom: 6px; transition: border 0.15s;
}
.tenant-selector input:focus { outline: none; border-color: #1565C0; }
.tenant-selector input.input-error { border-color: #D32F2F; }

/* Badge organisation */
.org-badge {
  display: flex; align-items: center; justify-content: space-between;
  background: #f0f4ff; border: 1px solid #d0dbff;
  padding: 8px 12px; border-radius: 8px; margin-bottom: 16px;
}
.org-badge-info {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: #1565C0;
}
.org-badge-logo { height: 24px; width: auto; object-fit: contain; }

/* Modal confirmation changement */
.confirm-modal-fond {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 300; padding: 16px;
}
.confirm-modal {
  background: #fff; border-radius: 10px; padding: 28px;
  width: 100%; max-width: 380px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.login-pied {
  position: relative; z-index: 2;
  color: rgba(255,255,255,0.7); font-size: 12px;
  margin-top: 20px; text-align: center;
}
</style>
