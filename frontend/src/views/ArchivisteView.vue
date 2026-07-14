<template>
  <div class="app-layout">

    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>
      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Archiviste</div>
      </div>
      <nav class="sidebar-nav">

  <button :class="['nav-item', { actif: page === 'dashboard' }]" @click="page = 'dashboard'">
    <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
    Tableau de bord
  </button>

  <div class="nav-section-titre">Courriers courants</div>
  <button :class="['nav-sous-item', { actif: page === 'a_archiver' }]" @click="page = 'a_archiver'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-download"></i></span>
    A archiver
    <span v-if="aArchiver.length > 0" class="nav-badge">{{ aArchiver.length }}</span>
  </button>
  <button :class="['nav-sous-item', { actif: page === 'archives_courantes' }]" @click="page = 'archives_courantes'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
    Archives courantes
  </button>

  <div class="nav-section-titre">Archives historiques</div>
  <button :class="['nav-sous-item', { actif: page === 'versement_unitaire' }]" @click="page = 'versement_unitaire'">
    <span class="nav-item-icone"><i class="fa-solid fa-file-arrow-up"></i></span>
    Versement unitaire
  </button>
  <button :class="['nav-sous-item', { actif: page === 'fonds_archives' }]" @click="page = 'fonds_archives'; chargerArchives()">
    <span class="nav-item-icone"><i class="fa-solid fa-folder-open"></i></span>
    Fonds d archives
  </button>

  <div class="nav-section-titre">Recherche</div>
  <button :class="['nav-sous-item', { actif: page === 'recherche' }]" @click="page = 'recherche'">
    <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
    Recherche documentaire
  </button>

  <button :class="['nav-item', { actif: page === 'notifications' }]" @click="page = 'notifications'; chargerNotifications()" style="margin-top:8px">
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

    <div class="main-zone">
      <header class="topbar">
        <span class="topbar-titre">{{ titresPages[page] }}</span>
        <div class="topbar-droite">
          <button class="notif-btn" @click="page = 'notifications'; chargerNotifications()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span v-if="notifsNonLues > 0" class="notif-dot"></span>
          </button>
        </div>
      </header>

      <main class="page-contenu">

        <!-- DASHBOARD -->
        <div v-if="page === 'dashboard'">
          <div class="stats-grille">
            <div class="stat-card">
              <div class="stat-icone jaune"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></div>
              <div><div class="stat-valeur">{{ aArchiver.length }}</div><div class="stat-label">A archiver</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone bleu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/><path d="M2 10h20"/></svg></div>
              <div><div class="stat-valeur">{{ archivesCourantes.length }}</div><div class="stat-label">Archives courantes</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone vert"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg></div>
              <div><div class="stat-valeur">{{ totalArchivesHisto }}</div><div class="stat-label">Archives historiques</div></div>
            </div>
          </div>

          <div class="carte">
            <div class="carte-titre">Courriers traites en attente d archivage</div>
            <div v-if="aArchiver.length === 0" class="msg-vide">Aucun courrier a archiver.</div>
            <div v-else>
              <div v-for="c in aArchiver.slice(0,4)" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }} — {{ c.expediteur }}</div>
                  </div>
                  <span class="badge badge-traite">Traite</span>
                </div>
                <div class="courrier-card-actions">
                  <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="archiver(c)" :disabled="enEnvoi">Archiver</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- A ARCHIVER -->
        <div v-if="page === 'a_archiver'">
          <div class="carte">
            <div class="carte-titre">Courriers traites — en attente d archivage</div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="aArchiver.length === 0" class="msg-vide">Aucun courrier a archiver.</div>
            <div v-else>
              <div v-for="c in aArchiver" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }} — {{ c.expediteur }}</div>
                  </div>
                  <span class="badge badge-traite">Traite</span>
                </div>
                <div class="courrier-card-meta">
                  <div><span class="meta-label">Date reception</span>{{ formaterDate(c.date_reception) }}</div>
                  <div><span class="meta-label">Date traitement</span>{{ formaterDate(c.date_traitement) }}</div>
                  <div><span class="meta-label">Traite par</span>{{ c.destinataire_nom }}</div>
                </div>
                <div class="courrier-card-actions">
                  <a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="font-size:13px;padding:6px 12px">Voir PDF</a>
                  <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="archiver(c)" :disabled="enEnvoi">Archiver</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ARCHIVES COURANTES -->
        <div v-if="page === 'archives_courantes'">
          <div class="carte">
            <div class="carte-titre">Fonds d archives courantes</div>
            <div v-if="archivesCourantes.length === 0" class="msg-vide">Aucune archive.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Numero</th><th>Objet</th><th>Expediteur</th><th>Date reception</th><th>Type</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="c in archivesCourantes" :key="c.id">
                    <td>{{ c.numero_officiel }}</td>
                    <td>{{ c.objet }}</td>
                    <td>{{ c.expediteur }}</td>
                    <td>{{ formaterDate(c.date_reception) }}</td>
                    <td>{{ c.type_courrier === 'ENT' ? 'Entrant' : 'Interne' }}</td>
                    <td><a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- MODULE 6 - VERSEMENT UNITAIRE -->
        <div v-if="page === 'versement_unitaire'">
          <div class="carte">
            <div class="carte-titre">Versement d un document historique</div>
            <p style="font-size:13px;color:#666;margin-bottom:20px">
              La reference systeme sera generee automatiquement au format ARC-XXX-AAAA-VNNNN.
              La reference d origine est conservee integralement.
            </p>

            <div class="grille-form">
              <div class="champ">
                <label class="champ-obligatoire">Fonds d archive</label>
                <select v-model="formArchive.fonds">
                  <option value="">-- Choisir le fonds --</option>
                  <option v-for="f in fondsDisponibles" :key="f.code" :value="f.code">{{ f.label }}</option>
                </select>
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Type de document</label>
                <select v-model="formArchive.type_document">
                  <option v-for="t in typesDocuments" :key="t.code" :value="t.code">{{ t.label }}</option>
                </select>
              </div>
              <div class="champ champ-large">
                <label class="champ-obligatoire">Intitule exact du document</label>
                <input v-model="formArchive.intitule" type="text" placeholder="Intitule exact tel qu il figure sur le document" />
              </div>
              <div class="champ">
                <label>Reference d origine</label>
                <input v-model="formArchive.reference_origine" type="text" placeholder="Reference figurant sur le document original" />
              </div>
              <div class="champ">
                <label class="champ-obligatoire">Date du document</label>
                <input v-model="formArchive.date_document" type="date" />
              </div>
              <div class="champ">
                <label>Expediteur</label>
                <input v-model="formArchive.expediteur" type="text" placeholder="Organisme ou personne emettrice" />
              </div>
              <div class="champ">
                <label>Categorie de classement</label>
                <input v-model="formArchive.categorie" type="text" placeholder="Ex: Personnel, Finances, Pedagogique..." />
              </div>
              <div class="champ">
                <label>Mots-cles</label>
                <input v-model="formArchive.mots_cles" type="text" placeholder="Mots-cles separes par des virgules" />
              </div>
              <div class="champ champ-large">
                <label>Resume</label>
                <textarea v-model="formArchive.resume" rows="3" placeholder="Resume du contenu du document pour faciliter la recherche"></textarea>
              </div>
              <div class="champ champ-large">
                <label class="champ-obligatoire">Document numerise (PDF, JPG, PNG — max 25 Mo)</label>
                <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="selectionnerFichierArchive" />
              </div>
            </div>

            <p v-if="erreurArchive" class="msg-erreur">{{ erreurArchive }}</p>
            <p v-if="msgSuccesArchive" class="msg-succes">{{ msgSuccesArchive }}</p>

            <div class="actions-form">
              <button class="btn btn-ghost" @click="reinitFormArchive">Effacer</button>
              <button class="btn btn-primary" @click="verserDocument" :disabled="enEnvoi">
                {{ enEnvoi ? 'Versement en cours...' : 'Verser le document' }}
              </button>
            </div>
          </div>
        </div>

        <!-- FONDS D ARCHIVES HISTORIQUES -->
        <div v-if="page === 'fonds_archives'">
          <div class="carte">
            <div class="carte-titre">Fonds d archives historiques</div>

            <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap">
              <input v-model="filtreArchive.q" type="text" placeholder="Intitule, expediteur, reference, mots-cles..." style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" @keyup.enter="chargerArchives" />
              <select v-model="filtreArchive.fonds" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                <option value="">Tous les fonds</option>
                <option v-for="f in fondsDisponibles" :key="f.code" :value="f.code">{{ f.label }}</option>
              </select>
              <button class="btn btn-primary" @click="chargerArchives">Filtrer</button>
            </div>

            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="archivesHisto.length === 0" class="msg-vide">Aucune archive trouvee.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr><th>Reference systeme</th><th>Ref. origine</th><th>Intitule</th><th>Fonds</th><th>Date</th><th>Type</th><th></th></tr>
                </thead>
                <tbody>
                  <tr v-for="a in archivesHisto" :key="a.id">
                    <td>{{ a.reference_systeme }}</td>
                    <td>{{ a.reference_origine || '-' }}</td>
                    <td>{{ a.intitule }}</td>
                    <td>{{ a.fonds }}</td>
                    <td>{{ formaterDate(a.date_document) }}</td>
                    <td>{{ a.type_document }}</td>
                    <td><a :href="a.fichier_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- MODULE 7 - RECHERCHE DOCUMENTAIRE -->
        <div v-if="page === 'recherche'">
          <div class="carte">
            <div class="carte-titre">Recherche documentaire</div>

            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ champ-large">
                <label>Recherche plein texte</label>
                <input v-model="recherche.q" type="text" placeholder="Objet, expediteur, numero, mots-cles..." @keyup.enter="lancerRecherche" />
              </div>
              <div class="champ">
                <label>Type de courrier</label>
                <select v-model="recherche.type">
                  <option value="">Tous</option>
                  <option value="ENT">Entrant</option>
                  <option value="INT">Interne</option>
                </select>
              </div>
              <div class="champ">
                <label>Priorite</label>
                <select v-model="recherche.priorite">
                  <option value="">Toutes</option>
                  <option value="HAUTE">Haute</option>
                  <option value="NORMALE">Normale</option>
                  <option value="BASSE">Basse</option>
                </select>
              </div>
              <div class="champ">
                <label>Date debut</label>
                <input v-model="recherche.date_debut" type="date" />
              </div>
              <div class="champ">
                <label>Date fin</label>
                <input v-model="recherche.date_fin" type="date" />
              </div>
              <div class="champ" style="display:flex;align-items:center;gap:8px;padding-top:20px">
                <input type="checkbox" v-model="recherche.avec_archives" id="avec_archives" style="accent-color:#1565C0;width:16px;height:16px" />
                <label for="avec_archives" style="cursor:pointer;font-size:14px">Inclure les archives historiques</label>
              </div>
            </div>

            <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px">
              <button class="btn btn-primary" @click="lancerRecherche" :disabled="rechercheEnCours">
                {{ rechercheEnCours ? 'Recherche...' : 'Lancer la recherche' }}
              </button>
              <button class="btn btn-ghost" @click="reinitRecherche">Reinitialiser</button>
            </div>

            <div v-if="rechercheEffectuee">
              <div v-if="resultats.courriers.length === 0 && resultats.archives.length === 0" class="msg-vide">
                Aucun resultat pour cette recherche.
              </div>

              <div v-if="resultats.courriers.length > 0">
                <div class="carte-titre" style="margin-bottom:12px">Courriers ({{ resultats.total_courriers }})</div>
                <div class="tableau-wrap">
                  <table class="tableau">
                    <thead><tr><th>Numero</th><th>Objet</th><th>Expediteur</th><th>Date</th><th>Statut</th><th></th></tr></thead>
                    <tbody>
                      <tr v-for="c in resultats.courriers" :key="c.id">
                        <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                        <td>{{ c.objet }}</td>
                        <td>{{ c.expediteur }}</td>
                        <td>{{ formaterDate(c.date_reception) }}</td>
                        <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                        <td><a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-if="resultats.archives.length > 0" style="margin-top:24px">
                <div class="carte-titre" style="margin-bottom:12px">Archives historiques ({{ resultats.total_archives }})</div>
                <div class="tableau-wrap">
                  <table class="tableau">
                    <thead><tr><th>Reference</th><th>Intitule</th><th>Fonds</th><th>Date</th><th></th></tr></thead>
                    <tbody>
                      <tr v-for="a in resultats.archives" :key="a.id">
                        <td>{{ a.reference_systeme }}</td>
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
          </div>
        </div>

        <!-- NOTIFICATIONS -->
        <div v-if="page === 'notifications'">
          <div class="carte">
            <div class="carte-titre">Notifications</div>
            <div v-if="notifications.length === 0" class="msg-vide">Aucune notification.</div>
            <div v-else>
              <div v-for="n in notifications" :key="n.id" :class="['notif-item', { 'non-lue': !n.lue }]">
                <div>{{ n.message }}</div>
                <div class="notif-item-heure">{{ formaterDateHeure(n.date) }}</div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

useInactivite()
const modules  = ref([])
const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')

const page          = ref('dashboard')
const chargement    = ref(false)
const enEnvoi       = ref(false)
const tousCourriers = ref([])
const notifications = ref([])
const notifsNonLues = ref(0)
const archivesHisto = ref([])
const totalArchivesHisto = ref(0)
const fondsDisponibles = ref([])
const typesDocuments   = ref([])

const rechercheEnCours  = ref(false)
const rechercheEffectuee = ref(false)
const resultats = ref({ courriers: [], archives: [], total_courriers: 0, total_archives: 0 })

const erreurArchive    = ref('')
const msgSuccesArchive = ref('')

const formArchive = ref({
  fonds: '', type_document: 'LETTRE', intitule: '', reference_origine: '',
  date_document: '', expediteur: '', categorie: '', mots_cles: '', resume: '', fichier: null,
})

const filtreArchive = ref({ q: '', fonds: '' })
const recherche = ref({ q: '', type: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false })

const titresPages = {
  dashboard:         'Tableau de bord',
  a_archiver:        'Courriers a archiver',
  archives_courantes: 'Archives courantes',
  versement_unitaire: 'Versement unitaire',
  fonds_archives:    'Fonds d archives historiques',
  recherche:         'Recherche documentaire',
  notifications:     'Notifications',
}

const aArchiver        = computed(() => tousCourriers.value.filter(c => c.statut === 'TRAITE'))
const archivesCourantes = computed(() => tousCourriers.value.filter(c => c.statut === 'ARCHIVE'))

const api = getApiClient()

async function chargerCourriers() {
  chargement.value = true
  try {
    const rep = await api.get('/courriers/')
    tousCourriers.value = rep.data
  } catch(e) { console.error(e) }
  finally { chargement.value = false }
}

async function chargerArchives() {
  chargement.value = true
  try {
    const params = {}
    if (filtreArchive.value.q)     params.q     = filtreArchive.value.q
    if (filtreArchive.value.fonds) params.fonds  = filtreArchive.value.fonds
    const rep = await api.get('/archives/', { params })
    archivesHisto.value      = rep.data
    totalArchivesHisto.value = rep.data.length
  } catch(e) { console.error(e) }
  finally { chargement.value = false }
}

async function chargerFonds() {
  try {
    const rep = await api.get('/archives/fonds/')
    fondsDisponibles.value = rep.data.fonds
    typesDocuments.value   = rep.data.types
  } catch(e) {}
}

async function chargerNotifications() {
  try {
    const rep = await api.get('/notifications/')
    notifications.value = rep.data.notifications || []
  } catch(e) {}
}

async function compterNotifications() {
  try {
    const rep = await api.get('/notifications/count/')
    notifsNonLues.value = rep.data.non_lues || 0
  } catch(e) {}
}

async function archiver(courrier) {
  enEnvoi.value = true
  try {
    await api.patch(`/courriers/${courrier.id}/archiver/`)
    chargerCourriers()
  } catch(e) { console.error(e) }
  finally { enEnvoi.value = false }
}

function selectionnerFichierArchive(event) {
  const f = event.target.files[0]
  if (f && f.size > 25 * 1024 * 1024) {
    erreurArchive.value = 'Le fichier depasse 25 Mo.'
    return
  }
  formArchive.value.fichier = f
}

async function verserDocument() {
  erreurArchive.value    = ''
  msgSuccesArchive.value = ''

  if (!formArchive.value.fonds || !formArchive.value.intitule ||
      !formArchive.value.date_document || !formArchive.value.fichier) {
    erreurArchive.value = 'Les champs obligatoires (*) doivent etre remplis.'
    return
  }

  enEnvoi.value = true
  const donnees = new FormData()
  Object.entries(formArchive.value).forEach(([k, v]) => {
    if (k === 'fichier' && v) donnees.append('fichier', v)
    else if (k !== 'fichier' && v) donnees.append(k, v)
  })

  try {
    const rep = await api.post('/archives/', donnees, { headers: { 'Content-Type': 'multipart/form-data' } })
    msgSuccesArchive.value = `Document verse avec succes. Reference systeme : ${rep.data.reference_systeme}`
    reinitFormArchive()
    totalArchivesHisto.value++
  } catch(e) {
    erreurArchive.value = 'Erreur lors du versement. Verifiez les donnees.'
  } finally {
    enEnvoi.value = false
  }
}

function reinitFormArchive() {
  formArchive.value = {
    fonds: '', type_document: 'LETTRE', intitule: '', reference_origine: '',
    date_document: '', expediteur: '', categorie: '', mots_cles: '', resume: '', fichier: null,
  }
}

async function lancerRecherche() {
  rechercheEnCours.value = true
  rechercheEffectuee.value = true
  try {
    const params = {}
    if (recherche.value.q)           params.q             = recherche.value.q
    if (recherche.value.type)        params.type           = recherche.value.type
    if (recherche.value.priorite)    params.priorite       = recherche.value.priorite
    if (recherche.value.date_debut)  params.date_debut     = recherche.value.date_debut
    if (recherche.value.date_fin)    params.date_fin       = recherche.value.date_fin
    if (recherche.value.avec_archives) params.avec_archives = 'true'
    const rep = await api.get('/recherche/', { params })
    resultats.value = rep.data
  } catch(e) { console.error(e) }
  finally { rechercheEnCours.value = false }
}

function reinitRecherche() {
  recherche.value = { q: '', type: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false }
  rechercheEffectuee.value = false
  resultats.value = { courriers: [], archives: [], total_courriers: 0, total_archives: 0 }
}

function formaterDate(d) { return d ? new Date(d).toLocaleDateString('fr-FR') : '' }
function formaterDateHeure(d) { return d ? new Date(d).toLocaleString('fr-FR') : '' }
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
  chargerFonds()
  chargerArchives()
  compterNotifications()
  intervalle = setInterval(compterNotifications, 30000)

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
