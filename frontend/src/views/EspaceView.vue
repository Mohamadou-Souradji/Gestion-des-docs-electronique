<template>
  <div class="app-layout">

    <SidebarNav
      :modules="modules"
      :profil="profil"
      :nom="nom"
      :prenom="prenom"
      :page-courante="page"
      :badges="badges"
      :logo-url="logoUrl"
      @naviguer="allerA"
      @deconnecter="seDeconnecter"
    />

    <div class="main-zone">
      <TopBar :titre="titrePage" :notifs-non-lues="badges.notifications" @notifications="allerA('notifications')" />

      <main class="page-contenu">

        <!-- TABLEAU DE BORD -->
        <div v-if="page === 'dashboard'">
          <div class="stats-grille">
            <div class="stat-card">
              <div class="stat-icone bleu"><i class="fa-solid fa-envelope"></i></div>
              <div><div class="stat-valeur">{{ courriers.length }}</div><div class="stat-label">Total courriers</div></div>
            </div>
            <div class="stat-card" v-if="hasModule('verification')">
              <div class="stat-icone jaune"><i class="fa-solid fa-hourglass-half"></i></div>
              <div><div class="stat-valeur">{{ badges.verification }}</div><div class="stat-label">À vérifier</div></div>
            </div>
            <div class="stat-card" v-if="hasModule('imputation')">
              <div class="stat-icone jaune"><i class="fa-solid fa-paper-plane"></i></div>
              <div><div class="stat-valeur">{{ badges.imputation }}</div><div class="stat-label">À imputer</div></div>
            </div>
            <div class="stat-card" v-if="hasModule('traitement')">
              <div class="stat-icone jaune"><i class="fa-solid fa-inbox"></i></div>
              <div><div class="stat-valeur">{{ badges.traitement }}</div><div class="stat-label">À traiter</div></div>
            </div>
            <div class="stat-card" v-if="hasModule('archivage')">
              <div class="stat-icone jaune"><i class="fa-solid fa-download"></i></div>
              <div><div class="stat-valeur">{{ badges.archivage }}</div><div class="stat-label">À archiver</div></div>
            </div>
          </div>

          <div class="carte">
            <div class="carte-titre">Derniers courriers</div>
            <div v-if="courriers.length === 0" class="msg-vide">Aucun courrier pour l'instant.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Référence</th><th>Objet</th><th>Expéditeur</th><th>Statut</th></tr></thead>
                <tbody>
                  <tr v-for="c in courriers.slice(0, 6)" :key="c.id">
                    <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                    <td>{{ c.objet }}</td>
                    <td>{{ c.expediteur }}</td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- MODULE COURRIERS : Saisie -->
        <SaisieCourrier v-if="page === 'saisie_courrier'" @soumis="chargerCourriers" />

        <!-- MODULE COURRIERS : Liste (BO) -->
        <ListeCourriers v-if="page === 'liste_courriers'" :courriers="courriers" :chargement="chargementCourriers" titre="Mes courriers" />

        <!-- MODULE COURRIERS : Vérification (Assistant) -->
        <VerificationCourrier v-if="page === 'verification' || page === 'courriers_traites'"
          :courriers="courriers" :chargement="chargementCourriers" :page-active="page" @rafraichir="chargerCourriers" />
        <!-- MODULE COURRIERS : Imputation (DG) -->
        <ImputationCourrier v-if="page === 'imputation' || page === 'suivi_imputation'"
          :key="page"
          :courriers="courriers" :chargement="chargementCourriers"
          :onglet-initial="page === 'suivi_imputation' ? 'suivi' : 'imputer'"
          @rafraichir="chargerCourriers" />
        <!-- MODULE COURRIERS : Validation SGA -->
   <ValidationSGA v-if="page === 'validation_sga' || page === 'historique_sga'"
  :key="page"
  :courriers="courriers" :chargement="chargementCourriers"
  :onglet-initial="page === 'historique_sga' ? 'historique' : 'attente'"
  @rafraichir="chargerCourriers" />

<ValidationSG v-if="page === 'validation_sg' || page === 'historique_sg'"
  :key="page"
  :courriers="courriers" :chargement="chargementCourriers"
  :onglet-initial="page === 'historique_sg' ? 'historique' : 'attente'"
  @rafraichir="chargerCourriers" />
        <!-- MODULE COURRIERS : Liste (DG) -->
        <ListeCourriers v-if="page === 'tous_courriers'" :courriers="courriers" :chargement="chargementCourriers"
          titre="Tous les courriers" afficher-destinataire />

      <!-- MODULE COURRIERS : Traitement (Destinataire) -->
<TraitementCourrier v-if="['a_traiter','en_cours','traites','en_copie'].includes(page)"
  :courriers="courriers" :chargement="chargementCourriers" :page-active="page" @rafraichir="chargerCourriers" />
      <!-- MODULE ARCHIVAGE COURANT -->
        <ArchivageCourant v-if="page === 'a_archiver' || page === 'archives_courantes'"
          :courriers="courriers" :chargement="chargementCourriers" :page-active="page" @rafraichir="chargerCourriers" />
        <!-- MODULE ARCHIVES HISTORIQUES -->
        <VersementArchive v-if="page === 'versement_unitaire'" />
        <FondsArchives     v-if="page === 'fonds_archives'" />

        <!-- MODULE RECHERCHE -->
        <RechercheDocumentaire v-if="page === 'recherche'" />

        <!-- MODULE STATISTIQUES -->
        <PanneauStatistiques v-if="page === 'statistiques'" />

        <!-- MODULE DÉLÉGATIONS -->
        <GestionDelegations v-if="page === 'delegations'" />

        <!-- MODULE AUDIT -->
        <JournalAudit v-if="page === 'audit'" />

        <!-- NOTIFICATIONS -->
        <ListeNotifications v-if="page === 'notifications'" :notifications="notifications" :chargement="chargementNotifs" />

      </main>

      <PiedPage />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

import SidebarNav from '../layout/SidebarNav.vue'
import TopBar     from '../layout/TopBar.vue'
import PiedPage   from '../layout/PiedPage.vue'

import SaisieCourrier      from '../modules/courriers/SaisieCourrier.vue'
import ListeCourriers      from '../modules/courriers/ListeCourriers.vue'
import VerificationCourrier from '../modules/courriers/VerificationCourrier.vue'
import ImputationCourrier  from '../modules/courriers/ImputationCourrier.vue'
import TraitementCourrier  from '../modules/courriers/TraitementCourrier.vue'

import ArchivageCourant  from '../modules/archives/ArchivageCourant.vue'
import VersementArchive  from '../modules/archives/VersementArchive.vue'
import FondsArchives     from '../modules/archives/FondsArchives.vue'

import RechercheDocumentaire from '../modules/recherche/RechercheDocumentaire.vue'
import PanneauStatistiques   from '../modules/statistiques/PanneauStatistiques.vue'
import GestionDelegations    from '../modules/delegations/GestionDelegations.vue'
import JournalAudit          from '../modules/audit/JournalAudit.vue'
import ListeNotifications    from '../modules/notifications/ListeNotifications.vue'

import { useModules, hasModule as hasModuleFn } from '../composables/useModules'
import { useParametres } from '../composables/useParametres'
import { useInactivite }  from '../composables/useInactivite'
import { courriersApi, notificationsApi } from '../services/api'
import ValidationSGA from '../modules/courriers/ValidationSGA.vue'
import ValidationSG  from '../modules/courriers/ValidationSG.vue'

useInactivite()

const router = useRouter()

const modules  = ref([])
const profil   = ref('')
const nom      = ref('')
const prenom   = ref('')
const logoUrl  = ref(null)

const page                 = ref('dashboard')
const courriers             = ref([])
const chargementCourriers   = ref(false)
const notifications         = ref([])
const chargementNotifs      = ref(false)

const badges = reactive({
  verification: 0, imputation: 0, traitement: 0, archivage: 0, notifications: 0, sga: 0, sg: 0, suivi: 0
})

const titresPages = {
  dashboard: 'Tableau de bord',
  saisie_courrier: 'Nouveau courrier',
  liste_courriers: 'Mes courriers',
  verification: 'Courriers à vérifier',
  courriers_traites: 'Courriers traités',
  imputation: 'Courriers à imputer',
  tous_courriers: 'Tous les courriers',
  a_traiter: 'Mes courriers',
  en_cours: 'Mes courriers',
  traites: 'Mes courriers',
  en_copie: 'Mes courriers',
  a_archiver: 'Archivage',
  archives_courantes: 'Archivage',
  versement_unitaire: 'Versement unitaire',
  fonds_archives: "Fonds d'archives",
  recherche: 'Recherche documentaire',
  statistiques: 'Statistiques',
  delegations: 'Délégations',
  audit: "Journal d'audit",
  notifications: 'Notifications',
  validation_sga: 'Validation SGA',
  validation_sg:  'Validation SG',
  historique_sga: 'Historique SGA',
  historique_sg:  'Historique SG',
  suivi_imputation: 'Suivi des courriers',
}

const titrePage = computed(() => titresPages[page.value] || '')

function hasModule(code) {
  return modules.value.includes(code)
}

function allerA(nomPage) {
  page.value = nomPage
  const pagesAvecTout = ['tous_courriers', 'suivi_imputation', 'historique_sga', 'historique_sg', 'verification', 'a_archiver', 'archives_courantes']
  const limite = pagesAvecTout.includes(nomPage) ? 100 : 20
  if (['saisie_courrier','liste_courriers','verification','imputation','suivi_imputation',
       'tous_courriers','a_traiter','en_cours','traites','en_copie','a_archiver',
       'archives_courantes','validation_sga','historique_sga','validation_sg','historique_sg'].includes(nomPage)) {
    chargerCourriers(limite)
  }
  if (nomPage === 'notifications') chargerNotifications()
}

async function chargerCourriers(limite = 20) {
  chargementCourriers.value = true
  try {
    courriers.value = (await courriersApi.liste()).data
    calculerBadges()
  } catch(e) { console.error(e) }
  finally { chargementCourriers.value = false }
}

async function chargerNotifications() {
  chargementNotifs.value = true
  try {
    const response = await notificationsApi.liste()
    console.log('API Response:', response)  // AJOUTE CETTE LIGNE
    console.log('Notifications:', response.data)  // ET CETTE LIGNE
    notifications.value = response.data.notifications || []
  } catch(e) { console.error(e) }
  finally { chargementNotifs.value = false }
}

async function compterNotifications() {
  try {
    badges.notifications = (await notificationsApi.compter()).data.non_lues || 0
  } catch(e) {}
}

function calculerBadges() {
  badges.verification = courriers.value.filter(c => c.statut === 'EN_VERIF').length
  badges.imputation   = courriers.value.filter(c => c.statut === 'EN_ATT_IMP').length
  badges.traitement   = courriers.value.filter(c => c.statut === 'IMPUTE' && c.copies !== undefined).length
  badges.archivage    = courriers.value.filter(c => c.statut === 'TRAITE').length
  badges.sga = courriers.value.filter(c => c.statut === 'EN_ATT_SGA').length
  badges.sg  = courriers.value.filter(c => c.statut === 'EN_ATT_SG').length
}

function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/')
}

let intervalle
onMounted(async () => {
  const infos   = await useModules()
  modules.value = infos.modules
  profil.value  = infos.profil
  nom.value     = infos.nom
  prenom.value  = infos.prenom

  const params = await useParametres()
  if (params.logo_url) logoUrl.value = params.logo_url

  chargerCourriers()
  compterNotifications()
  intervalle = setInterval(compterNotifications, 30000)
})
onUnmounted(() => clearInterval(intervalle))
</script>

 <style></style>