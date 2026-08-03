<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-folder-open"></i> Fonds d'archives historiques
    </div>

    <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap">
      <input v-model="filtre.q" type="text"
        placeholder="Référence, intitulé, expéditeur, mots-clés..."
        style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px"
        @keyup.enter="charger" />
      <select v-model="filtre.fonds" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Tous les fonds</option>
        <option v-for="f in fonds" :key="f.code" :value="f.code">{{ f.label }}</option>
      </select>
      <select v-model="filtre.type" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Tous les types</option>
        <option v-for="t in types" :key="t.code" :value="t.code">{{ t.label }}</option>
      </select>
      <input v-model="filtre.date_debut" type="date" style="padding:9px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" />
      <input v-model="filtre.date_fin"   type="date" style="padding:9px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" />
      <button class="btn btn-primary" @click="charger" :disabled="chargement">
        <i class="fa-solid fa-magnifying-glass"></i> Filtrer
      </button>
      <button class="btn btn-ghost" @click="reinitFiltre">Réinitialiser</button>
    </div>

    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
    </div>
    <div v-else-if="archives.length === 0" class="msg-vide">Aucune archive trouvée.</div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr>
            <th>Référence système</th>
            <th>Référence origine</th>
            <th>Intitulé</th>
            <th>Fonds</th>
            <th>Type</th>
            <th>Date</th>
            <th>Mots-clés</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in archives" :key="a.id">
            <td style="white-space:nowrap;font-size:12px;font-weight:700">{{ a.reference_systeme }}</td>
            <td style="font-size:12px">{{ a.reference_origine || '-' }}</td>
            <td>{{ a.intitule }}</td>
            <td><span class="badge badge-archive">{{ a.fonds }}</span></td>
            <td style="font-size:12px">{{ a.type_document }}</td>
            <td style="font-size:12px">{{ formaterDate(a.date_document) }}</td>
            <td style="font-size:11px;color:#888">{{ a.mots_cles || '-' }}</td>
            <td>
              <a :href="a.fichier_url" target="_blank"
                class="btn btn-outline" style="padding:4px 10px;font-size:12px">
                <i class="fa-solid fa-file-pdf"></i>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p style="font-size:12px;color:#999;margin-top:8px">{{ archives.length }} document(s) trouvé(s)</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { archivesApi } from '../../services/api'

const chargement = ref(false)
const archives   = ref([])
const fonds      = ref([])
const types      = ref([])
const filtre     = ref({ q: '', fonds: '', type: '', date_debut: '', date_fin: '' })

onMounted(async () => {
  try {
    const rep   = await archivesApi.fonds()
    fonds.value = rep.data.fonds || []
    types.value = rep.data.types || []
  } catch {}
  await charger()  // ← charger les archives séparément
})

async function charger() {
  chargement.value = true
  try {
    const params = {}
    if (filtre.value.q)          params.q          = filtre.value.q
    if (filtre.value.fonds)      params.fonds       = filtre.value.fonds
    if (filtre.value.type)       params.type        = filtre.value.type
    if (filtre.value.date_debut) params.date_debut  = filtre.value.date_debut
    if (filtre.value.date_fin)   params.date_fin    = filtre.value.date_fin

    const rep = await archivesApi.liste(params)    // ← BON ENDPOINT: /archives/
    archives.value = rep.data
  } catch { archives.value = [] }
  finally { chargement.value = false }
}
function reinitFiltre() {
  filtre.value = { q: '', fonds: '', type: '', date_debut: '', date_fin: '' }
  charger()
}

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}
</script>
