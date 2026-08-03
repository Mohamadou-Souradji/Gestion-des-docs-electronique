<template>
  <div>
    <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
    <div v-else-if="supervision">
      <div class="stats-grille">
        <div class="stat-card">
          <div class="stat-icone bleu"><i class="fa-solid fa-users"></i></div>
          <div><div class="stat-valeur">{{ supervision.utilisateurs.total }}</div><div class="stat-label">Comptes total</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icone vert"><i class="fa-solid fa-circle-check"></i></div>
          <div><div class="stat-valeur">{{ supervision.utilisateurs.actifs }}</div><div class="stat-label">Actifs</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icone rouge"><i class="fa-solid fa-lock"></i></div>
          <div><div class="stat-valeur">{{ supervision.utilisateurs.verrouilles }}</div><div class="stat-label">Verrouillés</div></div>
        </div>
        <div class="stat-card">
          <div class="stat-icone jaune"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <div><div class="stat-valeur">{{ supervision.audit.acces_refuses }}</div><div class="stat-label">Accès refusés</div></div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div class="carte">
          <div class="carte-titre">Volumétrie système</div>
          <div v-for="(val, label) in volumetrieAffichee" :key="label"
            style="display:flex;justify-content:space-between;padding:10px;background:#f5f8ff;border-radius:6px;margin-bottom:8px">
            <span style="font-size:14px;color:#444">{{ label }}</span>
            <strong style="color:#1565C0">{{ val }}</strong>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { dashboardApi } from '../services/api'

const chargement  = ref(false)
const supervision = ref(null)

const volumetrieAffichee = computed(() => supervision.value ? {
  'Total courriers':      supervision.value.volumetrie.total_courriers,
  'Archives historiques': supervision.value.volumetrie.total_archives,
  'Entrées journal':      supervision.value.audit.total_entrees,
} : {})

const systemeAffiche = computed(() => supervision.value ? {
  'Version Django':  supervision.value.systeme.django_version,
  'Heure serveur':   supervision.value.systeme.heure_serveur,
  'Dernière action': supervision.value.audit.derniere_action,
} : {})

async function charger() {
  chargement.value = true
  try { supervision.value = (await dashboardApi.supervision()).data }
  catch(e) { console.error(e) }
  finally { chargement.value = false }
}

onMounted(charger)
</script>
