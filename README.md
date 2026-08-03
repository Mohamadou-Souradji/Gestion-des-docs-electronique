# GED ESCEP-Niger — Architecture modulaire v2

## Nouveauté majeure : refonte frontend complète

Le frontend est désormais structuré en petits fichiers spécialisés au lieu
de vues monolithiques de 600+ lignes. Chaque module métier est un
composant indépendant, réutilisé par une seule vue d'espace de travail.

### Principe clé : les modules ne sont jamais liés à un profil

Un utilisateur nouvellement créé (DG, Assistant DG, Bureau d'Ordre,
Destinataire ou Archiviste) **n'a aucun module actif par défaut**.
L'Administrateur choisit librement, pour chaque compte, quels modules
il peut utiliser :

- `saisie` — Saisie de courrier
- `verification` — Vérification de courrier
- `imputation` — Imputation de courrier
- `traitement` — Traitement de courrier
- `archivage` — Archivage courant
- `archives` — Archives historiques (versement/consultation)
- `recherche` — Recherche documentaire
- `statistiques` — Tableaux de bord
- `delegations` — Gestion des délégations
- `audit` — Journal d'audit

Un module activé apparaît immédiatement dans le menu de l'utilisateur ;
désactivé, il disparaît. Rien n'est câblé en dur sur le profil.

---

## Structure du frontend

```
frontend/src/
├── services/
│   └── api.js                 # Instance axios unique + tous les endpoints
├── composables/
│   ├── useModules.js           # Modules actifs de l'utilisateur connecté
│   ├── useParametres.js        # Paramètres visuels de l'app (couleurs, logo...)
│   └── useInactivite.js        # Déconnexion automatique
├── layout/
│   ├── SidebarNav.vue          # Menu latéral dynamique selon les modules
│   ├── TopBar.vue              # Barre du haut
│   └── PiedPage.vue
├── modules/
│   ├── courriers/
│   │   ├── SaisieCourrier.vue
│   │   ├── ListeCourriers.vue
│   │   ├── CarteCourrierDetail.vue
│   │   ├── VerificationCourrier.vue
│   │   ├── ImputationCourrier.vue
│   │   └── TraitementCourrier.vue
│   ├── archives/
│   │   ├── ArchivageCourant.vue
│   │   ├── VersementArchive.vue
│   │   └── FondsArchives.vue
│   ├── recherche/RechercheDocumentaire.vue
│   ├── statistiques/
│   │   ├── PanneauStatistiques.vue
│   │   ├── IndicateursOperationnels.vue
│   │   └── IndicateursStrategiques.vue
│   ├── delegations/GestionDelegations.vue
│   ├── audit/JournalAudit.vue
│   └── notifications/ListeNotifications.vue
├── admin/
│   ├── modulesDisponibles.js    # Catalogue des modules (source unique)
│   ├── SelecteurModules.vue     # Sélecteur réutilisable de modules
│   ├── GestionComptes.vue
│   ├── NouveauCompte.vue
│   ├── ModifierCompteModal.vue
│   ├── GestionDirections.vue
│   ├── ParametresApp.vue
│   ├── ParametresSecurite.vue
│   └── SupervisionTechnique.vue
├── views/
│   ├── LoginView.vue            # Connexion + 2FA
│   ├── EspaceView.vue           # Espace de travail unique (tous profils métier)
│   └── AdminView.vue            # Espace administrateur (orchestrateur léger)
└── router/index.js              # 3 routes seulement
```

Chaque fichier fait entre 50 et 200 lignes. Aucune vue ne dépasse 250 lignes.

---

## Lancement

```bash
docker-compose up -d

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations users courriers archives dashboard
python manage.py migrate
python creer_utilisateurs.py
python manage.py runserver
```

```bash
cd frontend
npm install
npm run dev
```

## Icônes

Toutes les icônes utilisent Font Awesome (`@fortawesome/fontawesome-free`),
importé globalement dans `main.js`. Aucun SVG inline, aucun emoji.

## Comptes de test (mot de passe : Test@1234567)

Après création, ouvrez la page Admin → Utilisateurs → Modifier, et cochez
les modules à accorder à chaque compte pour qu'il puisse travailler.
