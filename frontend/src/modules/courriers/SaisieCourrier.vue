<template>
  <div>
    <div class="carte">
      <div class="carte-titre">
        <i class="fa-solid fa-plus"></i> Enregistrer un nouveau courrier
      </div>
      <p style="font-size:13px;color:#666;margin-bottom:20px">
        Un identifiant temporaire sera attribué automatiquement.
        Le numéro officiel sera généré lors de la validation par l'Assistant DG.
      </p>

      <div class="grille-form">
        <div class="champ">
          <label class="champ-obligatoire">Objet</label>
          <input v-model="form.objet" type="text" placeholder="Objet du courrier" />
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Expéditeur</label>
          <input v-model="form.expediteur" type="text" placeholder="Organisme ou personne" />
        </div>
        <div class="champ">
          <label>Référence expéditeur</label>
          <input v-model="form.reference_exp" type="text" placeholder="Ex: N°123/MIN/2026" />
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Origine</label>
          <select v-model="form.type_courrier">
            <option value="ENT">Courrier entrant (externe)</option>
            <option value="INT">Courrier interne</option>
          </select>
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Mode de réception</label>
          <select v-model="form.mode_reception">
            <option value="DEPOT">Dépôt direct</option>
            <option value="POSTAL">Courrier postal</option>
            <option value="EMAIL">Email imprimé</option>
            <option value="COURSIER">Coursier</option>
          </select>
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Niveau de priorité</label>
          <select v-model="form.priorite">
            <option value="NORMALE">Normale</option>
            <option value="URGENT">Urgent</option>
            <option value="TRES_URGENT">Très urgent</option>
          </select>
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Date du document</label>
          <input v-model="form.date_document" type="date" />
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Date de réception</label>
          <input v-model="form.date_reception" type="date" />
        </div>
        <div class="champ">
          <label class="champ-obligatoire">Heure de dépôt</label>
          <input v-model="form.heure_depot" type="time" />
        </div>
        <div class="champ champ-large">
          <label class="champ-obligatoire">Fichier scanné (PDF, JPG, PNG — max 25 Mo)</label>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="selectionnerFichier" />
          <span v-if="erreurFichier" class="msg-erreur">{{ erreurFichier }}</span>
        </div>
        <div class="champ champ-large">
          <label>Observations</label>
          <textarea v-model="form.observations" rows="3" placeholder="Observations éventuelles (facultatif)"></textarea>
        </div>
      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      <p v-if="succes" class="msg-succes">{{ succes }}</p>

      <div class="actions-form">
        <button class="btn btn-ghost" @click="reinit">
          <i class="fa-solid fa-rotate-left"></i> Effacer
        </button>
        <button class="btn btn-outline" @click="soumettre('BROUILLON')" :disabled="enEnvoi">
          <i class="fa-solid fa-floppy-disk"></i> Sauvegarder brouillon
        </button>
        <button class="btn btn-primary" @click="soumettre('SOUMETTRE')" :disabled="enEnvoi">
          <i class="fa-solid fa-paper-plane"></i>
          {{ enEnvoi ? 'Envoi...' : 'Soumettre ' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { courriersApi } from '../../services/api'

const emit = defineEmits(['soumis'])

const enEnvoi       = ref(false)
const erreur        = ref('')
const succes        = ref('')
const erreurFichier = ref('')

const form = ref({
  objet: '', expediteur: '', reference_exp: '',
  type_courrier: 'ENT', mode_reception: 'DEPOT',
  priorite: 'NORMALE', date_document: '', date_reception: '',
  heure_depot: '', observations: '', fichier: null,
})

function selectionnerFichier(e) {
  erreurFichier.value = ''
  const f = e.target.files[0]
  if (f && f.size > 25 * 1024 * 1024) {
    erreurFichier.value = 'Le fichier dépasse 25 Mo.'
    return
  }
  form.value.fichier = f
}

async function soumettre(action) {
  erreur.value = ''
  succes.value = ''

  if (action === 'SOUMETTRE') {
    if (!form.value.objet || !form.value.expediteur ||
        !form.value.date_document || !form.value.date_reception ||
        !form.value.heure_depot || !form.value.fichier) {
      erreur.value = 'Les champs obligatoires (*) doivent être remplis.'
      return
    }
  }

  enEnvoi.value = true
  const donnees = new FormData()
  Object.entries(form.value).forEach(([k, v]) => {
    if (k === 'fichier' && v) donnees.append('fichier_pdf', v)
    else if (k !== 'fichier' && v) donnees.append(k, v)
  })
  donnees.append('action', action)

  try {
    const rep = await courriersApi.creer(donnees)
    succes.value = action === 'SOUMETTRE'
      ? `Courrier soumis. Référence : ${rep.data.identifiant_temp}`
      : 'Brouillon sauvegardé.'
    reinit()
    emit('soumis', rep.data)
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de l\'enregistrement.'
  } finally {
    enEnvoi.value = false
  }
}

function reinit() {
  form.value = {
    objet: '', expediteur: '', reference_exp: '',
    type_courrier: 'ENT', mode_reception: 'DEPOT',
    priorite: 'NORMALE', date_document: '', date_reception: '',
    heure_depot: '', observations: '', fichier: null,
  }
  erreurFichier.value = ''
}
</script>