<template>
  <div class="app-layout">

    <!-- Menu lateral -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>

      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Bureau d'Ordre</div>
      </div>

      <nav class="sidebar-nav">

        <div class="nav-section">
          <button :class="['nav-item', { actif: page === 'dashboard' }]" @click="page = 'dashboard'">
            <font-awesome-icon :icon="faChartBar" class="nav-item-icone" /> Tableau de bord
          </button>
        </div>

        <div class="nav-section">
          <div class="nav-section-titre">Courriers</div>
          <button :class="['nav-sous-item', { actif: page === 'liste' }]" @click="page = 'liste'; chargerCourriers()">
            <font-awesome-icon :icon="faList" /> Liste
          </button>
          <button :class="['nav-sous-item', { actif: page === 'nouveau' }]" @click="page = 'nouveau'">
            <font-awesome-icon :icon="faPlus" /> Nouveau
          </button>
        </div>

        <!-- Modules supplémentaires accordés par l'admin -->
        <div v-if="modules.includes('recherche') || modules.includes('archives') || modules.includes('statistiques')" class="nav-section">
          <div class="nav-section-titre">Modules extra</div>
          <button v-if="modules.includes('recherche')" :class="['nav-sous-item', { actif: page === 'recherche_extra' }]" @click="page = 'recherche_extra'">
            <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
            Recherche
          </button>
          <button v-if="modules.includes('archives')" :class="['nav-sous-item', { actif: page === 'archives_extra' }]" @click="page = 'archives_extra'">
            <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
            Archives
          </button>
          <button v-if="modules.includes('statistiques')" :class="['nav-sous-item', { actif: page === 'statistiques_extra' }]" @click="page = 'statistiques_extra'">
            <span class="nav-item-icone"><i class="fa-solid fa-chart-bar"></i></span>
            Statistiques
          </button>
        </div>

        <div class="nav-section" style="margin-top:8px">
          <button :class="['nav-item', { actif: page === 'notifications' }]" @click="page = 'notifications'">
            <span class="nav-item-icone"><i class="fa-solid fa-bell"></i></span>
            Notifications
            <span v-if="notifsNonLues > 0" class="nav-badge">{{ notifsNonLues }}</span>
          </button>
        </div>

      </nav>

      <button class="nav-item" @click="seDeconnecter">
  <span class="nav-item-icone"><i class="fa-solid fa-right-from-bracket"></i></span>
  Deconnexion
</button>
    </aside>

    <!-- Zone principale -->
    <div class="main-zone">

      <header class="topbar">
        <span class="topbar-titre">{{ titresPages[page] }}</span>
        <div class="topbar-droite">
          <button class="notif-btn" @click="page = 'notifications'">
            <font-awesome-icon :icon="faBell" />
            <span v-if="notifsNonLues > 0" class="notif-dot"></span>
          </button>
        </div>
      </header>

      <main class="page-contenu">

        <!-- DASHBOARD -->
        <div v-if="page === 'dashboard'" class="dashboard-container">
          <!-- KPIs - Cartes statistiques modernes -->
          <div class="kpi-grid">
            <div class="kpi-card kpi-info">
              <div class="kpi-content">
                <div class="kpi-label">Total courriers</div>
                <div class="kpi-value">{{ stats.total }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-warning">
              <div class="kpi-content">
                <div class="kpi-label">En vérification</div>
                <div class="kpi-value">{{ stats.en_verification }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-success">
              <div class="kpi-content">
                <div class="kpi-label">Validés</div>
                <div class="kpi-value">{{ stats.valides }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-danger">
              <div class="kpi-content">
                <div class="kpi-label">Rejetés</div>
                <div class="kpi-value">{{ stats.rejetes }}</div>
              </div>
            </div>
          </div>

          <!-- Section principale des courriers -->
          <div class="dashboard-main">
            <div class="carte carte-fluide">
              <div class="carte-header">
                <div class="carte-titre-icon">
                  <font-awesome-icon :icon="faList" class="titre-icon" />
                  <span>Derniers courriers enregistrés</span>
                </div>
                <div class="carte-badge" v-if="courriers.length > 0">{{ courriers.length }}</div>
              </div>
              
              <div v-if="courriers.length === 0" class="msg-vide-moderne">
                <div class="empty-icon"><font-awesome-icon :icon="faEnvelope" /></div>
                <p>Aucun courrier enregistré</p>
              </div>
              
              <div v-else class="tableau-wrap">
                <table class="tableau">
                  <thead>
                    <tr>
                      <th>Référence</th>
                      <th>Objet</th>
                      <th>Expéditeur</th>
                      <th>Priorité</th>
                      <th>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="c in courriers.slice(0,5)" :key="c.id">
                      <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                      <td>{{ c.objet }}</td>
                      <td>{{ c.expediteur }}</td>
                      <td><span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span></td>
                      <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- LISTE COURRIERS -->
        <div v-if="page === 'liste'">
          <div class="carte">
            <div class="carte-titre"><font-awesome-icon :icon="faList" /> Tous mes courriers</div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="courriers.length === 0" class="msg-vide">Aucun courrier enregistre.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr>
                    <th>Reference</th>
                    <th>Objet</th>
                    <th>Expediteur</th>
                    <th>Date reception</th>
                    <th>Priorite</th>
                    <th>Statut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in courriers" :key="c.id">
                    <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                    <td>{{ c.objet }}</td>
                    <td>{{ c.expediteur }}</td>
                    <td>{{ formaterDate(c.date_reception) }}</td>
                    <td><span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span></td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                    <td>
                      <div style="display:flex;gap:4px">
                        <button v-if="['BROUILLON', 'EN_VERIF'].includes(c.statut)" class="btn btn-outline" style="padding:4px 10px;font-size:12px" @click="ouvrirModification(c)">
                          <font-awesome-icon :icon="faPencil" /> Modifier
                        </button>
                        <a v-if="c.fichier_pdf_url" :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px"><font-awesome-icon :icon="faFile" /> PDF</a>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- NOUVEAU COURRIER -->
        <div v-if="page === 'nouveau'">
          <div class="carte">
            <div class="carte-titre"><font-awesome-icon :icon="faPlus" /> Enregistrer un nouveau courrier</div>

            <div class="grille-form">
              <div class="champ">
                <label class="champ-obligatoire">Objet</label>
                <input v-model="form.objet" type="text" placeholder="Objet du courrier" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Expediteur</label>
                <input v-model="form.expediteur" type="text" placeholder="Nom de l organisme ou de la personne" />
              </div>
              <div class="champ">
                <label>Reference expediteur</label>
                <input v-model="form.reference_exp" type="text" placeholder="Ex: N123/MIN/2026" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Origine</label>
                <select v-model="form.type_courrier">
                  <option value="ENT">Courrier entrant (externe)</option>
                  <option value="INT">Courrier interne</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Mode de reception</label>
                <select v-model="form.mode_reception">
                  <option value="DEPOT">Depot direct</option>
                  <option value="POSTAL">Courrier postal</option>
                  <option value="EMAIL">Email imprime</option>
                  <option value="COURSIER">Coursier</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Niveau de priorite</label>
                <select v-model="form.priorite">
                  <option value="NORMALE">Normale</option>
                  <option value="HAUTE">Haute</option>
                  <option value="BASSE">Basse</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Date du document</label>
                <input v-model="form.date_document" type="date" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Date de reception</label>
                <input v-model="form.date_reception" type="date" />
              </div>
              <div class="champ champ-large">
                <label class="champ-obligatoire">Fichier PDF scanne (max 25 Mo)</label>
                <input type="file" accept=".pdf,.jpg,.png" @change="selectionnerFichier" />
                <span v-if="erreurFichier" class="msg-erreur">{{ erreurFichier }}</span>
              </div>
              <div class="champ champ-large">
                <label>Observations</label>
                <textarea v-model="form.observations" rows="3" placeholder="Observations eventuelles (facultatif)"></textarea>
              </div>
            </div>

            <p v-if="erreurForm" class="msg-erreur">{{ erreurForm }}</p>
            <p v-if="msgSucces" class="msg-succes">{{ msgSucces }}</p>

            <div class="actions-form">
              <button class="btn btn-ghost" @click="reinitForm"><font-awesome-icon :icon="faSync" /> Effacer</button>
              <button class="btn btn-outline" @click="soumettre('BROUILLON')" :disabled="enEnvoi"><font-awesome-icon :icon="faSave" /> Sauvegarder brouillon</button>
              <button class="btn btn-primary" @click="soumettre('SOUMETTRE')" :disabled="enEnvoi">
                <span v-if="enEnvoi">Envoi...</span>
                <span v-else><font-awesome-icon :icon="faPaperPlane" /> Soumettre a l Assistant DG</span>
              </button>
            </div>
          </div>
        </div>

        <!-- MODAL MODIFICATION COURRIER -->
        <div v-if="courrierModification" class="modal-overlay" @click="fermerModification">
          <div class="modal-contenu" @click.stop>
            <div class="modal-titre">
              <font-awesome-icon :icon="faPencil" /> Modifier courrier
              <button class="modal-fermeture" @click="fermerModification">×</button>
            </div>
            
            <div class="grille-form">
              <div class="champ">
                <label class="champ-obligatoire">Objet</label>
                <input v-model="formModification.objet" type="text" placeholder="Objet du courrier" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Expediteur</label>
                <input v-model="formModification.expediteur" type="text" placeholder="Nom de l organisme ou de la personne" />
              </div>
              <div class="champ">
                <label>Reference expediteur</label>
                <input v-model="formModification.reference_exp" type="text" placeholder="Ex: N123/MIN/2026" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Origine</label>
                <select v-model="formModification.type_courrier">
                  <option value="RECOMMANDE">Courrier recommande</option>
                  <option value="ORDINAIRE">Courrier ordinaire</option>
                  <option value="INTERNE">Courrier interne</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Mode de reception</label>
                <select v-model="formModification.mode_reception">
                  <option value="MANUELLE">Reception manuelle</option>
                  <option value="ELECTRONIQUE">Reception electronique</option>
                  <option value="COURSIER">Coursier</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Niveau de priorite</label>
                <select v-model="formModification.priorite">
                  <option value="NORMAL">Normal</option>
                  <option value="HAUTE">Haute</option>
                  <option value="BASSE">Basse</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Date du document</label>
                <input v-model="formModification.date_document" type="date" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Date de reception</label>
                <input v-model="formModification.date_reception" type="date" />
              </div>
              <div class="champ champ-large">
                <label>Nouveau fichier PDF (max 25 Mo)</label>
                <input type="file" accept=".pdf,.jpg,.png" @change="selectionnerFichierModification" />
              </div>
              <div class="champ champ-large">
                <label>Observations</label>
                <textarea v-model="formModification.observations" rows="3" placeholder="Observations eventuelles (facultatif)"></textarea>
              </div>
            </div>

            <p v-if="erreurForm" class="msg-erreur">{{ erreurForm }}</p>
            <p v-if="msgSucces" class="msg-succes">{{ msgSucces }}</p>

            <div class="actions-form">
              <button class="btn btn-ghost" @click="fermerModification"><font-awesome-icon :icon="faTimes" /> Annuler</button>
              <button class="btn btn-primary" @click="modifierCourrier" :disabled="enEnvoi">
                <span v-if="enEnvoi">Modification...</span>
                <span v-else><font-awesome-icon :icon="faSave" /> Enregistrer les modifications</span>
              </button>
            </div>
          </div>
        </div>

        <!-- NOTIFICATIONS -->
        <div v-if="page === 'notifications'">
          <div class="carte">
            <div class="carte-titre"><font-awesome-icon :icon="faBell" /> Mes notifications</div>
            <div v-if="notifications.length === 0" class="msg-vide">Aucune notification.</div>
            <div v-else>
              <div v-for="n in notifications" :key="n.id" :class="['notif-item', { 'non-lue': !n.lue }]">
                <div>{{ n.message }}</div>
                <div class="notif-item-heure">{{ formaterDateHeure(n.date) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- RECHERCHE EXTRA (module accordé par l'admin) -->
        <div v-if="page === 'recherche_extra'">
          <div class="carte">
            <div class="carte-titre">Recherche documentaire</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ champ-large">
                <label>Recherche plein texte</label>
                <input v-model="recherche.q" type="text" placeholder="Objet, expéditeur, numéro..." @keyup.enter="lancerRecherche" />
              </div>
              <div class="champ"><label>Type</label>
                <select v-model="recherche.type">
                  <option value="">Tous</option>
                  <option value="ENT">Entrant</option>
                  <option value="INT">Interne</option>
                </select>
              </div>
              <div class="champ"><label>Date début</label><input v-model="recherche.date_debut" type="date" /></div>
              <div class="champ"><label>Date fin</label><input v-model="recherche.date_fin" type="date" /></div>
            </div>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:16px">
              <button class="btn btn-primary" @click="lancerRecherche" :disabled="rechercheEnCours">
                {{ rechercheEnCours ? 'Recherche...' : 'Lancer la recherche' }}
              </button>
              <button class="btn btn-ghost" @click="reinitRecherche">Réinitialiser</button>
            </div>
            <div v-if="rechercheEffectuee">
              <div v-if="resultatsRecherche.length === 0" class="msg-vide">Aucun résultat.</div>
              <div v-else class="tableau-wrap">
                <table class="tableau">
                  <thead><tr><th>Numéro</th><th>Objet</th><th>Expéditeur</th><th>Date</th><th>Statut</th></tr></thead>
                  <tbody>
                    <tr v-for="c in resultatsRecherche" :key="c.id">
                      <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                      <td>{{ c.objet }}</td>
                      <td>{{ c.expediteur }}</td>
                      <td>{{ formaterDate(c.date_reception) }}</td>
                      <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>

  </div>
</template>

<script setup>
import PiedPage from '../components/PiedPage.vue'
import { useInactivite } from '../composables/useInactivite'
import { useParametres } from '../composables/useParametres'
import { useModules, subscribeModules } from '../composables/useModules'
import { getApiClient } from '../composables/api'
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { faChartBar, faList, faPlus, faBell, faSignOutAlt, faEnvelope, faHourglass, faCheck, faTimes, faFile, faSave, faPaperPlane, faSync, faPencil } from '@fortawesome/free-solid-svg-icons'

useInactivite()
const modules  = ref([])
const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')

const page         = ref('dashboard')
const chargement   = ref(false)
const enEnvoi      = ref(false)
const courriers    = ref([])
const notifications = ref([])
const erreurForm   = ref('')
const erreurFichier = ref('')
const msgSucces    = ref('')

// Modification de courrier
const courrierModification = ref(null)
const formModification = ref({
  objet: '',
  expediteur: '',
  reference_exp: '',
  type_courrier: 'RECOMMANDE',
  mode_reception: 'MANUELLE',
  priorite: 'NORMAL',
  date_document: '',
  date_reception: '',
  observations: '',
  fichier_pdf: null,
})

const titresPages = {
  dashboard:           'Tableau de bord',
  liste:               'Liste des courriers',
  nouveau:             'Nouveau courrier',
  notifications:       'Notifications',
  recherche_extra:     'Recherche documentaire',
  archives_extra:      'Archives',
  statistiques_extra:  'Statistiques',
}

const notifsNonLues = computed(() => notifications.value.filter(n => !n.lue).length)

const stats = computed(() => ({
  total:           courriers.value.length,
  en_verification: courriers.value.filter(c => c.statut === 'EN_VERIF').length,
  valides:         courriers.value.filter(c => ['VERIFIE','EN_ATT_IMP','IMPUTE','EN_COURS','TRAITE'].includes(c.statut)).length,
  rejetes:         courriers.value.filter(c => c.statut === 'REJETE').length,
}))

const form = ref({
  objet: '', expediteur: '', reference_exp: '',
  type_courrier: 'ENT', mode_reception: 'DEPOT',
  priorite: 'NORMALE', date_document: '', date_reception: '',
  observations: '', fichier: null,
})

const api = getApiClient()

function selectionnerFichier(event) {
  const fichier = event.target.files[0]
  erreurFichier.value = ''
  if (fichier && fichier.size > 25 * 1024 * 1024) {
    erreurFichier.value = 'Le fichier depasse 25 Mo.'
    form.value.fichier = null
    return
  }
  form.value.fichier = fichier
}

async function chargerCourriers() {
  chargement.value = true
  try {
    const rep = await api.get('/courriers/')
    courriers.value = rep.data
  } catch (e) {
    console.error(e)
  } finally {
    chargement.value = false
  }
}

async function chargerNotifications() {
  try {
    const rep = await api.get('/notifications/')
    notifications.value = rep.data
  } catch (e) { /* silencieux */ }
}

async function soumettre(action) {
  erreurForm.value = ''
  msgSucces.value  = ''

  if (action === 'SOUMETTRE') {
    if (!form.value.objet || !form.value.expediteur || !form.value.date_document ||
        !form.value.date_reception || !form.value.fichier) {
      erreurForm.value = 'Tous les champs obligatoires (*) doivent etre remplis.'
      return
    }
  }

  enEnvoi.value = true
  const donnees = new FormData()
  Object.entries(form.value).forEach(([k, v]) => {
    if (k === 'fichier' && v) donnees.append('fichier_pdf', v)
    else if (k !== 'fichier') donnees.append(k, v)
  })
  donnees.append('action', action)

  try {
    await api.post('/courriers/', donnees, { headers: { 'Content-Type': 'multipart/form-data' } })
    msgSucces.value = action === 'SOUMETTRE'
      ? 'Courrier soumis a l Assistant DG. Il recevra une notification.'
      : 'Brouillon sauvegarde.'
    reinitForm()
    chargerCourriers()
    if (action === 'SOUMETTRE') page.value = 'liste'
  } catch (e) {
    erreurForm.value = 'Erreur lors de l enregistrement. Verifiez les donnees.'
  } finally {
    enEnvoi.value = false
  }
}

function reinitForm() {
  form.value = {
    objet: '', expediteur: '', reference_exp: '',
    type_courrier: 'ENT', mode_reception: 'DEPOT',
    priorite: 'NORMALE', date_document: '', date_reception: '',
    observations: '', fichier: null,
  }
  erreurForm.value   = ''
  erreurFichier.value = ''
}

function ouvrirModification(courrier) {
  courrierModification.value = courrier
  formModification.value = {
    objet: courrier.objet || '',
    expediteur: courrier.expediteur || '',
    reference_exp: courrier.reference_exp || '',
    type_courrier: courrier.type_courrier || 'RECOMMANDE',
    mode_reception: courrier.mode_reception || 'MANUELLE',
    priorite: courrier.priorite || 'NORMAL',
    date_document: courrier.date_document || '',
    date_reception: courrier.date_reception || '',
    observations: courrier.observations || '',
    fichier_pdf: null,
  }
  erreurForm.value = ''
  msgSucces.value = ''
}

async function modifierCourrier() {
  enEnvoi.value = true
  erreurForm.value = ''
  msgSucces.value = ''
  try {
    const formData = new FormData()
    formData.append('objet', formModification.value.objet)
    formData.append('expediteur', formModification.value.expediteur)
    formData.append('reference_exp', formModification.value.reference_exp)
    formData.append('type_courrier', formModification.value.type_courrier)
    formData.append('mode_reception', formModification.value.mode_reception)
    formData.append('priorite', formModification.value.priorite)
    formData.append('date_document', formModification.value.date_document)
    formData.append('date_reception', formModification.value.date_reception)
    formData.append('observations', formModification.value.observations)
    if (formModification.value.fichier_pdf) {
      formData.append('fichier_pdf', formModification.value.fichier_pdf)
    }

    const response = await api.patch(
      `/courriers/${courrierModification.value.id}/modifier/`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )

    msgSucces.value = 'Courrier modifie avec succes.'
    courrierModification.value = null
    await chargerCourriers()
  } catch (e) {
    erreurForm.value = 'Erreur lors de la modification. Verifiez les donnees.'
  } finally {
    enEnvoi.value = false
  }
}

function fermerModification() {
  courrierModification.value = null
  formModification.value = {
    objet: '', expediteur: '', reference_exp: '',
    type_courrier: 'RECOMMANDE', mode_reception: 'MANUELLE',
    priorite: 'NORMAL', date_document: '', date_reception: '',
    observations: '', fichier_pdf: null,
  }
  erreurForm.value = ''
}

function selectionnerFichierModification(event) {
  const fichier = event.target.files[0]
  erreurForm.value = ''
  if (fichier && fichier.size > 25 * 1024 * 1024) {
    erreurForm.value = 'Le fichier depasse 25 Mo.'
    formModification.value.fichier_pdf = null
    return
  }
  formModification.value.fichier_pdf = fichier
}


// Charger les données selon la page active
watch(page, (newPage) => {
  if (newPage === 'archives_extra') chargerArchivesExtra()
})

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}

function formaterDateHeure(d) {
  return d ? new Date(d).toLocaleString('fr-FR') : ''
}


const rechercheEnCours   = ref(false)
const rechercheEffectuee = ref(false)
const resultatsRecherche = ref([])
const chargementArchives = ref(false)
const archivesExtra      = ref([])
const filtreArchives     = ref({ q: "", fonds: "" })
const rechercheForm      = ref({ q: "", type: "", date_debut: "", date_fin: "" })

async function lancerRecherche() {
  rechercheEnCours.value   = true
  rechercheEffectuee.value = true
  try {
    const params = {}
    Object.entries(rechercheForm.value).forEach(([k, v]) => { if (v) params[k] = v })
    const rep = await api.get("/recherche/", { params })
    resultatsRecherche.value = rep.data.courriers || []
  } catch(e) { console.error(e) }
  finally { rechercheEnCours.value = false }
}

function reinitRecherche() {
  rechercheForm.value      = { q: "", type: "", date_debut: "", date_fin: "" }
  rechercheEffectuee.value = false
  resultatsRecherche.value = []
}

async function chargerArchivesExtra() {
  chargementArchives.value = true
  try {
    const params = {}
    if (filtreArchives.value.q)     params.q    = filtreArchives.value.q
    if (filtreArchives.value.fonds) params.fonds = filtreArchives.value.fonds
    const rep = await api.get("/archives/", { params })
    archivesExtra.value = rep.data
  } catch(e) { console.error(e) }
  finally { chargementArchives.value = false }
}

function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/')
}

// Polling toutes les 30s pour les notifications
let intervalle
onMounted(async () => {
  await useParametres()
  try {
    const rep = await api.get('/moi/')
    modules.value = rep.data.modules || []
  } catch(e) {}
  chargerCourriers()
  chargerNotifications()
  intervalle = setInterval(chargerNotifications, 30000)

  const unsubscribe = subscribeModules(async () => {
    modules.value = await useModules(true)
  })

  onUnmounted(() => {
    unsubscribe()
    clearInterval(intervalle)
  })
})
onUnmounted(() => clearInterval(intervalle))
</script>

<style scoped src="../assets/layout.css" />
