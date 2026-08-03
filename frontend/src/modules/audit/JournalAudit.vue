<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-shield-halved"></i> Journal d'audit
    </div>

    <!-- Filtres -->
    <div class="grille-form" style="margin-bottom:16px">
      <div class="champ">
        <label>Recherche</label>
        <input v-model="filtres.q" type="text" placeholder="Description, objet, identifiant..."
          @keyup.enter="charger" />
      </div>
      <div class="champ">
        <label>Type d'action</label>
        <select v-model="filtres.type_action">
          <option value="">Tous</option>
          <option v-for="t in typesAction" :key="t.code" :value="t.code">{{ t.label }}</option>
        </select>
      </div>
      <div class="champ">
        <label>Issue</label>
        <select v-model="filtres.issue">
          <option value="">Toutes</option>
          <option value="SUCCES">Succès</option>
          <option value="ECHEC">Échec</option>
          <option value="REFUS">Refus</option>
        </select>
      </div>
      <div class="champ">
        <label>Identifiant utilisateur</label>
        <input v-model="filtres.identifiant" type="text" placeholder="ex: admin_escep" />
      </div>
      <div class="champ">
        <label>Date début</label>
        <input v-model="filtres.date_debut" type="date" />
      </div>
      <div class="champ">
        <label>Date fin</label>
        <input v-model="filtres.date_fin" type="date" />
      </div>
    </div>
    <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px;gap:8px">
      <button class="btn btn-primary" @click="charger" :disabled="chargement">
        <i class="fa-solid fa-magnifying-glass"></i>
        {{ chargement ? 'Chargement...' : 'Filtrer' }}
      </button>
      <button class="btn btn-ghost" @click="reinitialiser">
        <i class="fa-solid fa-rotate-left"></i> Réinitialiser
      </button>
      <span v-if="total > 0" style="font-size:12px;color:#888;padding:10px 0">
        {{ total }} entrée(s) trouvée(s)
      </span>
    </div>

    <!-- Tableau -->
    <div v-if="chargement" class="msg-vide">
      <i class="fa-solid fa-spinner fa-spin"></i> Chargement du journal...
    </div>
    <div v-else-if="entrees.length === 0" class="msg-vide">
      <i class="fa-solid fa-shield-halved" style="font-size:32px;opacity:0.2;display:block;margin-bottom:10px"></i>
      Aucune entrée dans le journal d'audit pour cette organisation.
    </div>
    <div v-else class="tableau-wrap">
      <table class="tableau">
        <thead>
          <tr>
            <th>Date/Heure</th>
            <th>Utilisateur</th>
            <th>Profil</th>
            <th>Action</th>
            <th>Description</th>
            <th>IP</th>
            <th>Issue</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in entrees" :key="e.id">
            <td style="white-space:nowrap;font-size:12px;color:#666">{{ e.horodatage }}</td>
            <td style="font-weight:600">{{ e.identifiant }}</td>
            <td>
              <span class="badge" :class="badgeProfil(e.profil)">{{ e.profil }}</span>
            </td>
            <td>
              <span style="font-size:12px;background:#f0f4ff;color:#1565C0;padding:3px 8px;border-radius:4px;font-weight:600">
                {{ e.type_action }}
              </span>
            </td>
            <td style="font-size:13px;max-width:300px">{{ e.description }}</td>
            <td style="font-size:12px;color:#888;font-family:monospace">{{ e.adresse_ip || '—' }}</td>
            <td>
              <span :class="['badge', badgeIssue(e.issue)]">{{ e.issue }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const entrees    = ref([])
const typesAction = ref([])
const chargement = ref(false)
const total      = ref(0)

const filtres = ref({
  q: '', type_action: '', issue: '',
  identifiant: '', date_debut: '', date_fin: '',
})

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  get headers() {
    return { Authorization: `Bearer ${localStorage.getItem('access')}` }
  }
})

async function charger() {
  chargement.value = true
  try {
    const params = {}
    Object.entries(filtres.value).forEach(([k, v]) => { if (v) params[k] = v })

    const rep = await api.get('/audit/', { params })

    // Gérer les deux formats possibles
    if (rep.data?.entrees) {
      // Format correct: { entrees: [...], types_action: [...], total: N }
      entrees.value    = rep.data.entrees
      typesAction.value = rep.data.types_action || []
      total.value      = rep.data.total || entrees.value.length
    } else if (Array.isArray(rep.data)) {
      // Ancien format: tableau direct
      entrees.value = rep.data
      total.value   = rep.data.length
    } else {
      entrees.value = []
      total.value   = 0
    }
  } catch(e) {
    console.error('Erreur journal audit:', e)
    entrees.value = []
    total.value   = 0
  } finally {
    chargement.value = false
  }
}

function reinitialiser() {
  filtres.value = { q: '', type_action: '', issue: '', identifiant: '', date_debut: '', date_fin: '' }
  charger()
}

function badgeProfil(profil) {
  const map = {
    ADMIN: 'badge-en_verif',
    DG:    'badge-impute',
    ASSIST:'badge-en_att_imp',
    BO:    'badge-brouillon',
    DEST:  'badge-en_cours',
    ARC:   'badge-archive',
  }
  return map[profil] || 'badge-brouillon'
}

function badgeIssue(issue) {
  if (issue === 'SUCCES') return 'badge-verifie'
  if (issue === 'ECHEC')  return 'badge-rejete'
  if (issue === 'REFUS')  return 'badge-rejete'
  return 'badge-brouillon'
}

onMounted(charger)
</script>
