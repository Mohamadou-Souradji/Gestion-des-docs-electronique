<template>
  <div class="app-layout">

    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>
      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">{{ entite }}</div>
      </div>
     <nav class="sidebar-nav">

  <button :class="['nav-item', { actif: page === 'dashboard' }]" @click="page = 'dashboard'">
    <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
    Tableau de bord
  </button>

  <div class="nav-section-titre">Mes courriers</div>

  <button :class="['nav-sous-item', { actif: page === 'a_traiter' }]" @click="page = 'a_traiter'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-envelope-open-text"></i></span>
    A traiter
    <span v-if="aTraiter.length > 0" class="nav-badge">{{ aTraiter.length }}</span>
  </button>

  <button :class="['nav-sous-item', { actif: page === 'en_cours' }]" @click="page = 'en_cours'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-spinner"></i></span>
    En cours
  </button>

  <button :class="['nav-sous-item', { actif: page === 'traites' }]" @click="page = 'traites'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-circle-check"></i></span>
    Traites
  </button>

  <button :class="['nav-sous-item', { actif: page === 'copies' }]" @click="page = 'copies'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-copy"></i></span>
    En copie
  </button>

  <div v-if="modules.includes('recherche')" class="nav-section-titre">Modules extra</div>
  <button v-if="modules.includes('recherche')" :class="['nav-sous-item', { actif: page === 'recherche_extra' }]" @click="page = 'recherche_extra'">
    <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
    Recherche
  </button>
  <button v-if="modules.includes('archives')" :class="['nav-sous-item', { actif: page === 'archives_extra' }]" @click="page = 'archives_extra'; chargerArchivesExtra()">
    <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
    Archives
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
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle;"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" /></svg>
            <span v-if="notifsNonLues > 0" class="notif-dot"></span>
          </button>
        </div>
      </header>

      <main class="page-contenu">

        <div v-if="page === 'dashboard'">
          <div class="stats-grille">
            <div class="stat-card">
              <div class="stat-icone jaune">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 21H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v7" /><line x1="16" y1="19" x2="22" y2="19" /><polyline points="19 16 22 19 19 22" /></svg>
              </div>
              <div><div class="stat-valeur">{{ aTraiter.length }}</div><div class="stat-label">À traiter</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone bleu">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </div>
              <div><div class="stat-valeur">{{ enCours.length }}</div><div class="stat-label">En cours</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone vert">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              </div>
              <div><div class="stat-valeur">{{ dejaTraites.length }}</div><div class="stat-label">Traités</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone rouge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
              </div>
              <div><div class="stat-valeur">{{ enCopie.length }}</div><div class="stat-label">En copie</div></div>
            </div>
          </div>

          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 13V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h9"></path><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path></svg>
              Courriers récents
            </div>
            <div v-if="tousCourriers.length === 0" class="msg-vide">Aucun courrier pour l'instant.</div>
            <div v-else>
              <div v-for="c in tousCourriers.slice(0,4)" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }} — {{ c.expediteur }}</div>
                  </div>
                  <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
                </div>
                <div class="courrier-card-actions">
                  <button class="btn btn-outline" style="font-size:13px;padding:6px 12px; display: inline-flex; align-items: center; gap: 6px;" @click="ouvrirCourrier(c)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    Consulter
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="page === 'a_traiter'">
          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 21H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v7" /><path d="M2 7h20" /></svg>
              Courriers à traiter
            </div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="aTraiter.length === 0" class="msg-vide">Aucun courrier en attente.</div>
            <div v-else>
              <div v-for="c in aTraiter" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }} — {{ c.expediteur }}</div>
                  </div>
                  <span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span>
                </div>
                <div class="courrier-card-meta">
                  <div><span class="meta-label">Date réception</span>{{ formaterDate(c.date_reception) }}</div>
                  <div><span class="meta-label">Date imputation</span>{{ formaterDate(c.date_imputation) }}</div>
                  <div><span class="meta-label">Instructions DG</span>{{ c.instructions_dg }}</div>
                </div>
                <div class="courrier-card-actions">
                  <a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="font-size:13px;padding:6px 12px; display: inline-flex; align-items: center; gap: 6px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    PDF
                  </a>
                  <button class="btn btn-primary" style="font-size:13px;padding:6px 14px; display: inline-flex; align-items: center; gap: 6px;" @click="ouvrirCourrier(c)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    Consulter et traiter
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="page === 'en_cours'">
          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              Courriers en cours de traitement
            </div>
            <div v-if="enCours.length === 0" class="msg-vide">Aucun courrier en cours.</div>
            <div v-else>
              <div v-for="c in enCours" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }}</div>
                  </div>
                  <span class="badge badge-en_cours">En cours</span>
                </div>
                <div class="courrier-card-meta">
                  <div><span class="meta-label">Instructions</span>{{ c.instructions_dg }}</div>
                </div>
                <div class="courrier-card-actions">
                  <button class="btn btn-success" style="font-size:13px;padding:6px 14px; display: inline-flex; align-items: center; gap: 6px;" @click="ouvrirTraitement(c)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    Marquer comme traité
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="page === 'traites'">
          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Courriers traités
            </div>
            <div v-if="dejaTraites.length === 0" class="msg-vide">Aucun courrier traité.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Numéro</th><th>Objet</th><th>Date traitement</th><th>Statut</th></tr></thead>
                <tbody>
                  <tr v-for="c in dejaTraites" :key="c.id">
                    <td>{{ c.numero_officiel }}</td>
                    <td>{{ c.objet }}</td>
                    <td>{{ formaterDate(c.date_traitement) }}</td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="page === 'copies'">
          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
              Courriers en copie
            </div>
            <p style="font-size:13px;color:#666;margin-bottom:16px">Ces courriers ne nécessitent pas de marquage comme traité.</p>
            <div v-if="enCopie.length === 0" class="msg-vide">Aucun courrier en copie.</div>
            <div v-else>
              <div v-for="c in enCopie" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.numero_officiel }} — {{ c.expediteur }}</div>
                  </div>
                  <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
                </div>
                <div class="courrier-card-actions">
                  <a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="font-size:13px;padding:6px 12px; display: inline-flex; align-items: center; gap: 6px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    PDF
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="page === 'notifications'">
          <div class="carte">
            <div class="carte-titre" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /></svg>
              Mes notifications
            </div>
            <div v-if="notifications.length === 0" class="msg-vide">Aucune notification.</div>
            <div v-else>
              <div v-for="n in notifications" :key="n.id" :class="['notif-item', { 'non-lue': !n.lue }]">
                <div>{{ n.message }}</div>
                <div class="notif-item-heure">{{ formaterDateHeure(n.date) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ARCHIVES (module extra) -->
        <div v-if="page === 'archives_extra'">
          <div class="carte">
            <div class="carte-titre">Consultation des archives historiques</div>
            <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
              <input v-model="filtreArchives.q" type="text" placeholder="Référence, intitulé..."
                style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px"
                @keyup.enter="chargerArchivesExtra" />
              <button class="btn btn-primary" @click="chargerArchivesExtra">Filtrer</button>
            </div>
            <div v-if="chargementArchives" class="msg-vide">Chargement...</div>
            <div v-else-if="archivesExtra.length === 0" class="msg-vide">Aucune archive trouvée.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Référence</th><th>Intitulé</th><th>Fonds</th><th>Date</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="a in archivesExtra" :key="a.id">
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

      </main>
    </div>

    <div v-if="courrierOuvert" class="modal-fond">
      <div class="modal" style="max-width:600px">
        <div class="modal-titre" style="display: flex; align-items: center; gap: 8px;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
          {{ courrierOuvert.objet }}
        </div>
        <div class="courrier-card-meta" style="margin-bottom:16px">
          <div><span class="meta-label">Numéro</span>{{ courrierOuvert.numero_officiel }}</div>
          <div><span class="meta-label">Expéditeur</span>{{ courrierOuvert.expediteur }}</div>
          <div><span class="meta-label">Date réception</span>{{ formaterDate(courrierOuvert.date_reception) }}</div>
          <div><span class="meta-label">Priorité</span><span :class="'priorite-' + courrierOuvert.priorite.toLowerCase()">{{ courrierOuvert.priorite }}</span></div>
        </div>
        <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:16px;font-size:13px">
          <strong style="color:#1565C0">Instructions du DG :</strong><br/>{{ courrierOuvert.instructions_dg }}
        </div>
        <div class="actions-form" style="margin-bottom:16px">
          <a :href="courrierOuvert.fichier_pdf_url" target="_blank" class="btn btn-outline" style="display: inline-flex; align-items: center; gap: 6px;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Ouvrir le PDF
          </a>
        </div>

        <div v-if="courrierOuvert.statut !== 'TRAITE' && courrierOuvert.copies !== undefined">
          <div class="champ" style="margin-bottom:12px">
            <label>Compte-rendu de traitement (facultatif)</label>
            <textarea v-model="reponseTraitement" rows="3" placeholder="Décrivez les actions entreprises..."></textarea>
          </div>
          <p v-if="erreurTraitement" class="msg-erreur">{{ erreurTraitement }}</p>
        </div>

        <div class="actions-form">
          <button class="btn btn-ghost" @click="courrierOuvert = null">Fermer</button>
          <button v-if="peutTraiter" class="btn btn-success" style="display: inline-flex; align-items: center; gap: 6px;" @click="traiter" :disabled="enEnvoi">
            <svg v-if="!enEnvoi" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            {{ enEnvoi ? 'Traitement...' : 'Marquer comme traité' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="courrierATraiter" class="modal-fond">
      <div class="modal">
        <div class="modal-titre" style="display: flex; align-items: center; gap: 8px;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          Marquer comme traité
        </div>
        <p style="font-size:14px;margin-bottom:12px">Courrier : <strong>{{ courrierATraiter.objet }}</strong></p>
        <div class="champ">
          <label>Compte-rendu (facultatif)</label>
          <textarea v-model="reponseTraitement" rows="3" placeholder="Décrivez les actions entreprises..."></textarea>
        </div>
        <p v-if="erreurTraitement" class="msg-erreur">{{ erreurTraitement }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="courrierATraiter = null">Annuler</button>
          <button class="btn btn-success" style="display: inline-flex; align-items: center; gap: 6px;" @click="confirmerTraitement" :disabled="enEnvoi">
            <svg v-if="!enEnvoi" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            {{ enEnvoi ? 'Traitement...' : 'Confirmer' }}
          </button>
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
const entite  = ref(payload.entite || 'Destinataire')

const page           = ref('dashboard')
const chargement     = ref(false)
const enEnvoi        = ref(false)
const tousCourriers  = ref([])
const notifications  = ref([])
const notifsNonLues  = ref(0)
const courrierOuvert = ref(null)
const courrierATraiter = ref(null)
const reponseTraitement = ref('')
const erreurTraitement  = ref('')

const titresPages = {
  dashboard:     'Tableau de bord',
  a_traiter:     'Courriers à traiter',
  en_cours:      'En cours de traitement',
  traites:       'Courriers traités',
  copies:        'Courriers en copie',
  notifications: 'Notifications',
}

const aTraiter    = computed(() => tousCourriers.value.filter(c => c.statut === 'IMPUTE' && c.copies !== undefined))
const enCours     = computed(() => tousCourriers.value.filter(c => c.statut === 'EN_COURS' && c.copies !== undefined))
const dejaTraites = computed(() => tousCourriers.value.filter(c => ['TRAITE','ARCHIVE'].includes(c.statut) && c.copies !== undefined))
const enCopie    = computed(() => tousCourriers.value.filter(c => c.copies === undefined || (c.destinataire && c.destinataire !== parseInt(payload.user_id))))
const peutTraiter = computed(() => courrierOuvert.value && !['TRAITE','ARCHIVE'].includes(courrierOuvert.value.statut))

const api = getApiClient()

async function chargerCourriers() {
  chargement.value = true
  try {
    const rep = await api.get('/courriers/')
    tousCourriers.value = rep.data
  } catch(e) { console.error(e) }
  finally { chargement.value = false }
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

async function ouvrirCourrier(courrier) {
  courrierOuvert.value   = courrier
  reponseTraitement.value = ''
  erreurTraitement.value  = ''
  if (courrier.statut === 'IMPUTE') {
    try { await api.patch(`/courriers/${courrier.id}/marquer-lu/`) } catch(e) {}
    chargerCourriers()
  }
}

function ouvrirTraitement(courrier) {
  courrierATraiter.value  = courrier
  reponseTraitement.value = ''
  erreurTraitement.value  = ''
}

async function traiter() {
  enEnvoi.value = true
  erreurTraitement.value = ''
  try {
    await api.patch(`/courriers/${courrierOuvert.value.id}/marquer-traite/`, { reponse: reponseTraitement.value })
    courrierOuvert.value = null
    chargerCourriers()
  } catch(e) {
    erreurTraitement.value = 'Erreur lors du traitement.'
  } finally { enEnvoi.value = false }
}

async function confirmerTraitement() {
  enEnvoi.value = true
  erreurTraitement.value = ''
  try {
    await api.patch(`/courriers/${courrierATraiter.value.id}/marquer-traite/`, { reponse: reponseTraitement.value })
    courrierATraiter.value = null
    chargerCourriers()
  } catch(e) {
    erreurTraitement.value = 'Erreur lors du traitement.'
  } finally { enEnvoi.value = false }
}


const rechercheEnCours   = ref(false)
const rechercheEffectuee = ref(false)
const resultatsRecherche = ref([])
const recherche = ref({ q: '', type: '', date_debut: '', date_fin: '' })

async function lancerRecherche() {
  rechercheEnCours.value   = true
  rechercheEffectuee.value = true
  try {
    const params = {}
    Object.entries(recherche.value).forEach(([k, v]) => { if (v) params[k] = v })
    const rep = await api.get('/recherche/', { params })
    resultatsRecherche.value = rep.data.courriers || []
  } catch(e) { console.error(e) }
  finally { rechercheEnCours.value = false }
}

function reinitRecherche() {
  recherche.value          = { q: '', type: '', date_debut: '', date_fin: '' }
  rechercheEffectuee.value = false
  resultatsRecherche.value = []
}


const chargementArchives = ref(false)
const archivesExtra      = ref([])
const filtreArchives     = ref({ q: "", fonds: "" })

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