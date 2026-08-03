<template>
  <div class="carte">
    <div class="carte-titre"><i class="fa-solid fa-users"></i> Gestion des utilisateurs</div>

    <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
      <input v-model="filtre.texte" type="text" placeholder="Nom, identifiant, direction..."
        style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
      <select v-model="filtre.profil" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Tous les profils</option>
        <option value="DG">DG</option>
        <option value="ASSIST">Assistant DG</option>
        <option value="BO">Bureau d'Ordre</option>
        <option value="DEST">Destinataire</option>
        <option value="ARC">Archiviste</option>
        <option value="ADMIN">Administrateur</option>
      </select>
      <select v-model="filtre.etat" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
        <option value="">Tous</option>
        <option value="actif">Actifs</option>
        <option value="inactif">Inactifs</option>
        <option value="verrouille">Verrouillés</option>
      </select>
    </div>

    <div v-if="chargement" class="msg-vide"><i class="fa-solid fa-spinner fa-spin"></i> Chargement...</div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr><th>Identifiant</th><th>Nom</th><th>Profil</th><th>Direction</th><th>Modules</th><th>2FA</th><th>État</th><th>MDP</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in utilisateursFiltres" :key="u.id">
            <td><strong>{{ u.identifiant }}</strong></td>
            <td>{{ u.prenom }} {{ u.nom }}</td>
            <td><span class="badge badge-en_verif" style="font-size:11px">{{ u.profil }}</span></td>
            <td style="font-size:12px">{{ u.direction_nom || '-' }}</td>
            <td style="font-size:11px;color:#666">{{ (u.modules_actifs || []).join(', ') || '-' }}</td>
            <td style="font-size:12px">
              <span :style="{ color: u.double_auth_active ? '#2E7D32' : '#999' }">{{ u.double_auth_active ? 'Oui' : 'Non' }}</span>
            </td>
            <td>
              <span v-if="u.est_verrouille" style="color:#E65100;font-weight:700;font-size:12px">Verrouillé</span>
              <span v-else-if="!u.is_active" style="color:#D32F2F;font-weight:700;font-size:12px">Inactif</span>
              <span v-else style="color:#2E7D32;font-weight:700;font-size:12px">Actif</span>
            </td>
            <td>
              <span v-if="u.mdp_expire" style="color:#D32F2F;font-size:12px;font-weight:700">Expiré</span>
              <span v-else style="color:#2E7D32;font-size:12px">OK</span>
            </td>
            <td>
              <div style="display:flex;gap:4px;flex-wrap:wrap">
                <button class="btn btn-outline" style="font-size:11px;padding:3px 8px" @click="$emit('modifier', u)">
                  <i class="fa-solid fa-pen"></i>
                </button>
                <button v-if="u.est_verrouille" class="btn btn-success" style="font-size:11px;padding:3px 8px" @click="deverrouiller(u)">
                  <i class="fa-solid fa-lock-open"></i>
                </button>
                <button :class="u.is_active ? 'btn btn-danger' : 'btn btn-success'" style="font-size:11px;padding:3px 8px" @click="basculer(u)">
                  <i :class="u.is_active ? 'fa-solid fa-ban' : 'fa-solid fa-check'"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '../services/api'

const emit = defineEmits(['modifier'])

const chargement   = ref(false)
const utilisateurs = ref([])
const filtre = ref({ texte: '', profil: '', etat: '' })

const utilisateursFiltres = computed(() => {
  return utilisateurs.value.filter(u => {
    const q = filtre.value.texte.toLowerCase()
    const matchTexte = !q || u.nom.toLowerCase().includes(q) || u.prenom.toLowerCase().includes(q) ||
      u.identifiant.toLowerCase().includes(q) || (u.direction_nom||'').toLowerCase().includes(q)
    const matchProfil = !filtre.value.profil || u.profil === filtre.value.profil
    const matchEtat = !filtre.value.etat ||
      (filtre.value.etat === 'actif'      && u.is_active && !u.est_verrouille) ||
      (filtre.value.etat === 'inactif'    && !u.is_active) ||
      (filtre.value.etat === 'verrouille' && u.est_verrouille)
    return matchTexte && matchProfil && matchEtat
  })
})

async function charger() {
  chargement.value = true
  try { utilisateurs.value = (await usersApi.liste()).data }
  catch(e) { console.error(e) }
  finally { chargement.value = false }
}

async function basculer(u) {
  try { await usersApi.basculer(u.id); charger() } catch(e) {}
}

async function deverrouiller(u) {
  try { await usersApi.deverrouiller(u.id); charger() } catch(e) {}
}

defineExpose({ charger })
onMounted(charger)
</script>
