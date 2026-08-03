<template>
  <div>
    <div class="onglets">
      <button :class="['onglet', { actif: onglet === 'a_verifier' }]" @click="onglet = 'a_verifier'">
        <i class="fa-solid fa-hourglass-half"></i>
        À vérifier ({{ aVerifier.length }})
      </button>
      <button :class="['onglet', { actif: onglet === 'traites' }]" @click="onglet = 'traites'">
        <i class="fa-solid fa-check-double"></i>
        Traités ({{ dejaTraites.length }})
      </button>
    </div>

    <!-- Courriers à vérifier -->
    <div v-if="onglet === 'a_verifier'">
      <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
      <div v-else-if="aVerifier.length === 0" class="msg-vide">Aucun courrier en attente de vérification.</div>
      <div v-else>
        <CarteCourrierDetail v-for="c in aVerifier" :key="c.id" :courrier="c">
          <template #actions>
            <button class="btn btn-outline" style="font-size:13px;padding:6px 12px" @click="ouvrirFiche(c)">
              <i class="fa-solid fa-magnifying-glass"></i> Examiner
            </button>
          </template>
        </CarteCourrierDetail>
      </div>
    </div>

    <!-- Courriers déjà traités -->
    <div v-if="onglet === 'traites'">
      <ListeCourriers :courriers="dejaTraites" :chargement="chargement" titre="Courriers traités" />
    </div>
  </div>

  <!-- Modal examen -->
  <div v-if="courrierExamine" class="modal-fond">
    <div class="modal" style="max-width:620px">
      <div class="modal-titre">
        <i class="fa-solid fa-magnifying-glass"></i> Vérification du courrier
      </div>

      <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:16px;font-size:13px">
        <strong>{{ courrierExamine.objet }}</strong><br/>
        <span style="color:#666">{{ courrierExamine.expediteur }} — {{ courrierExamine.identifiant_temp }}</span>
      </div>

      <!-- 5 points de contrôle CCFT obligatoires -->
      <div style="margin-bottom:16px">
        <div style="font-weight:600;font-size:13px;color:#1565C0;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center">
          <span>
            <i class="fa-solid fa-list-check"></i>
            Liste de contrôle — les 5 points doivent être cochés
          </span>
          <button type="button" class="btn btn-outline" style="font-size:12px;padding:4px 10px" @click="basculerTout">
            <i :class="tousCoches ? 'fa-solid fa-square' : 'fa-solid fa-check-double'"></i>
            {{ tousCoches ? 'Tout décocher' : 'Tout cocher' }}
          </button>
        </div>
        <ul class="checklist">
          <li v-for="(point, i) in checklist" :key="i">
            <input type="checkbox" v-model="checklist[i].coche" />
            {{ point.label }}
          </li>
        </ul>
        <div v-if="!tousCoches" style="color:#D32F2F;font-size:12px;margin-top:6px">
          <i class="fa-solid fa-triangle-exclamation"></i>
          Tous les points doivent être cochés pour valider.
        </div>
      </div>

      <div class="champ" style="margin-bottom:14px">
        <label>Observation pour le DG (facultatif)</label>
        <textarea v-model="observationDG" rows="2" placeholder="Remarque informative non bloquante..."></textarea>
      </div>

      <p v-if="erreur" class="msg-erreur">{{ erreur }}</p>

      <div class="actions-form">
        <button class="btn btn-ghost" @click="courrierExamine = null">Annuler</button>
        <button class="btn btn-danger" @click="ouvrirRejet">
          <i class="fa-solid fa-xmark"></i> Rejeter
        </button>
        <button class="btn btn-success" @click="valider" :disabled="!tousCoches || enEnvoi">
          <i class="fa-solid fa-check"></i> Valider et numéroter
        </button>
      </div>
    </div>
  </div>

  <!-- Modal rejet -->
  <div v-if="afficherModalRejet" class="modal-fond">
    <div class="modal">
      <div class="modal-titre">
        <i class="fa-solid fa-xmark"></i> Motif du rejet
      </div>
      <p style="font-size:14px;margin-bottom:12px">
        Courrier : <strong>{{ courrierExamine?.objet }}</strong>
      </p>
      <div class="champ">
        <label class="champ-obligatoire">Motif du rejet</label>
        <textarea v-model="motifRejet" rows="4"
          placeholder="Expliquez le motif : mauvaise qualité du scan, métadonnées incorrectes, doublon...">
        </textarea>
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
import ListeCourriers from './ListeCourriers.vue'

const props = defineProps({
  courriers:   { type: Array,   default: () => [] },
  chargement:  { type: Boolean, default: false },
  pageActive:  { type: String,  default: 'verification' },
})
const emit = defineEmits(['rafraichir'])

const onglet           = ref('a_verifier')
const enEnvoi          = ref(false)
const erreur           = ref('')
const erreurRejet      = ref('')
const courrierExamine  = ref(null)
const afficherModalRejet = ref(false)
const motifRejet       = ref('')
const observationDG    = ref('')

const aVerifier   = computed(() => props.courriers.filter(c => c.statut === 'EN_VERIF'))
const dejaTraites = computed(() => props.courriers.filter(c => c.statut !== 'EN_VERIF' && c.statut !== 'BROUILLON'))

const checklist = ref([
  { label: 'Le scan est lisible et de bonne qualité (min 200 dpi)', coche: false },
  { label: 'Les métadonnées sont exactes (expéditeur, dates, objet)', coche: false },
  { label: 'Le type et la priorité sont correctement renseignés', coche: false },
  { label: 'L\'adressage est conforme à l\'organisation', coche: false },
  { label: 'Le courrier ne constitue pas un doublon', coche: false },
])

const tousCoches = computed(() => checklist.value.every(c => c.coche))

// 🆕 Changer l'onglet automatiquement selon la page active
watch(() => props.pageActive, (newPage) => {
  if (newPage === 'courriers_traites') {
    onglet.value = 'traites'
  } else if (newPage === 'verification') {
    onglet.value = 'a_verifier'
  }
}, { immediate: true })

function ouvrirFiche(c) {
  courrierExamine.value = c
  observationDG.value   = ''
  erreur.value          = ''
  checklist.value.forEach(p => p.coche = false)
}

function basculerTout() {
  const valeur = !tousCoches.value
  checklist.value.forEach(p => p.coche = valeur)
}

async function valider() {
  enEnvoi.value = true
  erreur.value  = ''
  try {
    await courriersApi.valider(courrierExamine.value.id, { observation_dg: observationDG.value })
    courrierExamine.value = null
    emit('rafraichir')
  } catch(e) {
    erreur.value = e.response?.data?.detail || 'Erreur lors de la validation.'
  } finally { enEnvoi.value = false }
}

function ouvrirRejet() {
  afficherModalRejet.value = true
  motifRejet.value         = ''
  erreurRejet.value        = ''
}

async function confirmerRejet() {
  erreurRejet.value = ''
  if (!motifRejet.value.trim()) { erreurRejet.value = 'Le motif est obligatoire.'; return }
  enEnvoi.value = true
  try {
    await courriersApi.rejeter(courrierExamine.value.id, { motif_rejet: motifRejet.value })
    afficherModalRejet.value = false
    courrierExamine.value    = null
    emit('rafraichir')
  } catch(e) {
    erreurRejet.value = 'Erreur lors du rejet.'
  } finally { enEnvoi.value = false }
}
</script>