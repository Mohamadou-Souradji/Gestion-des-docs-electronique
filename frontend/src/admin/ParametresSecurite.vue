<template>
  <div class="carte">
    <div class="carte-titre"><i class="fa-solid fa-shield-halved"></i> Paramètres de sécurité</div>

    <div class="grille-form">
      <div class="champ">
        <label>Timeout d'inactivité (minutes)</label>
        <input v-model="form.timeout_inactivite" type="number" min="5" max="120" />
        <small style="color:#666;display:block;margin-top:4px">Durée avant déconnexion automatique</small>
      </div>
      <div class="champ">
        <label>Durée de validité du mot de passe (jours)</label>
        <input v-model="form.duree_validite_mdp" type="number" min="30" max="365" />
        <small style="color:#666;display:block;margin-top:4px">L'utilisateur devra changer son mot de passe après cette durée</small>
      </div>
      <div class="champ">
        <label>Tentatives avant verrouillage du compte</label>
        <input v-model="form.tentatives_max" type="number" min="3" max="10" />
      </div>
      <div class="champ champ-large" style="display:flex;align-items:center;gap:10px">
        <input type="checkbox" v-model="form.double_auth_active" id="2fa-global" style="accent-color:#1565C0;width:18px;height:18px;flex-shrink:0" />
        <div>
          <label for="2fa-global" style="cursor:pointer;font-size:14px;font-weight:600;display:block">Activer la double authentification globalement</label>
          <small style="color:#666">Les utilisateurs avec 2FA et email configurés recevront un code à chaque connexion</small>
        </div>
      </div>
      <div class="champ"><label>Email expéditeur pour les codes 2FA</label><input v-model="form.email_expediteur" type="email" placeholder="noreply@escep.ne" /></div>
      <div class="champ champ-large">
        <label>Texte de l'email de vérification 2FA</label>
        <small style="color:#666;display:block;margin-bottom:6px">Utiliser <code>{code}</code> pour insérer le code.</small>
        <textarea v-model="form.texte_email_2fa" rows="4" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px;font-family:inherit;box-sizing:border-box"></textarea>
      </div>
    </div>

    <p v-if="msg" class="msg-succes" style="margin-top:12px">{{ msg }}</p>
    <div class="actions-form">
      <button class="btn btn-primary" @click="sauvegarder" :disabled="enEnvoi">
        {{ enEnvoi ? 'Enregistrement...' : 'Enregistrer' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { parametresApi } from '../services/api'

const enEnvoi = ref(false)
const msg     = ref('')
const form = ref({
  timeout_inactivite: 30, duree_validite_mdp: 90, tentatives_max: 5,
  double_auth_active: false, email_expediteur: '', texte_email_2fa: '',
})

async function charger() {
  try {
    const rep = await parametresApi.get()
    form.value = { ...form.value, ...rep.data }
  } catch(e) {}
}

async function sauvegarder() {
  msg.value = ''
  enEnvoi.value = true
  try {
    const donnees = new FormData()
    Object.entries(form.value).forEach(([k, v]) => { if (v !== null && v !== undefined) donnees.append(k, v) })
    await parametresApi.modifier(donnees)
    msg.value = 'Paramètres de sécurité enregistrés.'
    setTimeout(() => msg.value = '', 4000)
  } catch(e) {
    msg.value = 'Erreur lors de l\'enregistrement.'
  } finally { enEnvoi.value = false }
}

onMounted(charger)
</script>
