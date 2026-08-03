<template>
  <div class="carte">
    <div class="carte-titre"><i class="fa-solid fa-building"></i> Directions et départements</div>

    <div class="grille-form" style="margin-bottom:16px">
      <div class="champ"><label class="champ-obligatoire">Nom complet</label><input v-model="form.nom" type="text" placeholder="Ex: Département Informatique" /></div>
      <div class="champ"><label>Sigle</label><input v-model="form.sigle" type="text" placeholder="Ex: DEP/DI" /></div>
      <div class="champ"><label>Description</label><input v-model="form.description" type="text" /></div>
      <div class="champ"><label>Ordre d'affichage</label><input v-model="form.ordre" type="number" min="0" /></div>
    </div>
    <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
    <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px">
      <button class="btn btn-primary" @click="creer" :disabled="enEnvoi">
        <i class="fa-solid fa-plus"></i> Ajouter la direction
      </button>
    </div>

    <div v-if="directions.length === 0" class="msg-vide">Aucune direction configurée.</div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead><tr><th>Sigle</th><th>Nom</th><th>Description</th><th>Ordre</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="d in directions" :key="d.id">
            <td><strong>{{ d.sigle || '-' }}</strong></td>
            <td>{{ d.nom }}</td>
            <td style="font-size:12px">{{ d.description || '-' }}</td>
            <td>{{ d.ordre }}</td>
            <td>
              <button class="btn btn-danger" style="font-size:12px;padding:4px 10px" @click="supprimer(d)">
                <i class="fa-solid fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { directionsApi } from '../services/api'

const enEnvoi    = ref(false)
const erreur     = ref('')
const directions = ref([])
const form = ref({ nom: '', sigle: '', description: '', ordre: 0 })

async function charger() {
  try { directions.value = (await directionsApi.liste()).data } catch(e) {}
}

async function creer() {
  erreur.value = ''
  if (!form.value.nom.trim()) { erreur.value = 'Le nom est obligatoire.'; return }
  enEnvoi.value = true
  try {
    await directionsApi.creer(form.value)
    form.value = { nom: '', sigle: '', description: '', ordre: 0 }
    charger()
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally { enEnvoi.value = false }
}

async function supprimer(d) {
  if (!confirm(`Supprimer la direction "${d.nom}" ?`)) return
  try { await directionsApi.supprimer(d.id); charger() } catch(e) {}
}

onMounted(charger)
</script>
