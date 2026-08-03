<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-list"></i> {{ titre }}
    </div>

    <!-- Filtres -->
    <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
      <input v-model="filtre.q" type="text" placeholder="Objet, expéditeur, numéro..."
        style="flex:1;min-width:180px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px"
        @keyup.enter="filtrerLocal" />
      <select v-model="filtre.statut" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Tous les statuts</option>
        <option value="BROUILLON">Brouillon</option>
        <option value="EN_VERIF">En vérification</option>
        <option value="REJETE">Rejeté</option>
        <option value="EN_ATT_IMP">En attente imputation</option>
        <option value="IMPUTE">Imputé</option>
        <option value="EN_COURS">En cours</option>
        <option value="TRAITE">Traité</option>
        <option value="ARCHIVE">Archivé</option>
      </select>
      <select v-model="filtre.priorite" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Toutes priorités</option>
        <option value="HAUTE">Haute</option>
        <option value="NORMALE">Normale</option>
        <option value="BASSE">Basse</option>
      </select>
    </div>

    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
    </div>
    <div v-else-if="courriersAffiches.length === 0" class="msg-vide">
      Aucun courrier trouvé.
    </div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr>
            <th>Référence</th>
            <th>Objet</th>
            <th>Expéditeur</th>
            <th>Date réception</th>
            <th>Priorité</th>
            <th v-if="afficherDestinataire">Destinataire</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in courriersAffiches" :key="c.id">
            <td style="white-space:nowrap;font-size:12px">
              {{ c.numero_officiel || c.identifiant_temp }}
            </td>
            <td>{{ c.objet }}</td>
            <td>{{ c.expediteur }}</td>
            <td>{{ formaterDate(c.date_reception) }}</td>
            <td>
              <span :class="classePriorite(c.priorite)">{{ c.priorite }}</span>
            </td>
            <td v-if="afficherDestinataire">{{ c.destinataire_nom || '-' }}</td>
            <td>
              <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
            </td>
            <td>
              <div style="display:flex;gap:4px">
                <a v-if="c.fichier_pdf_url" :href="c.fichier_pdf_url" target="_blank"
                  class="btn btn-outline" style="padding:4px 8px;font-size:12px" title="Voir le PDF">
                  <i class="fa-solid fa-file-pdf"></i>
                </a>
                <button v-if="$slots.actions" class="btn btn-outline" style="padding:4px 8px;font-size:12px"
                  @click="$emit('action', c)">
                  <i class="fa-solid fa-ellipsis"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p style="font-size:12px;color:#999;margin-top:8px">{{ courriersAffiches.length }} courrier(s) affiché(s)</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  courriers:           { type: Array,   default: () => [] },
  chargement:          { type: Boolean, default: false },
  titre:               { type: String,  default: 'Liste des courriers' },
  afficherDestinataire:{ type: Boolean, default: false },
})

defineEmits(['action'])

const filtre = ref({ q: '', statut: '', priorite: '' })

const courriersAffiches = computed(() => {
  return props.courriers.filter(c => {
    const q = filtre.value.q.toLowerCase()
    const matchQ = !q ||
      c.objet.toLowerCase().includes(q) ||
      c.expediteur.toLowerCase().includes(q) ||
      (c.numero_officiel || '').toLowerCase().includes(q) ||
      (c.identifiant_temp || '').toLowerCase().includes(q)
    const matchStatut   = !filtre.value.statut   || c.statut   === filtre.value.statut
    const matchPriorite = !filtre.value.priorite || c.priorite === filtre.value.priorite
    return matchQ && matchStatut && matchPriorite
  })
})

function filtrerLocal() {} // déclenchée par le filtre computed

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}

function classePriorite(p) {
  return { 'priorite-haute': p === 'HAUTE', 'priorite-normale': p === 'NORMALE', 'priorite-basse': p === 'BASSE' }
}
</script>
