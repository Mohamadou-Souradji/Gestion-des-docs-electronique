<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-user-shield"></i> Délégations ponctuelles
    </div>
    <div class="barre-actions" style="margin-bottom:16px">
      <button class="btn btn-primary" @click="afficherForm = true">
        <i class="fa-solid fa-plus"></i> Accorder une délégation
      </button>
    </div>

    <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
    <div v-else-if="delegations.length === 0" class="msg-vide">Aucune délégation accordée.</div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr><th>Bénéficiaire</th><th>Périmètre</th><th>Motif</th><th>Du</th><th>Au</th><th>État</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in delegations" :key="d.id">
            <td><strong>{{ d.beneficiaire_nom }}</strong><br/><span style="font-size:12px;color:#666">{{ d.beneficiaire_profil }}</span></td>
            <td>{{ d.perimetre }}</td>
            <td style="max-width:200px;font-size:13px">{{ d.motif }}</td>
            <td>{{ formaterDate(d.date_debut) }}</td>
            <td>{{ formaterDate(d.date_fin) }}</td>
            <td>
              <span v-if="!d.active" style="color:#999;font-size:12px;font-weight:700">Révoquée</span>
              <span v-else-if="d.expiree" style="color:#E65100;font-size:12px;font-weight:700">Expirée</span>
              <span v-else style="color:#2E7D32;font-size:12px;font-weight:700">Active</span>
            </td>
            <td>
              <button v-if="d.active && !d.expiree" class="btn btn-danger" style="font-size:12px;padding:4px 10px" @click="ouvrirRevocation(d)">
                Révoquer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Modal nouvelle délégation -->
  <div v-if="afficherForm" class="modal-fond">
    <div class="modal" style="max-width:580px">
      <div class="modal-titre"><i class="fa-solid fa-user-shield"></i> Accorder une délégation</div>
      <p style="font-size:13px;color:#666;margin-bottom:16px">
        Les droits accordés sont exclusivement en lecture. La délégation expire automatiquement.
      </p>

      <div class="champ" style="margin-bottom:14px">
        <label class="champ-obligatoire">Bénéficiaire</label>
        <select v-model="form.beneficiaire_id">
          <option value="">-- Choisir un agent --</option>
          <option v-for="u in utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }} ({{ u.profil }})</option>
        </select>
      </div>
      <div class="champ" style="margin-bottom:14px">
        <label class="champ-obligatoire">Périmètre</label>
        <select v-model="form.perimetre">
          <option value="">-- Choisir --</option>
          <option value="COURRIER">Un courrier spécifique</option>
          <option value="PERIODE">Une période donnée</option>
          <option value="FONDS">Un fonds d'archive</option>
          <option value="DOSSIER">Un dossier thématique</option>
        </select>
      </div>

      <div v-if="form.perimetre === 'COURRIER'" class="champ" style="margin-bottom:14px">
        <label>Numéro du courrier visé</label>
        <input v-model="form.courrier_id" type="text" placeholder="ID du courrier" />
      </div>
      <div v-if="form.perimetre === 'PERIODE'" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
        <div class="champ"><label>Début période</label><input v-model="form.periode_debut" type="date" /></div>
        <div class="champ"><label>Fin période</label><input v-model="form.periode_fin_perim" type="date" /></div>
      </div>
      <div v-if="form.perimetre === 'FONDS'" class="champ" style="margin-bottom:14px">
        <label>Fonds visé</label>
        <select v-model="form.fonds_vise">
          <option value="ESCEP">ESCEP</option>
          <option value="EST">EST (2011-2023)</option>
          <option value="CNIPT">CNIPT (1969-2011)</option>
        </select>
      </div>
      <div v-if="form.perimetre === 'DOSSIER'" class="champ" style="margin-bottom:14px">
        <label>Dossier thématique</label>
        <input v-model="form.dossier_thematique" type="text" />
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
        <div class="champ"><label class="champ-obligatoire">Date de début</label><input v-model="form.date_debut" type="date" /></div>
        <div class="champ"><label class="champ-obligatoire">Date de fin</label><input v-model="form.date_fin" type="date" /></div>
      </div>
      <div class="champ" style="margin-bottom:14px">
        <label class="champ-obligatoire">Motif</label>
        <textarea v-model="form.motif" rows="3" placeholder="Justification — enregistrée au journal d'audit"></textarea>
      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="afficherForm = false">Annuler</button>
        <button class="btn btn-primary" @click="creer" :disabled="enEnvoi">
          {{ enEnvoi ? 'Création...' : 'Accorder' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal révocation -->
  <div v-if="delegationARevoquer" class="modal-fond">
    <div class="modal">
      <div class="modal-titre"><i class="fa-solid fa-ban"></i> Révoquer la délégation</div>
      <p style="font-size:14px;margin-bottom:12px">Bénéficiaire : <strong>{{ delegationARevoquer.beneficiaire_nom }}</strong></p>
      <div class="champ">
        <label>Motif de révocation</label>
        <textarea v-model="motifRevocation" rows="3"></textarea>
      </div>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="delegationARevoquer = null">Annuler</button>
        <button class="btn btn-danger" @click="confirmerRevocation" :disabled="enEnvoi">Confirmer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi, usersApi } from '../../services/api'

const chargement  = ref(false)
const enEnvoi     = ref(false)
const delegations = ref([])
const utilisateurs = ref([])
const afficherForm = ref(false)
const delegationARevoquer = ref(null)
const motifRevocation     = ref('')
const erreur      = ref('')

const form = ref({
  beneficiaire_id: '', perimetre: '', motif: '', date_debut: '', date_fin: '',
  courrier_id: '', periode_debut: '', periode_fin_perim: '', fonds_vise: '', dossier_thematique: '',
})

async function charger() {
  chargement.value = true
  try {
    const [rd, ru] = await Promise.all([dashboardApi.delegations(), usersApi.liste()])
    delegations.value  = rd.data
    utilisateurs.value = ru.data
  } catch(e) { console.error(e) }
  finally { chargement.value = false }
}

async function creer() {
  erreur.value = ''
  if (!form.value.beneficiaire_id || !form.value.perimetre || !form.value.motif || !form.value.date_debut || !form.value.date_fin) {
    erreur.value = 'Tous les champs obligatoires doivent être remplis.'
    return
  }
  enEnvoi.value = true
  try {
    await dashboardApi.creerDeleg(form.value)
    afficherForm.value = false
    form.value = { beneficiaire_id:'', perimetre:'', motif:'', date_debut:'', date_fin:'', courrier_id:'', periode_debut:'', periode_fin_perim:'', fonds_vise:'', dossier_thematique:'' }
    charger()
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally { enEnvoi.value = false }
}

function ouvrirRevocation(d) {
  delegationARevoquer.value = d
  motifRevocation.value     = ''
}

async function confirmerRevocation() {
  enEnvoi.value = true
  try {
    await dashboardApi.revoquerDeleg(delegationARevoquer.value.id, { motif: motifRevocation.value })
    delegationARevoquer.value = null
    charger()
  } catch(e) { console.error(e) }
  finally { enEnvoi.value = false }
}

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}

onMounted(charger)
</script>
