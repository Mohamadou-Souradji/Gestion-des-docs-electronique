<template>
  <div class="login-page" :style="stylePage">

    <div class="login-overlay"></div>

    <div class="login-box">

      <img v-if="parametres.logo_url" :src="parametres.logo_url" alt="Logo" class="logo" />
      <img v-else src="../assets/logo_escep.png" alt="ESCEP-Niger" class="logo" />

      <h1 class="login-titre">{{ parametres.nom_application }}</h1>
      <p class="login-slogan">{{ parametres.slogan }}</p>

      <!-- Alerte timeout -->
      <div v-if="timeoutAlert" class="alerte-info">
        Vous avez été déconnecté automatiquement après une période d'inactivité.
      </div>

      <!-- Étape 1 : Identifiant + mot de passe -->
      <div v-if="!etape2fa">
        <div class="champ">
          <label>Identifiant</label>
          <input v-model="form.identifiant" type="text" placeholder="Votre identifiant" @keyup.enter="seConnecter" autocomplete="username" />
        </div>
        <div class="champ">
          <label>Mot de passe</label>
          <div style="position:relative">
            <input v-model="form.password" :type="afficherMdp ? 'text' : 'password'"
              placeholder="Votre mot de passe" @keyup.enter="seConnecter" autocomplete="current-password"
              style="padding-right:40px" />
            <button type="button" @click="afficherMdp = !afficherMdp"
              style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:#666;font-size:13px">
              {{ afficherMdp ? 'Cacher' : 'Voir' }}
            </button>
          </div>
        </div>
        <p v-if="erreur" class="erreur">{{ erreur }}</p>
        <button class="btn-connexion" @click="seConnecter" :disabled="enChargement">
          {{ enChargement ? 'Connexion...' : 'Se connecter' }}
        </button>
      </div>

      <!-- Étape 2 : Code 2FA -->
      <div v-else>
        <div class="alerte-info">{{ message2fa }}</div>
        <div class="champ">
          <label>Code de vérification (6 chiffres)</label>
          <input v-model="code2fa" type="text" maxlength="6" placeholder="000000"
            @keyup.enter="verifier2fa" style="letter-spacing:8px;font-size:20px;text-align:center" />
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useParametres } from '../composables/useParametres'

const router = useRouter()
const route  = useRoute()

const parametres    = ref({
  nom_application: 'GED ESCEP-Niger',
  slogan: 'Gestion Électronique des Documents',
  texte_pied_page: '© ESCEP-Niger',
  logo_url: null,
  image_fond_url: null,
})
const form          = ref({ identifiant: '', password: '' })
const erreur        = ref('')
const enChargement  = ref(false)
const afficherMdp   = ref(false)
const etape2fa      = ref(false)
const code2fa       = ref('')
const message2fa    = ref('')
const timeoutAlert  = ref(false)

const stylePage = computed(() => {
  if (parametres.value.image_fond_url) {
    return {
      backgroundImage: `url(${parametres.value.image_fond_url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  return { backgroundColor: '#1565C0' }
})

async function seConnecter() {
  erreur.value = ''
  enChargement.value = true
  try {
    const rep = await axios.post('http://localhost:8000/api/connexion/', {
      identifiant: form.value.identifiant,
      password:    form.value.password,
    })
    traiterConnexion(rep.data)
  } catch(e) {
    const data = e.response?.data
    const requires2fa = data?.requires_2fa || data?.detail === 'Code de vérification requis.' || data?.detail?.includes?.('Code de vérification')
    if (requires2fa) {
      etape2fa.value  = true
      const codeLocal = data?.code_2fa
      message2fa.value = codeLocal
        ? `${data.detail || 'Code envoyé par email.'} \nCode de test local : ${codeLocal}`
        : (data?.detail || 'Code envoyé par email.')
      erreur.value = ''
    } else {
      erreur.value = data?.detail || 'Identifiant ou mot de passe incorrect.'
    }
  } finally {
    enChargement.value = false
  }
}

async function verifier2fa() {
  erreur.value = ''
  enChargement.value = true
  try {
    const rep = await axios.post('http://localhost:8000/api/2fa/verifier/', {
      identifiant: form.value.identifiant,
      code:        code2fa.value,
    })
    traiterConnexion(rep.data)
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Code incorrect.'
  } finally {
    enChargement.value = false
  }
}

async function renvoyer2fa() {
  try {
    await axios.post('http://localhost:8000/api/2fa/renvoyer/', { identifiant: form.value.identifiant })
    message2fa.value = 'Nouveau code envoyé.'
  } catch(e) {
    erreur.value = 'Erreur lors du renvoi du code.'
  }
}

function traiterConnexion(data) {
  localStorage.setItem('access',  data.access)
  localStorage.setItem('refresh', data.refresh)

  const payload = JSON.parse(atob(data.access.split('.')[1]))

  // Alerte expiration mot de passe
  if (data.mdp_expire) {
    localStorage.setItem('mdp_expire', '1')
  }

  const redirections = {
    DG:    '/dg',
    ASSIST: '/assistant',
    BO:    '/bureau-ordre',
    DEST:  '/destinataire',
    ARC:   '/archiviste',
    ADMIN: '/admin-ged',
  }
  router.push(redirections[payload.profil] || '/')
}

onMounted(async () => {
  timeoutAlert.value = route.query.timeout === '1'
  parametres.value   = await useParametres()
})
</script>

<style scoped src="../assets/login.css" />
