<template>
  <div>
    <!-- Filtres et export -->
    <div class="carte" style="padding:16px">
      <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end">
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Période</label>
          <select v-model="periode" @change="charger" style="padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
            <option value="jour">Aujourd'hui</option>
            <option value="semaine">Cette semaine</option>
            <option value="mois">Ce mois</option>
            <option value="trimestre">Ce trimestre</option>
            <option value="annee">Cette année</option>
          </select>
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Du</label>
          <input v-model="dateDebut" type="date" style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" @change="charger" />
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Au</label>
          <input v-model="dateFin" type="date" style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" @change="charger" />
        </div>
        <div style="margin-left:auto;display:flex;gap:8px">
          <button class="btn btn-outline" style="font-size:13px;padding:7px 14px" @click="exporterExcel">
            <i class="fa-solid fa-file-excel"></i> Exporter Excel
          </button>
          <button class="btn btn-primary" style="font-size:13px;padding:7px 14px" @click="exporterPdf">
            <i class="fa-solid fa-file-pdf"></i> Exporter PDF
          </button>
        </div>
      </div>
    </div>

    <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
    <template v-else-if="stats">
      <IndicateursOperationnels :stats="stats.operationnels" />
      <IndicateursStrategiques  :stats="stats.strategiques" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '../../services/api'
import IndicateursOperationnels from './IndicateursOperationnels.vue'
import IndicateursStrategiques  from './IndicateursStrategiques.vue'

const chargement = ref(false)
const stats      = ref(null)
const periode    = ref('mois')
const dateDebut  = ref('')
const dateFin    = ref('')

async function charger() {
  chargement.value = true
  try {
    const params = { periode: periode.value }
    if (dateDebut.value) params.date_debut = dateDebut.value
    if (dateFin.value)   params.date_fin   = dateFin.value
    stats.value = (await dashboardApi.statistiques(params)).data
  } catch(e) { console.error(e) }
  finally { chargement.value = false }
}

function telecharger(blob, nomFichier) {
  const url  = URL.createObjectURL(blob)
  const lien = document.createElement('a')
  lien.href  = url
  lien.setAttribute('download', nomFichier)
  document.body.appendChild(lien)
  lien.click()
  document.body.removeChild(lien)
  URL.revokeObjectURL(url)
}

async function exporterExcel() {
  try {
    const params = { periode: periode.value }
    if (dateDebut.value) params.date_debut = dateDebut.value
    if (dateFin.value)   params.date_fin   = dateFin.value
    const rep = await dashboardApi.exportExcel(params)
    telecharger(new Blob([rep.data]), 'statistiques_ged.xlsx')
  } catch(e) { console.error(e) }
}

async function exporterPdf() {
  try {
    const params = { periode: periode.value }
    if (dateDebut.value) params.date_debut = dateDebut.value
    if (dateFin.value)   params.date_fin   = dateFin.value
    const rep = await dashboardApi.exportPdf(params)
    telecharger(new Blob([rep.data], { type: 'application/pdf' }), 'statistiques_ged.pdf')
  } catch(e) { console.error(e) }
}

onMounted(charger)
</script>
