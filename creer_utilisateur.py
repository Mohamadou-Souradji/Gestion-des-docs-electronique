"""
Script pour creer les comptes de test pour chaque profil.
Mot de passe : 1234 pour tous les comptes.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Utilisateur

utilisateurs = [
    {'identifiant': 'dg_escep',     'nom': 'Mahamadou', 'prenom': 'Issoufou',  'profil': 'DG',    'entite': 'Direction Generale'},
    {'identifiant': 'assistant_dg', 'nom': 'Moussa',    'prenom': 'Adamou',    'profil': 'ASSIST', 'entite': 'Direction Generale'},
    {'identifiant': 'bureau_ordre', 'nom': 'Harouna',   'prenom': 'Saidou',    'profil': 'BO',     'entite': 'Bureau d Ordre'},
    {'identifiant': 'dest_di',      'nom': 'Issa',      'prenom': 'Boubacar',  'profil': 'DEST',   'entite': 'DEP/DI'},
    {'identifiant': 'dest_dep',     'nom': 'Balkissa',  'prenom': 'Fatouma',   'profil': 'DEST',   'entite': 'DEP/Sciences'},
    {'identifiant': 'admin_sys',      'nom': 'Systeme',    'prenom': 'Admin',     'profil': 'ADMIN',  'entite': 'DSI'},
    {'identifiant': 'archiviste',   'nom': 'Zalika',    'prenom': 'Ibrahim',   'profil': 'ARC',    'entite': 'Archives'},
]

for u in utilisateurs:
    if Utilisateur.objects.filter(identifiant=u['identifiant']).exists():
        print(f"Existe deja : {u['identifiant']}")
        continue
    Utilisateur.objects.create_user(
        identifiant=u['identifiant'],
        password='1234',
        nom=u['nom'],
        prenom=u['prenom'],
        profil=u['profil'],
        entite=u['entite'],
    )
    print(f"Cree : {u['identifiant']} ({u['profil']})")

print("\nTermine.")