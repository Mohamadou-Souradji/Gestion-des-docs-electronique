<template>
  <div class="super-admin-layout">

    <!-- ═══ SIDEBAR SUPER-ADMIN ═══ -->
    <aside class="super-sidebar">
      <div class="super-sidebar-header">
        <div class="super-logo">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <div>
          <div class="super-titre">Super Admin</div>
          <div class="super-sous-titre">GED SaaS</div>
        </div>
      </div>

      <nav class="super-nav">
        <div class="super-nav-section">Gestion</div>
        <button :class="['super-nav-item', { actif: section === 'organisations' }]" @click="section = 'organisations'">
          <i class="fa-solid fa-building"></i> Organisations
          <span class="super-badge">{{ organisations.length }}</span>
        </button>

        <div class="super-nav-section">Configuration</div>
        <button :class="['super-nav-item', { actif: section === 'securite' }]" @click="section = 'securite'">
          <i class="fa-solid fa-lock"></i> Sécurité globale
        </button>

        <div class="super-nav-section">Analyse</div>
        <button :class="['super-nav-item', { actif: section === 'supervision' }]" @click="section = 'supervision'">
          <i class="fa-solid fa-chart-line"></i> Supervision
        </button>
      </nav>

      <div class="super-sidebar-bas">
        <div class="super-user-info">
          <div class="super-user-avatar">
            <i class="fa-solid fa-user-shield"></i>
          </div>
          <div>
            <div style="font-weight:600;font-size:13px;color:#fff">{{ identifiant }}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6)">Super Administrateur</div>
          </div>
        </div>
        <button class="btn-deconnexion" @click="seDeconnecter">
          <i class="fa-solid fa-right-from-bracket"></i> Déconnexion
        </button>
      </div>
    </aside>

    <!-- ═══ CONTENU PRINCIPAL ═══ -->
    <main class="super-main">

      <!-- ─── ORGANISATIONS ─── -->
      <div v-if="section === 'organisations'">
        <div class="super-page-header">
          <div>
            <h1 class="super-page-titre">
              <i class="fa-solid fa-building"></i> Organisations
            </h1>
            <p class="super-page-sous-titre">
              {{ organisations.filter(o => o.active).length }} active(s) sur {{ organisations.length }}
            </p>
          </div>
          <button class="btn-super-primary" @click="ouvrirCreation">
            <i class="fa-solid fa-plus"></i> Nouvelle organisation
          </button>
        </div>

        <div v-if="chargement" class="super-chargement">
          <i class="fa-solid fa-spinner fa-spin"></i> Chargement...
        </div>

        <div v-else-if="organisations.length === 0" class="super-vide-total">
          <i class="fa-solid fa-building" style="font-size:48px;opacity:0.2;display:block;margin-bottom:12px"></i>
          <p>Aucune organisation. Créez votre première organisation.</p>
          <button class="btn-super-primary" style="margin-top:12px" @click="ouvrirCreation">
            <i class="fa-solid fa-plus"></i> Créer la première organisation
          </button>
        </div>

        <div v-else class="orgs-grille">
          <div v-for="org in organisations" :key="org.id" class="org-card">
            <div class="org-card-header" :style="{ background: `linear-gradient(135deg, ${org.couleur_principale}, ${org.couleur_principale}cc)` }">
              <div class="org-card-logo">
                <img v-if="org.logo_url" :src="org.logo_url" alt="Logo" />
                <i v-else class="fa-solid fa-building"></i>
              </div>
              <div class="org-card-badges">
                <span class="org-badge-plan">{{ org.plan }}</span>
                <span :class="['org-badge-statut', org.active ? 'statut-actif' : 'statut-inactif']">
                  {{ org.active ? '● Actif' : '● Inactif' }}
                </span>
              </div>
            </div>

            <div class="org-card-body">
              <h3 class="org-card-nom">{{ org.nom }}</h3>
              <p class="org-card-code"><i class="fa-solid fa-at"></i> {{ org.code_tenant }}</p>
              <p v-if="org.slogan" class="org-card-slogan">{{ org.slogan }}</p>
              <p v-if="org.domaine_personnalise" class="org-card-domaine">
                <i class="fa-solid fa-globe"></i> {{ org.domaine_personnalise }}
              </p>

              <div class="org-card-stats">
                <div class="org-stat">
                  <span class="org-stat-val">{{ org.utilisateurs_count }}</span>
                  <span class="org-stat-label">Utilisateurs</span>
                </div>
                <div class="org-stat">
                  <span class="org-stat-val">{{ org.max_utilisateurs }}</span>
                  <span class="org-stat-label">Max</span>
                </div>
                <div class="org-stat">
                  <div class="org-progress-bar">
                    <div class="org-progress-fill"
                      :style="{ width: `${Math.min(100, (org.utilisateurs_count / org.max_utilisateurs) * 100)}%`,
                                background: org.couleur_principale }">
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="org.admin_nom" class="org-admin-info">
                <i class="fa-solid fa-user-tie"></i> {{ org.admin_nom }}
              </div>
            </div>

            <div class="org-card-actions">
              <button class="btn-org-action btn-modifier" @click="ouvrirModification(org)" title="Modifier">
                <i class="fa-solid fa-pencil"></i> Modifier
              </button>
              <button class="btn-org-action btn-admins" @click="ouvrirAdmins(org)" title="Gérer admins">
                <i class="fa-solid fa-users-gear"></i> Admins
              </button>
              <button class="btn-org-action btn-securite-org" @click="ouvrirSecuriteOrg(org)" title="Sécurité">
                <i class="fa-solid fa-lock"></i> Sécu.
              </button>
              <button class="btn-org-action" :class="org.active ? 'btn-desactiver' : 'btn-activer'"
                @click="basculerOrg(org)">
                <i :class="org.active ? 'fa-solid fa-ban' : 'fa-solid fa-check'"></i>
                {{ org.active ? 'Désactiver' : 'Activer' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── SÉCURITÉ GLOBALE ─── -->
      <div v-if="section === 'securite'">
        <div class="super-page-header">
          <div>
            <h1 class="super-page-titre"><i class="fa-solid fa-lock"></i> Sécurité globale</h1>
            <p class="super-page-sous-titre">Configurez la sécurité pour chaque organisation</p>
          </div>
        </div>

        <div class="super-card">
          <div class="super-card-titre">
            <i class="fa-solid fa-building"></i> Sélectionner une organisation
          </div>
          <select v-model="orgSecuriteId" style="padding:9px 14px;border:1px solid #ddd;border-radius:6px;font-size:14px;width:100%;max-width:400px">
            <option value="">-- Choisir une organisation --</option>
            <option v-for="o in organisations" :key="o.id" :value="o.id">{{ o.nom }} ({{ o.code_tenant }})</option>
          </select>
          <button class="btn-super-primary" style="margin-top:12px" @click="chargerSecurite" :disabled="!orgSecuriteId">
            <i class="fa-solid fa-arrow-right"></i> Charger
          </button>
        </div>

        <div v-if="formSecurite.timeout_inactivite !== undefined" class="super-card" style="margin-top:16px">
          <div class="super-card-titre">
            <i class="fa-solid fa-sliders"></i> Paramètres de sécurité — {{ organisations.find(o => o.id == orgSecuriteId)?.nom }}
          </div>
          <div class="super-grille-form">
            <div class="super-champ">
              <label>Timeout inactivité (minutes)</label>
              <input v-model.number="formSecurite.timeout_inactivite" type="number" min="5" max="120" />
              <small>Durée avant déconnexion automatique</small>
            </div>
            <div class="super-champ">
              <label>Validité mot de passe (jours)</label>
              <input v-model.number="formSecurite.duree_validite_mdp" type="number" min="30" max="365" />
            </div>
            <div class="super-champ">
              <label>Tentatives avant verrouillage</label>
              <input v-model.number="formSecurite.tentatives_max" type="number" min="3" max="10" />
            </div>
            <div class="super-champ">
              <label>Email expéditeur (codes 2FA)</label>
              <input v-model="formSecurite.email_expediteur" type="email" placeholder="noreply@organisation.ne" />
              <small>Cet email enverra les codes de vérification</small>
            </div>
            <div class="super-champ super-champ-large">
              <div style="display:flex;align-items:center;gap:10px;padding:12px;background:#f5f8ff;border-radius:8px">
                <input type="checkbox" v-model="formSecurite.double_auth_active"
                  style="width:20px;height:20px;accent-color:#1a237e;cursor:pointer" />
                <div>
                  <label style="font-weight:600;font-size:14px;cursor:pointer;display:block">
                    Activer la double authentification (2FA)
                  </label>
                  <small style="color:#666">Les utilisateurs avec email recevront un code à chaque connexion</small>
                </div>
              </div>
            </div>
            <div v-if="formSecurite.double_auth_active" class="super-champ super-champ-large">
              <label>Texte de l'email 2FA</label>
              <small style="display:block;color:#666;margin-bottom:4px">Utilisez <code>{code}</code> pour insérer le code.</small>
              <textarea v-model="formSecurite.texte_email_2fa" rows="3"
                style="width:100%;padding:9px;border:1px solid #ddd;border-radius:6px;font-size:13px;box-sizing:border-box"></textarea>
            </div>
          </div>
          <p v-if="msgSecurite" :class="msgSecurite.includes('✅') ? 'super-msg-succes' : 'super-msg-erreur'">
            {{ msgSecurite }}
          </p>
          <div style="margin-top:16px">
            <button class="btn-super-primary" @click="sauvegarderSecurite" :disabled="enEnvoi">
              <i class="fa-solid fa-floppy-disk"></i>
              {{ enEnvoi ? 'Sauvegarde...' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ─── SUPERVISION ─── -->
      <div v-if="section === 'supervision'">
        <div class="super-page-header">
          <h1 class="super-page-titre"><i class="fa-solid fa-chart-line"></i> Supervision globale</h1>
        </div>
        <div class="supervision-grille">
          <div class="supervision-card">
            <div class="supervision-icone" style="background:#e8eaf6;color:#1a237e">
              <i class="fa-solid fa-building"></i>
            </div>
            <div>
              <div class="supervision-val">{{ organisations.length }}</div>
              <div class="supervision-label">Organisations</div>
            </div>
          </div>
          <div class="supervision-card">
            <div class="supervision-icone" style="background:#e8f5e9;color:#2e7d32">
              <i class="fa-solid fa-circle-check"></i>
            </div>
            <div>
              <div class="supervision-val">{{ organisations.filter(o => o.active).length }}</div>
              <div class="supervision-label">Actives</div>
            </div>
          </div>
          <div class="supervision-card">
            <div class="supervision-icone" style="background:#e3f2fd;color:#1565C0">
              <i class="fa-solid fa-users"></i>
            </div>
            <div>
              <div class="supervision-val">{{ totalUtilisateurs }}</div>
              <div class="supervision-label">Utilisateurs totaux</div>
            </div>
          </div>
          <div class="supervision-card">
            <div class="supervision-icone" style="background:#fff3e0;color:#e65100">
              <i class="fa-solid fa-crown"></i>
            </div>
            <div>
              <div class="supervision-val">{{ organisations.filter(o => o.plan === 'PRO' || o.plan === 'ENTERPRISE').length }}</div>
              <div class="supervision-label">Plans payants</div>
            </div>
          </div>
        </div>

        <!-- Tableau des organisations -->
        <div class="super-card" style="margin-top:24px">
          <div class="super-card-titre"><i class="fa-solid fa-table"></i> Vue d'ensemble</div>
          <div class="tableau-wrap">
            <table class="tableau">
              <thead>
                <tr>
                  <th>Organisation</th>
                  <th>Code</th>
                  <th>Plan</th>
                  <th>Utilisateurs</th>
                  <th>Admin</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="org in organisations" :key="org.id">
                  <td>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div class="mini-logo" :style="{ background: org.couleur_principale }">
                        <img v-if="org.logo_url" :src="org.logo_url" style="width:100%;height:100%;object-fit:contain" />
                        <i v-else class="fa-solid fa-building" style="font-size:10px;color:#fff"></i>
                      </div>
                      <span style="font-weight:600">{{ org.nom }}</span>
                    </div>
                  </td>
                  <td><code style="background:#f0f4ff;padding:2px 6px;border-radius:4px">{{ org.code_tenant }}</code></td>
                  <td><span class="badge-plan">{{ org.plan }}</span></td>
                  <td>{{ org.utilisateurs_count }} / {{ org.max_utilisateurs }}</td>
                  <td>{{ org.admin_nom || '—' }}</td>
                  <td>
                    <span :style="{ color: org.active ? '#2e7d32' : '#d32f2f', fontWeight:600, fontSize:'12px' }">
                      {{ org.active ? '● Actif' : '● Inactif' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </main>

    <!-- ═══ MODAL CRÉATION ORGANISATION ═══ -->
    <div v-if="modalCreation" class="super-modal-fond" @click.self="modalCreation = false">
      <div class="super-modal">
        <div class="super-modal-header">
          <h2><i class="fa-solid fa-building-circle-plus"></i> Nouvelle organisation</h2>
          <button @click="modalCreation = false" class="super-modal-close">&times;</button>
        </div>
        <div class="super-modal-body">
          <div class="super-section-titre"><i class="fa-solid fa-id-card"></i> Identité</div>
          <div class="super-grille-form">
            <div class="super-champ">
              <label class="super-label-oblig">Code tenant</label>
              <input v-model="formCreation.code_tenant" type="text" placeholder="escep, ministere-fin..."
                @input="formCreation.code_tenant = formCreation.code_tenant.toLowerCase().replace(/[^a-z0-9-]/g,'-')" />
              <small>Minuscules, tirets autorisés. Unique et permanent.</small>
            </div>
            <div class="super-champ">
              <label class="super-label-oblig">Nom</label>
              <input v-model="formCreation.nom" type="text" placeholder="ex: Ministère des Finances" />
            </div>
            <div class="super-champ super-champ-large">
              <label>Slogan</label>
              <input v-model="formCreation.slogan" type="text" placeholder="ex: Gérer vos documents efficacement" />
            </div>
            <div class="super-champ super-champ-large">
              <label>Domaine personnalisé (optionnel)</label>
              <input v-model="formCreation.domaine_personnalise" type="text" placeholder="ged.ministere.ne" />
            </div>
          </div>

          <div class="super-section-titre" style="margin-top:20px"><i class="fa-solid fa-palette"></i> Apparence</div>
          <div class="super-grille-form">
            <div class="super-champ">
              <label>Couleur principale</label>
              <div style="display:flex;gap:8px;align-items:center">
                <input v-model="formCreation.couleur_principale" type="color" class="color-picker" />
                <input v-model="formCreation.couleur_principale" type="text"
                  style="flex:1;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px" />
              </div>
            </div>
            <div class="super-champ">
              <label>Couleur accent</label>
              <div style="display:flex;gap:8px;align-items:center">
                <input v-model="formCreation.couleur_accent" type="color" class="color-picker" />
                <input v-model="formCreation.couleur_accent" type="text"
                  style="flex:1;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px" />
              </div>
            </div>
            <div class="super-champ super-champ-large">
              <label>Logo</label>
              <input type="file" accept=".png,.jpg,.jpeg,.svg" @change="e => formCreation.logo = e.target.files[0]" />
            </div>
            <div class="super-champ super-champ-large">
              <label>Image de fond (connexion)</label>
              <input type="file" accept=".png,.jpg,.jpeg" @change="e => formCreation.image_fond_login = e.target.files[0]" />
            </div>
          </div>

          <div class="super-section-titre" style="margin-top:20px"><i class="fa-solid fa-crown"></i> Plan</div>
          <div class="super-grille-form">
            <div class="super-champ">
              <label>Plan</label>
              <select v-model="formCreation.plan">
              
                <option value="GRATUIT">Gratuit</option>
                <option value="PRO">Pro</option>
                <option value="ENTERPRISE">Entreprise</option>
              </select>
              <div class="super-champ">
            <label>Type de workflow</label>
            <select v-model="formCreation.workflow_type">
              <option value="CLASSIQUE">Classique</option>
              <option value="ETENDU">Étendu</option>
            </select>
          </div>
                      </div>
                      <div class="super-champ">
                <label>Préfixe courrier</label>
                <input v-model="formCreation.prefixe_courrier" type="text"
                  placeholder="ex: OT, MIN-FIN, ESCEP" maxlength="10"
                  @input="formCreation.prefixe_courrier = formCreation.prefixe_courrier.toUpperCase()" />
                <small>Préfixe des numéros officiels. Laissez vide pour utiliser le code tenant.</small>
              </div>
                          <div class="super-champ">
              <label>Max utilisateurs</label>
              <input v-model.number="formCreation.max_utilisateurs" type="number" min="1" />
            </div>
          </div>

          <div class="super-section-titre" style="margin-top:20px"><i class="fa-solid fa-user-tie"></i> Administrateur principal</div>
          <div class="super-grille-form">
            <div class="super-champ">
              <label class="super-label-oblig">Nom de famille</label>
              <input v-model="formCreation.admin_nom" type="text" />
            </div>
            <div class="super-champ">
              <label class="super-label-oblig">Prénom</label>
              <input v-model="formCreation.admin_prenom" type="text" />
            </div>
            <div class="super-champ">
              <label>Identifiant de connexion</label>
              <input v-model="formCreation.admin_identifiant" type="text"
                :placeholder="`admin_${formCreation.code_tenant || 'org'}`" />
              <small>Laissez vide pour générer automatiquement</small>
            </div>
            <div class="super-champ">
              <label>Email admin</label>
              <input v-model="formCreation.admin_email" type="email" placeholder="admin@org.ne" />
            </div>
          </div>
        </div>
        <p v-if="erreurCreation" class="super-msg-erreur" style="padding:0 24px 8px">{{ erreurCreation }}</p>
        <div class="super-modal-footer">
          <button class="btn-super-ghost" @click="modalCreation = false">Annuler</button>
          <button class="btn-super-primary" @click="creerOrganisation" :disabled="enEnvoi">
            <i class="fa-solid fa-building-circle-plus"></i>
            {{ enEnvoi ? 'Création...' : "Créer l'organisation" }}
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ MODAL RÉSULTAT CRÉATION ═══ -->
    <div v-if="resultatCreation" class="super-modal-fond">
      <div class="super-modal" style="max-width:500px">
        <div class="super-modal-header" style="background:#2e7d32">
          <h2><i class="fa-solid fa-circle-check"></i> Organisation créée !</h2>
          <button @click="fermerResultat" class="super-modal-close" style="color:#fff">&times;</button>
        </div>
        <div class="super-modal-body">
          <div style="background:#f5f8ff;border-radius:8px;padding:14px;margin-bottom:14px">
            <p style="margin:4px 0;font-size:14px"><strong>Organisation :</strong> {{ resultatCreation.organisation?.nom }}</p>
            <p style="margin:4px 0;font-size:14px"><strong>Code :</strong> {{ resultatCreation.organisation?.code_tenant }}</p>
          </div>
          <div style="background:#fff8e1;border:2px solid #FFD54F;border-radius:8px;padding:14px">
            <div style="font-weight:700;color:#F57F17;margin-bottom:10px;display:flex;align-items:center;gap:6px">
              <i class="fa-solid fa-key"></i> Identifiants administrateur
            </div>
            <p style="margin:6px 0;font-size:14px">
              <strong>Identifiant :</strong>
              <code style="background:#fff3cd;padding:2px 8px;border-radius:4px;margin-left:6px">{{ resultatCreation.admin_identifiant }}</code>
            </p>
            <p style="margin:6px 0;font-size:14px">
              <strong>Mot de passe :</strong>
              <code style="background:#fff3cd;padding:2px 8px;border-radius:4px;margin-left:6px">{{ resultatCreation.admin_password }}</code>
            </p>
            <div style="background:#ffebee;color:#c62828;padding:10px;border-radius:6px;font-size:12px;font-weight:600;margin-top:10px">
              <i class="fa-solid fa-triangle-exclamation"></i>
              Notez ces identifiants maintenant ! Ils ne seront plus affichés.
            </div>
          </div>
        </div>
        <div class="super-modal-footer">
          <button class="btn-super-primary" @click="copierIdentifiants">
            <i class="fa-solid fa-copy"></i> Copier
          </button>
          <button class="btn-super-ghost" @click="fermerResultat">Fermer</button>
        </div>
      </div>
    </div>

    <!-- ═══ MODAL MODIFICATION ═══ -->
    <div v-if="modalModification" class="super-modal-fond" @click.self="modalModification = false">
      <div class="super-modal">
        <div class="super-modal-header">
          <h2><i class="fa-solid fa-pencil"></i> Modifier — {{ orgSelectionnee?.nom }}</h2>
          <button @click="modalModification = false" class="super-modal-close">&times;</button>
        </div>
        <div class="super-modal-body">
          <div class="super-grille-form">
            <div class="super-champ"><label>Nom</label><input v-model="formModif.nom" type="text" /></div>
            <div class="super-champ"><label>Slogan</label><input v-model="formModif.slogan" type="text" /></div>
            <div class="super-champ super-champ-large"><label>Domaine personnalisé</label>
              <input v-model="formModif.domaine_personnalise" type="text" placeholder="ged.org.ne" />
            </div>
            <div class="super-champ">
              <label>Couleur principale</label>
              <div style="display:flex;gap:8px;align-items:center">
                <input v-model="formModif.couleur_principale" type="color" class="color-picker" />
                <input v-model="formModif.couleur_principale" type="text"
                  style="flex:1;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px" />
              </div>
            </div>
            <div class="super-champ"><label>Plan</label>
              <select v-model="formModif.plan">
                <option value="GRATUIT">Gratuit</option>
                <option value="PRO">Pro</option>
                <option value="ENTERPRISE">Entreprise</option>
              </select>
            </div>
            <div class="super-champ">
            <label>Type de workflow</label>
            <select v-model="formModif.workflow_type">
              <option value="CLASSIQUE">Classique — Assistant → DG</option>
              <option value="ETENDU">Étendu — SGA → SG → DG</option>
            </select>
          </div>
          <div class="super-champ">
            <label>Préfixe courrier</label>
            <input v-model="formCreation.prefixe_courrier" type="text"
              placeholder="ex: OT, MIN-FIN, ESCEP" maxlength="10"
              @input="formCreation.prefixe_courrier = formCreation.prefixe_courrier.toUpperCase()" />
            <small>Préfixe des numéros officiels. Laissez vide pour utiliser le code tenant.</small>
          </div>
                      <div class="super-champ"><label>Max utilisateurs</label>
              <input v-model.number="formModif.max_utilisateurs" type="number" />
            </div>
            <div class="super-champ super-champ-large"><label>Logo</label>
              <input type="file" accept=".png,.jpg,.jpeg,.svg" @change="e => formModif.logo = e.target.files[0]" />
            </div>
            <div class="super-champ super-champ-large"><label>Image de fond</label>
              <input type="file" accept=".png,.jpg,.jpeg" @change="e => formModif.image_fond_login = e.target.files[0]" />
            </div>
          </div>
        </div>
        <p v-if="erreurModif" class="super-msg-erreur" style="padding:0 24px 8px">{{ erreurModif }}</p>
        <div class="super-modal-footer">
          <button class="btn-super-ghost" @click="modalModification = false">Annuler</button>
          <button class="btn-super-primary" @click="sauvegarderModif" :disabled="enEnvoi">
            {{ enEnvoi ? 'Sauvegarde...' : 'Sauvegarder' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ MODAL ADMINS ═══ -->
    <div v-if="modalAdmins" class="super-modal-fond" @click.self="modalAdmins = false">
      <div class="super-modal">
        <div class="super-modal-header">
          <h2><i class="fa-solid fa-users-gear"></i> Admins — {{ orgSelectionnee?.nom }}</h2>
          <button @click="modalAdmins = false" class="super-modal-close">&times;</button>
        </div>
        <div class="super-modal-body">
          <!-- Liste admins -->
          <div v-if="adminsOrg.length" class="admin-liste">
            <div v-for="a in adminsOrg" :key="a.id" class="admin-item">
              <div class="admin-info">
                <span class="admin-nom">{{ a.prenom }} {{ a.nom }}</span>
                <code class="admin-id">@{{ a.identifiant }}</code>
                <span :class="a.is_active ? 'badge-actif' : 'badge-inactif-sm'">
                  {{ a.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </div>
              <button class="btn-org-action" style="font-size:11px"
                :class="a.is_active ? 'btn-desactiver' : 'btn-activer'"
                @click="basculerAdmin(a)">
                {{ a.is_active ? 'Désactiver' : 'Activer' }}
              </button>
            </div>
          </div>
          <p v-else class="super-vide">Aucun admin.</p>

          <!-- Ajouter admin -->
          <div class="super-section-titre" style="margin-top:20px">
            <i class="fa-solid fa-user-plus"></i> Ajouter un admin
          </div>
          <div class="super-grille-form">
            <div class="super-champ"><label>Nom</label><input v-model="formNouvelAdmin.nom" type="text" /></div>
            <div class="super-champ"><label>Prénom</label><input v-model="formNouvelAdmin.prenom" type="text" /></div>
            <div class="super-champ"><label>Email</label><input v-model="formNouvelAdmin.email" type="email" /></div>
            <div class="super-champ"><label>Mot de passe</label>
              <input v-model="formNouvelAdmin.password" type="text" placeholder="Généré si vide" />
            </div>
          </div>
          <div v-if="resultatNouvelAdmin" class="super-msg-succes" style="margin-top:10px">
            Admin créé ! Identifiant: <strong>{{ resultatNouvelAdmin.identifiant }}</strong>
            — Mot de passe: <strong>{{ resultatNouvelAdmin.admin_password }}</strong>
          </div>
          <button class="btn-super-primary" style="margin-top:12px" @click="ajouterAdmin" :disabled="enEnvoi">
            <i class="fa-solid fa-user-plus"></i> Ajouter
          </button>
        </div>
        <div class="super-modal-footer">
          <button class="btn-super-ghost" @click="modalAdmins = false">Fermer</button>
        </div>
      </div>
    </div>

    <!-- ═══ MODAL SÉCURITÉ ORG (depuis org-card) ═══ -->
    <div v-if="modalSecuriteOrg" class="super-modal-fond" @click.self="modalSecuriteOrg = false">
      <div class="super-modal" style="max-width:500px">
        <div class="super-modal-header">
          <h2><i class="fa-solid fa-lock"></i> Sécurité — {{ orgSelectionnee?.nom }}</h2>
          <button @click="modalSecuriteOrg = false" class="super-modal-close">&times;</button>
        </div>
        <div class="super-modal-body">
          <div class="super-grille-form">
            <div class="super-champ">
              <label>Timeout inactivité (min)</label>
              <input v-model.number="formSecuriteOrg.timeout_inactivite" type="number" min="5" />
            </div>
            <div class="super-champ">
              <label>Validité mot de passe (jours)</label>
              <input v-model.number="formSecuriteOrg.duree_validite_mdp" type="number" min="30" />
            </div>
            <div class="super-champ">
              <label>Tentatives avant verrouillage</label>
              <input v-model.number="formSecuriteOrg.tentatives_max" type="number" min="3" max="10" />
            </div>
            <div class="super-champ">
              <label>Email expéditeur 2FA</label>
              <input v-model="formSecuriteOrg.email_expediteur" type="email" />
            </div>
            <div class="super-champ super-champ-large">
              <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
                <input type="checkbox" v-model="formSecuriteOrg.double_auth_active"
                  style="width:18px;height:18px;accent-color:#1a237e" />
                Activer la 2FA pour cette organisation
              </label>
            </div>
          </div>
        </div>
        <p v-if="msgSecuriteOrg" class="super-msg-succes" style="padding:0 24px 8px">{{ msgSecuriteOrg }}</p>
        <div class="super-modal-footer">
          <button class="btn-super-ghost" @click="modalSecuriteOrg = false">Annuler</button>
          <button class="btn-super-primary" @click="sauvegarderSecuriteOrg" :disabled="enEnvoi">
            <i class="fa-solid fa-floppy-disk"></i>
            {{ enEnvoi ? 'Sauvegarde...' : 'Enregistrer' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router       = useRouter()
const section      = ref('organisations')
const organisations = ref([])
const chargement   = ref(false)
const enEnvoi      = ref(false)

const modalCreation    = ref(false)
const modalModification = ref(false)
const modalAdmins      = ref(false)
const modalSecuriteOrg = ref(false)

const orgSelectionnee     = ref(null)
const adminsOrg           = ref([])
const resultatCreation    = ref(null)
const resultatNouvelAdmin = ref(null)
const erreurCreation      = ref('')
const erreurModif         = ref('')
const msgSecurite         = ref('')
const msgSecuriteOrg      = ref('')

// Sécurité globale
const orgSecuriteId = ref('')
const formSecurite  = ref({})
const formSecuriteOrg = ref({})
const formCreation = ref({
  code_tenant: '', nom: '', slogan: '', domaine_personnalise: '',
  couleur_principale: '#1565C0', couleur_accent: '#FDD835',
  plan: 'GRATUIT', max_utilisateurs: 50,
  workflow_type: 'CLASSIQUE',   // ← ajouter cette ligne

  admin_nom: '', admin_prenom: '', admin_identifiant: '', admin_email: '',
  logo: null, image_fond_login: null,
})

const identifiant = computed(() => {
  try {
    const t = localStorage.getItem('access')
    return t ? JSON.parse(atob(t.split('.')[1])).identifiant : ''
  } catch { return '' }
})

const totalUtilisateurs = computed(() =>
  organisations.value.reduce((s, o) => s + (o.utilisateurs_count || 0), 0)
)

const api = axios.create({
baseURL: import.meta.env.VITE_API_URL || 'https://gestion-des-docs-electronique.onrender.com/api',  get headers() {
    return { Authorization: `Bearer ${localStorage.getItem('access')}` }
  }
})

async function charger() {
  chargement.value = true
  try {
    const rep = await api.get('/super/organisations/')
    organisations.value = rep.data
  } catch(e) {
    if (e.response?.status === 403) router.push('/')
  } finally { chargement.value = false }
}

// ── Création ──
function ouvrirCreation() {
  formCreation.value = {
    code_tenant: '', nom: '', slogan: '', domaine_personnalise: '',
    couleur_principale: '#1565C0', couleur_accent: '#FDD835',
    plan: 'GRATUIT', max_utilisateurs: 50,
    workflow_type: 'CLASSIQUE',   // ← ajouter cette ligne
    admin_nom: '', admin_prenom: '', admin_identifiant: '', admin_email: '',
    logo: null, image_fond_login: null,
    prefixe_courrier: '',
  }
  erreurCreation.value = ''
  modalCreation.value  = true
}
async function creerOrganisation() {
  erreurCreation.value = ''
  enEnvoi.value = true
  try {
    const fd = new FormData()
    Object.entries(formCreation.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') fd.append(k, v)
    })
    const rep = await api.post('/super/organisations/', fd)
    resultatCreation.value = rep.data
    modalCreation.value    = false
  } catch(e) {
    erreurCreation.value = e.response?.data?.detail || JSON.stringify(e.response?.data) || 'Erreur.'
  } finally { enEnvoi.value = false }
}

function fermerResultat() {
  resultatCreation.value = null
  charger()
}

function copierIdentifiants() {
  if (!resultatCreation.value) return
  const t = `Organisation: ${resultatCreation.value.organisation?.nom}\nIdentifiant: ${resultatCreation.value.admin_identifiant}\nMot de passe: ${resultatCreation.value.admin_password}`
  navigator.clipboard.writeText(t).then(() => alert('Copié dans le presse-papiers !'))
}

// ── Modification ──
function ouvrirModification(org) {
  orgSelectionnee.value = org
  formModif.value = {
    nom: org.nom, slogan: org.slogan || '',
    domaine_personnalise: org.domaine_personnalise || '',
    couleur_principale: org.couleur_principale,
    plan: org.plan, max_utilisateurs: org.max_utilisateurs,
    workflow_type: org.workflow_type || 'CLASSIQUE', 
    prefixe_courrier: '', 
    logo: null, image_fond_login: null,

  }
  erreurModif.value       = ''
  modalModification.value = true
}

const formModif = ref({})

async function sauvegarderModif() {
  enEnvoi.value = true
  erreurModif.value = ''
  try {
    const fd = new FormData()
    Object.entries(formModif.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined) fd.append(k, v)
    })
    await api.patch(`/super/organisations/${orgSelectionnee.value.id}/`, fd)
    modalModification.value = false
    charger()
  } catch(e) {
    erreurModif.value = e.response?.data?.detail || 'Erreur.'
  } finally { enEnvoi.value = false }
}

// ── Admins ──
async function ouvrirAdmins(org) {
  orgSelectionnee.value   = org
  resultatNouvelAdmin.value = null
  formNouvelAdmin.value   = { nom: '', prenom: '', email: '', password: '' }
  try {
    const rep = await api.get(`/super/organisations/${org.id}/admins/`)
    adminsOrg.value = rep.data
  } catch { adminsOrg.value = [] }
  modalAdmins.value = true
}

const formNouvelAdmin = ref({ nom: '', prenom: '', email: '', password: '' })

async function ajouterAdmin() {
  enEnvoi.value = true
  resultatNouvelAdmin.value = null
  try {
    const rep = await api.post(`/super/organisations/${orgSelectionnee.value.id}/admins/ajouter/`, formNouvelAdmin.value)
    resultatNouvelAdmin.value = rep.data
    formNouvelAdmin.value = { nom: '', prenom: '', email: '', password: '' }
    const rep2 = await api.get(`/super/organisations/${orgSelectionnee.value.id}/admins/`)
    adminsOrg.value = rep2.data
  } catch(e) {
    alert(e.response?.data?.detail || 'Erreur.')
  } finally { enEnvoi.value = false }
}

async function basculerAdmin(a) {
  try {
    await api.patch(`/super/organisations/${orgSelectionnee.value.id}/admins/${a.id}/`, { is_active: !a.is_active })
    a.is_active = !a.is_active
  } catch { alert('Erreur.') }
}

// ── Sécurité depuis section ──
async function chargerSecurite() {
  if (!orgSecuriteId.value) return
  try {
    const rep = await api.get(`/super/organisations/${orgSecuriteId.value}/securite/`)
    formSecurite.value = rep.data
  } catch { alert('Erreur lors du chargement.') }
}

async function sauvegarderSecurite() {
  enEnvoi.value = true
  msgSecurite.value = ''
  try {
    await api.patch(`/super/organisations/${orgSecuriteId.value}/securite/`, formSecurite.value)
    msgSecurite.value = ' Sécurité mise à jour.'
  } catch { msgSecurite.value = ' Erreur.' }
  finally { enEnvoi.value = false }
}

// ── Sécurité depuis org-card ──
async function ouvrirSecuriteOrg(org) {
  orgSelectionnee.value = org
  msgSecuriteOrg.value  = ''
  try {
    const rep = await api.get(`/super/organisations/${org.id}/securite/`)
    formSecuriteOrg.value = rep.data
  } catch { formSecuriteOrg.value = {} }
  modalSecuriteOrg.value = true
}

async function sauvegarderSecuriteOrg() {
  enEnvoi.value = true
  msgSecuriteOrg.value = ''
  try {
    await api.patch(`/super/organisations/${orgSelectionnee.value.id}/securite/`, formSecuriteOrg.value)
    msgSecuriteOrg.value = 'Sécurité mise à jour.'
  } catch { msgSecuriteOrg.value = ' Erreur.' }
  finally { enEnvoi.value = false }
}

// ── Activer/désactiver org ──
async function basculerOrg(org) {
  if (!confirm(`${org.active ? 'Désactiver' : 'Activer'} "${org.nom}" ?`)) return
  try {
    await api.patch(`/super/organisations/${org.id}/`, { active: !org.active })
    org.active = !org.active
  } catch { alert('Erreur.') }
}

function seDeconnecter() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/super-admin/login')
}

onMounted(charger)
</script>

<style scoped>
.super-admin-layout { display:flex; min-height:100vh; background:#f0f2f5; font-family:'Segoe UI',sans-serif; }

/* ── Sidebar ── */
.super-sidebar { width:230px; min-height:100vh; background:linear-gradient(180deg,#1a237e 0%,#283593 100%); display:flex; flex-direction:column; position:fixed; top:0; left:0; z-index:50; box-shadow:2px 0 8px rgba(0,0,0,0.2); }
.super-sidebar-header { display:flex; align-items:center; gap:12px; padding:20px 16px; border-bottom:1px solid rgba(255,255,255,0.15); }
.super-logo { width:44px; height:44px; background:rgba(255,255,255,0.2); border-radius:12px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:20px; flex-shrink:0; }
.super-titre { color:#fff; font-weight:700; font-size:15px; }
.super-sous-titre { color:rgba(255,255,255,0.6); font-size:11px; }
.super-nav { flex:1; padding:8px 0; }
.super-nav-section { color:rgba(255,255,255,0.4); font-size:10px; text-transform:uppercase; letter-spacing:1px; padding:12px 16px 4px; font-weight:600; }
.super-nav-item { display:flex; align-items:center; gap:10px; width:100%; padding:11px 16px; color:rgba(255,255,255,0.8); background:none; border:none; border-left:3px solid transparent; cursor:pointer; font-size:14px; font-weight:500; transition:all 0.15s; text-align:left; }
.super-nav-item:hover { background:rgba(255,255,255,0.1); color:#fff; }
.super-nav-item.actif { color:#fff; background:rgba(255,255,255,0.15); border-left-color:#FFD54F; font-weight:600; }
.super-badge { margin-left:auto; background:rgba(255,255,255,0.25); color:#fff; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; }
.super-sidebar-bas { padding:16px; border-top:1px solid rgba(255,255,255,0.15); }
.super-user-info { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.super-user-avatar { width:36px; height:36px; background:rgba(255,255,255,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:16px; }
.btn-deconnexion { width:100%; padding:8px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; cursor:pointer; font-size:13px; display:flex; align-items:center; justify-content:center; gap:6px; }
.btn-deconnexion:hover { background:rgba(255,255,255,0.2); }

/* ── Main ── */
.super-main { margin-left:230px; flex:1; padding:24px; }
.super-page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; }
.super-page-titre { font-size:22px; font-weight:700; color:#1a237e; display:flex; align-items:center; gap:10px; }
.super-page-sous-titre { font-size:13px; color:#666; margin-top:4px; }
.super-chargement { text-align:center; padding:60px; color:#666; }
.super-vide-total { text-align:center; padding:60px; color:#888; }
.super-vide { color:#999; font-size:13px; text-align:center; padding:16px; }

/* ── Grille orgs ── */
.orgs-grille { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:20px; }
.org-card { background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08); transition:transform 0.2s,box-shadow 0.2s; }
.org-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.12); }
.org-card-header { padding:20px; display:flex; justify-content:space-between; align-items:flex-start; min-height:80px; }
.org-card-logo { width:52px; height:52px; background:rgba(255,255,255,0.25); border-radius:10px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:22px; overflow:hidden; }
.org-card-logo img { width:100%; height:100%; object-fit:contain; }
.org-card-badges { display:flex; flex-direction:column; gap:4px; align-items:flex-end; }
.org-badge-plan { background:rgba(255,255,255,0.3); color:#fff; padding:3px 8px; border-radius:4px; font-size:10px; font-weight:700; }
.org-badge-statut { font-size:11px; font-weight:700; padding:3px 8px; border-radius:4px; }
.statut-actif { background:rgba(255,255,255,0.9); color:#2e7d32; }
.statut-inactif { background:rgba(0,0,0,0.3); color:#fff; }
.org-card-body { padding:14px 16px; }
.org-card-nom { font-size:15px; font-weight:700; color:#222; margin-bottom:2px; }
.org-card-code { font-size:12px; color:#888; margin-bottom:4px; }
.org-card-slogan { font-size:12px; color:#666; margin-bottom:4px; }
.org-card-domaine { font-size:12px; color:#1565C0; margin-bottom:8px; }
.org-card-stats { display:flex; gap:16px; margin-bottom:8px; align-items:center; }
.org-stat { text-align:center; }
.org-stat-val { display:block; font-size:18px; font-weight:700; color:#1a237e; }
.org-stat-label { font-size:11px; color:#888; }
.org-progress-bar { flex:1; height:6px; background:#eee; border-radius:3px; overflow:hidden; min-width:60px; }
.org-progress-fill { height:100%; border-radius:3px; transition:width 0.3s; }
.org-admin-info { font-size:12px; color:#666; display:flex; align-items:center; gap:4px; }
.org-card-actions { display:flex; flex-wrap:wrap; gap:5px; padding:10px 14px; border-top:1px solid #f0f0f0; }
.btn-org-action { flex:1; min-width:60px; padding:6px 8px; border:none; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:4px; }
.btn-modifier { background:#e3f2fd; color:#1565C0; }
.btn-admins { background:#e8f5e9; color:#2e7d32; }
.btn-securite-org { background:#fff3e0; color:#e65100; }
.btn-desactiver { background:#ffebee; color:#d32f2f; }
.btn-activer { background:#e8f5e9; color:#2e7d32; }

/* ── Supervision ── */
.supervision-grille { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; }
.supervision-card { background:#fff; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); display:flex; align-items:center; gap:16px; }
.supervision-icone { width:50px; height:50px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px; flex-shrink:0; }
.supervision-val { font-size:30px; font-weight:700; color:#1a237e; }
.supervision-label { font-size:13px; color:#666; margin-top:2px; }
.mini-logo { width:28px; height:28px; border-radius:6px; display:flex; align-items:center; justify-content:center; flex-shrink:0; overflow:hidden; }
.badge-plan { background:#e8eaf6; color:#1a237e; font-size:11px; font-weight:700; padding:3px 8px; border-radius:4px; }

/* ── Super-card ── */
.super-card { background:#fff; border-radius:10px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,0.07); }
.super-card-titre { font-size:14px; font-weight:700; color:#1a237e; margin-bottom:14px; display:flex; align-items:center; gap:8px; padding-bottom:10px; border-bottom:2px solid #e8eaf6; }

/* ── Modals ── */
.super-modal-fond { position:fixed; inset:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:200; padding:16px; }
.super-modal { background:#fff; border-radius:12px; width:100%; max-width:680px; max-height:90vh; overflow-y:auto; box-shadow:0 10px 40px rgba(0,0,0,0.2); }
.super-modal-header { display:flex; align-items:center; justify-content:space-between; padding:20px 24px; background:#1a237e; color:#fff; border-radius:12px 12px 0 0; }
.super-modal-header h2 { font-size:17px; font-weight:600; display:flex; align-items:center; gap:10px; }
.super-modal-close { background:none; border:none; color:#fff; font-size:24px; cursor:pointer; line-height:1; }
.super-modal-body { padding:24px; }
.super-modal-footer { display:flex; justify-content:flex-end; gap:10px; padding:16px 24px; border-top:1px solid #eee; }
.super-section-titre { font-size:13px; font-weight:700; color:#1a237e; margin-bottom:12px; padding-bottom:6px; border-bottom:2px solid #e3f2fd; display:flex; align-items:center; gap:8px; }
.super-grille-form { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
.super-champ { display:flex; flex-direction:column; gap:4px; }
.super-champ-large { grid-column:span 2; }
.super-champ label { font-size:12px; font-weight:600; color:#555; }
.super-label-oblig::after { content:' *'; color:#d32f2f; }
.super-champ input, .super-champ select, .super-champ textarea { padding:9px 12px; border:1px solid #d0d0d0; border-radius:6px; font-size:14px; background:#fafafa; }
.super-champ input:focus, .super-champ select:focus, .super-champ textarea:focus { outline:none; border-color:#1a237e; background:#fff; }
.super-champ small { font-size:11px; color:#888; }
.super-msg-erreur { color:#d32f2f; font-size:13px; margin-top:8px; }
.super-msg-succes { color:#2e7d32; font-size:13px; margin-top:8px; background:#e8f5e9; padding:8px 12px; border-radius:6px; }
.btn-super-primary { padding:10px 20px; background:#1a237e; color:#fff; border:none; border-radius:6px; font-size:14px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:8px; }
.btn-super-primary:hover:not(:disabled) { background:#283593; }
.btn-super-primary:disabled { opacity:0.6; cursor:not-allowed; }
.btn-super-ghost { padding:10px 20px; background:#f5f5f5; color:#555; border:1px solid #ddd; border-radius:6px; font-size:14px; cursor:pointer; }
.btn-super-ghost:hover { background:#eee; }
.color-picker { width:48px; height:36px; padding:2px; border:1px solid #ddd; border-radius:4px; cursor:pointer; }
.admin-liste { display:flex; flex-direction:column; gap:8px; margin-bottom:4px; }
.admin-item { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:#f5f8ff; border-radius:8px; }
.admin-info { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.admin-nom { font-weight:600; font-size:14px; }
.admin-id { font-size:12px; color:#888; background:#eee; padding:2px 6px; border-radius:4px; }
.badge-actif { background:#e8f5e9; color:#2e7d32; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; }
.badge-inactif-sm { background:#ffebee; color:#d32f2f; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; }
</style>
