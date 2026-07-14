# GED ESCEP-Niger — Version finale complète

## Lancement rapide

```bash
# 1. Base de données
docker-compose up -d

# 2. Backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

pip install -r requirements.txt

python manage.py makemigrations users
python manage.py makemigrations courriers
python manage.py makemigrations archives
python manage.py makemigrations dashboard
python manage.py migrate

python creer_utilisateurs.py
python manage.py runserver

# 3. Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Ouvrir : http://localhost:5173

## Comptes de test (mot de passe : Test@1234567)

| Identifiant   | Profil          |
|---------------|-----------------|
| dg_escep      | Directeur Général |
| assistant_dg  | Assistant DG    |
| bureau_ordre  | Bureau d'Ordre  |
| dest_di       | Destinataire (+ Recherche) |
| dest_sc       | Destinataire    |
| archiviste    | Archiviste      |
| admin_sys     | Administrateur  |

## Sécurité

- Double authentification 2FA par email (paramétrable)
- Verrouillage après N tentatives (paramétrable)
- Déconnexion automatique après inactivité (paramétrable)
- Expiration mot de passe avec changement obligatoire
- Journal d'audit immutable sur toutes les actions
- Cloisonnement strict des données par profil

## Module Admin — Paramètres

- Nom, slogan, pied de page
- Logo et image de fond floutée (page connexion)
- Couleurs (appliquées immédiatement)
- Suppression des images
- Timeout, durée MDP, tentatives max
- 2FA globale et par utilisateur
- Directions et départements
- Modules supplémentaires par utilisateur

## Corrections v.finale

1. Journal d'audit — toutes les actions de tous les profils
2. Couleurs dynamiques — injection CSS immédiate
3. Suppression logo et image de fond
4. Pas de pied de page sur la page de connexion
5. Modules supplémentaires affichés dans le menu utilisateur
6. Direction remplace entite partout
