<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-chart-line"></i> Indicateurs stratégiques
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:20px">
      <div style="background:#f5f8ff;padding:16px;border-radius:8px">
        <div style="font-size:11px;text-transform:uppercase;color:#999;font-weight:700;margin-bottom:8px">Volume sur la période</div>
        <div style="font-size:32px;font-weight:bold;color:#1565C0">{{ stats.volume_mois_actuel }}</div>
        <div style="font-size:12px;color:#666">vs {{ stats.volume_mois_passe }} période précédente</div>
      </div>
      <div style="background:#fff9c4;padding:16px;border-radius:8px">
        <div style="font-size:11px;text-transform:uppercase;color:#999;font-weight:700;margin-bottom:8px">Taux de rejet Bureau d'Ordre</div>
        <div style="font-size:32px;font-weight:bold;color:#E65100">{{ stats.taux_rejet }}%</div>
        <div style="font-size:12px;color:#666">Indicateur qualité</div>
      </div>
    </div>

    <div style="margin-bottom:20px">
      <div style="font-size:13px;font-weight:700;color:#444;margin-bottom:10px">Répartition par statut</div>
      <div v-for="s in stats.par_statut" :key="s.statut" style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
        <span :class="'badge badge-' + s.statut.toLowerCase()" style="min-width:120px;text-align:center">{{ s.statut }}</span>
        <div style="flex:1;background:#eee;border-radius:4px;height:8px">
          <div :style="{ width: (s.total / maxStatut * 100) + '%', background:'#1565C0', height:'8px', borderRadius:'4px' }"></div>
        </div>
        <span style="font-size:13px;font-weight:bold;min-width:30px">{{ s.total }}</span>
      </div>
    </div>

    <div v-if="stats.performance_dest && stats.performance_dest.length > 0">
      <div style="font-size:13px;font-weight:700;color:#444;margin-bottom:10px">Performance par destinataire</div>
      <div class="tableau-wrap">
        <table class="tableau">
          <thead><tr><th>Nom</th><th>Direction</th><th>Courriers traités</th></tr></thead>
          <tbody>
            <tr v-for="d in stats.performance_dest" :key="d.destinataire__nom">
              <td>{{ d.destinataire__prenom }} {{ d.destinataire__nom }}</td>
              <td>{{ d.destinataire__direction__nom || '-' }}</td>
              <td><strong>{{ d.total_traites }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, required: true },
})

const maxStatut = computed(() => {
  if (!props.stats.par_statut || props.stats.par_statut.length === 0) return 1
  return Math.max(...props.stats.par_statut.map(x => x.total), 1)
})
</script>
