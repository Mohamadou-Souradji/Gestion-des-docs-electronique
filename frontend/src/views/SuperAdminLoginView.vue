<template>
  <div class="sa-login-page">
    <div class="sa-login-box">
      <div class="sa-logo">
        <i class="fa-solid fa-shield-halved"></i>
      </div>
      <h1 class="sa-titre">GED SaaS</h1>
      <p class="sa-sous-titre">Espace Super-Administrateur</p>

      <div class="sa-champ">
        <label>Identifiant</label>
        <input v-model="form.identifiant" type="text" placeholder="Identifiant super-admin"
          @keyup.enter="seConnecter" />
      </div>
      <div class="sa-champ">
        <label>Mot de passe</label>
        <input v-model="form.password" type="password" placeholder="Mot de passe"
          @keyup.enter="seConnecter" />
      </div>

      <p v-if="erreur" class="sa-erreur">{{ erreur }}</p>

      <button class="sa-btn" @click="seConnecter" :disabled="enChargement">
        {{ enChargement ? 'Connexion...' : 'Se connecter' }}
      </button>

      <a href="/" class="sa-retour">
        <i class="fa-solid fa-arrow-left"></i> Retour page normale
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router      = useRouter()
const form        = ref({ identifiant: '', password: '' })
const erreur      = ref('')
const enChargement = ref(false)

async function seConnecter() {
  erreur.value = ''
  enChargement.value = true
  try {
const BASE = import.meta.env.VITE_API_URL || 'https://gestion-des-docs-electronique.onrender.com/api'
await axios.post(`${BASE}/connexion/`, {      identifiant: form.value.identifiant,
      password:    form.value.password,
    })

    const payload = JSON.parse(atob(rep.data.access.split('.')[1]))

    if (!payload.is_superuser) {
      erreur.value = 'Accès refusé. Cette page est réservée au Super-Admin.'
      return
    }

    localStorage.setItem('access',  rep.data.access)
    localStorage.setItem('refresh', rep.data.refresh)
    router.push('/super-admin')

  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Identifiant ou mot de passe incorrect.'
  } finally {
    enChargement.value = false
  }
}
</script>

<style scoped>
.sa-login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565C0 100%);
  display: flex; align-items: center; justify-content: center;
}

.sa-login-box {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  width: 100%; max-width: 380px;
  border-top: 5px solid #FFD54F;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  text-align: center;
}

.sa-logo {
  width: 64px; height: 64px;
  background: linear-gradient(135deg, #1a237e, #1565C0);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
  font-size: 28px; color: #fff;
}

.sa-titre { font-size: 22px; font-weight: 700; color: #1a237e; margin-bottom: 4px; }
.sa-sous-titre { font-size: 13px; color: #888; margin-bottom: 24px; }

.sa-champ { margin-bottom: 14px; text-align: left; }
.sa-champ label { display: block; font-size: 13px; font-weight: 600; color: #444; margin-bottom: 6px; }
.sa-champ input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #CCC; border-radius: 6px;
  font-size: 14px; box-sizing: border-box;
}
.sa-champ input:focus { outline: none; border-color: #1a237e; }

.sa-erreur { color: #D32F2F; font-size: 13px; margin-bottom: 10px; }

.sa-btn {
  width: 100%; padding: 12px;
  background: #1a237e; color: #fff;
  border: none; border-radius: 6px;
  font-size: 15px; font-weight: 600;
  cursor: pointer; margin-bottom: 16px;
}
.sa-btn:hover:not(:disabled) { background: #283593; }
.sa-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.sa-retour {
  display: block; font-size: 13px;
  color: #888; text-decoration: none;
}
.sa-retour:hover { color: #1a237e; }
</style>
