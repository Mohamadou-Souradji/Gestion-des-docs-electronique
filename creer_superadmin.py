import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import Utilisateur

if not Utilisateur.objects.filter(identifiant='superadmin').exists():
    Utilisateur.objects.create_superuser(
        identifiant='superadmin',
        password='admin1234',
        nom='Admin',
        prenom='Super',
        profil='ADMIN',
    )
    print('Superadmin créé.')
else:
    print('Superadmin existe déjà.')
