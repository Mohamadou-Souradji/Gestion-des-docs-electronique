<template>
  <div class="carte">
    <div class="carte-titre"><i class="fa-solid fa-user-plus"></i> Créer un nouveau compte</div>
    <p style="font-size:13px;color:#666;margin-bottom:20px">
      Le compte est créé sans aucun module actif. Accordez ensuite les modules nécessaires ci-dessous.
    </p>

    <div class="grille-form">
      <div class="champ"><label class="champ-obligatoire">Identifiant</label><input v-model="form.identifiant" type="text" /></div>
      <div class="champ">
        <label class="champ-obligatoire">Profil</label>
        <select v-model="form.profil">
          <option value="">-- Choisir --</option>
          <option value="DG">Directeur Général</option>
          <option v-if="workflowType === 'CLASSIQUE'" value="ASSIST">Assistant DG</option>
          <option v-if="workflowType === 'ETENDU'" value="SGA">Secrétaire Général Adjoint</option>
          <option v-if="workflowType === 'ETENDU'" value="SG">Secrétaire Général</option>
          <option value="BO">Bureau d'Ordre</option>
          <option value="DEST">Destinataire</option>
          <option value="ARC">Archiviste</option>
        </select>
      </div>
      <div class="champ"><label class="champ-obligatoire">Nom</label><input v-model="form.nom" type="text" /></div>
      <div class="champ"><label class="champ-obligatoire">Prénom</label><input v-model="form.prenom" type="text" /></div>
      <div class="champ">
        <label :class="form.profil === 'DEST' ? 'champ-obligatoire' : ''">Direction</label>
        <select v-model="form.direction_id">
          <option value="">-- Aucune --</option>
          <option v-for="d in directions" :key="d.id" :value="d.id">{{ d.sigle ? d.sigle + ' — ' : '' }}{{ d.nom }}</option>
        </select>
      </div>
      <div class="champ"><label>Fonction</label><input v-model="form.fonction" type="text" /></div>
      <div class="champ"><label>Email</label><input v-model="form.email" type="email" placeholder="Pour la double authentification" /></div>
      <div class="champ"><label class="champ-obligatoire">Mot de passe initial</label><input v-model="form.password" type="password" placeholder="Min. 12 caractères" /></div>
    </div>

    <div style="margin-bottom:16px">
      <SelecteurModules v-model="form.modules_actifs" />
    </div>

    <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
    <p v-if="succes" class="msg-succes">{{ succes }}</p>
    <div class="actions-form">
      <button class="btn btn-ghost" @click="reinit">Effacer</button>
      <button class="btn btn-primary" @click="creer" :disabled="enEnvoi">
        {{ enEnvoi ? 'Création...' : 'Créer le compte' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usersApi, directionsApi } from '../services/api'
import SelecteurModules from './SelecteurModules.vue'
const workflowType = ref('CLASSIQUE')
import { useModules } from '../composables/useModules'

onMounted(async () => {
  try {
    const [dirs, infos] = await Promise.all([
      directionsApi.liste(),
      useModules()
    ])
    directions.value   = dirs.data
    workflowType.value = infos.workflow_type || 'CLASSIQUE'
  } catch(e) {}
})

const enEnvoi    = ref(false)
const erreur     = ref('')
const succes     = ref('')
const directions = ref([])

const form = ref({
  identifiant: '', profil: '', nom: '', prenom: '',
  direction_id: '', fonction: '', email: '', password: '',
  modules_actifs: [],
})



async function creer() {
  erreur.value = ''
  succes.value = ''
  if (!form.value.identifiant || !form.value.profil || !form.value.nom || !form.value.prenom || !form.value.password) {
    erreur.value = 'Les champs obligatoires (*) doivent être remplis.'
    return
  }
  enEnvoi.value = true
  try {
    await usersApi.creer(form.value)
    succes.value = `Compte "${form.value.identifiant}" créé avec succès.`
    reinit()
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally { enEnvoi.value = false }
}

function reinit() {
  form.value = { identifiant:'', profil:'', nom:'', prenom:'', direction_id:'', fonction:'', email:'', password:'', modules_actifs:[] }
}
</script>
