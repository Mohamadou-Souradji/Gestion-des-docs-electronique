<template>
  <div>
    <!-- Onglets DG -->
    <div class="onglets" style="margin-bottom:16px">
      <button :class="['onglet',{actif:ongletDG==='imputer'}]" @click="ongletDG='imputer'">
        <i class="fa-solid fa-paper-plane"></i> À imputer
        <span v-if="aImputer.length" style="background:#e53935;color:#fff;border-radius:10px;padding:1px 7px;font-size:11px;margin-left:6px">
          {{ aImputer.length }}
        </span>
      </button>
      <button :class="['onglet',{actif:ongletDG==='suivi'}]" @click="ongletDG='suivi'">
        <i class="fa-solid fa-eye"></i> Suivi
        <span v-if="enSuivi.length" style="background:#1565C0;color:#fff;border-radius:10px;padding:1px 7px;font-size:11px;margin-left:6px">
          {{ enSuivi.length }}
        </span>
      </button>
    </div>

    <!-- Onglet À imputer -->
    <div v-if="ongletDG==='imputer'">
      <div v-if="chargement" class="msg-vide">
        <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
      </div>
      <div v-else-if="aImputer.length === 0" class="msg-vide">
        Aucun courrier en attente d'imputation.
      </div>
      <div v-else>
        <CarteCourrierDetail v-for="c in aImputer" :key="c.id" :courrier="c">
          <template #actions>
            <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="ouvrirImputation(c)">
              <i class="fa-solid fa-paper-plane"></i> Imputer
            </button>
          </template>
        </CarteCourrierDetail>
      </div>
    </div>

    <!-- Onglet Suivi -->
    <div v-if="ongletDG==='suivi'">
      <div v-if="chargement" class="msg-vide">
        <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
      </div>
      <div v-else-if="enSuivi.length === 0" class="msg-vide">
        Aucun courrier imputé.
      </div>
      <div v-else>
        <CarteCourrierDetail v-for="c in enSuivi" :key="c.id" :courrier="c">
          <template #actions>
            <button class="btn btn-outline" style="font-size:13px;padding:6px 12px" @click="ouvrirDetails(c)">
              <i class="fa-solid fa-circle-info"></i> Détails
            </button>
          </template>
        </CarteCourrierDetail>
      </div>
    </div>
  </div>

  <!-- ═══ Modal détails compte rendu ═══ -->
  <div v-if="courrierDetails" class="modal-fond" @click.self="courrierDetails=null">
    <div class="modal" style="max-width:620px;max-height:90vh;overflow-y:auto">
      <div class="modal-titre">
        <i class="fa-solid fa-circle-info"></i> Détails du courrier
        <button class="btn btn-ghost" style="margin-left:auto;padding:4px 10px" @click="courrierDetails=null">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Infos générales -->
      <div style="background:#f5f8ff;padding:14px;border-radius:8px;margin-bottom:16px;font-size:13px">
        <div style="font-weight:700;font-size:15px;margin-bottom:4px">{{ courrierDetails.objet }}</div>
        <div style="color:#666">{{ courrierDetails.numero_officiel }} — {{ courrierDetails.expediteur }}</div>
      </div>

      <!-- Instructions envoyées -->
      <div style="margin-bottom:16px">
        <div style="font-weight:600;font-size:13px;color:#1565C0;margin-bottom:8px">
          <i class="fa-solid fa-list-check"></i> Instructions envoyées au destinataire
        </div>
        <div style="background:#e8f4ff;border-left:3px solid #1565C0;padding:10px 14px;border-radius:4px;font-size:13px;white-space:pre-line">
          {{ courrierDetails.instructions_dg || '—' }}
        </div>
      </div>

      <!-- Compte rendu -->
      <div style="margin-bottom:16px">
        <div style="font-weight:600;font-size:13px;color:#444;margin-bottom:8px">
          <i class="fa-solid fa-clock-rotate-left"></i> Compte rendu du destinataire
        </div>

        <div v-if="!courrierDetails.reponse_traitement && !courrierDetails.fichier_reponse_url"
          style="color:#999;font-size:13px;padding:12px;background:#f9f9f9;border-radius:6px;text-align:center">
          <i class="fa-solid fa-hourglass-half"></i> Pas encore de compte rendu.
        </div>

        <div v-else style="background:#f1f8f1;border-left:3px solid #2e7d32;padding:12px 14px;border-radius:4px">
          <div v-if="courrierDetails.date_traitement" style="font-size:12px;color:#666;margin-bottom:8px">
            <i class="fa-solid fa-calendar-check"></i>
            Traité le {{ new Date(courrierDetails.date_traitement).toLocaleDateString('fr-FR') }}
          </div>
          <div v-if="courrierDetails.reponse_traitement"
            style="font-size:13px;white-space:pre-line;margin-bottom:10px">
            {{ courrierDetails.reponse_traitement }}
          </div>
          <a v-if="courrierDetails.fichier_reponse_url"
            :href="courrierDetails.fichier_reponse_url" target="_blank"
            style="display:inline-flex;align-items:center;gap:8px;background:#2e7d32;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:13px">
            <i class="fa-solid fa-file-arrow-down"></i> Télécharger le fichier joint
          </a>
        </div>
      </div>
      <!-- Compte-rendus en copie -->
<div v-if="courrierDetails.copies && courrierDetails.copies.length > 0" style="margin-bottom:16px">
  <div style="font-weight:600;font-size:13px;color:#444;margin-bottom:8px">
    <i class="fa-solid fa-copy"></i> Compte-rendus des destinataires en copie
  </div>
  <div v-for="copie in courrierDetails.copies" :key="copie.id"
    style="background:#f9f9f9;border-left:3px solid #1565C0;padding:10px 14px;border-radius:4px;margin-bottom:8px">
    <div style="font-weight:600;font-size:13px;margin-bottom:4px">
      {{ copie.destinataire_nom }}
      <span v-if="copie.date_lecture" style="font-size:11px;color:#888;font-weight:400;margin-left:8px">
        <i class="fa-solid fa-check"></i> Lu
      </span>
    </div>
    <div v-if="copie.reponse" style="font-size:13px;color:#333;margin-bottom:6px">
      {{ copie.reponse }}
    </div>
    <div v-if="copie.fichier_reponse_url">
      <a :href="copie.fichier_reponse_url" target="_blank"
        style="display:inline-flex;align-items:center;gap:6px;background:#1565C0;color:#fff;padding:5px 12px;border-radius:6px;text-decoration:none;font-size:12px">
        <i class="fa-solid fa-file-arrow-down"></i> Fichier joint
      </a>
    </div>
    <div v-if="!copie.reponse && !copie.fichier_reponse_url"
      style="font-size:12px;color:#999;font-style:italic">
      Pas encore de compte-rendu.
    </div>
  </div>
</div>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="courrierDetails=null">Fermer</button>
      </div>
    </div>
  </div>

  <!-- ═══ Modal imputation ═══ -->
  <div v-if="courrierAImputer" class="modal-fond" @click.self="courrierAImputer = null">
    <div class="modal" style="max-width:720px;max-height:90vh;display:flex;flex-direction:column">
      <div class="modal-titre">
        <i class="fa-solid fa-paper-plane"></i> Imputer le courrier
        <button class="btn btn-ghost" style="margin-left:auto;padding:4px 10px" @click="courrierAImputer = null">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div style="overflow-y:auto;padding:0 4px;flex:1">
        <!-- Infos courrier -->
        <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:16px;font-size:13px">
          <strong>{{ courrierAImputer.numero_officiel }}</strong> — {{ courrierAImputer.objet }}<br/>
          <span style="color:#666">{{ courrierAImputer.expediteur }}</span>
          <span v-if="courrierAImputer.observation_dg" style="display:block;margin-top:6px;color:#1565C0">
            <i class="fa-solid fa-comment"></i> Note de l'assistant : {{ courrierAImputer.observation_dg }}
          </span>
        </div>

        <!-- Destinataire principal -->
        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Destinataire principal</label>
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
            Consignes pour le destinataire principal
            <span style="font-weight:400;color:#888;font-size:12px;margin-left:8px">
              ({{ form.consignes_types.length }} sélectionnée{{ form.consignes_types.length > 1 ? 's' : '' }})
            </span>
          </label>
          <div style="border:1px solid #e0e0e0;border-radius:6px;padding:10px;max-height:200px;overflow-y:auto;background:#fafafa">
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
          <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
            <button type="button" class="btn btn-outline" style="font-size:11px;padding:3px 10px"
              @click="form.consignes_types = consignesTypes.map(c => c.code)">
              Tout sélectionner
            </button>
            <button type="button" class="btn btn-outline" style="font-size:11px;padding:3px 10px"
              @click="form.consignes_types = []">
              Tout désélectionner
            </button>
          </div>
        </div>

        <!-- Consigne libre principale -->
        <div class="champ" style="margin-bottom:20px">
          <label>Consigne spécifique pour le destinataire principal (facultatif)</label>
          <textarea v-model="form.consigne_libre" rows="2"
            placeholder="Instructions spécifiques..."
            style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:13px;resize:vertical">
          </textarea>
        </div>

        <!-- Copies avec consignes individuelles -->
        <div style="border-top:2px dashed #e0e0e0;margin-bottom:16px;padding-top:16px">
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
                  <label v-for="c in consignesTypes" :key="`copie-${d.id}-${c.code}`"
                    :class="['consigne-item', { selected: getCopieConsignes(d.id).includes(c.code) }]"
                    style="display:flex;align-items:center;gap:6px;font-size:12px;cursor:pointer;padding:4px 8px;border-radius:4px;border:1px solid transparent">
                    <input type="checkbox"
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

        <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      </div>

      <div class="actions-form" style="border-top:1px solid #eee;padding-top:16px;margin-top:8px">
        <button class="btn btn-ghost" @click="courrierAImputer = null">Annuler</button>
        <button class="btn btn-primary" @click="confirmerImputation" :disabled="enEnvoi">
          <i class="fa-solid fa-check"></i>
          {{ enEnvoi ? 'Imputation...' : "Valider l'imputation" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { courriersApi } from '../../services/api'
import CarteCourrierDetail from './CarteCourrierDetail.vue'

const props = defineProps({
  courriers:  { type: Array,   default: () => [] },
  chargement: { type: Boolean, default: false },
  ongletInitial: { type: String,  default: 'imputer' },  

})
const emit = defineEmits(['rafraichir'])

const enEnvoi          = ref(false)
const erreur           = ref('')
const courrierAImputer = ref(null)
const courrierDetails  = ref(null)
const destinataires    = ref([])
const consignesTypes   = ref([])
const copiesSelectionnees  = ref([])
const copiesConsignes      = ref({})
const copiesConsigneLibre  = ref({})
const ongletDG = ref(props.ongletInitial)  

const form = ref({ destinataire_id: '', consignes_types: [], consigne_libre: '' })

const aImputer = computed(() => props.courriers.filter(c => c.statut === 'EN_ATT_IMP'))
const enSuivi  = computed(() => props.courriers.filter(c => ['IMPUTE','EN_COURS','TRAITE','ARCHIVE'].includes(c.statut)))

function ouvrirDetails(c) {
  courrierDetails.value = c
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

async function ouvrirImputation(c) {
  courrierAImputer.value    = c
  erreur.value              = ''
  copiesSelectionnees.value = []
  copiesConsignes.value     = {}
  copiesConsigneLibre.value = {}
  form.value                = { destinataire_id: '', consignes_types: [], consigne_libre: '' }

  const prop = c.proposition_sg || c.proposition_sga || {}
  if (prop.destinataire_id) {
    form.value.destinataire_id = prop.destinataire_id
    form.value.consignes_types = [...(prop.consignes_types || [])]  // spread ← fix bug partage
    form.value.consigne_libre  = prop.consigne_libre || ''

    if (prop.copies_items && prop.copies_items.length > 0) {
      const newSelectionnees = []
      const newConsignes     = {}
      const newLibres        = {}
      prop.copies_items.forEach(item => {
        newSelectionnees.push(item.id)
        newConsignes[item.id] = [...(item.consignes_types || [])]  // spread ← fix bug partage
        newLibres[item.id]    = item.consigne_libre || ''
      })
      copiesSelectionnees.value = newSelectionnees
      copiesConsignes.value     = newConsignes
      copiesConsigneLibre.value = newLibres
    }
  }

  try {
    const [rd, rc] = await Promise.all([courriersApi.destinataires(), courriersApi.consignes()])
    destinataires.value  = rd.data || []
    consignesTypes.value = rc.data || []
  } catch(e) {
    console.error('Erreur chargement:', e)
  }
}

async function confirmerImputation() {
  erreur.value = ''
  if (!form.value.destinataire_id) {
    erreur.value = 'Veuillez choisir un destinataire principal.'
    return
  }
  if (!form.value.consignes_types.length) {
    erreur.value = 'Veuillez cocher au moins une consigne type.'
    return
  }

  const copies_items = copiesSelectionnees.value
    .filter(id => id != form.value.destinataire_id)
    .map(id => ({
      id,
      consignes_types: copiesConsignes.value[id]     || [],
      consigne_libre:  copiesConsigneLibre.value[id] || '',
    }))

  enEnvoi.value = true
  try {
    await courriersApi.imputer(courrierAImputer.value.id, {
      destinataire_id: form.value.destinataire_id,
      consignes_types: form.value.consignes_types,
      consigne_libre:  form.value.consigne_libre,
      copies_items,
    })
    courrierAImputer.value = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = e.response?.data?.detail || "Erreur lors de l'imputation."
  } finally { enEnvoi.value = false }
}
</script>

<style scoped>
.consigne-item { transition: all 0.15s ease; }
.consigne-item:hover { background: #e3f0ff; border-color: #90caf9 !important; }
.consigne-item.selected { background: #e3f0ff; border-color: #1565C0 !important; }
.modal-fond {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
}
</style>