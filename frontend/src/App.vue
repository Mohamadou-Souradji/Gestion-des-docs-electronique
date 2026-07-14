<template>
  <div>
    <!-- Alerte expiration mot de passe -->
    <div v-if="mdpExpire" class="alerte-mdp-fond">
      <div class="alerte-mdp-box">
        <div style="font-size:18px;font-weight:700;color:#1565C0;margin-bottom:8px">
          Mot de passe expiré
        </div>
        <p style="font-size:14px;color:#555;margin-bottom:20px">
          Votre mot de passe a expiré. Vous devez le changer pour continuer à utiliser le système.
        </p>
        <div class="champ" style="margin-bottom:12px">
          <label style="font-weight:600;font-size:13px">Ancien mot de passe</label>
          <input v-model="formMdp.ancien" type="password" placeholder="Votre mot de passe actuel"
            style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <div class="champ" style="margin-bottom:12px">
          <label style="font-weight:600;font-size:13px">Nouveau mot de passe</label>
          <input v-model="formMdp.nouveau" type="password" placeholder="Minimum 12 caractères"
            style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <div class="champ" style="margin-bottom:16px">
          <label style="font-weight:600;font-size:13px">Confirmer</label>
          <input v-model="formMdp.confirmation" type="password" placeholder="Répéter le nouveau mot de passe"
            style="width:100%;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box" />
        </div>
        <p v-if="erreurMdp" style="color:#D32F2F;font-size:13px;margin-bottom:10px">{{ erreurMdp }}</p>
        <button @click="changerMdp" :disabled="enChargement"
          style="width:100%;padding:11px;background:#1565C0;color:#fff;border:none;border-radius:6px;font-size:15px;font-weight:600;cursor:pointer">
          {{ enChargement ? 'Changement...' : 'Changer le mot de passe' }}
        </button>
      </div>
    </div>

    <!-- Application principale -->
    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import axios from 'axios'

const mdpExpire    = ref(false)
const enChargement = ref(false)
const erreurMdp    = ref('')
const formMdp      = ref({ ancien: '', nouveau: '', confirmation: '' })

async function changerMdp() {
  erreurMdp.value = ''
  enChargement.value = true
  const token = localStorage.getItem('access')
  try {
    await axios.post('http://localhost:8000/api/mot-de-passe/', {
      ancien_mdp:  formMdp.value.ancien,
      nouveau_mdp: formMdp.value.nouveau,
      confirmation: formMdp.value.confirmation,
    }, { headers: { Authorization: `Bearer ${token}` } })

    localStorage.removeItem('mdp_expire')
    mdpExpire.value = false
  } catch(e) {
    erreurMdp.value = e.response?.data?.detail || 'Erreur lors du changement.'
  } finally {
    enChargement.value = false
  }
}

onMounted(() => {
  mdpExpire.value = localStorage.getItem('mdp_expire') === '1'
})
</script>

<style>
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
</style>
