<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-bell"></i> Mes notifications
    </div>
    <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
    <div v-else-if="notifications.length === 0" class="msg-vide">Aucune notification.</div>
    <div v-else>
      <div v-for="n in notifications" :key="n.id" :class="['notif-item', { 'non-lue': !n.lue }]">
        <div>{{ n.message }}</div>
        <div class="notif-item-heure">{{ formaterDateHeure(n.date) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  notifications: { type: Array,   default: () => [] },
  chargement:    { type: Boolean, default: false },
})

function formaterDateHeure(d) {
  return d ? new Date(d).toLocaleString('fr-FR') : ''
}
</script>
