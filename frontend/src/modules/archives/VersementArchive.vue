<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-file-arrow-up"></i> Versement unitaire
    </div>

    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement des fonds...
    </div>

    <div v-else-if="fonds.length === 0" class="msg-vide">
      <i class="fa-solid fa-folder-open" style="font-size:32px;opacity:0.3;display:block;margin-bottom:10px"></i>
      <p>Aucun fonds d'archives disponible pour votre organisation.</p>
      <p style="font-size:12px;color:#aaa;margin-top:6px">
        Demandez à l'administrateur de créer des fonds dans : Admin → Fonds d'archives
      </p>
    </div>

    <div v-else>
      <div class="grille-form">

        <!-- Fonds d'archives -->
        <div class="champ">
          <label class="champ-obligatoire">Fonds d'archives</label>
          <select v-model="form.fonds">
            <option value="">-- Sélectionner un fonds --</option>
           <option v-for="f in fonds" :key="f.id" :value="f.id">
  {{ f.code }} — {{ f.label }}
</option>
          </select>
        </div>

        <!-- Type de document -->
        <div class="champ">
          <label class="champ-obligatoire">Type de document</label>
          <select v-model="form.type_document">
            <option value="">-- Sélectionner un type --</option>
            <option v-for="t in types" :key="t.code" :value="t.code">
              {{ t.label }}
            </option>
          </select>
        </div>

        <!-- Intitulé -->
        <div class="champ champ-large">
          <label class="champ-obligatoire">Intitulé du document</label>
          <input v-model="form.intitule" type="text"
            placeholder="ex: Rapport annuel 2024, Décision n°001..." />
        </div>

        <!-- Référence système (auto-générée ou manuelle) -->
        <div class="champ">
          <label>Référence (optionnel)</label>
          <input v-model="form.reference_systeme" type="text"
            placeholder="Généré automatiquement si vide" />
          <small style="color:#888;font-size:11px;display:block;margin-top:3px">
            Ex: ESCEP-ARC-2024-00001
          </small>
        </div>

        <!-- Date du document -->
        <div class="champ">
          <label>Date du document</label>
          <input v-model="form.date_document" type="date" />
        </div>

        <!-- Mots-clés -->
        <div class="champ champ-large">
          <label>Mots-clés</label>
          <input v-model="form.mots_cles" type="text"
            placeholder="Séparés par des virgules : rapport, bilan, 2024..." />
        </div>

        <!-- Description -->
        <div class="champ champ-large">
          <label>Description / Résumé</label>
          <textarea v-model="form.description" rows="3"
            placeholder="Contenu ou résumé du document..."></textarea>
        </div>

        <!-- Fichier PDF -->
        <div class="champ champ-large">
          <label class="champ-obligatoire">Fichier PDF</label>
          <input type="file" accept=".pdf,.PDF" @change="e => form.fichier = e.target.files[0]" />
          <small style="color:#888;font-size:11px;display:block;margin-top:3px">
            Formats acceptés : PDF uniquement
          </small>
        </div>

      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      <p v-if="succes" class="msg-succes">{{ succes }}</p>

      <div class="actions-form">
        <button class="btn btn-ghost" @click="reinitialiser">
          <i class="fa-solid fa-rotate-left"></i> Réinitialiser
        </button>
        <button class="btn btn-primary" @click="verser" :disabled="enEnvoi">
          <i class="fa-solid fa-file-arrow-up"></i>
          {{ enEnvoi ? 'Versement en cours...' : 'Verser le document' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const fonds     = ref([])
const types     = ref([])
const chargement = ref(false)
const enEnvoi   = ref(false)
const erreur    = ref('')
const succes    = ref('')

const form = ref({
  fonds:            '',
  type_document:    '',
  intitule:         '',
  reference_systeme:'',
  date_document:    '',
  mots_cles:        '',
  description:      '',
  fichier:          null,
})

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  get headers() {
    return { Authorization: `Bearer ${localStorage.getItem('access')}` }
  }
})

async function chargerFonds() {
  chargement.value = true
  try {
    const rep = await api.get('/archives/fonds/')

    //  Gérer le nouveau format { fonds, types, liste }
    if (rep.data?.fonds) {
      fonds.value = rep.data.fonds    // [{id, code, label, intitule, ...}]
      types.value = rep.data.types    // [{code, label}]
    } else if (Array.isArray(rep.data)) {
      // Ancien format (tableau direct)
      fonds.value = rep.data.map(f => ({
        code:    f.code,
        label:   f.intitule || f.label || f.code,
        intitule:f.intitule || f.code,
        id:      f.id,
      }))
      types.value = getTypesDefaut()
    } else {
      fonds.value = []
      types.value = getTypesDefaut()
    }
  } catch(e) {
    fonds.value = []
    types.value = getTypesDefaut()
  } finally {
    chargement.value = false
  }
}

function getTypesDefaut() {
  return [
    { code: 'LETTRE',        label: 'Lettre' },
    { code: 'RAPPORT',       label: 'Rapport' },
    { code: 'DECISION',      label: 'Décision' },
    { code: 'CIRCULAIRE',    label: 'Circulaire' },
    { code: 'PROCES_VERBAL', label: 'Procès-verbal' },
    { code: 'CONTRAT',       label: 'Contrat' },
    { code: 'CONVENTION',    label: 'Convention' },
    { code: 'ARRETE',        label: 'Arrêté' },
    { code: 'DECRET',        label: 'Décret' },
    { code: 'NOTE',          label: 'Note de service' },
    { code: 'FACTURE',       label: 'Facture' },
    { code: 'BON_COMMANDE',  label: 'Bon de commande' },
    { code: 'AUTRE',         label: 'Autre' },
  ]
}

async function verser() {
  erreur.value = ''
  succes.value = ''

  if (!form.value.fonds)         { erreur.value = 'Sélectionnez un fonds.'; return }
  if (!form.value.type_document) { erreur.value = 'Sélectionnez un type de document.'; return }
  if (!form.value.intitule.trim()){ erreur.value = "L'intitulé est obligatoire."; return }
  if (!form.value.fichier)       { erreur.value = 'Sélectionnez un fichier PDF.'; return }

  enEnvoi.value = true
  try {
    const fd = new FormData()
    fd.append('fonds',             form.value.fonds)
    fd.append('type_document',     form.value.type_document)
    fd.append('intitule',          form.value.intitule)
    fd.append('mots_cles',         form.value.mots_cles)
    fd.append('description',       form.value.description)
    fd.append('fichier_pdf',       form.value.fichier)

    if (form.value.reference_systeme.trim())
      fd.append('reference_systeme', form.value.reference_systeme)
    if (form.value.date_document)
      fd.append('date_document', form.value.date_document)

    await api.post('/archives/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    succes.value = ' Document versé avec succès dans les archives.'
    reinitialiser()
  } catch(e) {
    erreur.value = e.response?.data?.detail
      || JSON.stringify(e.response?.data)
      || 'Erreur lors du versement.'
  } finally {
    enEnvoi.value = false
  }
}

function reinitialiser() {
  form.value = {
    fonds: '', type_document: '', intitule: '',
    reference_systeme: '', date_document: '',
    mots_cles: '', description: '', fichier: null,
  }
  erreur.value = ''
}

onMounted(chargerFonds)
</script>
