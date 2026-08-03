<template>
  <div class="app-layout">

    <aside class="sidebar">
      <div class="sidebar-logo">
        <!-- Logo dynamique de l'organisation — JAMAIS logo ESCEP par défaut -->
        <img v-if="logoUrl" :src="logoUrl" alt="Logo" />
        <div v-else class="sidebar-logo-placeholder">
          <i class="fa-solid fa-building"></i>
        </div>
      </div>
      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Administrateur</div>
      </div>

      <nav class="sidebar-nav">
        <button :class="['nav-item', { actif: page === 'supervision' }]" @click="page = 'supervision'">
          <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
          Supervision
        </button>

        <div class="nav-section-titre">Comptes</div>
        <button :class="['nav-sous-item', { actif: page === 'comptes' }]" @click="page = 'comptes'">
          <span class="nav-item-icone"><i class="fa-solid fa-users"></i></span>
          Utilisateurs
        </button>
        <button :class="['nav-sous-item', { actif: page === 'nouveau_compte' }]" @click="page = 'nouveau_compte'">
          <span class="nav-item-icone"><i class="fa-solid fa-user-plus"></i></span>
          Nouveau compte
        </button>
        <button :class="['nav-sous-item', { actif: page === 'directions' }]" @click="page = 'directions'">
          <span class="nav-item-icone"><i class="fa-solid fa-building"></i></span>
          Directions
        </button>

        <div class="nav-section-titre">Archives</div>
        <!-- Nouveau lien Fonds d'archives -->
        <button :class="['nav-sous-item', { actif: page === 'fonds' }]" @click="page = 'fonds'">
          <span class="nav-item-icone"><i class="fa-solid fa-folder-open"></i></span>
          Fonds d'archives
        </button>

        <div class="nav-section-titre">Système</div>
        <button :class="['nav-sous-item', { actif: page === 'parametres' }]" @click="page = 'parametres'">
          <span class="nav-item-icone"><i class="fa-solid fa-sliders"></i></span>
          Paramètres
        </button>
        <!-- Sécurité RETIRÉE — gérée par Super-Admin uniquement -->
        <button :class="['nav-sous-item', { actif: page === 'journal' }]" @click="page = 'journal'">
          <span class="nav-item-icone"><i class="fa-solid fa-list-check"></i></span>
          Journal d'audit
        </button>
      </nav>

      <div class="sidebar-bas">
        <button class="nav-item" @click="seDeconnecter">
          <span class="nav-item-icone"><i class="fa-solid fa-right-from-bracket"></i></span>
          Déconnexion
        </button>
      </div>
    </aside>

    <div class="main-zone">
      <header class="topbar">
        <span class="topbar-titre">{{ titresPages[page] }}</span>
        <span style="font-size:12px;color:#999;font-style:italic">Espace Administration</span>
      </header>

      <main class="page-contenu">
        <SupervisionTechnique v-if="page === 'supervision'" />
        <GestionComptes       v-if="page === 'comptes'" ref="compteRef" @modifier="ouvrirModif" />
        <NouveauCompte        v-if="page === 'nouveau_compte'" />
        <GestionDirections    v-if="page === 'directions'" />
        <GestionFonds         v-if="page === 'fonds'" />
        <ParametresApp        v-if="page === 'parametres'" />
        <JournalAudit         v-if="page === 'journal'" />
      </main>

      <PiedPage />
    </div>

    <ModifierCompteModal v-if="compteAModifier" :utilisateur="compteAModifier"
      @fermer="compteAModifier = null"
      @enregistre="onCompteModifie" />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import PiedPage              from '../layout/PiedPage.vue'
import SupervisionTechnique  from '../admin/SupervisionTechnique.vue'
import GestionComptes        from '../admin/GestionComptes.vue'
import NouveauCompte         from '../admin/NouveauCompte.vue'
import GestionDirections     from '../admin/GestionDirections.vue'
import GestionFonds          from '../admin/GestionFonds.vue'
import ParametresApp         from '../admin/ParametresOrg.vue'
import ModifierCompteModal   from '../admin/ModifierCompteModal.vue'
import JournalAudit          from '../modules/audit/JournalAudit.vue'

import { useInactivite }  from '../composables/useInactivite'
import { useParametres }  from '../composables/useParametres'

useInactivite()

const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')
const logoUrl = ref(null)

const page           = ref('supervision')
const compteAModifier = ref(null)
const compteRef       = ref(null)

const titresPages = {
  supervision:    'Supervision',
  comptes:        'Gestion des utilisateurs',
  nouveau_compte: 'Nouveau compte',
  directions:     'Directions et départements',
  fonds:          "Fonds d'archives",
  parametres:     "Paramètres de l'organisation",
  journal:        "Journal d'audit",
}

function ouvrirModif(u) { compteAModifier.value = u }

function onCompteModifie() {
  compteAModifier.value = null
  compteRef.value?.charger()
}

function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  // NE PAS supprimer tenant_code — l'organisation reste mémorisée
  router.push('/')
}

onMounted(async () => {
  const p = await useParametres()
  // Utiliser uniquement le logo de l'organisation courante
  if (p?.logo_url) logoUrl.value = p.logo_url
})
</script>

<style>
.sidebar-logo-placeholder {
  display: flex; align-items: center; justify-content: center;
  width: 60px; height: 60px;
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
  font-size: 28px; color: #fff;
  margin: 0 auto;
}
</style>
