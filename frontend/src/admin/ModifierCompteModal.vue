<template>
  <div class="modal-fond">
    <div class="modal" style="max-width:800px">
      <div class="modal-titre">Modifier — {{ utilisateur.identifiant }}</div>

      <div class="grille-form">
        <div class="champ"><label>Nom</label><input v-model="form.nom" type="text" /></div>
        <div class="champ"><label>Prénom</label><input v-model="form.prenom" type="text" /></div>
        <div class="champ">
          <label>Direction</label>
          <select v-model="form.direction_id">
            <option value="">-- Aucune --</option>
            <option v-for="d in directions" :key="d.id" :value="d.id">{{ d.sigle ? d.sigle+' — ' : '' }}{{ d.nom }}</option>
          </select>
        </div>
        <div class="champ"><label>Fonction</label><input v-model="form.fonction" type="text" /></div>
        <div class="champ"><label>Email</label><input v-model="form.email" type="email" /></div>
        <div class="champ"><label>Nouveau mot de passe</label><input v-model="form.password" type="password" placeholder="Laisser vide pour ne pas changer" /></div>
        <div class="champ champ-large" style="display:flex;align-items:center;gap:8px">
          <input type="checkbox" v-model="form.double_auth_active" id="2fa-user" style="accent-color:#1565C0;width:16px;height:16px" />
          <label for="2fa-user" style="cursor:pointer;font-size:14px">Double authentification activée pour cet utilisateur</label>
        </div>
        
      </div>

      <div style="margin:16px 0">
        <SelecteurModules v-model="form.modules_actifs" />
      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="$emit('fermer')">Annuler</button>
        <button class="btn btn-primary" @click="enregistrer" :disabled="enEnvoi">
          {{ enEnvoi ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usersApi, directionsApi } from '../services/api'
import SelecteurModules from './SelecteurModules.vue'

const props = defineProps({
  utilisateur: { type: Object, required: true },
})
const emit = defineEmits(['fermer', 'enregistre'])

const enEnvoi    = ref(false)
const erreur     = ref('')
const directions = ref([])

const form = ref({
  nom: props.utilisateur.nom,
  prenom: props.utilisateur.prenom,
  direction_id: props.utilisateur.direction_id || '',
  fonction: props.utilisateur.fonction || '',
  email: props.utilisateur.email || '',
  password: '',
  double_auth_active: props.utilisateur.double_auth_active,
  double_auth_desactive_admin: props.utilisateur.double_auth_desactive_admin,
  modules_actifs: [...(props.utilisateur.modules_actifs || [])],
})

onMounted(async () => {
  try { directions.value = (await directionsApi.liste()).data } catch(e) {}
})

async function enregistrer() {
  enEnvoi.value = true
  erreur.value  = ''
  try {
    await usersApi.modifier(props.utilisateur.id, form.value)
    emit('enregistre')
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la modification.'
  } finally { enEnvoi.value = false }
}
</script>