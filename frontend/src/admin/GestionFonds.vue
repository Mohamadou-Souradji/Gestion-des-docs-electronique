<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-folder-open"></i> Fonds d'archives de l'organisation
    </div>
    <p style="font-size:13px;color:#666;margin-bottom:16px">
      Ces fonds seront disponibles pour vos archivistes lors du versement de documents.
    </p>

    <!-- Bouton ajouter -->
    <div style="margin-bottom:20px">
      <button class="btn btn-primary" @click="ouvrirAjout">
        <i class="fa-solid fa-plus"></i> Ajouter un fonds
      </button>
    </div>

    <!-- Liste des fonds -->
    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
    </div>
    <div v-else-if="fonds.length === 0" class="msg-vide">
      <i class="fa-solid fa-folder-open" style="font-size:32px;opacity:0.3;display:block;margin-bottom:10px"></i>
      Aucun fonds créé. Ajoutez votre premier fonds d'archives.
    </div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr>
            <th>Code</th>
            <th>Intitulé</th>
            <th>Description</th>
            <th>Nb documents</th>
            <th style="width:100px">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in fonds" :key="f.id">
            <td><span style="font-weight:700;font-family:monospace;background:#f0f4ff;padding:3px 8px;border-radius:4px">{{ f.code }}</span></td>
            <td>{{ f.intitule }}</td>
            <td style="color:#666;font-size:13px">{{ f.description || '—' }}</td>
            <td style="text-align:center">
              <span style="font-weight:600;color:#1565C0">{{ f.nb_documents }}</span>
            </td>
            <td>
              <div style="display:flex;gap:6px">
                <button class="btn btn-outline" style="padding:5px 10px;font-size:12px" @click="ouvrirModif(f)">
                  <i class="fa-solid fa-pencil"></i>
                </button>
                <button class="btn btn-danger" style="padding:5px 10px;font-size:12px"
                  @click="supprimerFonds(f)" :disabled="f.nb_documents > 0" :title="f.nb_documents > 0 ? 'Impossible : contient des documents' : 'Supprimer'">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal ajout/modification -->
    <div v-if="modalOuvert" class="modal-fond" @click.self="modalOuvert = false">
      <div class="modal">
        <div class="modal-titre">
          <i class="fa-solid fa-folder-plus"></i>
          {{ fondsAModifier ? 'Modifier le fonds' : 'Nouveau fonds d\'archives' }}
        </div>

        <div class="grille-form" style="grid-template-columns:1fr 2fr;gap:14px;margin-bottom:16px">
          <div class="champ">
            <label class="champ-obligatoire">Code</label>
            <input v-model="form.code" type="text" placeholder="ex: ADM, FIN, RH"
              style="text-transform:uppercase" @input="form.code = form.code.toUpperCase()" />
            <small style="color:#888;display:block;margin-top:4px">Court, unique, sans espaces</small>
          </div>
          <div class="champ">
            <label class="champ-obligatoire">Intitulé</label>
            <input v-model="form.intitule" type="text" placeholder="ex: Fonds Administratif, Finances..." />
          </div>
          <div class="champ" style="grid-column:span 2">
            <label>Description (optionnel)</label>
            <textarea v-model="form.description" rows="2"
              placeholder="Description du type de documents archivés dans ce fonds..."></textarea>
          </div>
        </div>

        <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="modalOuvert = false">Annuler</button>
          <button class="btn btn-primary" @click="sauvegarder" :disabled="enEnvoi">
            {{ enEnvoi ? 'Sauvegarde...' : (fondsAModifier ? 'Modifier' : 'Créer le fonds') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const fonds       = ref([])
const chargement  = ref(false)
const enEnvoi     = ref(false)
const modalOuvert = ref(false)
const fondsAModifier = ref(null)
const erreur      = ref('')

const form = ref({ code: '', intitule: '', description: '' })

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
})

async function charger() {
  chargement.value = true
  try {
    const rep = await api.get('/archives/fonds/')
    fonds.value = rep.data.liste || rep.data
  } catch { fonds.value = [] }
  finally { chargement.value = false }
}

function ouvrirAjout() {
  fondsAModifier.value = null
  form.value = { code: '', intitule: '', description: '' }
  erreur.value = ''
  modalOuvert.value = true
}

function ouvrirModif(f) {
  fondsAModifier.value = f
  form.value = { code: f.code, intitule: f.intitule, description: f.description }
  erreur.value = ''
  modalOuvert.value = true
}

async function sauvegarder() {
  erreur.value = ''
  if (!form.value.code.trim()) { erreur.value = 'Le code est obligatoire.'; return }
  if (!form.value.intitule.trim()) { erreur.value = "L'intitulé est obligatoire."; return }

  enEnvoi.value = true
  try {
    if (fondsAModifier.value) {
      await api.patch(`/archives/fonds/${fondsAModifier.value.id}/`, form.value)
    } else {
      await api.post('/archives/fonds/', form.value)
    }
    modalOuvert.value = false
    await charger()
  } catch(e) {
    erreur.value = e.response?.data?.detail || JSON.stringify(e.response?.data) || 'Erreur lors de la sauvegarde.'
  } finally { enEnvoi.value = false }
}

async function supprimerFonds(f) {
  if (f.nb_documents > 0) return
  if (!confirm(`Supprimer le fonds "${f.intitule}" ?`)) return
  try {
    await api.delete(`/archives/fonds/${f.id}/`)
    await charger()
  } catch(e) {
    alert(e.response?.data?.detail || 'Impossible de supprimer ce fonds.')
  }
}

onMounted(charger)
</script>
