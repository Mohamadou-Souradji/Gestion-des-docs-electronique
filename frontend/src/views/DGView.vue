<template>
  <div class="app-layout">

    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>
      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Directeur General</div>
      </div>
     <nav class="sidebar-nav">

  <button :class="['nav-item', { actif: page === 'dashboard' }]" @click="page = 'dashboard'">
    <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
    Tableau de bord
  </button>

  <div class="nav-section-titre">Courriers</div>
  <button :class="['nav-sous-item', { actif: page === 'a_imputer' }]" @click="page = 'a_imputer'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-inbox"></i></span>
    A imputer <span v-if="aImputer.length > 0" class="nav-badge">{{ aImputer.length }}</span>
  </button>
  <button :class="['nav-sous-item', { actif: page === 'en_cours' }]" @click="page = 'en_cours'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-spinner"></i></span>
    En cours
  </button>
  <button :class="['nav-sous-item', { actif: page === 'tous' }]" @click="page = 'tous'; chargerCourriers()">
    <span class="nav-item-icone"><i class="fa-solid fa-envelope"></i></span>
    Tous les courriers
  </button>

  <div class="nav-section-titre">Analyse</div>
  <button :class="['nav-sous-item', { actif: page === 'statistiques' }]" @click="page = 'statistiques'; chargerStats()">
    <span class="nav-item-icone"><i class="fa-solid fa-chart-bar"></i></span>
    Statistiques
  </button>
  <button :class="['nav-sous-item', { actif: page === 'recherche' }]" @click="page = 'recherche'">
    <span class="nav-item-icone"><i class="fa-solid fa-magnifying-glass"></i></span>
    Recherche
  </button>

  <div class="nav-section-titre">Administration</div>
  <button :class="['nav-sous-item', { actif: page === 'audit' }]" @click="page = 'audit'; chargerAudit()">
    <span class="nav-item-icone"><i class="fa-solid fa-shield-halved"></i></span>
    Journal d audit
  </button>
  <button :class="['nav-sous-item', { actif: page === 'delegations' }]" @click="page = 'delegations'; chargerDelegations()">
    <span class="nav-item-icone"><i class="fa-solid fa-user-shield"></i></span>
    Delegations
  </button>

  <button :class="['nav-item', { actif: page === 'notifications' }]" @click="page = 'notifications'; chargerNotifications()" style="margin-top:8px">
    <span class="nav-item-icone"><i class="fa-solid fa-bell"></i></span>
    Notifications
    <span v-if="notifsNonLues > 0" class="nav-badge">{{ notifsNonLues }}</span>
  </button>

</nav>
     <button class="nav-item" @click="seDeconnecter">
  <span class="nav-item-icone"><i class="fa-solid fa-right-from-bracket"></i></span>
  Deconnexion
</button>
    </aside>

    <div class="main-zone">
      <header class="topbar">
        <span class="topbar-titre">{{ titresPages[page] }}</span>
        <div class="topbar-droite">
          <button class="notif-btn" @click="page = 'notifications'; chargerNotifications()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span v-if="notifsNonLues > 0" class="notif-dot"></span>
          </button>
        </div>
      </header>

      <main class="page-contenu">

        <!-- DASHBOARD -->
        <div v-if="page === 'dashboard'">
          <div class="stats-grille">
            <div class="stat-card">
              <div class="stat-icone bleu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 13V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h9"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg></div>
              <div><div class="stat-valeur">{{ tousCourriers.length }}</div><div class="stat-label">Total courriers</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone jaune"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
              <div><div class="stat-valeur">{{ aImputer.length }}</div><div class="stat-label">A imputer</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone rouge"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
              <div><div class="stat-valeur">{{ nonConsultes.length }}</div><div class="stat-label">Non consultes J+3</div></div>
            </div>
            <div class="stat-card">
              <div class="stat-icone vert"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg></div>
              <div><div class="stat-valeur">{{ traites.length }}</div><div class="stat-label">Traites</div></div>
            </div>
          </div>

          <div v-if="nonConsultes.length > 0" class="carte" style="border-left:4px solid #D32F2F">
            <div class="carte-titre">Alerte — Courriers non consultes depuis plus de 3 jours</div>
            <div v-for="c in nonConsultes" :key="c.id" class="courrier-card">
              <div class="courrier-card-header">
                <div>
                  <div class="courrier-card-objet">{{ c.objet }}</div>
                  <div class="courrier-card-exp">Impute a : {{ c.destinataire_nom }}</div>
                </div>
                <span class="badge badge-impute">Non consulte</span>
              </div>
            </div>
          </div>

          <div class="carte">
            <div class="carte-titre">Courriers a imputer</div>
            <div v-if="aImputer.length === 0" class="msg-vide">Aucun courrier en attente d imputation.</div>
            <div v-else>
              <div v-for="c in aImputer.slice(0,4)" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.expediteur }} — {{ c.numero_officiel }}</div>
                  </div>
                  <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
                </div>
                <div class="courrier-card-actions">
                  <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="ouvrirImputation(c)">Imputer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- A IMPUTER -->
        <div v-if="page === 'a_imputer'">
          <div class="carte">
            <div class="carte-titre">Courriers en attente d imputation</div>
            <div v-if="chargement" class="msg-vide">Chargement...</div>
            <div v-else-if="aImputer.length === 0" class="msg-vide">Aucun courrier en attente.</div>
            <div v-else>
              <div v-for="c in aImputer" :key="c.id" class="courrier-card">
                <div class="courrier-card-header">
                  <div>
                    <div class="courrier-card-objet">{{ c.objet }}</div>
                    <div class="courrier-card-exp">{{ c.expediteur }} — {{ c.numero_officiel }}</div>
                  </div>
                  <div style="display:flex;gap:6px;flex-direction:column;align-items:flex-end">
                    <span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span>
                    <span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span>
                  </div>
                </div>
                <div class="courrier-card-meta">
                  <div><span class="meta-label">Date reception</span>{{ formaterDate(c.date_reception) }}</div>
                  <div><span class="meta-label">Date validation</span>{{ formaterDate(c.date_verification) }}</div>
                  <div v-if="c.observation_dg"><span class="meta-label">Observation assistant</span>{{ c.observation_dg }}</div>
                </div>
                <div class="courrier-card-actions">
                  <a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="font-size:13px;padding:6px 12px">Voir PDF</a>
                  <button class="btn btn-primary" style="font-size:13px;padding:6px 14px" @click="ouvrirImputation(c)">Imputer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- EN COURS -->
        <div v-if="page === 'en_cours'">
          <div class="carte">
            <div class="carte-titre">Courriers en cours de traitement</div>
            <div v-if="enCours.length === 0" class="msg-vide">Aucun courrier en cours.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Numero</th><th>Objet</th><th>Destinataire</th><th>Date imputation</th><th>Statut</th></tr></thead>
                <tbody>
                  <tr v-for="c in enCours" :key="c.id">
                    <td>{{ c.numero_officiel }}</td><td>{{ c.objet }}</td>
                    <td>{{ c.destinataire_nom }}</td><td>{{ formaterDate(c.date_imputation) }}</td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- TOUS -->
        <div v-if="page === 'tous'">
          <div class="carte">
            <div class="carte-titre">Tous les courriers</div>
            <div class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Numero</th><th>Objet</th><th>Expediteur</th><th>Priorite</th><th>Destinataire</th><th>Statut</th></tr></thead>
                <tbody>
                  <tr v-for="c in tousCourriers" :key="c.id">
                    <td>{{ c.numero_officiel || c.identifiant_temp }}</td><td>{{ c.objet }}</td>
                    <td>{{ c.expediteur }}</td>
                    <td><span :class="'priorite-' + c.priorite.toLowerCase()">{{ c.priorite }}</span></td>
                    <td>{{ c.destinataire_nom || '-' }}</td>
                    <td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
<!-- STATISTIQUES -->
<div v-if="page === 'statistiques'">
  <div v-if="chargementStats" class="msg-vide">Chargement des statistiques...</div>
  <div v-else-if="stats">

    <!-- Filtres et export -->
    <div class="carte" style="padding:16px">
      <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end">
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Periode</label>
          <select v-model="filtrePeriode" @change="chargerStats" style="padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
            <option value="jour">Aujourd hui</option>
            <option value="semaine">Cette semaine</option>
            <option value="mois">Ce mois</option>
            <option value="trimestre">Ce trimestre</option>
            <option value="annee">Cette annee</option>
          </select>
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Du</label>
          <input v-model="filtreDebut" type="date" style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" @change="chargerStats" />
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#444;display:block;margin-bottom:6px">Au</label>
          <input v-model="filtreFin" type="date" style="padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px" @change="chargerStats" />
        </div>
        <div style="margin-left:auto;display:flex;gap:8px;align-items:flex-end">
         <button @click="exporterExcel" class="btn btn-outline" style="font-size:13px;padding:8px 14px">
  Exporter Excel
</button>
<button @click="exporterPdf" class="btn btn-primary" style="font-size:13px;padding:8px 14px">
  Exporter PDF
</button>
        </div>
      </div>
      <div v-if="stats.periode" style="font-size:12px;color:#999;margin-top:10px">
        Periode affichee : du {{ formaterDate(stats.periode.debut) }} au {{ formaterDate(stats.periode.fin) }}
      </div>
    </div>

    <div class="carte">
      <div class="carte-titre">Indicateurs operationnels</div>
      <div class="stats-grille">
        <div class="stat-card"><div class="stat-icone bleu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.recu_jour }}</div><div class="stat-label">Recus aujourd hui</div></div></div>
        <div class="stat-card"><div class="stat-icone bleu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.recu_semaine }}</div><div class="stat-label">Recus cette semaine</div></div></div>
        <div class="stat-card"><div class="stat-icone bleu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.recu_mois }}</div><div class="stat-label">Recus ce mois</div></div></div>
        <div class="stat-card"><div class="stat-icone jaune"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.en_attente_imputation }}</div><div class="stat-label">En attente imputation</div></div></div>
        <div class="stat-card"><div class="stat-icone rouge"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.non_consultes_j3 }}</div><div class="stat-label">Non consultes J+3</div></div></div>
        <div class="stat-card"><div class="stat-icone rouge"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div><div><div class="stat-valeur">{{ stats.operationnels.en_retard_j7 }}</div><div class="stat-label">En retard J+7</div></div></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">
        <div style="background:#f5f8ff;padding:16px;border-radius:8px;text-align:center">
          <div style="font-size:28px;font-weight:bold;color:#1565C0">{{ stats.operationnels.delai_reception_imputation ?? 'N/A' }}</div>
          <div style="font-size:12px;color:#666;margin-top:4px">Delai moyen reception vers imputation (jours)</div>
        </div>
        <div style="background:#f5f8ff;padding:16px;border-radius:8px;text-align:center">
          <div style="font-size:28px;font-weight:bold;color:#1565C0">{{ stats.operationnels.delai_imputation_traitement ?? 'N/A' }}</div>
          <div style="font-size:12px;color:#666;margin-top:4px">Delai moyen imputation vers traitement (jours)</div>
        </div>
      </div>
    </div>

    <div class="carte">
      <div class="carte-titre">Indicateurs strategiques</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:20px">
        <div style="background:#f5f8ff;padding:16px;border-radius:8px">
          <div style="font-size:11px;text-transform:uppercase;color:#999;font-weight:700;margin-bottom:8px">Volume sur la periode</div>
          <div style="font-size:32px;font-weight:bold;color:#1565C0">{{ stats.strategiques.volume_mois_actuel }}</div>
          <div style="font-size:12px;color:#666">vs {{ stats.strategiques.volume_mois_passe }} periode precedente</div>
        </div>
        <div style="background:#fff9c4;padding:16px;border-radius:8px">
          <div style="font-size:11px;text-transform:uppercase;color:#999;font-weight:700;margin-bottom:8px">Taux de rejet Bureau d Ordre</div>
          <div style="font-size:32px;font-weight:bold;color:#E65100">{{ stats.strategiques.taux_rejet }}%</div>
          <div style="font-size:12px;color:#666">Indicateur qualite</div>
        </div>
      </div>
      <div style="margin-bottom:20px">
        <div style="font-size:13px;font-weight:700;color:#444;margin-bottom:10px">Repartition par statut</div>
        <div v-for="s in stats.strategiques.par_statut" :key="s.statut" style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
          <span :class="'badge badge-' + s.statut.toLowerCase()" style="min-width:120px;text-align:center">{{ s.statut }}</span>
          <div style="flex:1;background:#eee;border-radius:4px;height:8px">
            <div :style="{ width: (s.total / Math.max(...stats.strategiques.par_statut.map(x=>x.total)) * 100) + '%', background:'#1565C0', height:'8px', borderRadius:'4px' }"></div>
          </div>
          <span style="font-size:13px;font-weight:bold;min-width:30px">{{ s.total }}</span>
        </div>
      </div>
      <div v-if="stats.strategiques.performance_dest.length > 0">
        <div style="font-size:13px;font-weight:700;color:#444;margin-bottom:10px">Performance par destinataire</div>
        <div class="tableau-wrap">
          <table class="tableau">
            <thead><tr><th>Nom</th><th>Entite</th><th>Courriers traites</th></tr></thead>
            <tbody>
              <tr v-for="d in stats.strategiques.performance_dest" :key="d.destinataire__nom">
                <td>{{ d.destinataire__prenom }} {{ d.destinataire__nom }}</td>
                <td>{{ d.destinataire__entite }}</td>
                <td><strong>{{ d.total_traites }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</div>

        <!-- RECHERCHE -->
        <div v-if="page === 'recherche'">
          <div class="carte">
            <div class="carte-titre">Recherche documentaire</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ champ-large">
                <label>Recherche plein texte</label>
                <input v-model="recherche.q" type="text" placeholder="Objet, expediteur, numero, reference..." @keyup.enter="lancerRecherche" />
              </div>
              <div class="champ"><label>Type</label><select v-model="recherche.type"><option value="">Tous</option><option value="ENT">Entrant</option><option value="INT">Interne</option></select></div>
              <div class="champ"><label>Statut</label>
                <select v-model="recherche.statut">
                  <option value="">Tous</option>
                  <option value="BROUILLON">Brouillon</option>
                  <option value="EN_VERIF">En verification</option>
                  <option value="EN_ATT_IMP">En attente imputation</option>
                  <option value="IMPUTE">Impute</option>
                  <option value="EN_COURS">En cours</option>
                  <option value="TRAITE">Traite</option>
                  <option value="ARCHIVE">Archive</option>
                  <option value="REJETE">Rejete</option>
                </select>
              </div>
              <div class="champ"><label>Priorite</label><select v-model="recherche.priorite"><option value="">Toutes</option><option value="HAUTE">Haute</option><option value="NORMALE">Normale</option><option value="BASSE">Basse</option></select></div>
              <div class="champ"><label>Date debut</label><input v-model="recherche.date_debut" type="date" /></div>
              <div class="champ"><label>Date fin</label><input v-model="recherche.date_fin" type="date" /></div>
              <div class="champ" style="display:flex;align-items:center;gap:8px;padding-top:20px">
                <input type="checkbox" v-model="recherche.avec_archives" id="arc_dg" style="accent-color:#1565C0;width:16px;height:16px" />
                <label for="arc_dg" style="cursor:pointer;font-size:14px">Inclure les archives historiques</label>
              </div>
            </div>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px">
              <button class="btn btn-primary" @click="lancerRecherche" :disabled="rechercheEnCours">{{ rechercheEnCours ? 'Recherche...' : 'Lancer la recherche' }}</button>
              <button class="btn btn-ghost" @click="reinitRecherche">Reinitialiser</button>
            </div>
            <div v-if="rechercheEffectuee">
              <div v-if="resultats.courriers.length === 0 && resultats.archives.length === 0" class="msg-vide">Aucun resultat.</div>
              <div v-if="resultats.courriers.length > 0">
                <div style="font-weight:700;color:#1565C0;margin-bottom:10px">Courriers ({{ resultats.total_courriers }})</div>
                <div class="tableau-wrap"><table class="tableau"><thead><tr><th>Numero</th><th>Objet</th><th>Expediteur</th><th>Date</th><th>Destinataire</th><th>Statut</th><th></th></tr></thead>
                  <tbody><tr v-for="c in resultats.courriers" :key="c.id"><td>{{ c.numero_officiel || c.identifiant_temp }}</td><td>{{ c.objet }}</td><td>{{ c.expediteur }}</td><td>{{ formaterDate(c.date_reception) }}</td><td>{{ c.destinataire_nom || '-' }}</td><td><span :class="'badge badge-' + c.statut.toLowerCase()">{{ c.statut_label }}</span></td><td><a :href="c.fichier_pdf_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td></tr></tbody>
                </table></div>
              </div>
              <div v-if="resultats.archives.length > 0" style="margin-top:24px">
                <div style="font-weight:700;color:#1565C0;margin-bottom:10px">Archives historiques ({{ resultats.total_archives }})</div>
                <div class="tableau-wrap"><table class="tableau"><thead><tr><th>Reference</th><th>Intitule</th><th>Fonds</th><th>Date</th><th></th></tr></thead>
                  <tbody><tr v-for="a in resultats.archives" :key="a.id"><td>{{ a.reference_systeme }}</td><td>{{ a.intitule }}</td><td>{{ a.fonds }}</td><td>{{ formaterDate(a.date_document) }}</td><td><a :href="a.fichier_url" target="_blank" class="btn btn-outline" style="padding:4px 10px;font-size:12px">PDF</a></td></tr></tbody>
                </table></div>
              </div>
            </div>
          </div>
        </div>

        <!-- MODULE 9 - JOURNAL D AUDIT -->
        <div v-if="page === 'audit'">
          <div class="carte">
            <div class="carte-titre">Journal d audit — Lecture seule</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ">
                <label>Type d action</label>
                <select v-model="filtreAudit.type_action" @change="chargerAudit">
                  <option value="">Tous</option>
                  <option v-for="t in typesAction" :key="t.code" :value="t.code">{{ t.label }}</option>
                </select>
              </div>
              <div class="champ">
                <label>Resultat</label>
                <select v-model="filtreAudit.issue" @change="chargerAudit">
                  <option value="">Tous</option>
                  <option value="SUCCES">Succes</option>
                  <option value="REFUS">Refus</option>
                  <option value="ERREUR">Erreur</option>
                </select>
              </div>
              <div class="champ"><label>Identifiant utilisateur</label><input v-model="filtreAudit.identifiant" type="text" placeholder="Identifiant..." @keyup.enter="chargerAudit" /></div>
              <div class="champ"><label>Date debut</label><input v-model="filtreAudit.date_debut" type="date" @change="chargerAudit" /></div>
              <div class="champ"><label>Date fin</label><input v-model="filtreAudit.date_fin" type="date" @change="chargerAudit" /></div>
              <div class="champ champ-large"><label>Recherche dans la description</label><input v-model="filtreAudit.q" type="text" placeholder="Mot cle..." @keyup.enter="chargerAudit" /></div>
            </div>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:16px">
              <button class="btn btn-primary" @click="chargerAudit">Filtrer</button>
              <button class="btn btn-ghost" @click="reinitAudit">Reinitialiser</button>
            </div>
            <p style="font-size:12px;color:#999;margin-bottom:12px">{{ entresAudit.length }} entree(s) affichee(s) — maximum 500 par requete</p>
            <div v-if="chargementAudit" class="msg-vide">Chargement...</div>
            <div v-else-if="entresAudit.length === 0" class="msg-vide">Aucune entree dans le journal.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr><th>Horodatage</th><th>Utilisateur</th><th>Profil</th><th>Action</th><th>Description</th><th>IP</th><th>Resultat</th></tr>
                </thead>
                <tbody>
                  <tr v-for="e in entresAudit" :key="e.id">
                    <td style="white-space:nowrap;font-size:12px">{{ e.horodatage }}</td>
                    <td><strong>{{ e.identifiant }}</strong></td>
                    <td>{{ e.profil }}</td>
                    <td style="font-size:12px">{{ e.type_action }}</td>
                    <td style="font-size:12px;max-width:300px">{{ e.description }}</td>
                    <td style="font-size:12px">{{ e.adresse_ip || '-' }}</td>
                    <td>
                      <span :style="{ color: e.issue === 'SUCCES' ? '#2E7D32' : e.issue === 'REFUS' ? '#D32F2F' : '#E65100', fontWeight: 'bold', fontSize: '12px' }">{{ e.issue }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- MODULE 10 - DELEGATIONS -->
        <div v-if="page === 'delegations'">
          <div class="carte">
            <div class="carte-titre">Delegations ponctuelles</div>
            <div class="barre-actions" style="margin-bottom:16px">
              <button class="btn btn-primary" @click="afficherFormDeleg = true">Accorder une delegation</button>
            </div>

            <div v-if="chargementDeleg" class="msg-vide">Chargement...</div>
            <div v-else-if="delegations.length === 0" class="msg-vide">Aucune delegation accordee.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr><th>Beneficiaire</th><th>Perimetre</th><th>Motif</th><th>Du</th><th>Au</th><th>Etat</th><th>Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="d in delegations" :key="d.id">
                    <td><strong>{{ d.beneficiaire_nom }}</strong><br/><span style="font-size:12px;color:#666">{{ d.beneficiaire_profil }}</span></td>
                    <td>{{ d.perimetre }}</td>
                    <td style="max-width:200px;font-size:13px">{{ d.motif }}</td>
                    <td>{{ formaterDate(d.date_debut) }}</td>
                    <td>{{ formaterDate(d.date_fin) }}</td>
                    <td>
                      <span v-if="!d.active" style="color:#999;font-size:12px;font-weight:700">Revoquee</span>
                      <span v-else-if="d.expiree" style="color:#E65100;font-size:12px;font-weight:700">Expiree</span>
                      <span v-else style="color:#2E7D32;font-size:12px;font-weight:700">Active</span>
                    </td>
                    <td>
                      <button v-if="d.active && !d.expiree" class="btn btn-danger" style="font-size:12px;padding:4px 10px" @click="ouvrirRevocation(d)">Revoquer</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- NOTIFICATIONS -->
        <div v-if="page === 'notifications'">
          <div class="carte">
            <div class="carte-titre">Notifications</div>
            <div v-if="notifications.length === 0" class="msg-vide">Aucune notification.</div>
            <div v-else>
              <div v-for="n in notifications" :key="n.id" :class="['notif-item', { 'non-lue': !n.lue }]">
                <div>{{ n.message }}</div>
                <div class="notif-item-heure">{{ formaterDateHeure(n.date) }}</div>
              </div>
            </div>
          </div>
        </div>

      </main>
    <PiedPage />
    </div>

    <!-- Modal imputation -->
    <div v-if="courrierAImputer" class="modal-fond">
      <div class="modal" style="max-width:620px">
        <div class="modal-titre">Imputer le courrier</div>
        <div style="background:#f5f8ff;padding:12px;border-radius:6px;margin-bottom:16px;font-size:13px">
          <strong>{{ courrierAImputer.numero_officiel }}</strong> — {{ courrierAImputer.objet }}<br/>
          <span style="color:#666">{{ courrierAImputer.expediteur }}</span>
        </div>
        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Destinataire principal</label>
          <select v-model="imputation.destinataire_id">
            <option value="">-- Choisir un destinataire --</option>
            <option v-for="d in destinataires" :key="d.id" :value="d.id">{{ d.prenom }} {{ d.nom }} — {{ d.entite }}</option>
          </select>
        </div>
        <div class="champ" style="margin-bottom:14px">
          <label>Destinataires en copie (facultatif)</label>
          <div style="border:1px solid #ddd;border-radius:6px;padding:10px;max-height:120px;overflow-y:auto">
            <label v-for="d in destinataires" :key="d.id" style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:13px;cursor:pointer">
              <input type="checkbox" :value="d.id" v-model="imputation.copies_ids" :disabled="d.id == imputation.destinataire_id" />
              {{ d.prenom }} {{ d.nom }} — {{ d.entite }}
            </label>
          </div>
        </div>
        <div style="margin-bottom:14px">
          <label style="font-weight:600;font-size:13px;display:block;margin-bottom:8px" class="champ-obligatoire">Consignes types (au moins une)</label>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <label v-for="c in consignesTypes" :key="c.code" style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;padding:6px;border:1px solid #eee;border-radius:4px">
              <input type="checkbox" :value="c.code" v-model="imputation.consignes_types" style="accent-color:#1565C0" />
              {{ c.label }}
            </label>
          </div>
        </div>
        <div class="champ" style="margin-bottom:14px">
          <label>Consigne specifique (facultatif)</label>
          <textarea v-model="imputation.consigne_libre" rows="3" placeholder="Instructions specifiques..."></textarea>
        </div>
        <p v-if="erreurImputation" class="msg-erreur">{{ erreurImputation }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="courrierAImputer = null">Annuler</button>
          <button class="btn btn-primary" @click="confirmerImputation" :disabled="enEnvoi">{{ enEnvoi ? 'Imputation en cours...' : 'Valider l imputation' }}</button>
        </div>
      </div>
    <PiedPage />
    </div>

    <!-- Modal nouvelle delegation -->
    <div v-if="afficherFormDeleg" class="modal-fond">
      <div class="modal" style="max-width:580px">
        <div class="modal-titre">Accorder une delegation</div>
        <p style="font-size:13px;color:#666;margin-bottom:16px">Les droits accordes sont exclusivement en lecture. La delegation expire automatiquement a la date prevue.</p>

        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Beneficiaire</label>
          <select v-model="formDeleg.beneficiaire_id">
            <option value="">-- Choisir un agent --</option>
            <option v-for="u in utilisateurs" :key="u.id" :value="u.id">{{ u.prenom }} {{ u.nom }} ({{ u.profil }}) — {{ u.entite }}</option>
          </select>
        </div>
        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Perimetre de la delegation</label>
          <select v-model="formDeleg.perimetre">
            <option value="">-- Choisir --</option>
            <option value="COURRIER">Un courrier specifique</option>
            <option value="PERIODE">Une periode donnee</option>
            <option value="FONDS">Un fonds d archive</option>
            <option value="DOSSIER">Un dossier thematique</option>
          </select>
        </div>

        <!-- Detail perimetre COURRIER -->
        <div v-if="formDeleg.perimetre === 'COURRIER'" class="champ" style="margin-bottom:14px">
          <label>Numero du courrier vise</label>
          <input v-model="formDeleg.courrier_id" type="text" placeholder="ID du courrier (laisser vide pour tous)" />
        </div>

        <!-- Detail perimetre PERIODE -->
        <div v-if="formDeleg.perimetre === 'PERIODE'" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
          <div class="champ"><label>Debut periode</label><input v-model="formDeleg.periode_debut" type="date" /></div>
          <div class="champ"><label>Fin periode</label><input v-model="formDeleg.periode_fin_perim" type="date" /></div>
        </div>

        <!-- Detail perimetre FONDS -->
        <div v-if="formDeleg.perimetre === 'FONDS'" class="champ" style="margin-bottom:14px">
          <label>Fonds d archive vise</label>
          <select v-model="formDeleg.fonds_vise">
            <option value="ESCEP">ESCEP (2023-present)</option>
            <option value="EST">EST (2011-2023)</option>
            <option value="CNIPT">CNIPT (1969-2011)</option>
            <option value="AUTRE">Autre</option>
          </select>
        </div>

        <!-- Detail perimetre DOSSIER -->
        <div v-if="formDeleg.perimetre === 'DOSSIER'" class="champ" style="margin-bottom:14px">
          <label>Dossier thematique</label>
          <input v-model="formDeleg.dossier_thematique" type="text" placeholder="Ex: Conseil d Administration 2026" />
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
          <div class="champ"><label class="champ-obligatoire">Date de debut</label><input v-model="formDeleg.date_debut" type="date" /></div>
          <div class="champ"><label class="champ-obligatoire">Date de fin</label><input v-model="formDeleg.date_fin" type="date" /></div>
        </div>
        <div class="champ" style="margin-bottom:14px">
          <label class="champ-obligatoire">Motif de la delegation</label>
          <textarea v-model="formDeleg.motif" rows="3" placeholder="Justification obligatoire — sera enregistree dans le journal d audit"></textarea>
        </div>

        <p v-if="erreurDeleg" class="msg-erreur">{{ erreurDeleg }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="afficherFormDeleg = false">Annuler</button>
          <button class="btn btn-primary" @click="creerDelegation" :disabled="enEnvoi">{{ enEnvoi ? 'Creation...' : 'Accorder la delegation' }}</button>
        </div>
      </div>
    <PiedPage />
    </div>

    <!-- Modal revocation -->
    <div v-if="delegationARevoque" class="modal-fond">
      <div class="modal">
        <div class="modal-titre">Revoquer la delegation</div>
        <p style="font-size:14px;margin-bottom:12px">Beneficiaire : <strong>{{ delegationARevoque.beneficiaire_nom }}</strong></p>
        <div class="champ">
          <label>Motif de revocation (facultatif)</label>
          <textarea v-model="motifRevocation" rows="3" placeholder="Raison de la revocation..."></textarea>
        </div>
        <p v-if="erreurRevocation" class="msg-erreur">{{ erreurRevocation }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="delegationARevoque = null">Annuler</button>
          <button class="btn btn-danger" @click="confirmerRevocation" :disabled="enEnvoi">Confirmer la revocation</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import PiedPage from '../components/PiedPage.vue'
import { useInactivite } from '../composables/useInactivite'
import { useParametres } from '../composables/useParametres'
import { useModules } from '../composables/useModules'
import { getApiClient } from '../composables/api'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

useInactivite()
const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')

const page             = ref('dashboard')
const chargement       = ref(false)
const chargementStats  = ref(false)
const chargementAudit  = ref(false)
const chargementDeleg  = ref(false)
const enEnvoi          = ref(false)
const tousCourriers    = ref([])
const destinataires    = ref([])
const utilisateurs     = ref([])
const consignesTypes   = ref([])
const notifications    = ref([])
const notifsNonLues    = ref(0)
const stats            = ref(null)
const entresAudit      = ref([])
const typesAction      = ref([])
const delegations      = ref([])
const courrierAImputer = ref(null)
const erreurImputation = ref('')
const afficherFormDeleg = ref(false)
const delegationARevoque = ref(null)
const motifRevocation  = ref('')
const erreurDeleg      = ref('')
const erreurRevocation = ref('')
const rechercheEnCours  = ref(false)
const rechercheEffectuee = ref(false)
const resultats = ref({ courriers: [], archives: [], total_courriers: 0, total_archives: 0 })

const imputation = ref({ destinataire_id: '', copies_ids: [], consignes_types: [], consigne_libre: '' })
const recherche  = ref({ q: '', type: '', statut: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false })
const filtreAudit = ref({ type_action: '', identifiant: '', date_debut: '', date_fin: '', issue: '', q: '' })
const formDeleg  = ref({ beneficiaire_id: '', perimetre: '', motif: '', date_debut: '', date_fin: '', courrier_id: '', periode_debut: '', periode_fin_perim: '', fonds_vise: '', dossier_thematique: '' })

const titresPages = {
  dashboard: 'Tableau de bord', a_imputer: 'Courriers a imputer',
  en_cours: 'Courriers en cours', tous: 'Tous les courriers',
  statistiques: 'Statistiques', recherche: 'Recherche documentaire',
  audit: 'Journal d audit', delegations: 'Delegations ponctuelles',
  notifications: 'Notifications',
}

const aImputer    = computed(() => tousCourriers.value.filter(c => c.statut === 'EN_ATT_IMP'))
const enCours     = computed(() => tousCourriers.value.filter(c => ['IMPUTE','EN_COURS'].includes(c.statut)))
const traites     = computed(() => tousCourriers.value.filter(c => ['TRAITE','ARCHIVE'].includes(c.statut)))
const nonConsultes = computed(() => {
  const limite = new Date(); limite.setDate(limite.getDate() - 3)
  return tousCourriers.value.filter(c => c.statut === 'IMPUTE' && new Date(c.date_imputation) < limite)
})

const api = getApiClient()

async function chargerCourriers() {
  chargement.value = true
  try { tousCourriers.value = (await api.get('/courriers/')).data }
  catch(e) { console.error(e) } finally { chargement.value = false }
}

const filtrePeriode = ref('mois')
const filtreDebut   = ref('')
const filtreFin     = ref('')

async function chargerStats() {
  chargementStats.value = true
  try {
    const params = { periode: filtrePeriode.value }
    if (filtreDebut.value) params.date_debut = filtreDebut.value
    if (filtreFin.value)   params.date_fin   = filtreFin.value
    stats.value = (await api.get('/dashboard/statistiques/', { params })).data
  }
  catch(e) { console.error(e) } finally { chargementStats.value = false }
}
async function chargerAudit() {
  chargementAudit.value = true
  try {
    const params = {}
    Object.entries(filtreAudit.value).forEach(([k,v]) => { if (v) params[k] = v })
    const rep = await api.get('/audit/', { params })
    entresAudit.value = rep.data.entrees
    typesAction.value = rep.data.types_action
  } catch(e) { console.error(e) } finally { chargementAudit.value = false }
}

async function chargerDelegations() {
  chargementDeleg.value = true
  try {
    const [rd, ru] = await Promise.all([api.get('/delegations/'), api.get('/utilisateurs/')])
    delegations.value = rd.data
    utilisateurs.value = ru.data
  } catch(e) { console.error(e) } finally { chargementDeleg.value = false }
}

async function chargerNotifications() {
  try { notifications.value = (await api.get('/notifications/')).data.notifications || [] }
  catch(e) {}
}

async function compterNotifications() {
  try { notifsNonLues.value = (await api.get('/notifications/count/')).data.non_lues || 0 }
  catch(e) {}
}

async function ouvrirImputation(courrier) {
  courrierAImputer.value = courrier
  erreurImputation.value = ''
  imputation.value = { destinataire_id: '', copies_ids: [], consignes_types: [], consigne_libre: '' }
  try {
    const [rd, rc] = await Promise.all([api.get('/destinataires/'), api.get('/consignes-types/')])
    destinataires.value  = rd.data
    consignesTypes.value = rc.data
  } catch(e) {}
}

async function confirmerImputation() {
  erreurImputation.value = ''
  if (!imputation.value.destinataire_id) { erreurImputation.value = 'Veuillez choisir un destinataire principal.'; return }
  if (!imputation.value.consignes_types.length) { erreurImputation.value = 'Veuillez cocher au moins une consigne type.'; return }
  enEnvoi.value = true
  try {
    await api.patch(`/courriers/${courrierAImputer.value.id}/imputer/`, imputation.value)
    courrierAImputer.value = null
    chargerCourriers()
  } catch(e) {
    erreurImputation.value = e.response?.data?.detail || 'Erreur lors de l imputation.'
  } finally { enEnvoi.value = false }
}

async function creerDelegation() {
  erreurDeleg.value = ''
  if (!formDeleg.value.beneficiaire_id || !formDeleg.value.perimetre || !formDeleg.value.motif || !formDeleg.value.date_debut || !formDeleg.value.date_fin) {
    erreurDeleg.value = 'Tous les champs obligatoires doivent etre remplis.'
    return
  }
  enEnvoi.value = true
  try {
    await api.post('/delegations/', formDeleg.value)
    afficherFormDeleg.value = false
    formDeleg.value = { beneficiaire_id: '', perimetre: '', motif: '', date_debut: '', date_fin: '', courrier_id: '', periode_debut: '', periode_fin_perim: '', fonds_vise: '', dossier_thematique: '' }
    chargerDelegations()
  } catch(e) {
    erreurDeleg.value = e.response?.data?.detail || 'Erreur lors de la creation.'
  } finally { enEnvoi.value = false }
}

function ouvrirRevocation(delegation) {
  delegationARevoque.value = delegation
  motifRevocation.value    = ''
  erreurRevocation.value   = ''
}

async function confirmerRevocation() {
  enEnvoi.value = true
  try {
    await api.patch(`/delegations/${delegationARevoque.value.id}/revoquer/`, { motif: motifRevocation.value })
    delegationARevoque.value = null
    chargerDelegations()
  } catch(e) {
    erreurRevocation.value = 'Erreur lors de la revocation.'
  } finally { enEnvoi.value = false }
}

async function lancerRecherche() {
  rechercheEnCours.value = true
  rechercheEffectuee.value = true
  try {
    const params = {}
    Object.entries(recherche.value).forEach(([k, v]) => { if (v && v !== false) params[k] = k === 'avec_archives' ? 'true' : v })
    resultats.value = (await api.get('/recherche/', { params })).data
  } catch(e) { console.error(e) } finally { rechercheEnCours.value = false }
}

function reinitRecherche() {
  recherche.value = { q: '', type: '', statut: '', priorite: '', date_debut: '', date_fin: '', avec_archives: false }
  rechercheEffectuee.value = false
  resultats.value = { courriers: [], archives: [], total_courriers: 0, total_archives: 0 }
}

function reinitAudit() {
  filtreAudit.value = { type_action: '', identifiant: '', date_debut: '', date_fin: '', issue: '', q: '' }
  chargerAudit()
}

function formaterDate(d) { return d ? new Date(d).toLocaleDateString('fr-FR') : '' }
function formaterDateHeure(d) { return d ? new Date(d).toLocaleString('fr-FR') : '' }
function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/')
}

let intervalle
onMounted(async () => {
  await useParametres()
  await useModules()
  chargerCourriers()
  compterNotifications()
  intervalle = setInterval(compterNotifications, 30000)
})
onUnmounted(() => clearInterval(intervalle))

async function exporterExcel() {
  try {
    const params = { periode: filtrePeriode.value }
    if (filtreDebut.value) params.date_debut = filtreDebut.value
    if (filtreFin.value)   params.date_fin   = filtreFin.value

    const rep = await api.get('/dashboard/export/excel/', {
      params,
      responseType: 'blob'
    })

    const url  = URL.createObjectURL(new Blob([rep.data]))
    const lien = document.createElement('a')
    lien.href  = url
    lien.setAttribute('download', `statistiques_ged.xlsx`)
    document.body.appendChild(lien)
    lien.click()
    document.body.removeChild(lien)
    URL.revokeObjectURL(url)
  } catch(e) {
    console.error('Erreur export Excel', e)
  }
}

async function exporterPdf() {
  try {
    const params = { periode: filtrePeriode.value }
    if (filtreDebut.value) params.date_debut = filtreDebut.value
    if (filtreFin.value)   params.date_fin   = filtreFin.value

    const rep = await api.get('/dashboard/export/pdf/', {
      params,
      responseType: 'blob'
    })

    const url  = URL.createObjectURL(new Blob([rep.data], { type: 'application/pdf' }))
    const lien = document.createElement('a')
    lien.href  = url
    lien.setAttribute('download', `statistiques_ged.pdf`)
    document.body.appendChild(lien)
    lien.click()
    document.body.removeChild(lien)
    URL.revokeObjectURL(url)
  } catch(e) {
    console.error('Erreur export PDF', e)
  }
}
</script>

<style scoped src="../assets/layout.css" />
