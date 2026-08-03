from apps.users.models import Utilisateur

if not Utilisateur.objects.filter(identifiant='superadmin').exists():
    u = Utilisateur(
        identifiant='superadmin',
        nom='Admin',
        prenom='Super',
        profil='ADMIN',
        is_staff=True,
        is_superuser=True,
    )
    u.set_password('Admin1234!')
    u.save()
    print('Superadmin créé.')
else:
    print('Superadmin existe déjà.')
