<template>
  <aside class="sidebar">
    <!-- Logo dynamique de l'organisation -->
    <div class="sidebar-logo">
      <img v-if="logoUrl" :src="logoUrl" alt="Logo" style="max-height:70px;max-width:160px;object-fit:contain" />
      <div v-else class="sidebar-logo-placeholder">
        <i class="fa-solid fa-building"></i>
      </div>
    </div>

    <!-- Profil -->
    <div class="sidebar-profil">
      <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
      <div class="sidebar-profil-role">{{ labelProfil }}</div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">

      <button :class="['nav-item', { actif: pageCourante === 'dashboard' }]" @click="naviguer('dashboard')">
        <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
        Tableau de bord
      </button>

      <template v-if="hasCourriersModule">
        <div class="nav-section-titre">Courriers</div>

        <button v-if="peutSaisir" :class="['nav-sous-item', { actif: pageCourante === 'saisie_courrier' }]"
          @click="naviguer('saisie_courrier')">
          <span class="nav-item-icone"><i class="fa-solid fa-plus"></i></span>
          Nouveau courrier
        </button>

        <button v-if="peutSaisir" :class="['nav-sous-item', { actif: pageCourante === 'liste_courriers' }]"
          @click="naviguer('liste_courriers')">
          <span class="nav-item-icone"><i class="fa-solid fa-list"></i></span>
          Mes courriers
        </button>

        <button v-if="hasModule('verification')"
          :class="['nav-sous-item', { actif: pageCourante === 'verification' }]"
          @click="naviguer('verification')">
          <span class="nav-item-icone"><i class="fa-solid fa-circle-check"></i></span>
          À vérifier
          <span v-if="badges.verification > 0" class="nav-badge">{{ badges.verification }}</span>
        </button>
<button v-if="hasModule('validation_sga')"
  :class="['nav-sous-item', { actif: pageCourante === 'validation_sga' }]"
  @click="naviguer('validation_sga')">
  <span class="nav-item-icone"><i class="fa-solid fa-user-check"></i></span>
  À valider
  <span v-if="badges.sga > 0" class="nav-badge">{{ badges.sga }}</span>
</button>
<button v-if="hasModule('validation_sga')"
  :class="['nav-sous-item', { actif: pageCourante === 'historique_sga' }]"
  @click="naviguer('historique_sga')">
  <span class="nav-item-icone"><i class="fa-solid fa-clock-rotate-left"></i></span>
  Historique SGA
</button>

<button v-if="hasModule('validation_sg')"
  :class="['nav-sous-item', { actif: pageCourante === 'validation_sg' }]"
  @click="naviguer('validation_sg')">
  <span class="nav-item-icone"><i class="fa-solid fa-user-tie"></i></span>
  À valider
  <span v-if="badges.sg > 0" class="nav-badge">{{ badges.sg }}</span>
</button>
<button v-if="hasModule('validation_sg')"
  :class="['nav-sous-item', { actif: pageCourante === 'historique_sg' }]"
  @click="naviguer('historique_sg')">
  <span class="nav-item-icone"><i class="fa-solid fa-clock-rotate-left"></i></span>
  Historique SG
</button>

        <button v-if="hasModule('imputation')"
          :class="['nav-sous-item', { actif: pageCourante === 'imputation' }]"
          @click="naviguer('imputation')">
          <span class="nav-item-icone"><i class="fa-solid fa-paper-plane"></i></span>
          À imputer
          <span v-if="badges.imputation > 0" class="nav-badge">{{ badges.imputation }}</span>
        </button>
        <button v-if="hasModule('imputation')"
          :class="['nav-sous-item', { actif: pageCourante === 'suivi_imputation' }]"
          @click="naviguer('suivi_imputation')">
          <span class="nav-item-icone"><i class="fa-solid fa-eye"></i></span>
          Suivi
          <span v-if="badges.suivi > 0" class="nav-badge">{{ badges.suivi }}</span>
        </button>
        <button v-if="hasModule('imputation')"
          :class="['nav-sous-item', { actif: pageCourante === 'tous_courriers' }]"
          @click="naviguer('tous_courriers')">
          <span class="nav-item-icone"><i class="fa-solid fa-envelope"></i></span>
          Tous les courriers
        </button>

        <button v-if="hasModule('traitement')"
          :class="['nav-sous-item', { actif: pageCourante === 'a_traiter' }]"
          @click="naviguer('a_traiter')">
          <span class="nav-item-icone"><i class="fa-solid fa-inbox"></i></span>
          À traiter
          <span v-if="badges.traitement > 0" class="nav-badge">{{ badges.traitement }}</span>
        </button>
        <button v-if="hasModule('traitement')"
          :class="['nav-sous-item', { actif: pageCourante === 'en_cours' }]"
          @click="naviguer('en_cours')">
          <span class="nav-item-icone"><i class="fa-solid fa-spinner"></i></span>
          En cours
        </button>
        <button v-if="hasModule('traitement')"
          :class="['nav-sous-item', { actif: pageCourante === 'traites' }]"
          @click="naviguer('traites')">
          <span class="nav-item-icone"><i class="fa-solid fa-circle-check"></i></span>
          Traités
        </button>
        <button v-if="hasModule('traitement')"
          :class="['nav-sous-item', { actif: pageCourante === 'en_copie' }]"
          @click="naviguer('en_copie')">
          <span class="nav-item-icone"><i class="fa-solid fa-copy"></i></span>
          En copie
        </button>

        <button v-if="hasModule('archivage')"
          :class="['nav-sous-item', { actif: pageCourante === 'a_archiver' }]"
          @click="naviguer('a_archiver')">
          <span class="nav-item-icone"><i class="fa-solid fa-download"></i></span>
          À archiver
          <span v-if="badges.archivage > 0" class="nav-badge">{{ badges.archivage }}</span>
        </button>
        <button v-if="hasModule('archivage')"
          :class="['nav-sous-item', { actif: pageCourante === 'archives_courantes' }]"
          @click="naviguer('archives_courantes')">
          <span class="nav-item-icone"><i class="fa-solid fa-box-archive"></i></span>
          Archives courantes
        </button>
      </template>

      <template v-if="hasModule('archives')">
        <div class="nav-section-titre">Archives historiques</div>
        <button :class="['nav-sous-item', { actif: pageCourante === 'versement_unitaire' }]"
          @click="naviguer('versement_unitaire')">
          <span class="nav-item-icone"><i class="fa-solid fa-file-arrow-up"></i></span>
          Versement unitaire
        </button>
        <button :class="['nav-sous-item', { actif: pageCourante === 'fonds_archives' }]"
          @click="naviguer('fonds_archives')">
          <span class="nav-item-icone"><i class="fa-solid fa-folder-open"></i></span>
          Fonds d'archives
        </button>
      </template>

      <template v-if="hasModule('recherche')">
        <div class="nav-section-titre">Recherche</div>
        <button :class="['nav-sous-item', { actif: pageCourante === 'recherche' }]"
          @click="naviguer('recherche')">
          <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
          Recherche documentaire
        </button>
      </template>

      <template v-if="hasModule('statistiques')">
        <div class="nav-section-titre">Analyse</div>
        <button :class="['nav-sous-item', { actif: pageCourante === 'statistiques' }]"
          @click="naviguer('statistiques')">
          <span class="nav-item-icone"><i class="fa-solid fa-chart-bar"></i></span>
          Statistiques
        </button>
      </template>

      <template v-if="hasModule('audit')">
        <div class="nav-section-titre">Système</div>
        <button :class="['nav-sous-item', { actif: pageCourante === 'audit' }]"
          @click="naviguer('audit')">
          <span class="nav-item-icone"><i class="fa-solid fa-shield-halved"></i></span>
          Journal d'audit
        </button>
      </template>

      <button :class="['nav-item', { actif: pageCourante === 'notifications' }]"
        @click="naviguer('notifications')" style="margin-top:8px">
        <span class="nav-item-icone"><i class="fa-solid fa-bell"></i></span>
        Notifications
        <span v-if="badges.notifications > 0" class="nav-badge">{{ badges.notifications }}</span>
      </button>

    </nav>

    <div class="sidebar-bas">
      <button class="nav-item" @click="$emit('deconnecter')">
        <span class="nav-item-icone"><i class="fa-solid fa-right-from-bracket"></i></span>
        Déconnexion
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modules:      { type: Array,   default: () => [] },
  profil:       { type: String,  default: '' },
  nom:          { type: String,  default: '' },
  prenom:       { type: String,  default: '' },
  pageCourante: { type: String,  default: 'dashboard' },
  badges:       { type: Object,  default: () => ({ verification:0, imputation:0, traitement:0, archivage:0, notifications:0, sga:0, sg:0 }) },
  logoUrl:      { type: String,  default: null },
})

const emit = defineEmits(['naviguer', 'deconnecter'])

function hasModule(code) { return props.modules.includes(code) }
function naviguer(page)  { emit('naviguer', page) }

const peutSaisir = computed(() => hasModule('saisie'))

const hasCourriersModule = computed(() =>
  ['saisie','verification','imputation','traitement','archivage','validation_sga','validation_sg'].some(c => hasModule(c))
)

const labelProfil = computed(() => ({
  DG: 'Directeur Général', ASSIST: 'Assistant DG', BO: "Bureau d'Ordre",
  DEST: 'Destinataire', ARC: 'Archiviste', ADMIN: 'Administrateur',
  SGA: 'Secrétaire Général Adjoint', SG: 'Secrétaire Général',
}[props.profil] || props.profil))
</script>

<style>
.sidebar-logo-placeholder {
  display: flex; align-items: center; justify-content: center;
  width: 64px; height: 64px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  font-size: 28px; color: #fff;
  margin: 0 auto;
}
</style>
