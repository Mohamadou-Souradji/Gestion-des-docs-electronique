"""
Script de création des comptes de test.
Mot de passe : Test@1234567 (12 caractères)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Utilisateur, Direction, ParametresApplication
from django.utils import timezone

# Créer le singleton paramètres si absent
ParametresApplication.get()
print("Paramètres initialisés.")

# Créer les directions
directions_data = [
    {'nom': 'Direction Générale',             'sigle': 'DG',      'ordre': 1},
    {'nom': 'Département Informatique',       'sigle': 'DEP/DI',  'ordre': 2},
    {'nom': 'Département Sciences',           'sigle': 'DEP/SC',  'ordre': 3},
    {'nom': 'Département Sciences Humaines',  'sigle': 'DEP/SH',  'ordre': 4},
    {'nom': 'Département Administration',     'sigle': 'DEP/ADM', 'ordre': 5},
    {'nom': 'Service des Archives',           'sigle': 'ARC',     'ordre': 6},
]

dirs = {}
for d in directions_data:
    obj, created = Direction.objects.get_or_create(nom=d['nom'], defaults={'sigle': d['sigle'], 'ordre': d['ordre']})
    dirs[d['sigle']] = obj
    print(f"{'Créée' if created else 'Existante'} : {obj}")

# Créer les utilisateurs
utilisateurs = [
    # Les modules ne sont jamais liés au profil : ils sont accordés
    # ici uniquement pour permettre de tester l'application immédiatement.
    # L'Administrateur peut les modifier à tout moment.
    {'identifiant': 'dg_escep',     'nom': 'Mahamadou', 'prenom': 'Issoufou', 'profil': 'DG',    'direction': dirs['DG'],      'modules_actifs': ['imputation', 'statistiques', 'audit', 'delegations', 'recherche']},
    {'identifiant': 'assistant_dg', 'nom': 'Moussa',    'prenom': 'Adamou',   'profil': 'ASSIST','direction': dirs['DG'],      'modules_actifs': ['verification']},
    {'identifiant': 'bureau_ordre', 'nom': 'Harouna',   'prenom': 'Saidou',   'profil': 'BO',    'direction': dirs['DG'],      'modules_actifs': ['saisie']},
    {'identifiant': 'dest_di',      'nom': 'Issa',      'prenom': 'Boubacar', 'profil': 'DEST',  'direction': dirs['DEP/DI'],  'modules_actifs': ['traitement', 'recherche']},
    {'identifiant': 'dest_sc',      'nom': 'Balkissa',  'prenom': 'Fatouma',  'profil': 'DEST',  'direction': dirs['DEP/SC'],  'modules_actifs': ['traitement']},
    {'identifiant': 'archiviste',   'nom': 'Zalika',    'prenom': 'Ibrahim',  'profil': 'ARC',   'direction': dirs['ARC'],     'modules_actifs': ['archivage', 'archives', 'recherche']},
    {'identifiant': 'admin_sys',    'nom': 'Système',   'prenom': 'Admin',    'profil': 'ADMIN', 'direction': None,            'modules_actifs': []},
]

for u in utilisateurs:
    if Utilisateur.objects.filter(identifiant=u['identifiant']).exists():
        print(f"Existe déjà : {u['identifiant']}")
        continue
    Utilisateur.objects.create_user(
        identifiant       = u['identifiant'],
        password          = '1234',
        nom               = u['nom'],
        prenom            = u['prenom'],
        profil            = u['profil'],
        direction         = u['direction'],
        modules_actifs    = u['modules_actifs'],
        date_derniere_mdp = timezone.now(),
    )
    print(f"Créé : {u['identifiant']} ({u['profil']})")

print("\n--- Comptes disponibles (mot de passe : Test@1234567) ---")
print("  dg_escep     — Directeur Général")
print("  assistant_dg — Assistant DG")
print("  bureau_ordre — Bureau d'Ordre")
print("  dest_di      — Destinataire DEP/DI (module Recherche activé)")
print("  dest_sc      — Destinataire DEP/SC")
print("  archiviste   — Archiviste")
print("  admin_sys    — Administrateur système")
