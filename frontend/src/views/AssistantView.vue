<template>
  <div class="app-layout">

    <!-- Menu lateral -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>

      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Assistant DG</div>
      </div>

      <nav class="sidebar-nav">

  <button :class="['nav-item', { actif: page === 'dashboard' }]" @click="page = 'dashboard'">
    <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
    Tableau de bord
  </button>

  <div class="nav-section-titre">Courriers</div>
  <button :class="['nav-sous-item', { actif: page === 'a_traiter' }]" @click="page = 'a_traiter'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-hourglass-half"></i></span>
    A traiter
    <span v-if="aTraiter.length > 0" class="nav-badge">{{ aTraiter.length }}</span>
  </button>
  <button :class="['nav-sous-item', { actif: page === 'traites' }]" @click="page = 'traites'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-check"></i></span>
    Traites
  </button>

  <div v-if="modules.includes('archives')" class="nav-section-titre">Archives</div>
  <button v-if="modules.includes('archives')" :class="['nav-sous-item', { actif: page === 'archives_extra' }]" @click="page = 'archives'">
    <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
    Consulter archives
  </button>

  <div v-if="modules.includes('archives') || modules.includes('recherche')" class="nav-section-titre">Modules extra</div>
  <button v-if="modules.includes('archives')" :class="['nav-sous-item', { actif: page === 'archives_extra' }]" @click="page = 'archives_extra'; chargerArchivesExtra()">
    <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
    Archives
  </button>
  <button v-if="modules.includes('recherche')" :class="['nav-sous-item', { actif: page === 'recherche_extra' }]" @click="page = 'recherche_extra'">
    <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
    Recherche
  </button>

    <button :class="['nav-item', { actif: page === 'notifications' }]" @click="page = 'notifications'" style="margin-top:8px">
    <span class="nav-item-icone"><i class="fa-solid fa-bell"></i></span>
    Notifications
    <span v-if="notifsNonLues > 0" class="nav-badge">{{ notifsNonLues }}</span>
  </button>

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
            <div class="kpi-card kpi-warning">
              <div class="kpi-content">
                <div class="kpi-label">A vérifier</div>
                <div class="kpi-value">{{ aTraiter.length }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-success">
              <div class="kpi-content">
                <div class="kpi-label">Validés</div>
                <div class="kpi-value">{{ valides.length }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-danger">
              <div class="kpi-content">
                <div class="kpi-label">Rejetés</div>
                <div class="kpi-value">{{ rejetes.length }}</div>
              </div>
            </div>
            
            <div class="kpi-card kpi-info">
              <div class="kpi-content">
                <div class="kpi-label">Total traités</div>
                <div class="kpi-value">{{ tousCourriers.length }}</div>
              </div>
            </div>
          </div>

          <!-- Section principale des courriers -->
          <div class="dashboard-main">
            <div class="carte carte-fluide">
              <div class="carte-header">
                <div class="carte-titre-icon">
                  <font-awesome-icon :icon="faHourglass" class="titre-icon" />
                  <span>Courriers en attente</span>
                </div>
                <div class="carte-badge" v-if="aTraiter.length > 0">{{ aTraiter.length }}</div>
              </div>
              
              <div v-if="aTraiter.length === 0" class="msg-vide-moderne">
                <div class="empty-icon"><font-awesome-icon :icon="faEnvelope" /></div>
                <p>Aucun courrier en attente de vérification</p>
              </div>
              
              <div v-else class="courriers-container">
                <div v-for="c in aTraiter.slice(0,3)" :key="c.id" class="courrier-card-moderne">
                  <div class="courrier-card-left">
                    <div class="courrier-priority" :class="'priority-' + c.priorite.toLowerCase()"></div>
                    <div class="courrier-info">
                      <div class="courrier-objet">{{ c.objet }}</div>
                      <div class="courrier-meta">
                        <span class="courrier-exp">{{ c.expediteur }}</span>
                        <span class="courrier-date">{{ formaterDate(c.date_reception) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="courrier-card-right">
                    <button class="btn btn-primary-small" @click="ouvrirFiche(c)">
                      <font-awesome-icon :icon="faSearch" />
                    </button>
                  </div>
                </div>
                
                <button v-if="aTraiter.length > 3" class="btn-see-all" @click="page = 'a_traiter'">
                  Voir tous ({{ aTraiter.length }})
                  <font-awesome-icon :icon="faSearch" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- A TRAITER -->
        <div v-if="page === 'a_traiter'">
          <div class="carte">
            <div class="carte-titre"><font-awesome-icon :icon="faHourglass" /> Courriers a verifier</div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="aTraiter.length === 0" class="msg-vide">Aucun courrier en attente.</div>
            <div v-else>
              <div v-for="c in aTraiter" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.expediteur }}</div>
                  </div>
                  <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">
                    <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
                    <span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span>
                  </div>
                </div>
                <div class="courrier-card-meta">
                  <div><span class="meta-label">Date reception</span>{{ formaterDate(c.date_reception) }}</div>
                  <div><span class="meta-label">Date document</span>{{ formaterDate(c.date_document) }}</div>
                  <div><span class="meta-label">Mode reception</span>{{ c.mode_reception }}</div>
                  <div><span class="meta-label">Saisi par</span>{{ c.saisi_par_nom }}</div>
                </div>
                <div class="courrier-card-actions">
                  <a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="font-size:13px;padding:6px 12px"><font-awesome-icon :icon="faFile" /> Voir PDF</a>
                  <button class="btn btn-outline" style="font-size:13px;padding:6px 12px" @click="ouvrirFiche(c)"><font-awesome-icon :icon="faSearch" /> Examiner</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TRAITES -->
        <div v-if="page === 'traites'">
          <div class="carte">
            <div class="carte-titre"><font-awesome-icon :icon="faCheck" /> Courriers traités</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ"><label>Recherche</label><input v-model="filtreTraites.q" type="text" placeholder="Objet, expéditeur, numéro..." /></div>
              <div class="champ"><label>Expéditeur</label><input v-model="filtreTraites.expediteur" type="text" placeholder="Nom expéditeur" /></div>
              <div class="champ"><label>Statut</label>
                <select v-model="filtreTraites.statut">
                  <option value="">Tous</option>
                  <option value="VERIFIE">Vérifié</option>
                  <option value="EN_ATT_IMP">En attente import</option>
                  <option value="REJETE">Rejeté</option>
                </select>
              </div>
              <div class="champ"><label>Date début</label><input v-model="filtreTraites.date_debut" type="date" /></div>
              <div class="champ"><label>Date fin</label><input v-model="filtreTraites.date_fin" type="date" /></div>
            </div>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:16px">
              <button class="btn btn-primary" @click="appliquerFiltresTraites">Appliquer</button>
              <button class="btn btn-ghost" @click="reinitialiserFiltresTraites">Réinitialiser</button>
            </div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="dejaTraitesFiltres.length === 0" class="msg-vide">Aucun courrier traité.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr>
                    <th>Numero officiel</th>
                    <th>Objet</th>
                    <th>Expediteur</th>
                    <th>Date verification</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in dejaTraitesFiltres" :key="c.id">
                    <td>{{ c.numero_officiel || '-' }}</td>
                    <td>{{ c.objet }}</td>
                    <td>{{ c.expediteur }}</td>
                    <td>{{ formaterDate(c.date_verification) }}</td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ARCHIVES (module accordé par l'admin) -->
        <!-- ARCHIVES (module accordé par l'admin) -->
        <div v-if="page === 'archives_extra'">
          <div class="carte">
            <div class="carte-titre">Consultation des archives historiques</div>
            <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
              <input v-model="filtreArchives.q" type="text" placeholder="Référence, intitulé, expéditeur..."
                style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px"
                @keyup.enter="chargerArchivesExtra" />
              <select v-model="filtreArchives.fonds" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                <option value="">Tous les fonds</option>
                <option value="ESCEP">ESCEP</option>
                <option value="EST">EST (2011-2023)</option>
                <option value="CNIPT">CNIPT (1969-2011)</option>
              </select>
              <button class="btn btn-primary" @click="chargerArchivesExtra">Filtrer</button>
            </div>
            <div v-if="chargementArchives" class="msg-vide">Chargement...</div>
            <div v-else-if="archivesExtra.length === 0" class="msg-vide">Aucune archive trouvée.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Référence système</th><th>Référence origine</th><th>Intitulé</th><th>Fonds</th><th>Date</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="a in archivesExtra" :key="a.id">
                    <td>{{ a.reference_systeme }}</td>
                    <td>{{ a.reference_origine || '-' }}</td>
                    <td>{{ a.intitule }}</td>
                    <td>{{ a.fonds }}</td>
                    <td>{{ formaterDate(a.date_document) }}</td>
                    <td><a :href="a.fichier_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- RECHERCHE (module accordé par l'admin) -->
        <div v-if="page === 'recherche_extra'">
          <div class="carte">
            <div class="carte-titre">Recherche documentaire</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ champ-large">
                <label>Recherche plein texte</label>
                <input v-model="rechercheForm.q" type="text" placeholder="Objet, expéditeur, numéro de courrier..." @keyup.enter="lancerRecherche" />
              </div>
              <div class="champ">
                <label>Type</label>
                <select v-model="rechercheForm.type">
                  <option value="">Tous</option>
                  <option value="ENT">Entrant</option>
                  <option value="INT">Interne</option>
                </select>
              </div>
              <div class="champ"><label>Date début</label><input v-model="rechercheForm.date_debut" type="date" /></div>
              <div class="champ"><label>Date fin</label><input v-model="rechercheForm.date_fin" type="date" /></div>
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
      </main>
    <PiedPage />
    </div>

    <!-- Modal d'examen du courrier -->
    <div v-if="courrierExamine" class="modal-fond">
      <div class="modal" style="max-width:600px">
        <div class="modal-titre"><font-awesome-icon :icon="faSearch" /> Verification du courrier</div>

        <div class="courrier-card-meta" style="margin-bottom:16px">
          <div><span class="meta-label">Objet</span>{{ courrierExamine.objet }}</div>
          <div><span class="meta-label">Expediteur</span>{{ courrierExamine.expediteur }}</div>
          <div><span class="meta-label">Date reception</span>{{ formaterDate(courrierExamine.date_reception) }}</div>
          <div><span class="meta-label">Priorite</span>{{ courrierExamine.priorite }}</div>
        </div>

        <!-- Liste de controle obligatoire (5 points CCFT) -->
        <div style="margin-bottom:16px">
          <strong style="color:#1565C0;font-size:14px">Liste de controle (tous les points doivent etre coches)</strong>
          <ul class="checklist">
            <li v-for="(point, i) in checklist" :key="i">
              <input type="checkbox" v-model="checklist[i].coche" />
              {{ point.label }}
            </li>
          </ul>
        </div>

        <!-- Observation libre pour le DG -->
        <div class="champ" style="margin-bottom:16px">
          <label>Observation pour le DG (facultatif)</label>
          <textarea v-model="observationDG" rows="2" placeholder="Remarque informative pour le DG..."></textarea>
        </div>

        <p v-if="erreurModal" class="msg-erreur">{{ erreurModal }}</p>

        <div class="actions-form" style="justify-content:space-between;align-items:center">
          <div style="display:flex;gap:10px;align-items:center">
            <input type="checkbox" id="cocher-tout" v-model="toutCoche" />
            <label for="cocher-tout" style="margin:0;cursor:pointer;font-size:14px">Cocher toutes les cases</label>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn btn-ghost" @click="courrierExamine = null">Annuler</button>
            <button class="btn btn-danger" @click="ouvrirRejet"><font-awesome-icon :icon="faTimes" /> Rejeter</button>
            <button class="btn btn-success" @click="valider" :disabled="!tousCoches">
              <font-awesome-icon :icon="faCheck" /> Valider et numéroter
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de rejet -->
    <div v-if="afficherModalRejet" class="modal-fond">
      <div class="modal">
        <div class="modal-titre"><font-awesome-icon :icon="faTimes" /> Motif du rejet</div>
        <p style="font-size:14px;margin-bottom:12px">Courrier : <strong>{{ courrierExamine?.objet }}</strong></p>
        <div class="champ">
          <label class="champ-obligatoire">Motif du rejet</label>
          <textarea v-model="motifRejet" rows="4"
            placeholder="Expliquez le motif du rejet : mauvaise qualite du scan, metadonnees incorrectes, doublon...">
          </textarea>
        </div>
        <p v-if="erreurRejet" class="msg-erreur">{{ erreurRejet }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="afficherModalRejet = false">Annuler</button>
          <button class="btn btn-danger" @click="confirmerRejet">Confirmer le rejet</button>
        </div>
      </div>
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
import { faChartBar, faHourglass, faCheck, faTimes, faBell, faSignOutAlt, faEnvelope, faSearch, faFile } from '@fortawesome/free-solid-svg-icons'

useInactivite()
const modules  = ref([])
const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')

const page             = ref('dashboard')
const chargement       = ref(false)
const tousCourriers    = ref([])
const notifications    = ref([])
const courrierExamine  = ref(null)
const afficherModalRejet = ref(false)
const motifRejet       = ref('')
const observationDG    = ref('')
const erreurModal      = ref('')
const erreurRejet      = ref('')

const titresPages = {
  dashboard:     'Tableau de bord',
  a_traiter:     'Courriers à traiter',
  traites:       'Courriers traités',
  notifications: 'Notifications',
  archives:            'Archives historiques',
  recherche_extra:     'Recherche documentaire',
}

// Les 5 points de controle obligatoires (CCFT Annexe B)
const checklist = ref([
  { label: 'Le scan est lisible et de bonne qualité (min. 200 dpi)', coche: false },
  { label: 'Les métadonnées sont exactes (expéditeur, dates, objet)', coche: false },
  { label: 'Le type et la priorité sont correctement renseignés', coche: false },
  { label: 'L adressage est conforme à ESCEP-Niger', coche: false },
  { label: 'Le courrier ne constitue pas un doublon', coche: false },
])

const toutCoche = ref(false)
const tousCoches = computed(() => checklist.value.every(c => c.coche))
const filtreTraites = ref({ q:'', statut:'', expediteur:'', date_debut:'', date_fin:'' })
const aTraiter      = computed(() => tousCourriers.value.filter(c => c.statut === 'EN_VERIF'))
const dejaTraites   = computed(() => tousCourriers.value.filter(c => c.statut !== 'EN_VERIF'))
const dejaTraitesFiltres = computed(() => {
  return dejaTraites.value.filter(c => {
    const q = filtreTraites.value.q.toLowerCase()
    const matchTexte = !q || c.objet.toLowerCase().includes(q) || c.expediteur.toLowerCase().includes(q) || (c.numero_officiel || '').toLowerCase().includes(q)
    const matchExpediteur = !filtreTraites.value.expediteur || c.expediteur.toLowerCase().includes(filtreTraites.value.expediteur.toLowerCase())
    const matchStatut = !filtreTraites.value.statut || c.statut === filtreTraites.value.statut
    const dateDebut = filtreTraites.value.date_debut ? new Date(filtreTraites.value.date_debut) : null
    const dateFin = filtreTraites.value.date_fin ? new Date(filtreTraites.value.date_fin) : null
    const dateCourrier = c.date_verification ? new Date(c.date_verification) : null
    const matchDateDebut = !dateDebut || (dateCourrier && dateCourrier >= dateDebut)
    const matchDateFin = !dateFin || (dateCourrier && dateCourrier <= dateFin)
    return matchTexte && matchExpediteur && matchStatut && matchDateDebut && matchDateFin
  })
})
const valides       = computed(() => tousCourriers.value.filter(c => c.statut === 'VERIFIE' || c.statut === 'EN_ATT_IMP'))
const rejetes       = computed(() => tousCourriers.value.filter(c => c.statut === 'REJETE'))
const notifsNonLues = computed(() => notifications.value.filter(n => !n.lue).length)

const api = getApiClient()

async function chargerCourriers() {
  chargement.value = true
  try {
    const rep = await api.get('/courriers/')
    tousCourriers.value = rep.data
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

function ouvrirFiche(courrier) {
  courrierExamine.value = courrier
  erreurModal.value     = ''
  observationDG.value   = ''
  toutCoche.value       = false
  checklist.value.forEach(c => c.coche = false)
}

watch(toutCoche, value => {
  checklist.value.forEach(c => c.coche = value)
})

watch(checklist, () => {
  toutCoche.value = checklist.value.every(c => c.coche)
}, { deep: true })

async function valider() {
  if (!tousCoches.value) {
    erreurModal.value = 'Vous devez cocher les 5 points de contrôle.'
    return
  }
  try {
    await api.patch(`/courriers/${courrierExamine.value.id}/valider/`, {
      observation_dg: observationDG.value
    })
    courrierExamine.value = null
    chargerCourriers()
    chargerNotifications()
  } catch (e) {
    erreurModal.value = 'Erreur lors de la validation.'
  }
}

function ouvrirRejet() {
  afficherModalRejet.value = true
  motifRejet.value         = ''
  erreurRejet.value        = ''
}

async function confirmerRejet() {
  erreurRejet.value = ''
  if (!motifRejet.value.trim()) {
    erreurRejet.value = 'Le motif du rejet est obligatoire.'
    return
  }
  try {
    await api.patch(`/courriers/${courrierExamine.value.id}/rejeter/`, {
      motif_rejet: motifRejet.value
    })
    afficherModalRejet.value = false
    courrierExamine.value    = null
    chargerCourriers()
    chargerNotifications()
  } catch (e) {
    erreurRejet.value = 'Erreur lors du rejet.'
  }
}


// Charger les données selon la page active
watch(page, (newPage) => {
  if (newPage === 'archives') chargerArchivesExtra()
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

let intervalle
onMounted(async () => {
  await useParametres()
  modules.value = await useModules()
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
</script>

<style scoped src="../assets/layout.css" />
