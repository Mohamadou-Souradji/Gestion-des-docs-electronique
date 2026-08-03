<template>
  <div class="courrier-card">
    <div class="courrier-card-header">
      <div style="flex:1">
        <div class="courrier-card-objet">{{ courrier.objet }}</div>
        <div class="courrier-card-exp">{{ courrier.expediteur }}</div>
        <div style="font-size:12px;color:#888;margin-top:2px;display:flex;align-items:center;gap:8px">
          {{ courrier.numero_officiel || courrier.identifiant_temp }}
          <span v-if="courrier.mon_role === 'COPIE'"
            style="background:#E3F2FD;color:#1565C0;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600">
            <i class="fa-solid fa-copy"></i> En copie
          </span>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
        <span :class="'badge badge-' + courrier.statut.toLowerCase()">{{ courrier.statut_label }}</span>
        <span :class="classePriorite(courrier.priorite)" style="font-size:12px">
          <i class="fa-solid fa-flag"></i> {{ courrier.priorite }}
        </span>
      </div>
    </div>

    <div class="courrier-card-meta">
      <div><span class="meta-label">Date réception</span>{{ formaterDate(courrier.date_reception) }}</div>
      <div><span class="meta-label">Date document</span>{{ formaterDate(courrier.date_document) }}</div>
      <div v-if="courrier.heure_depot"><span class="meta-label">Heure dépôt</span>{{ courrier.heure_depot }}</div>
      <div><span class="meta-label">Mode réception</span>{{ courrier.mode_reception }}</div>
      <div v-if="courrier.saisi_par_nom"><span class="meta-label">Saisi par</span>{{ courrier.saisi_par_nom }}</div>
      <div v-if="courrier.destinataire_nom && courrier.mon_role === 'PRINCIPAL'">
        <span class="meta-label">Destinataire</span>{{ courrier.destinataire_nom }}
      </div>

      <!-- Instructions selon le rôle -->
      <div v-if="courrier.mon_role === 'PRINCIPAL' && courrier.instructions_dg">
        <span class="meta-label">Instructions DG</span>{{ courrier.instructions_dg }}
      </div>
      <div v-else-if="courrier.mon_role === 'COPIE' && courrier.mes_consignes_copie?.consignes_types?.length">
        <span class="meta-label">Vos consignes</span>
        {{ courrier.mes_consignes_copie.consignes_types.join(', ') }}
      </div>
      <div v-else-if="courrier.mon_role === 'COPIE' && !courrier.mes_consignes_copie?.consignes_types?.length">
        <span class="meta-label">Vos consignes</span>
        <span style="color:#999;font-size:12px">Aucune consigne spécifique</span>
      </div>

      <div v-if="courrier.motif_rejet" style="grid-column:1/-1">
        <span class="meta-label" style="color:#D32F2F">Motif du rejet</span>
        <span style="color:#D32F2F">{{ courrier.motif_rejet }}</span>
      </div>
    </div>

    <div class="courrier-card-actions">
      <a v-if="courrier.fichier_pdf_url" :href="courrier.fichier_pdf_url" target="_blank"
        class="btn btn-outline" style="font-size:13px;padding:6px 12px">
        <i class="fa-solid fa-file-pdf"></i> Voir PDF
      </a>
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  courrier: { type: Object, required: true },
})

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}

function classePriorite(p) {
  if (p === 'HAUTE')   return 'priorite-haute'
  if (p === 'BASSE')   return 'priorite-basse'
  return 'priorite-normale'
}
</script>