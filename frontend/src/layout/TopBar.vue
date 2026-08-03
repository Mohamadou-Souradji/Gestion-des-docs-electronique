<template>
  <header class="topbar">
    <span class="topbar-titre">{{ titre }}</span>
    <div class="topbar-droite">
      <button class="notif-btn" @click="$emit('notifications')">
        <i class="fa-solid fa-bell"></i>
        <span v-if="notifsNonLues > 0" class="notif-dot"></span>
      </button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  titre:         { type: String,  default: '' },
  notifsNonLues: { type: Number,  default: 0  },
})
defineEmits(['notifications'])
</script>
