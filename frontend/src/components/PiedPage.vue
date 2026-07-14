<template>
  <footer class="pied-page">
    <span>{{ texte }}</span>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useParametres } from '../composables/useParametres'

const texte = ref('© ESCEP-Niger — Système de Gestion Électronique des Documents')

onMounted(async () => {
  const p = await useParametres()
  if (p.texte_pied_page) texte.value = p.texte_pied_page
})
</script>

<style scoped>
.pied-page {
  background-color: #1565C0;
  color: rgba(255, 255, 255, 0.75);
  text-align: center;
  padding: 10px 24px;
  font-size: 12px;
  border-top: 3px solid #FDD835;
}
</style>
