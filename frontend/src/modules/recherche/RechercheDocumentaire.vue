<template>
  <div class="carte">
    <div class="carte-titre">
      <i class="fa-solid fa-magnifying-glass"></i> Recherche documentaire
    </div>

    <div class="grille-form" style="margin-bottom:16px">
      <div class="champ champ-large">
        <label>Recherche plein texte</label>
        <input v-model="form.q" type="text" placeholder="Objet, expéditeur, numéro, référence..." @keyup.enter="lancer" />
      </div>
      <div class="champ">
        <label>Type</label>
        <select v-model="form.type">
          <option value="">Tous</option>
          <option value="ENT">Entrant</option>
          <option value="INT">Interne</option>
        </select>
      </div>
      <div class="champ">
        <label>Statut</label>
        <select v-model="form.statut">
          <option value="">Tous</option>
          <option value="BROUILLON">Brouillon</option>
          <option value="EN_VERIF">En vérification</option>
          <option value="EN_ATT_IMP">En attente imputation</option>
          <option value="IMPUTE">Imputé</option>
          <option value="EN_COURS">En cours</option>
          <option value="TRAITE">Traité</option>
          <option value="ARCHIVE">Archivé</option>
          <option value="REJETE">Rejeté</option>
        </select>
      </div>
      <div class="champ">
        <label>Priorité</label>
        <select v-model="form.priorite">
          <option value="">Toutes</option>
          <option value="HAUTE">URGENT</option>
          <option value="NORMALE"><Nav></Nav></option>
          <option value="BASSE">Très URGENT</option>
        </select>
      </div>
      <div class="champ">
    <label>Type de document (archives)</label>
    <select v-model="form.type_document">
      <option value="">Tous</option>
      <option value="LETTRE">Lettre</option>
      <option value="RAPPORT">Rapport</option>
      <option value="DECISION">Décision</option>
      <option value="CIRCULAIRE">Circulaire</option>
      <option value="PROCES_VERBAL">Procès-verbal</option>
      <option value="CONTRAT">Contrat</option>
      <option value="CONVENTION">Convention</option>
      <option value="ARRETE">Arrêté</option>
      <option value="DECRET">Décret</option>
      <option value="NOTE">Note de service</option>
      <option value="FACTURE">Facture</option>
      <option value="BON_COMMANDE">Bon de commande</option>
      <option value="AUTRE">Autre</option>
    </select>
  </div>
      <div class="champ"><label>Date début</label><input v-model="form.date_debut" type="date" /></div>
      <div class="champ"><label>Date fin</label><input v-model="form.date_fin" type="date" /></div>
      <div class="champ" style="display:flex;align-items:center;gap:8px;padding-top:20px">
        <input type="checkbox" v-model="form.avec_archives" id="arc-chk" style="accent-color:#1565C0;width:16px;height:16px" />
        <label for="arc-chk" style="cursor:pointer;font-size:14px">Inclure les archives historiques</label>
      </div>
    </div>

    <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px">
      <button class="btn btn-primary" @click="lancer" :disabled="enCours">
        <i class="fa-solid fa-magnifying-glass"></i>
        {{ enCours ? 'Recherche...' : 'Lancer la recherche' }}
      </button>
      <button class="btn btn-ghost" @click="reinit">Réinitialiser</button>
    </div>

    <div v-if="effectuee">
      <div v-if="resultats.courriers.length === 0 && resultats.archives.length === 0" class="msg-vide">
        Aucun résultat pour cette recherche.
      </div>

      <!-- Courriers (Brouillon, En verif, En attente imputation, Imputé, En cours, Traité, Rejeté) -->
      <div v-if="resultats.courriers.length > 0">
        <div style="font-weight:700;color:#1565C0;margin-bottom:10px">
          <i class="fa-solid fa-envelope"></i> Courriers ({{ resultats.total_courriers }})
        </div>
        <div class="tableau-wrap">
          <table class="tableau">
            <thead>
              <tr>
                <th>Numéro</th>
                <th>Objet</th>
                <th>Expéditeur</th>
                <th>Date</th>
                <th>Statut</th>
                <th style="text-align:center;width:80px">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in resultats.courriers" :key="c.id">
                <td>{{ c.numero_officiel || c.identifiant_temp }}</td>
                <td>{{ c.objet }}</td>
                <td>{{ c.expediteur }}</td>
                <td>{{ formaterDate(c.date_reception) }}</td>
                <td>
                  <span :class="'badge badge-' + c.statut.toLowerCase()">
                    {{ c.statut_label }}
                  </span>
                </td>
                <td style="text-align:center">
                  <a v-if="c.fichier_pdf_url" :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:6px 10px;font-size:11px;white-space:nowrap">
                    <i class="fa-solid fa-file-pdf"></i> PDF
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Archives historiques -->
      <div v-if="resultats.archives.length > 0" style="margin-top:24px">
        <div style="font-weight:700;color:#1565C0;margin-bottom:10px">
          <i class="fa-solid fa-box-archive"></i> Archives historiques ({{ resultats.total_archives }})
        </div>
        <div class="tableau-wrap">
          <table class="tableau">
            <thead>
              <tr>
                <th>Référence</th>
                <th>Intitulé</th>
                <th>Fonds</th>
                <th>Date document</th>
                <th style="text-align:center;width:80px">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in resultats.archives" :key="a.id">
                <td>{{ a.reference_systeme }}</td>
                <td>{{ a.intitule }}</td>
                <td>{{ a.fonds }}</td>
                <td>{{ formaterDate(a.date_document) }}</td>
                <td style="text-align:center">
                  <a v-if="a.fichier_pdf_url" :href="a.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:6px 10px;font-size:11px;white-space:nowrap">
                    <i class="fa-solid fa-file-pdf"></i> PDF
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { dashboardApi } from '../../services/api'

const enCours   = ref(false)
const effectuee = ref(false)
const resultats = ref({ courriers: [], archives: [], total_courriers: 0, total_archives: 0 })
const form = ref({ q: '', type: '', statut: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false })

async function lancer() {
  enCours.value   = true
  effectuee.value = true
  try {
    const params = {}
    Object.entries(form.value).forEach(([k, v]) => {
      if (v && v !== false) params[k] = k === 'avec_archives' ? 'true' : v
    })
    resultats.value = (await dashboardApi.recherche(params)).data
  } catch(e) { 
    console.error(e)
    resultats.value = { courriers: [], archives: [], total_courriers: 0, total_archives: 0 }
  }
  finally { enCours.value = false }
}

function reinit() {
  form.value = { q: '', type: '', statut: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false, type_document: '' }
  effectuee.value = false
  resultats.value = { courriers: [], archives: [], total_courriers: 0, total_archives: 0 ,type_document: ''}
}

function formaterDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : ''
}
</script>