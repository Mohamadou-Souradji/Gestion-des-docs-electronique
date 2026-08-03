<template>
  <div>
    <div class="onglets">
      <button :class="['onglet', { actif: onglet === 'a_traiter' }]" @click="onglet = 'a_traiter'">
        <i class="fa-solid fa-inbox"></i> À traiter ({{ aTraiter.length }})
      </button>
      <button :class="['onglet', { actif: onglet === 'en_cours' }]" @click="onglet = 'en_cours'">
        <i class="fa-solid fa-spinner"></i> En cours ({{ enCours.length }})
      </button>
      <button :class="['onglet', { actif: onglet === 'traites' }]" @click="onglet = 'traites'">
        <i class="fa-solid fa-circle-check"></i> Traités ({{ traites.length }})
      </button>
      <button :class="['onglet', { actif: onglet === 'en_copie' }]" @click="onglet = 'en_copie'">
        <i class="fa-solid fa-copy"></i> En copie ({{ enCopie.length }})
      </button>
    </div>

    <div v-if="onglet === 'a_traiter'">
      <div v-if="aTraiter.length === 0" class="msg-vide">Aucun courrier à traiter.</div>
      <CarteCourrierDetail v-for="c in aTraiter" :key="c.id" :courrier="c">
        <template #actions>
          <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="ouvrirConsultation(c)">
            <i class="fa-solid fa-eye"></i> Consulter et traiter
          </button>
        </template>
      </CarteCourrierDetail>
    </div>

    <div v-if="onglet === 'en_cours'">
      <div v-if="enCours.length === 0" class="msg-vide">Aucun courrier en cours.</div>
      <CarteCourrierDetail v-for="c in enCours" :key="c.id" :courrier="c">
        <template #actions>
          <button class="btn btn-success" style="font-size:13px;padding:6px 14px" @click="ouvrirTraitement(c)">
            <i class="fa-solid fa-check"></i> Marquer comme traité
          </button>
        </template>
      </CarteCourrierDetail>
    </div>

    <div v-if="onglet === 'traites'">
      <ListeCourriers :courriers="traites" titre="Courriers traités" />
    </div>

    <div v-if="onglet === 'en_copie'">
      <p style="font-size:13px;color:#666;margin-bottom:16px">
        <i class="fa-solid fa-circle-info"></i>
        Ces courriers sont pour information. Vous n'avez pas à les marquer comme traités.
      </p>
      <div v-if="enCopie.length === 0" class="msg-vide">Aucun courrier en copie.</div>
      <CarteCourrierDetail v-for="c in enCopie" :key="c.id" :courrier="c">
        <template #actions>
          <button class="btn btn-outline" style="font-size:13px;padding:6px 14px" @click="ouvrirConsultation(c)">
            <i class="fa-solid fa-eye"></i> Consulter
          </button>
        </template>
      </CarteCourrierDetail>
    </div>
  </div>

  <!-- Modal consultation -->
  <div v-if="courrierOuvert" class="modal-fond" @click.self="courrierOuvert = null">
    <div class="modal" style="max-width:650px;max-height:90vh;display:flex;flex-direction:column">
      <div class="modal-titre" style="display:flex;justify-content:space-between;align-items:center;flex-shrink:0">
        <span><i class="fa-solid fa-eye"></i> {{ courrierOuvert.objet }}</span>
        <button class="btn btn-ghost" style="padding:4px 10px" @click="courrierOuvert = null">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div style="overflow-y:auto;padding:0 4px;flex:1">
        <!-- Badge mon_role -->
        <div v-if="courrierOuvert.mon_role" style="margin-bottom:12px">
          <span :class="`badge-role badge-${courrierOuvert.mon_role.toLowerCase()}`">
            <i v-if="courrierOuvert.mon_role === 'PRINCIPAL'" class="fa-solid fa-envelope"></i>
            <i v-if="courrierOuvert.mon_role === 'COPIE'" class="fa-solid fa-copy"></i>
            {{ courrierOuvert.mon_role === 'PRINCIPAL' ? 'Destinataire principal' : 'En copie' }}
          </span>
        </div>

        <!-- Métadonnées -->
        <div class="courrier-card-meta" style="margin-bottom:16px">
          <div><span class="meta-label">Numero</span>{{ courrierOuvert.numero_officiel }}</div>
          <div><span class="meta-label">Expediteur</span>{{ courrierOuvert.expediteur }}</div>
          <div><span class="meta-label">Date reception</span>{{ formaterDate(courrierOuvert.date_reception) }}</div>
          <div><span class="meta-label">Priorite</span>
            <span :class="`priorite-${courrierOuvert.priorite.toLowerCase()}`">
              {{ courrierOuvert.priorite }}
            </span>
          </div>
        </div>

       

        <!-- Instructions/Consignes selon le rôle -->
        <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:12px;font-size:13px">
          <strong style="color:#1565C0">
            <i class="fa-solid fa-comment"></i>
            {{ courrierOuvert.mon_role === 'COPIE' ? 'Vos consignes (en copie) :' : 'Instructions du DG :' }}
          </strong><br/>

          <!-- PRINCIPAL : instructions_dg texte + consignes badges -->
          <template v-if="courrierOuvert.mon_role === 'PRINCIPAL'">
            <div style="margin-top:6px">{{ courrierOuvert.instructions_dg }}</div>
          </template>

          <!-- COPIE : mes_consignes_copie uniquement -->
          <template v-else-if="courrierOuvert.mon_role === 'COPIE'">
            <div v-if="courrierOuvert.mes_consignes_copie?.consignes_types?.length"
              style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
              <span v-for="c in courrierOuvert.mes_consignes_copie.consignes_types" :key="c"
                style="background:#1565C0;color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:500">
                {{ c }}
              </span>
            </div>
            <div v-if="courrierOuvert.mes_consignes_copie?.consigne_libre"
              style="margin-top:6px;font-style:italic;color:#555;font-size:12px">
              {{ courrierOuvert.mes_consignes_copie.consigne_libre }}
            </div>
            <div v-if="!courrierOuvert.mes_consignes_copie?.consignes_types?.length"
              style="color:#999;font-size:12px;margin-top:4px">
              Aucune consigne spécifique.
            </div>
          </template>
        </div>

        <!-- PDF -->
        <div class="actions-form" style="margin-bottom:16px">
          <a :href="courrierOuvert.fichier_pdf_url" target="_blank" class="btn btn-outline">
            <i class="fa-solid fa-file-pdf"></i> Ouvrir le PDF
          </a>
         <a v-if="courrierOuvert.mon_role === 'PRINCIPAL' && courrierOuvert.fichier_reponse_url"
  :href="courrierOuvert.fichier_reponse_url"
  target="_blank" class="btn btn-outline">
  <i class="fa-solid fa-paperclip"></i> Fichier joint
</a>
        </div>

        <!-- Compte-rendu : SEULEMENT si PRINCIPAL -->
        <div v-if="courrierOuvert.mon_role === 'PRINCIPAL'" class="champ" style="margin-bottom:12px">
          <label>Compte-rendu de traitement (facultatif)</label>
          <textarea v-model="reponse" rows="3"
            placeholder="Decrivez les actions entreprises..."
            style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:13px;resize:vertical">
          </textarea>
        </div>

        <!-- Fichier joint : SEULEMENT si PRINCIPAL -->
        <div v-if="courrierOuvert.mon_role === 'PRINCIPAL'" class="champ" style="margin-bottom:12px">
          <label>Fichier joint (facultatif)</label>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            @change="e => fichierReponse = e.target.files[0]" />
        </div>
        <!-- Compte-rendu copie : SEULEMENT si COPIE -->
<div v-if="courrierOuvert.mon_role === 'COPIE'" class="champ" style="margin-bottom:12px">
  <label>Compte-rendu (facultatif)</label>
  <textarea v-model="reponse" rows="3"
    placeholder="Votre compte-rendu..."
    style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:13px;resize:vertical">
  </textarea>
</div>
<div v-if="courrierOuvert.mon_role === 'COPIE'" class="champ" style="margin-bottom:12px">
  <label>Fichier joint (facultatif)</label>
  <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
    @change="e => fichierReponse = e.target.files[0]" />
</div>

        <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      </div>

      <!-- Actions -->
      <div class="actions-form" style="border-top:1px solid #eee;padding-top:14px;margin-top:6px;flex-shrink:0">
        <button class="btn btn-ghost" @click="courrierOuvert = null">Fermer</button>
        <button v-if="courrierOuvert.mon_role === 'PRINCIPAL'"
          class="btn btn-success" @click="traiter" :disabled="enEnvoi">
          <i class="fa-solid fa-check"></i>
          {{ enEnvoi ? 'Traitement...' : 'Marquer comme traite' }}
        </button>
        <button v-if="courrierOuvert.mon_role === 'COPIE'"
          class="btn btn-primary" @click="traiterCopie" :disabled="enEnvoi">
          <i class="fa-solid fa-paper-plane"></i>
          {{ enEnvoi ? 'Envoi...' : 'Envoyer compte-rendu' }}
        </button>
      </div>

    </div>
  </div>

  <!-- Modal traitement depuis En cours -->
  <div v-if="courrierATraiter" class="modal-fond" @click.self="courrierATraiter = null">
    <div class="modal" style="max-width:500px">
      <div class="modal-titre">
        <i class="fa-solid fa-check"></i> Marquer comme traite
      </div>
      <p style="font-size:14px;margin-bottom:12px">
        Courrier : <strong>{{ courrierATraiter.objet }}</strong>
      </p>
      <div class="champ">
        <label>Compte-rendu (facultatif)</label>
        <textarea v-model="reponse" rows="3"
          placeholder="Actions entreprises..."
          style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:13px;resize:vertical">
        </textarea>
      </div>
      <div class="champ" style="margin-top:10px">
        <label>Fichier joint (facultatif)</label>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
          @change="e => fichierReponse = e.target.files[0]" />
      </div>
      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>
      <div class="actions-form">
        <button class="btn btn-ghost" @click="courrierATraiter = null">Annuler</button>
        <button class="btn btn-success" @click="confirmerTraitement" :disabled="enEnvoi">
          <i class="fa-solid fa-check"></i>
          {{ enEnvoi ? 'Traitement...' : 'Confirmer' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { courriersApi } from '../../services/api'
import CarteCourrierDetail from './CarteCourrierDetail.vue'
import ListeCourriers from './ListeCourriers.vue'

const props = defineProps({
  courriers:   { type: Array,   default: () => [] },
  chargement:  { type: Boolean, default: false },
  pageActive:  { type: String,  default: 'a_traiter' },
})
const emit = defineEmits(['rafraichir'])

const onglet           = ref('a_traiter')
const enEnvoi          = ref(false)
const erreur           = ref('')
const reponse          = ref('')
const fichierReponse   = ref(null)
const courrierOuvert   = ref(null)
const courrierATraiter = ref(null)

const aTraiter = computed(() =>
  props.courriers.filter(c => c.mon_role === 'PRINCIPAL' && c.statut === 'IMPUTE')
)
const enCours = computed(() =>
  props.courriers.filter(c => c.mon_role === 'PRINCIPAL' && c.statut === 'EN_COURS')
)
const traites = computed(() =>
  props.courriers.filter(c => c.mon_role === 'PRINCIPAL' && ['TRAITE', 'ARCHIVE'].includes(c.statut))
)
const enCopie = computed(() =>
  props.courriers.filter(c => c.mon_role === 'COPIE')
)

watch(() => props.pageActive, (newPage) => {
  if (['a_traiter', 'en_cours', 'traites', 'en_copie'].includes(newPage)) {
    onglet.value = newPage
  }
}, { immediate: true })

async function ouvrirConsultation(c) {
  courrierOuvert.value = c
  reponse.value        = ''
  erreur.value         = ''
  fichierReponse.value = null
  if (c.statut === 'IMPUTE') {
    try { await courriersApi.marquerLu(c.id) } catch(e) {}
    emit('rafraichir')
  }
}

function ouvrirTraitement(c) {
  courrierATraiter.value = c
  reponse.value          = ''
  erreur.value           = ''
  fichierReponse.value   = null
}

async function traiter() {
  enEnvoi.value = true
  try {
    const fd = new FormData()
    fd.append('reponse', reponse.value)
    if (fichierReponse.value) fd.append('fichier_reponse', fichierReponse.value)
    await courriersApi.marquerTraite(courrierOuvert.value.id, fd)
    courrierOuvert.value = null
    fichierReponse.value = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = 'Erreur lors du traitement.'
  } finally { enEnvoi.value = false }
}

async function traiterCopie() {
  enEnvoi.value = true
  try {
    const fd = new FormData()
    fd.append('reponse', reponse.value)
    if (fichierReponse.value) fd.append('fichier_reponse', fichierReponse.value)
    await courriersApi.traiterCopie(courrierOuvert.value.id, fd)
    courrierOuvert.value = null
    fichierReponse.value = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = 'Erreur lors de l\'envoi.'
  } finally { enEnvoi.value = false }
}

async function confirmerTraitement() {
  enEnvoi.value = true
  try {
    const fd = new FormData()
    fd.append('reponse', reponse.value)
    if (fichierReponse.value) fd.append('fichier_reponse', fichierReponse.value)
    await courriersApi.marquerTraite(courrierATraiter.value.id, fd)
    courrierATraiter.value = null
    fichierReponse.value   = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = 'Erreur lors du traitement.'
  } finally { enEnvoi.value = false }
}

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}
</script>

<style scoped>
.badge-role {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 4px;
  font-size: 12px; font-weight: 600; white-space: nowrap;
}
.badge-principal { background: #E8F5E9; color: #2E7D32; }
.badge-copie { background: #E3F2FD; color: #1565C0; }
.priorite-haute { color: #D32F2F; font-weight: 600; }
.priorite-normale { color: #F57C00; font-weight: 500; }
.priorite-basse { color: #388E3C; font-weight: 500; }
.modal-fond {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
}
.modal {
  background: white; border-radius: 8px; padding: 24px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  max-height: 90vh; display: flex; flex-direction: column;
}
.modal-titre {
  font-size: 18px; font-weight: 600; color: #1a237e;
  margin-bottom: 16px; display: flex;
  justify-content: space-between; align-items: center; flex-shrink: 0;
}
.courrier-card-meta {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; font-size: 13px; background: #f8f9fa;
  padding: 12px; border-radius: 6px;
}
.meta-label { color: #888; margin-right: 8px; font-weight: 500; }
.msg-erreur {
  color: #D32F2F; font-size: 13px; padding: 8px 12px;
  background: #FFEBEE; border-radius: 4px; margin: 8px 0;
}
.actions-form { display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap; }
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border: none; border-radius: 6px;
  font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s;
}
.btn-primary { background: #1565C0; color: white; }
.btn-primary:hover { background: #0D47A1; }
.btn-success { background: #2E7D32; color: white; }
.btn-success:hover { background: #1B5E20; }
.btn-outline { background: transparent; color: #1565C0; border: 1.5px solid #1565C0; }
.btn-outline:hover { background: #E3F2FD; }
.btn-ghost { background: transparent; color: #666; }
.btn-ghost:hover { background: #f0f0f0; }
.btn-danger { background: #D32F2F; color: white; }
.btn-danger:hover { background: #B71C1C; }
.msg-vide { text-align: center; padding: 40px; color: #999; font-size: 14px; }
</style>