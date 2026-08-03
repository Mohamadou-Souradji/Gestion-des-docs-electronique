<template>
  <div>
    <div class="onglets">
      <button :class="['onglet', { actif: onglet === 'a_archiver' }]" @click="onglet = 'a_archiver'">
        <i class="fa-solid fa-download"></i> À archiver ({{ aArchiver.length }})
      </button>
      <button :class="['onglet', { actif: onglet === 'archives' }]" @click="onglet = 'archives'">
        <i class="fa-solid fa-box-archive"></i> Archives courantes ({{ archivees.length }})
      </button>
    </div>

    <div v-if="onglet === 'a_archiver'">
      <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
      <div v-else-if="aArchiver.length === 0" class="msg-vide">Aucun courrier à archiver.</div>
      <div v-else>
        <CarteCourrierDetail v-for="c in aArchiver" :key="c.id" :courrier="c">
          <template #actions>
            <button class="btn btn-primary" style="font-size:13px;padding:6px 14px"
              @click="archiver(c)" :disabled="enEnvoi">
              <i class="fa-solid fa-box-archive"></i> Archiver
            </button>
          </template>
        </CarteCourrierDetail>
      </div>
    </div>

    <div v-if="onglet === 'archives'">
      <ListeCourriers :courriers="archivees" titre="Fonds d'archives courantes" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { courriersApi } from '../../services/api'
import CarteCourrierDetail from '../courriers/CarteCourrierDetail.vue'
import ListeCourriers from '../courriers/ListeCourriers.vue'

const props = defineProps({
  courriers:   { type: Array,   default: () => [] },
  chargement:  { type: Boolean, default: false },
  pageActive:  { type: String,  default: 'a_archiver' },
})
const emit = defineEmits(['rafraichir'])

const onglet  = ref('a_archiver')
const enEnvoi = ref(false)

const aArchiver = computed(() => props.courriers.filter(c => c.statut === 'TRAITE'))
const archivees = computed(() => props.courriers.filter(c => c.statut === 'ARCHIVE'))

watch(() => props.pageActive, (newPage) => {
  if (['a_archiver', 'archives_courantes'].includes(newPage)) {
    onglet.value = newPage === 'a_archiver' ? 'a_archiver' : 'archives'
  }
}, { immediate: true })

async function archiver(c) {
  enEnvoi.value = true
  try {
    await courriersApi.archiver(c.id)
    emit('rafraichir')
  } catch(e) { console.error(e) }
  finally { enEnvoi.value = false }
}
</script>