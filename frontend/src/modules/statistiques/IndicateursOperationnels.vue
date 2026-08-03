<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-chart-simple"></i> Indicateurs opérationnels
    </div>
    <div class="stats-grille">
      <div class="stat-card">
        <div class="stat-icone bleu"><i class="fa-solid fa-calendar-day"></i></div>
        <div><div class="stat-valeur">{{ stats.recu_jour }}</div><div class="stat-label">Reçus aujourd'hui</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icone bleu"><i class="fa-solid fa-calendar-week"></i></div>
        <div><div class="stat-valeur">{{ stats.recu_semaine }}</div><div class="stat-label">Reçus cette semaine</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icone bleu"><i class="fa-solid fa-calendar"></i></div>
        <div><div class="stat-valeur">{{ stats.recu_mois }}</div><div class="stat-label">Reçus ce mois</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icone jaune"><i class="fa-solid fa-hourglass-half"></i></div>
        <div><div class="stat-valeur">{{ stats.en_attente_imputation }}</div><div class="stat-label">En attente imputation</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icone rouge"><i class="fa-solid fa-triangle-exclamation"></i></div>
        <div><div class="stat-valeur">{{ stats.non_consultes_j3 }}</div><div class="stat-label">Non consultés J+3</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icone rouge"><i class="fa-solid fa-clock"></i></div>
        <div><div class="stat-valeur">{{ stats.en_retard_j7 }}</div><div class="stat-label">En retard J+7</div></div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">
      <div style="background:#f5f8ff;padding:16px;border-radius:8px;text-align:center">
        <div style="font-size:28px;font-weight:bold;color:#1565C0">{{ stats.delai_reception_imputation ?? 'N/A' }}</div>
        <div style="font-size:12px;color:#666;margin-top:4px">Délai moyen réception → imputation (jours)</div>
      </div>
      <div style="background:#f5f8ff;padding:16px;border-radius:8px;text-align:center">
        <div style="font-size:28px;font-weight:bold;color:#1565C0">{{ stats.delai_imputation_traitement ?? 'N/A' }}</div>
        <div style="font-size:12px;color:#666;margin-top:4px">Délai moyen imputation → traitement (jours)</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, required: true },
})
</script>
