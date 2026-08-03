/**
 * Catalogue des modules disponibles dans le système.
 * Un module n'est JAMAIS lié à un profil : l'admin choisit
 * librement lesquels accorder à chaque utilisateur, quel que
 * soit son profil (DG, Assistant, BO, Destinataire, Archiviste).
 *
 * Un compte nouvellement créé n'a AUCUN module actif par défaut.
 */

export const MODULES_DISPONIBLES = [
  {
    code: 'saisie',
    label: 'Saisie de courrier',
    description: 'Enregistrer de nouveaux courriers entrants ou internes',
    icone: 'fa-solid fa-plus',
  },
  {
    code: 'verification',
    label: 'Vérification de courrier',
    description: 'Contrôler et valider ou rejeter les courriers saisis',
    icone: 'fa-solid fa-circle-check',
  },
 {
    code: 'validation_sga',
    label: 'Validation SGA',
    description: 'Valider les courriers et proposer une imputation (workflow étendu)',
    icone: 'fa-solid fa-user-check',
  },
  {
    code: 'validation_sg',
    label: 'Validation SG',
    description: 'Contrôler et valider la proposition du SGA (workflow étendu)',
    icone: 'fa-solid fa-user-tie',
  },
  {
    code: 'imputation',
    label: 'Imputation de courrier',
    description: 'Attribuer les courriers validés à un destinataire',
    icone: 'fa-solid fa-paper-plane',
  },
  {
    code: 'traitement',
    label: 'Traitement de courrier',
    description: 'Consulter et traiter les courriers reçus',
    icone: 'fa-solid fa-inbox',
  },
  {
    code: 'archivage',
    label: 'Archivage courant',
    description: 'Classer les courriers traités en archive',
    icone: 'fa-solid fa-box-archive',
  },
  {
    code: 'archives',
    label: 'Archives historiques',
    description: 'Versement et consultation des fonds Archive',
    icone: 'fa-solid fa-folder-open',
  },
  {
    code: 'recherche',
    label: 'Recherche documentaire',
    description: 'Recherche multicritères dans les courriers et archives',
    icone: 'fa-solid fa-magnifying-glass',
  },
  {
    code: 'statistiques',
    label: 'Statistiques',
    description: 'Tableaux de bord et indicateurs de pilotage',
    icone: 'fa-solid fa-chart-bar',
  },
  {
    code: 'delegations',
    label: 'Délégations',
    description: 'Accorder ou gérer des délégations ponctuelles',
    icone: 'fa-solid fa-user-shield',
  },
  {
    code: 'audit',
    label: "Journal d'audit",
    description: 'Consultation de la trace complète des actions du système',
    icone: 'fa-solid fa-shield-halved',
  },
]
