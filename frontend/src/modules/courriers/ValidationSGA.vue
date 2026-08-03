<template>
  <div>
    <!-- Onglets -->
    <div class="onglets" style="margin-bottom:16px">
      <button :class="['onglet', { actif: onglet === 'attente' }]" @click="onglet = 'attente'">
        <i class="fa-solid fa-hourglass-half"></i> En attente
        <span v-if="aValider.length" style="background:#e53935;color:#fff;border-radius:10px;padding:1px 7px;font-size:11px;margin-left:6px">
          {{ aValider.length }}
        </span>
      </button>
      <button :class="['onglet', { actif: onglet === 'historique' }]" @click="onglet = 'historique'">
        <i class="fa-solid fa-clock-rotate-left"></i> Historique
      </button>
    </div>

    <!-- Onglet En attente -->
    <div v-if="onglet === 'attente'">
      <div v-if="chargement" class="msg-vide">
        <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
      </div>
      <div v-else-if="aValider.length === 0" class="msg-vide">
        Aucun courrier en attente de validation SGA.
      </div>
      <div v-else>
        <CarteCourrierDetail v-for="c in aValider" :key="c.id" :courrier="c">
          <template #actions>
            <button class="btn btn-outline" style="font-size:13px;padding:6px 12px" @click="ouvrirFiche(c)">
              <i class="fa-solid fa-magnifying-glass"></i> Examiner
            </button>
          </template>
        </CarteCourrierDetail>
      </div>
    </div>

    <!-- Onglet Historique -->
    <div v-if="onglet === 'historique'">
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;align-items:flex-end">
        <input v-model="filtres.q" type="text" placeholder="Rechercher un objet..."
          style="flex:1;min-width:180px;padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px"
          @keyup.enter="chargerHistorique" />
        <input v-model="filtres.date_debut" type="date"
          style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px"
          @change="chargerHistorique" />
        <input v-model="filtres.date_fin" type="date"
          style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px"
          @change="chargerHistorique" />
        <select v-model="filtres.statut" @change="chargerHistorique"
          style="padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px">
          <option value="">Tous les statuts</option>
          <option value="EN_ATT_SG">Transmis au SG</option>
          <option value="EN_ATT_IMP">Transmis au DG</option>
          <option value="IMPUTE">Imputé</option>
          <option value="TRAITE">Traité</option>
          <option value="ARCHIVE">Archivé</option>
          <option value="BROUILLON">Rejeté (retourné)</option>
        </select>
        <button class="btn btn-primary" style="font-size:13px;padding:8px 14px" @click="chargerHistorique">
          <i class="fa-solid fa-magnifying-glass"></i> Filtrer
        </button>
        <button class="btn btn-ghost" style="font-size:13px;padding:8px 14px" @click="reinitFiltres">
          Réinitialiser
        </button>
      </div>

      <div v-if="chargementHistorique" class="msg-vide">
        <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
      </div>
      <div v-else-if="historique.length === 0" class="msg-vide">
        Aucun courrier dans l'historique.
      </div>
      <div v-else>
        <CarteCourrierDetail v-for="c in historique" :key="c.id" :courrier="c" />
        <p style="font-size:12px;color:#999;margin-top:8px">{{ historique.length }} courrier(s)</p>
      </div>
    </div>
  </div>

  <!-- Modal validation + proposition imputation -->
  <div v-if="courrierExamine" class="modal-fond" @click.self="courrierExamine = null">
    <div class="modal" style="max-width:720px;max-height:90vh;display:flex;flex-direction:column">
      <div class="modal-titre">
        <i class="fa-solid fa-user-check"></i> Validation SGA — Proposition d'imputation
        <button class="btn btn-ghost" style="margin-left:auto;padding:4px 10px" @click="courrierExamine = null">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div style="overflow-y:auto;padding:0 4px;flex:1">
        <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:16px;font-size:13px">
          <strong>{{ courrierExamine.objet }}</strong><br/>
          <span style="color:#666">{{ courrierExamine.expediteur }} — {{ courrierExamine.identifiant_temp }}</span>
        </div>

        <!-- Destinataire principal -->
        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Destinataire principal proposé</label>
          <select v-model="form.destinataire_id">
            <option value="">-- Choisir un destinataire --</option>
            <option v-for="d in destinataires" :key="d.id" :value="d.id">
              {{ d.prenom }} {{ d.nom }} — {{ d.entite }}
            </option>
          </select>
        </div>

        <!-- Consignes principales -->
        <div style="margin-bottom:14px">
          <label style="font-weight:600;font-size:13px;display:block;margin-bottom:8px" class="champ-obligatoire">
            Consignes pour le destinataire principal (au moins une)
          </label>
          <div style="border:1px solid #e0e0e0;border-radius:6px;padding:10px;max-height:180px;overflow-y:auto;background:#fafafa">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
              <label v-for="c in consignesTypes" :key="c.code"
                :class="['consigne-item', { selected: form.consignes_types.includes(c.code) }]"
                style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;padding:6px 10px;border-radius:4px;border:1px solid transparent">
                <input type="checkbox" :value="c.code" v-model="form.consignes_types"
                  style="accent-color:#1565C0;width:14px;height:14px;flex-shrink:0" />
                <span>{{ c.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Consigne libre principale -->
        <div class="champ" style="margin-bottom:20px">
          <label>Consigne spécifique pour le destinataire principal (facultatif)</label>
          <textarea v-model="form.consigne_libre" rows="2" placeholder="Instruction particulière..."></textarea>
        </div>

        <!-- Copies avec consignes individuelles -->
        <div style="border-top:2px dashed #e0e0e0;padding-top:16px;margin-bottom:14px">
          <div style="font-size:13px;font-weight:600;color:#444;margin-bottom:12px">
            <i class="fa-solid fa-copy" style="color:#1565C0"></i> Destinataires en copie
            <span style="font-weight:400;color:#888;font-size:12px;margin-left:6px">(consignes individuelles)</span>
          </div>

          <div v-for="d in destinataires" :key="d.id"
            v-show="d.id != form.destinataire_id"
            style="border:1px solid #e8e8e8;border-radius:6px;padding:12px;margin-bottom:10px;background:#fafafa">
            <label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;margin-bottom:8px">
              <input type="checkbox" :value="d.id" v-model="copiesSelectionnees"
                style="accent-color:#1565C0;width:15px;height:15px;flex-shrink:0" />
              <strong>{{ d.prenom }} {{ d.nom }}</strong>
              <span style="color:#888;font-size:12px">— {{ d.entite }}</span>
            </label>

            <div v-if="copiesSelectionnees.includes(d.id)" style="margin-left:23px">
              <div style="border:1px solid #e0e0e0;border-radius:4px;padding:8px;max-height:150px;overflow-y:auto;background:#fff;margin-bottom:6px">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">
                  <label v-for="c in consignesTypes" :key="c.code"
                    :class="['consigne-item', { selected: getCopieConsignes(d.id).includes(c.code) }]"
                    style="display:flex;align-items:center;gap:6px;font-size:12px;cursor:pointer;padding:4px 8px;border-radius:4px;border:1px solid transparent">
                    <input type="checkbox" :value="c.code"
                      :checked="getCopieConsignes(d.id).includes(c.code)"
                      @change="toggleCopieConsigne(d.id, c.code)"
                      style="accent-color:#1565C0;width:12px;height:12px;flex-shrink:0" />
                    <span>{{ c.label }}</span>
                  </label>
                </div>
              </div>
              <input v-model="copiesConsigneLibre[d.id]" type="text"
                placeholder="Consigne spécifique (facultatif)..."
                style="width:100%;padding:6px 10px;border:1px solid #ddd;border-radius:4px;font-size:12px;box-sizing:border-box" />
            </div>
          </div>
        </div>
      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>

      <div class="actions-form">
        <button class="btn btn-ghost" @click="courrierExamine = null">Annuler</button>
        <button class="btn btn-danger" @click="ouvrirRejet">
          <i class="fa-solid fa-xmark"></i> Rejeter
        </button>
        <button class="btn btn-success" @click="confirmerValidation" :disabled="enEnvoi">
          <i class="fa-solid fa-check"></i> Valider et proposer au SG
        </button>
      </div>
    </div>
  </div>

  <!-- Modal rejet -->
  <div v-if="afficherModalRejet" class="modal-fond">
    <div class="modal">
      <div class="modal-titre"><i class="fa-solid fa-xmark"></i> Motif du rejet</div>
      <p style="font-size:14px;margin-bottom:12px">
        Courrier : <strong>{{ courrierExamine?.objet }}</strong>
      </p>
      <div class="champ">
        <label class="champ-obligatoire">Motif du rejet</label>
        <textarea v-model="motifRejet" rows="4"
          placeholder="Expliquez pourquoi ce courrier est retourné au Bureau d'Ordre..."></textarea>
      </div>
      <p v-if="erreurRejet" class="msg-erreur">{{ erreurRejet }}</p>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="afficherModalRejet = false">Annuler</button>
        <button class="btn btn-danger" @click="confirmerRejet" :disabled="enEnvoi">
          Confirmer le rejet
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { courriersApi } from '../../services/api'
import CarteCourrierDetail from './CarteCourrierDetail.vue'

const props = defineProps({
  courriers:  { type: Array,   default: () => [] },
  chargement: { type: Boolean, default: false },
    ongletInitial: { type: String,  default: 'attente' },  // ← AJOUTER
})
const emit = defineEmits(['rafraichir'])

// const onglet               = ref('attente')  // ← supprimer cette ligne car redondante avec la ligne 234
const enEnvoi              = ref(false)
const erreur               = ref('')
const erreurRejet          = ref('')
const courrierExamine      = ref(null)
const afficherModalRejet   = ref(false)
const motifRejet           = ref('')
const destinataires        = ref([])
const consignesTypes       = ref([])
const historique           = ref([])
const chargementHistorique = ref(false)
const filtres              = ref({ q: '', date_debut: '', date_fin: '', statut: '' })
const copiesSelectionnees  = ref([])
const copiesConsignes      = ref({})
const copiesConsigneLibre  = ref({})
const form                 = ref({ destinataire_id: '', consignes_types: [], consigne_libre: '' })

const aValider = computed(() => props.courriers.filter(c => c.statut === 'EN_ATT_SGA'))
const onglet = ref(props.ongletInitial)  // ← utiliser la prop

watch(onglet, (val) => {
  if (val === 'historique' && historique.value.length === 0) chargerHistorique()
})

async function chargerHistorique() {
  chargementHistorique.value = true
  try {
    const params = {}
    if (filtres.value.q)          params.q         = filtres.value.q
    if (filtres.value.date_debut) params.date_debut = filtres.value.date_debut
    if (filtres.value.date_fin)   params.date_fin   = filtres.value.date_fin
    if (filtres.value.statut)     params.statut     = filtres.value.statut

    const rep = await courriersApi.liste(params)
    let data = rep.data.filter(c => c.statut !== 'EN_ATT_SGA') // adapter pour SG

    // 10 derniers par défaut si aucun filtre actif
    const filtreActif = filtres.value.q || filtres.value.date_debut ||
                        filtres.value.date_fin || filtres.value.statut
    if (!filtreActif) data = data.slice(0, 10)
    params.limite = filtreActif ? 100 : 10

    historique.value = data
  } catch(e) { console.error(e) }
  finally { chargementHistorique.value = false }
}

function reinitFiltres() {
  filtres.value = { q: '', date_debut: '', date_fin: '', statut: '' }
  chargerHistorique()
}

function getCopieConsignes(id) {
  return copiesConsignes.value[id] || []
}

function toggleCopieConsigne(id, code) {
  const current = copiesConsignes.value[id] ? [...copiesConsignes.value[id]] : []
  const idx = current.indexOf(code)
  if (idx === -1) current.push(code)
  else current.splice(idx, 1)
  copiesConsignes.value = { ...copiesConsignes.value, [id]: current }
}

async function ouvrirFiche(c) {
  courrierExamine.value    = c
  erreur.value             = ''
  copiesSelectionnees.value = []
  copiesConsignes.value    = {}
  copiesConsigneLibre.value = {}
  form.value               = { destinataire_id: '', consignes_types: [], consigne_libre: '' }
  try {
    const [rd, rc] = await Promise.all([courriersApi.destinataires(), courriersApi.consignes()])
    destinataires.value  = rd.data || []
    consignesTypes.value = rc.data || []
  } catch(e) { console.error(e) }
}

async function confirmerValidation() {
  erreur.value = ''
  if (!form.value.destinataire_id) { erreur.value = 'Veuillez choisir un destinataire principal.'; return }
  if (!form.value.consignes_types.length) { erreur.value = 'Veuillez cocher au moins une consigne type.'; return }

  const copies_items = copiesSelectionnees.value
    .filter(id => id != form.value.destinataire_id)
    .map(id => ({
      id,
      consignes_types: copiesConsignes.value[id]      || [],
      consigne_libre:  copiesConsigneLibre.value[id]  || '',
    }))

  enEnvoi.value = true
  try {
    await courriersApi.validerSga(courrierExamine.value.id, {
      destinataire_id: form.value.destinataire_id,
      consignes_types: form.value.consignes_types,
      consigne_libre:  form.value.consigne_libre,
      copies_items,
    })
    courrierExamine.value = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la validation.'
  } finally { enEnvoi.value = false }
}

function ouvrirRejet() {
  afficherModalRejet.value = true
  motifRejet.value  = ''
  erreurRejet.value = ''
}

async function confirmerRejet() {
  erreurRejet.value = ''
  if (!motifRejet.value.trim()) { erreurRejet.value = 'Le motif est obligatoire.'; return }
  enEnvoi.value = true
  try {
    await courriersApi.rejeterSga(courrierExamine.value.id, { motif_rejet: motifRejet.value })
    afficherModalRejet.value = false
    courrierExamine.value    = null
    emit('rafraichir')
  } catch(e) {
    erreurRejet.value = e.response?.data?.detail || 'Erreur lors du rejet.'
  } finally { enEnvoi.value = false }
}
</script>

<style scoped>
.consigne-item:hover { background: #e3f0ff; border-color: #90caf9 !important; }
.consigne-item.selected { background: #e3f0ff; border-color: #1565C0 !important; }
</style>