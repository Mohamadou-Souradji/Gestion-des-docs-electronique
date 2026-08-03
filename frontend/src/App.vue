<template>
  <div>
    <div v-if="mdpExpire" class="alerte-mdp-fond">
      <div class="alerte-mdp-box">
        <div style="font-size:18px;font-weight:700;color:#1565C0;margin-bottom:8px">Mot de passe expire</div>
        <p style="font-size:14px;color:#555;margin-bottom:20px">
          Votre mot de passe a expire. Vous devez le changer pour continuer.
        </p>
        <div class="champ" style="margin-bottom:12px">
          <label style="font-weight:600;font-size:13px">Ancien mot de passe</label>
          <input v-model="form.ancien" type="password" style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <div class="champ" style="margin-bottom:12px">
          <label style="font-weight:600;font-size:13px">Nouveau mot de passe</label>
          <input v-model="form.nouveau" type="password" placeholder="Minimum 12 caracteres" style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <div class="champ" style="margin-bottom:16px">
          <label style="font-weight:600;font-size:13px">Confirmer</label>
          <input v-model="form.confirmation" type="password" style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <p v-if="erreur" style="color:#D32F2F;font-size:13px;margin-bottom:10px">{{ erreur }}</p>
        <button @click="changerMdp" :disabled="enChargement"
          style="width:100%;padding:11px;background:#1565C0;color:#fff;border:none;border-radius:6px;font-size:15px;font-weight:600;cursor:pointer">
          {{ enChargement ? 'Changement...' : 'Changer le mot de passe' }}
        </button>
      </div>
    </div>
    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { usersApi } from './services/api'
import { useParametres } from './composables/useParametres'

const mdpExpire    = ref(false)
const enChargement = ref(false)
const erreur       = ref('')
const form = ref({ ancien: '', nouveau: '', confirmation: '' })

async function changerMdp() {
  erreur.value = ''
  enChargement.value = true
  try {
    await usersApi.changerMdp({
      ancien_mdp: form.value.ancien,
      nouveau_mdp: form.value.nouveau,
      confirmation: form.value.confirmation,
    })
    localStorage.removeItem('mdp_expire')
    mdpExpire.value = false
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors du changement.'
  } finally { enChargement.value = false }
}

onMounted(async () => {
  mdpExpire.value = localStorage.getItem('mdp_expire') === '1'

  try {
    const p = await useParametres()
    if (p?.nom_application) {
      document.title = p.nom_application
    }
    
    // Appliquer le logo et favicon
    if (p?.logo_url) {
      const logoImg = document.getElementById('organisation-logo')
      if (logoImg) {
        logoImg.src = p.logo_url
      }
    }
    
    if (p?.favicon_url) {
      const favicon = document.querySelector('link[rel="icon"]')
      if (favicon) {
        favicon.href = p.favicon_url
      }
    }
  } catch {}
})
</script>

<style scoped>
.alerte-mdp-fond {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

.alerte-mdp-box {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 32px;
  width: 100%;
  max-width: 420px;
  border-top: 5px solid #FDD835;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.champ {
  margin-bottom: 12px;
}

.champ label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 13px;
  color: #333;
}

.champ input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.champ input:focus {
  outline: none;
  border-color: #1565C0;
}
</style>