<template>
  <div class="app-layout">

    <aside class="sidebar">
      <div class="sidebar-logo">
        <img v-if="logoUrl" :src="logoUrl" alt="Logo" />
        <img v-else src="../assets/logo_escep.png" alt="ESCEP-Niger" />
      </div>
      <div class="sidebar-profil">
        <div class="sidebar-profil-nom">{{ prenom }} {{ nom }}</div>
        <div class="sidebar-profil-role">Administrateur Système</div>
      </div>
      <nav class="sidebar-nav">

        <button :class="['nav-item', { actif: page === 'supervision' }]" @click="page = 'supervision'; chargerSupervision()">
          <span class="nav-item-icone"><i class="fa-solid fa-gauge"></i></span>
          Supervision
        </button>

        <div class="nav-section-titre">Comptes</div>
        <button :class="['nav-sous-item', { actif: page === 'comptes' }]" @click="page = 'comptes'; chargerUtilisateurs()">
          <span class="nav-item-icone"><i class="fa-solid fa-users"></i></span>
          Utilisateurs
        </button>
        <button :class="['nav-sous-item', { actif: page === 'nouveau_compte' }]" @click="page = 'nouveau_compte'; chargerDirections()">
          <span class="nav-item-icone"><i class="fa-solid fa-user-plus"></i></span>
          Nouveau compte
        </button>
        <button :class="['nav-sous-item', { actif: page === 'directions' }]" @click="page = 'directions'; chargerDirections()">
          <span class="nav-item-icone"><i class="fa-solid fa-building"></i></span>
          Directions
        </button>

        <div class="nav-section-titre">Système</div>
        <button :class="['nav-sous-item', { actif: page === 'parametres' }]" @click="page = 'parametres'; chargerParametres()">
          <span class="nav-item-icone"><i class="fa-solid fa-sliders"></i></span>
          Paramètres
        </button>
        <button :class="['nav-sous-item', { actif: page === 'securite' }]" @click="page = 'securite'; chargerParametres()">
          <span class="nav-item-icone"><i class="fa-solid fa-shield-halved"></i></span>
          Sécurité
        </button>
        <button :class="['nav-sous-item', { actif: page === 'journal' }]" @click="page = 'journal'; chargerJournal()">
          <span class="nav-item-icone"><i class="fa-solid fa-list-check"></i></span>
          Journal d'audit
        </button>

      </nav>
      <div class="sidebar-bas">
        <button class="nav-item" @click="seDeconnecter">
          <span class="nav-item-icone"><i class="fa-solid fa-right-from-bracket"></i></span>
          Déconnexion
        </button>
      </div>
    </aside>

    <div class="main-zone">
      <header class="topbar">
        <span class="topbar-titre">{{ titresPages[page] }}</span>
        <div class="topbar-droite">
          <span style="font-size:12px;color:#999;font-style:italic">Accès technique — aucun accès au contenu des courriers</span>
        </div>
      </header>

      <main class="page-contenu">

        <!-- SUPERVISION -->
        <div v-if="page === 'supervision'">
          <div v-if="chargement" class="msg-vide">Chargement...</div>
          <div v-else-if="supervision">
            <div class="stats-grille">
              <div class="stat-card">
                <div class="stat-icone bleu"><i class="fa-solid fa-users" style="font-size:22px"></i></div>
                <div><div class="stat-valeur">{{ supervision.utilisateurs.total }}</div><div class="stat-label">Comptes total</div></div>
              </div>
              <div class="stat-card">
                <div class="stat-icone vert"><i class="fa-solid fa-circle-check" style="font-size:22px"></i></div>
                <div><div class="stat-valeur">{{ supervision.utilisateurs.actifs }}</div><div class="stat-label">Actifs</div></div>
              </div>
              <div class="stat-card">
                <div class="stat-icone rouge"><i class="fa-solid fa-lock" style="font-size:22px"></i></div>
                <div><div class="stat-valeur">{{ supervision.utilisateurs.verrouilles }}</div><div class="stat-label">Verrouillés</div></div>
              </div>
              <div class="stat-card">
                <div class="stat-icone jaune"><i class="fa-solid fa-triangle-exclamation" style="font-size:22px"></i></div>
                <div><div class="stat-valeur">{{ supervision.audit.acces_refuses }}</div><div class="stat-label">Accès refusés</div></div>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
              <div class="carte">
                <div class="carte-titre">Volumétrie système</div>
                <div v-for="(val, label) in {'Total courriers': supervision.volumetrie.total_courriers, 'Archives historiques': supervision.volumetrie.total_archives, 'Entrées journal': supervision.audit.total_entrees}" :key="label"
                  style="display:flex;justify-content:space-between;padding:10px;background:#f5f8ff;border-radius:6px;margin-bottom:8px">
                  <span style="font-size:14px;color:#444">{{ label }}</span>
                  <strong style="color:#1565C0">{{ val }}</strong>
                </div>
              </div>
              <div class="carte">
                <div class="carte-titre">Informations système</div>
                <div v-for="(val, label) in {'Version Django': supervision.systeme.django_version, 'Heure serveur': supervision.systeme.heure_serveur, 'Dernière action': supervision.audit.derniere_action}" :key="label"
                  style="display:flex;justify-content:space-between;padding:10px;background:#f5f8ff;border-radius:6px;margin-bottom:8px">
                  <span style="font-size:14px;color:#444">{{ label }}</span>
                  <strong style="color:#1565C0;font-size:13px">{{ val }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- COMPTES UTILISATEURS -->
        <div v-if="page === 'comptes'">
          <div class="carte">
            <div class="carte-titre">Gestion des utilisateurs</div>
            <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
              <input v-model="filtreUsers" type="text" placeholder="Nom, identifiant, direction..."
                style="flex:1;min-width:200px;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
              <select v-model="filtreProfil" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                <option value="">Tous les profils</option>
                <option value="DG">DG</option>
                <option value="ASSIST">Assistant DG</option>
                <option value="BO">Bureau d'Ordre</option>
                <option value="DEST">Destinataire</option>
                <option value="ARC">Archiviste</option>
                <option value="ADMIN">Administrateur</option>
              </select>
              <select v-model="filtreEtat" style="padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                <option value="">Tous</option>
                <option value="actif">Actifs</option>
                <option value="inactif">Inactifs</option>
                <option value="verrouille">Verrouillés</option>
              </select>
            </div>
            <div v-if="chargementUsers" class="msg-vide">Chargement...</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead>
                  <tr><th>Identifiant</th><th>Nom</th><th>Profil</th><th>Direction</th><th>Modules extra</th><th>2FA</th><th>État</th><th>MDP</th><th>Actions</th></tr>
                </thead>
                <tbody>
                  <tr v-for="u in utilisateursFiltres" :key="u.id">
                    <td><strong>{{ u.identifiant }}</strong></td>
                    <td>{{ u.prenom }} {{ u.nom }}</td>
                    <td><span class="badge badge-en_verif" style="font-size:11px">{{ u.profil }}</span></td>
                    <td style="font-size:12px">{{ u.direction_nom || '-' }}</td>
                    <td style="font-size:11px;color:#666">
                      {{ (u.modules_actifs && u.modules_actifs.length) ? u.modules_actifs.join(', ') : '-' }}
                    </td>
                    <td style="font-size:12px">
                      <span :style="{ color: u.double_auth_active ? '#2E7D32' : '#999' }">
                        {{ u.double_auth_active ? 'Oui' : 'Non' }}
                      </span>
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
                        <button class="btn btn-outline" style="font-size:11px;padding:3px 8px" @click="ouvrirModif(u)">Modifier</button>
                        <button v-if="u.est_verrouille" class="btn btn-success" style="font-size:11px;padding:3px 8px" @click="deverrouiller(u)">Déverrouiller</button>
                        <button :class="u.is_active ? 'btn btn-danger' : 'btn btn-success'" style="font-size:11px;padding:3px 8px" @click="basculer(u)">
                          {{ u.is_active ? 'Désactiver' : 'Activer' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- NOUVEAU COMPTE -->
        <div v-if="page === 'nouveau_compte'">
          <div class="carte">
            <div class="carte-titre">Créer un nouveau compte</div>
            <div class="grille-form">
              <div class="champ"><label class="champ-obligatoire">Identifiant</label><input v-model="formCompte.identifiant" type="text" placeholder="Identifiant unique" /></div>
              <div class="champ"><label class="champ-obligatoire">Profil</label>
                <select v-model="formCompte.profil">
                  <option value="">-- Choisir --</option>
                  <option value="DG">Directeur Général</option>
                  <option value="ASSIST">Assistant DG</option>
                  <option value="BO">Bureau d'Ordre</option>
                  <option value="DEST">Destinataire</option>
                  <option value="ARC">Archiviste</option>
                  <option value="ADMIN">Administrateur</option>
                </select>
              </div>
              <div class="champ"><label class="champ-obligatoire">Nom</label><input v-model="formCompte.nom" type="text" /></div>
              <div class="champ"><label class="champ-obligatoire">Prénom</label><input v-model="formCompte.prenom" type="text" /></div>
              <div class="champ">
                <label :class="formCompte.profil === 'DEST' ? 'champ-obligatoire' : ''">Direction</label>
                <select v-model="formCompte.direction_id">
                  <option value="">-- Aucune --</option>
                  <option v-for="d in directions" :key="d.id" :value="d.id">{{ d.sigle ? d.sigle + ' — ' : '' }}{{ d.nom }}</option>
                </select>
              </div>
              <div class="champ"><label>Fonction</label><input v-model="formCompte.fonction" type="text" placeholder="Ex: Chef de département" /></div>
              <div class="champ"><label>Email</label><input v-model="formCompte.email" type="email" placeholder="Pour la double authentification" /></div>
              <div class="champ"><label class="champ-obligatoire">Mot de passe initial</label><input v-model="formCompte.password" type="password" placeholder="Min. 12 caractères" /></div>
            </div>

            <div style="margin-bottom:16px">
              <label style="font-weight:600;font-size:13px;display:block;margin-bottom:10px">
                Modules supplémentaires
                <span style="font-weight:400;color:#666;font-size:12px"> — s'ajoutent aux modules par défaut du profil</span>
              </label>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px">
                <label v-for="m in modulesDisponibles" :key="m.code"
                  style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;padding:10px;border:1px solid #eee;border-radius:6px;background:#fafafa">
                  <input type="checkbox" :value="m.code" v-model="formCompte.modules_actifs" style="accent-color:#1565C0;width:15px;height:15px" />
                  <div>
                    <div style="font-weight:600">{{ m.label }}</div>
                    <div style="font-size:11px;color:#888">{{ m.description }}</div>
                  </div>
                </label>
              </div>
            </div>

            <p v-if="erreurCompte" class="msg-erreur">{{ erreurCompte }}</p>
            <p v-if="msgSucces" class="msg-succes">{{ msgSucces }}</p>
            <div class="actions-form">
              <button class="btn btn-ghost" @click="reinitFormCompte">Effacer</button>
              <button class="btn btn-primary" @click="creerCompte" :disabled="enEnvoi">{{ enEnvoi ? 'Création...' : 'Créer le compte' }}</button>
            </div>
          </div>
        </div>

        <!-- DIRECTIONS -->
        <div v-if="page === 'directions'">
          <div class="carte">
            <div class="carte-titre">Directions et départements</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ"><label class="champ-obligatoire">Nom complet</label><input v-model="formDir.nom" type="text" placeholder="Ex: Département Informatique" /></div>
              <div class="champ"><label>Sigle</label><input v-model="formDir.sigle" type="text" placeholder="Ex: DEP/DI" /></div>
              <div class="champ"><label>Description</label><input v-model="formDir.description" type="text" /></div>
              <div class="champ"><label>Ordre d'affichage</label><input v-model="formDir.ordre" type="number" min="0" /></div>
            </div>
            <p v-if="erreurDir" class="msg-erreur">{{ erreurDir }}</p>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:20px">
              <button class="btn btn-primary" @click="creerDirection" :disabled="enEnvoi">Ajouter la direction</button>
            </div>
            <div v-if="directions.length === 0" class="msg-vide">Aucune direction configurée.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Sigle</th><th>Nom</th><th>Description</th><th>Ordre</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="d in directions" :key="d.id">
                    <td><strong>{{ d.sigle || '-' }}</strong></td>
                    <td>{{ d.nom }}</td>
                    <td style="font-size:12px">{{ d.description || '-' }}</td>
                    <td>{{ d.ordre }}</td>
                    <td>
                      <button class="btn btn-danger" style="font-size:12px;padding:4px 10px" @click="supprimerDirection(d)">Supprimer</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- PARAMÈTRES APPARENCE -->
        <div v-if="page === 'parametres'">
          <div class="carte">
            <div class="carte-titre">Paramètres de l'application</div>
            <div class="grille-form">
              <div class="champ champ-large"><label class="champ-obligatoire">Nom de l'application</label><input v-model="formParams.nom_application" type="text" /></div>
              <div class="champ champ-large"><label>Slogan</label><input v-model="formParams.slogan" type="text" /></div>
              <div class="champ champ-large"><label>Texte du pied de page</label><input v-model="formParams.texte_pied_page" type="text" /></div>

              <div class="champ">
                <label>Couleur principale</label>
                <div style="display:flex;gap:10px;align-items:center">
                  <input v-model="formParams.couleur_principale" type="color" style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
                  <input v-model="formParams.couleur_principale" type="text" style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
                </div>
              </div>
              <div class="champ">
                <label>Couleur accent</label>
                <div style="display:flex;gap:10px;align-items:center">
                  <input v-model="formParams.couleur_accent" type="color" style="width:50px;height:36px;padding:2px;border:1px solid #ddd;border-radius:4px;cursor:pointer" />
                  <input v-model="formParams.couleur_accent" type="text" style="flex:1;padding:9px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px" />
                </div>
              </div>

              <!-- Logo -->
              <div class="champ champ-large">
                <label>Logo de l'application</label>
                <input type="file" accept=".png,.jpg,.jpeg,.svg" @change="e => fichiers.logo = e.target.files[0]" />
                <div v-if="formParams.logo_url" style="display:flex;align-items:center;gap:12px;margin-top:10px;padding:10px;background:#f5f8ff;border-radius:6px">
                  <img :src="formParams.logo_url" style="height:50px;object-fit:contain" />
                  <button class="btn btn-danger" style="font-size:12px;padding:5px 12px" type="button" @click="supprimerLogo">
                    <i class="fa-solid fa-trash"></i> Supprimer le logo
                  </button>
                </div>
              </div>

              <!-- Image de fond -->
              <div class="champ champ-large">
                <label>Image de fond de la page de connexion</label>
                <small style="color:#666;display:block;margin-bottom:6px">L'image sera floutée automatiquement.</small>
                <input type="file" accept=".png,.jpg,.jpeg" @change="e => fichiers.fond = e.target.files[0]" />
                <div v-if="formParams.image_fond_url" style="margin-top:10px;border-radius:6px;overflow:hidden;position:relative">
                  <img :src="formParams.image_fond_url" style="width:100%;height:100px;object-fit:cover;display:block" />
                  <button class="btn btn-danger" style="position:absolute;top:8px;right:8px;font-size:12px;padding:5px 12px" type="button" @click="supprimerFond">
                    <i class="fa-solid fa-trash"></i> Supprimer
                  </button>
                </div>
              </div>

            </div>

            <!-- Aperçu couleurs -->
            <div style="margin-top:16px;padding:16px;border:1px solid #eee;border-radius:8px;background:#fafafa">
              <div style="font-size:13px;font-weight:600;color:#444;margin-bottom:12px">Aperçu des couleurs</div>
              <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">
                <div :style="{ background: formParams.couleur_principale, color:'#fff', padding:'8px 16px', borderRadius:'6px', fontSize:'13px' }">
                  Principale
                </div>
                <div :style="{ background: formParams.couleur_accent, color:'#333', padding:'8px 16px', borderRadius:'6px', fontSize:'13px' }">
                  Accent
                </div>
                <div style="flex:1;height:6px;border-radius:3px" :style="{ background: formParams.couleur_principale }"></div>
              </div>
            </div>

            <p v-if="msgParams" class="msg-succes" style="margin-top:12px">{{ msgParams }}</p>
            <div class="actions-form">
              <button class="btn btn-primary" @click="sauvegarderParams" :disabled="enEnvoi">
                {{ enEnvoi ? 'Enregistrement...' : 'Enregistrer et appliquer' }}
              </button>
            </div>
          </div>
        </div>

        <!-- SÉCURITÉ -->
        <div v-if="page === 'securite'">
          <div class="carte">
            <div class="carte-titre">Paramètres de sécurité</div>
            <div class="grille-form">
              <div class="champ">
                <label>Timeout d'inactivité (minutes)</label>
                <input v-model="formParams.timeout_inactivite" type="number" min="5" max="120" />
                <small style="color:#666;display:block;margin-top:4px">Durée avant déconnexion automatique</small>
              </div>
              <div class="champ">
                <label>Durée de validité du mot de passe (jours)</label>
                <input v-model="formParams.duree_validite_mdp" type="number" min="30" max="365" />
                <small style="color:#666;display:block;margin-top:4px">L'utilisateur devra changer son mot de passe après cette durée</small>
              </div>
              <div class="champ">
                <label>Tentatives avant verrouillage du compte</label>
                <input v-model="formParams.tentatives_max" type="number" min="3" max="10" />
              </div>
              <div class="champ champ-large" style="display:flex;align-items:center;gap:10px;padding-top:10px">
                <input type="checkbox" v-model="formParams.double_auth_active" id="2fa_global" style="accent-color:#1565C0;width:18px;height:18px;flex-shrink:0" />
                <div>
                  <label for="2fa_global" style="cursor:pointer;font-size:14px;font-weight:600;display:block">Activer la double authentification globalement</label>
                  <small style="color:#666">Les utilisateurs avec email configuré recevront un code à chaque connexion</small>
                </div>
              </div>
              <div class="champ"><label>Email expéditeur pour les codes 2FA</label><input v-model="formParams.email_expediteur" type="email" placeholder="noreply@escep.ne" /></div>
              <div class="champ champ-large">
                <label>Texte de l'email de vérification 2FA</label>
                <small style="color:#666;display:block;margin-bottom:6px">Utiliser <code style="background:#f5f5f5;padding:2px 4px;border-radius:3px">{code}</code> pour insérer le code automatiquement.</small>
                <textarea v-model="formParams.texte_email_2fa" rows="4" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px;font-family:inherit;box-sizing:border-box"></textarea>
              </div>
            </div>
            <p v-if="msgParams" class="msg-succes" style="margin-top:12px">{{ msgParams }}</p>
            <div class="actions-form">
              <button class="btn btn-primary" @click="sauvegarderParams" :disabled="enEnvoi">{{ enEnvoi ? 'Enregistrement...' : 'Enregistrer' }}</button>
            </div>
          </div>
        </div>

        <!-- JOURNAL D'AUDIT -->
        <div v-if="page === 'journal'">
          <div class="carte">
            <div class="carte-titre">Journal d'audit — Lecture seule</div>
            <div class="grille-form" style="margin-bottom:16px">
              <div class="champ"><label>Identifiant</label><input v-model="filtreJournal.identifiant" type="text" @keyup.enter="chargerJournal" /></div>
              <div class="champ"><label>Type d'action</label>
                <select v-model="filtreJournal.type_action">
                  <option value="">Tous</option>
                  <option v-for="t in typesAction" :key="t.code" :value="t.code">{{ t.label }}</option>
                </select>
              </div>
              <div class="champ"><label>Résultat</label>
                <select v-model="filtreJournal.issue">
                  <option value="">Tous</option>
                  <option value="SUCCES">Succès</option>
                  <option value="REFUS">Refus</option>
                  <option value="ERREUR">Erreur</option>
                </select>
              </div>
              <div class="champ"><label>Du</label><input v-model="filtreJournal.date_debut" type="date" /></div>
              <div class="champ"><label>Au</label><input v-model="filtreJournal.date_fin" type="date" /></div>
              <div class="champ champ-large"><label>Recherche</label><input v-model="filtreJournal.q" type="text" placeholder="Mot-clé dans la description..." @keyup.enter="chargerJournal" /></div>
            </div>
            <div class="actions-form" style="justify-content:flex-start;margin-bottom:16px">
              <button class="btn btn-primary" @click="chargerJournal">Filtrer</button>
              <button class="btn btn-ghost" @click="reinitJournal">Réinitialiser</button>
            </div>
            <p style="font-size:12px;color:#999;margin-bottom:10px">{{ entresJournal.length }} entrée(s) affichée(s) — maximum 500 par requête</p>
            <div v-if="chargementJournal" class="msg-vide">Chargement...</div>
            <div v-else-if="entresJournal.length === 0" class="msg-vide">Aucune entrée dans le journal.</div>
            <div v-else class="tableau-wrap">
              <table class="tableau">
                <thead><tr><th>Horodatage</th><th>Utilisateur</th><th>Profil</th><th>Action</th><th>Description</th><th>IP</th><th>Résultat</th></tr></thead>
                <tbody>
                  <tr v-for="e in entresJournal" :key="e.id">
                    <td style="white-space:nowrap;font-size:12px">{{ e.horodatage }}</td>
                    <td><strong>{{ e.identifiant }}</strong></td>
                    <td style="font-size:12px">{{ e.profil }}</td>
                    <td style="font-size:12px">{{ e.type_action }}</td>
                    <td style="font-size:12px;max-width:280px">{{ e.description }}</td>
                    <td style="font-size:12px">{{ e.adresse_ip || '-' }}</td>
                    <td><span :style="{ color: e.issue==='SUCCES'?'#2E7D32':e.issue==='REFUS'?'#D32F2F':'#E65100', fontWeight:'bold', fontSize:'12px' }">{{ e.issue }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </main>

      <PiedPage />
    </div>

    <!-- Modal modification compte -->
    <div v-if="compteAModifier" class="modal-fond">
      <div class="modal" style="max-width:620px">
        <div class="modal-titre">Modifier — {{ compteAModifier.identifiant }}</div>
        <div class="grille-form">
          <div class="champ"><label>Nom</label><input v-model="formModif.nom" type="text" /></div>
          <div class="champ"><label>Prénom</label><input v-model="formModif.prenom" type="text" /></div>
          <div class="champ"><label>Direction</label>
            <select v-model="formModif.direction_id">
              <option value="">-- Aucune --</option>
              <option v-for="d in directions" :key="d.id" :value="d.id">{{ d.sigle ? d.sigle+' — ' : '' }}{{ d.nom }}</option>
            </select>
          </div>
          <div class="champ"><label>Fonction</label><input v-model="formModif.fonction" type="text" /></div>
          <div class="champ"><label>Email</label><input v-model="formModif.email" type="email" /></div>
          <div class="champ"><label>Nouveau mot de passe</label><input v-model="formModif.password" type="password" placeholder="Laisser vide pour ne pas changer" /></div>
          <div class="champ champ-large" style="display:flex;align-items:center;gap:8px">
            <input type="checkbox" v-model="formModif.double_auth_active" id="2fa_user" style="accent-color:#1565C0;width:16px;height:16px;flex-shrink:0" />
            <label for="2fa_user" style="cursor:pointer;font-size:14px">Double authentification activée pour cet utilisateur</label>
          </div>
          <div class="champ champ-large" style="display:flex;align-items:center;gap:8px">
            <input type="checkbox" v-model="formModif.double_auth_desactive_admin" id="2fa_off" style="accent-color:#D32F2F;width:16px;height:16px;flex-shrink:0" />
            <label for="2fa_off" style="cursor:pointer;font-size:14px;color:#D32F2F">Désactiver la 2FA pour cet utilisateur (exception administrateur)</label>
          </div>
        </div>

        <div style="margin:16px 0">
          <label style="font-weight:600;font-size:13px;display:block;margin-bottom:4px">Modules supplémentaires</label>
          <small style="color:#666;font-size:12px;display:block;margin-bottom:10px">Ces modules s'ajoutent aux modules par défaut du profil {{ compteAModifier.profil }}.</small>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px">
            <label v-for="m in modulesDisponibles" :key="m.code"
              style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;padding:10px;border:1px solid #eee;border-radius:6px;background:#fafafa">
              <input type="checkbox" :value="m.code" v-model="formModif.modules_actifs" style="accent-color:#1565C0;width:15px;height:15px" />
              <div>
                <div style="font-weight:600">{{ m.label }}</div>
                <div style="font-size:11px;color:#888">{{ m.description }}</div>
              </div>
            </label>
          </div>
        </div>

        <p v-if="erreurModif" class="msg-erreur">{{ erreurModif }}</p>
        <div class="actions-form">
          <button class="btn btn-ghost" @click="compteAModifier = null">Annuler</button>
          <button class="btn btn-primary" @click="confirmerModif" :disabled="enEnvoi">{{ enEnvoi ? 'Enregistrement...' : 'Enregistrer' }}</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import PiedPage from '../components/PiedPage.vue'
import { useInactivite } from '../composables/useInactivite'
import { useParametres } from '../composables/useParametres'
import { clearModulesCache } from '../composables/useModules'
import { getApiClient } from '../composables/api'

useInactivite()

const router  = useRouter()
const token   = localStorage.getItem('access')
const payload = token ? JSON.parse(atob(token.split('.')[1])) : {}
const nom     = ref(payload.nom || '')
const prenom  = ref(payload.prenom || '')
const logoUrl = ref(null)

const page              = ref('supervision')
const chargement        = ref(false)
const chargementUsers   = ref(false)
const chargementJournal = ref(false)
const enEnvoi           = ref(false)
const supervision       = ref(null)
const utilisateurs      = ref([])
const directions        = ref([])
const entresJournal     = ref([])
const typesAction       = ref([])
const compteAModifier   = ref(null)
const filtreUsers       = ref('')
const filtreProfil      = ref('')
const filtreEtat        = ref('')
const erreurCompte      = ref('')
const msgSucces         = ref('')
const erreurDir         = ref('')
const erreurModif       = ref('')
const msgParams         = ref('')

// Modules avec descriptions claires
const modulesDisponibles = [
  { code: 'archives',     label: 'Archives historiques', description: 'Versement et consultation des archives CNIPT/EST' },
  { code: 'recherche',    label: 'Recherche documentaire', description: 'Recherche multicritères dans tous les documents' },
  { code: 'statistiques', label: 'Statistiques',           description: 'Tableau de bord et indicateurs' },
  { code: 'audit',        label: 'Journal d\'audit',       description: 'Consultation du journal d\'audit' },
  { code: 'delegations',  label: 'Délégations',            description: 'Gestion des délégations ponctuelles' },
]

const formCompte = ref({ identifiant:'', profil:'', nom:'', prenom:'', direction_id:'', fonction:'', email:'', password:'', modules_actifs:[] })
const formDir    = ref({ nom:'', sigle:'', description:'', ordre:0 })
const formModif  = ref({ nom:'', prenom:'', direction_id:'', fonction:'', email:'', password:'', double_auth_active:false, double_auth_desactive_admin:false, modules_actifs:[] })
const formParams = ref({ nom_application:'', slogan:'', texte_pied_page:'', couleur_principale:'#1565C0', couleur_accent:'#FDD835', timeout_inactivite:30, duree_validite_mdp:90, tentatives_max:5, double_auth_active:false, email_expediteur:'', texte_email_2fa:'', logo_url:null, image_fond_url:null })
const fichiers   = ref({ logo:null, fond:null, supprimer_logo:false, supprimer_fond:false })
const filtreJournal = ref({ identifiant:'', type_action:'', issue:'', date_debut:'', date_fin:'', q:'' })

const titresPages = {
  supervision:    'Supervision technique',
  comptes:        'Gestion des utilisateurs',
  nouveau_compte: 'Nouveau compte',
  directions:     'Directions et départements',
  parametres:     'Paramètres de l\'application',
  securite:       'Sécurité',
  journal:        'Journal d\'audit',
}

const utilisateursFiltres = computed(() => {
  return utilisateurs.value.filter(u => {
    const q = filtreUsers.value.toLowerCase()
    const matchTexte = !q
      || u.nom.toLowerCase().includes(q)
      || u.prenom.toLowerCase().includes(q)
      || u.identifiant.toLowerCase().includes(q)
      || (u.direction_nom || '').toLowerCase().includes(q)
    const matchProfil = !filtreProfil.value || u.profil === filtreProfil.value
    const matchEtat   = !filtreEtat.value
      || (filtreEtat.value === 'actif'      && u.is_active && !u.est_verrouille)
      || (filtreEtat.value === 'inactif'    && !u.is_active)
      || (filtreEtat.value === 'verrouille' && u.est_verrouille)
    return matchTexte && matchProfil && matchEtat
  })
})

const api = getApiClient()

async function chargerSupervision() {
  chargement.value = true
  try { supervision.value = (await api.get('/supervision/')).data }
  catch(e) { console.error(e) } finally { chargement.value = false }
}

async function chargerUtilisateurs() {
  chargementUsers.value = true
  try { utilisateurs.value = (await api.get('/utilisateurs/')).data }
  catch(e) { console.error(e) } finally { chargementUsers.value = false }
}

async function chargerDirections() {
  try { directions.value = (await api.get('/directions/')).data }
  catch(e) { console.error(e) }
}

async function chargerParametres() {
  try {
    const rep = await api.get('/parametres/')
    formParams.value = { ...formParams.value, ...rep.data }
  } catch(e) { console.error(e) }
}

async function chargerJournal() {
  chargementJournal.value = true
  try {
    const params = {}
    Object.entries(filtreJournal.value).forEach(([k, v]) => { if (v) params[k] = v })
    const rep = await api.get('/audit/', { params })
    entresJournal.value = rep.data.entrees    || []
    typesAction.value   = rep.data.types_action || []
  } catch(e) { console.error(e) } finally { chargementJournal.value = false }
}

async function creerCompte() {
  erreurCompte.value = ''
  msgSucces.value    = ''
  if (!formCompte.value.identifiant || !formCompte.value.profil || !formCompte.value.nom || !formCompte.value.prenom || !formCompte.value.password) {
    erreurCompte.value = 'Les champs obligatoires (*) doivent être remplis.'
    return
  }
  enEnvoi.value = true
  try {
    await api.post('/utilisateurs/creer/', formCompte.value)
    msgSucces.value = `Compte "${formCompte.value.identifiant}" créé avec succès.`
    reinitFormCompte()
  } catch(e) {
    erreurCompte.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally { enEnvoi.value = false }
}

function reinitFormCompte() {
  formCompte.value = { identifiant:'', profil:'', nom:'', prenom:'', direction_id:'', fonction:'', email:'', password:'', modules_actifs:[] }
}

async function creerDirection() {
  erreurDir.value = ''
  if (!formDir.value.nom.trim()) { erreurDir.value = 'Le nom est obligatoire.'; return }
  enEnvoi.value = true
  try {
    await api.post('/directions/', formDir.value)
    formDir.value = { nom:'', sigle:'', description:'', ordre:0 }
    chargerDirections()
  } catch(e) {
    erreurDir.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally { enEnvoi.value = false }
}

async function supprimerDirection(dir) {
  if (!confirm(`Supprimer la direction "${dir.nom}" ?`)) return
  try {
    await api.delete(`/directions/${dir.id}/`)
    chargerDirections()
  } catch(e) { console.error(e) }
}

function ouvrirModif(u) {
  compteAModifier.value = u
  formModif.value = {
    nom:    u.nom,
    prenom: u.prenom,
    direction_id: u.direction_id || '',
    fonction:     u.fonction     || '',
    email:        u.email        || '',
    password:     '',
    double_auth_active:          u.double_auth_active,
    double_auth_desactive_admin: u.double_auth_desactive_admin,
    modules_actifs: [...(u.modules_actifs || [])],
  }
  erreurModif.value = ''
}

async function confirmerModif() {
  enEnvoi.value     = true
  erreurModif.value = ''
  try {
    const idModifie = compteAModifier.value.id // Sauvegarder l'ID avant de réinitialiser
    await api.patch(`/utilisateurs/${compteAModifier.value.id}/modifier/`, formModif.value)
    clearModulesCache() // Invalider le cache des modules pour l'utilisateur modifié
    compteAModifier.value = null
    chargerUtilisateurs()
    // Si l'admin a modifié les modules du user actuellement connecté, recharger ses modules
    if (idModifie == payload.id) {
      const rep = await api.get('/moi/')
      localStorage.setItem('modules', JSON.stringify(rep.data.modules || []))
    }
  } catch(e) {
    erreurModif.value = e.response?.data?.detail || 'Erreur lors de la modification.'
  } finally { enEnvoi.value = false }
}

async function basculer(u) {
  enEnvoi.value = true
  try {
    await api.patch(`/utilisateurs/${u.id}/basculer/`)
    chargerUtilisateurs()
  } catch(e) { console.error(e) } finally { enEnvoi.value = false }
}

async function deverrouiller(u) {
  try {
    await api.patch(`/utilisateurs/${u.id}/deverrouiller/`)
    chargerUtilisateurs()
  } catch(e) { console.error(e) }
}

// Suppression des images
function supprimerLogo() {
  formParams.value.logo_url   = null
  fichiers.value.supprimer_logo = true
}

function supprimerFond() {
  formParams.value.image_fond_url = null
  fichiers.value.supprimer_fond   = true
}

async function sauvegarderParams() {
  msgParams.value = ''
  enEnvoi.value   = true
  try {
    const donnees = new FormData()
    Object.entries(formParams.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined && !['logo_url', 'image_fond_url'].includes(k)) {
        donnees.append(k, v)
      }
    })
    if (fichiers.value.logo)            donnees.append('logo',            fichiers.value.logo)
    if (fichiers.value.fond)            donnees.append('image_fond_login', fichiers.value.fond)
    if (fichiers.value.supprimer_logo)  donnees.append('supprimer_logo',   'true')
    if (fichiers.value.supprimer_fond)  donnees.append('supprimer_fond',   'true')

    await api.patch('/parametres/', donnees, { headers: { 'Content-Type': 'multipart/form-data' } })

    // Forcer un reload du cache et appliquer immédiatement
    await useParametres(true)

    msgParams.value = 'Paramètres enregistrés et appliqués.'
    fichiers.value  = { logo:null, fond:null, supprimer_logo:false, supprimer_fond:false }
    setTimeout(() => msgParams.value = '', 4000)
  } catch(e) {
    msgParams.value = 'Erreur lors de l\'enregistrement.'
  } finally { enEnvoi.value = false }
}

function reinitJournal() {
  filtreJournal.value = { identifiant:'', type_action:'', issue:'', date_debut:'', date_fin:'', q:'' }
  chargerJournal()
}

function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/')
}

onMounted(async () => {
  chargerSupervision()
  chargerDirections()
  // Charger les paramètres publics pour le logo et les couleurs
  const p = await useParametres()
  if (p.logo_url) logoUrl.value = p.logo_url
})
</script>

<style scoped src="../assets/layout.css" />
