"""
Commande: python manage.py creer_organisation
Crée une nouvelle organisation avec son administrateur.
"""

from django.core.management.base import BaseCommand
import secrets, string


class Command(BaseCommand):
    help = 'Crée une nouvelle organisation SaaS avec son admin'

    def add_arguments(self, parser):
        parser.add_argument('--code',         type=str, help='Code tenant unique')
        parser.add_argument('--nom',          type=str, help="Nom de l'organisation")
        parser.add_argument('--admin-nom',    type=str, help='Nom de famille admin')
        parser.add_argument('--admin-prenom', type=str, help='Prénom admin')
        parser.add_argument('--admin-email',  type=str, help='Email admin', default='')
        parser.add_argument('--plan',         type=str, default='GRATUIT',
                            choices=['GRATUIT', 'PRO', 'ENTERPRISE'])

    def handle(self, *args, **options):
        from apps.organisations.models import Organisation
        from apps.users.models import Utilisateur

        code   = options.get('code')   or input('Code tenant (ex: escep): ').strip()
        nom    = options.get('nom')    or input("Nom de l'organisation: ").strip()
        plan   = options.get('plan', 'GRATUIT')

        if Organisation.objects.filter(code_tenant=code).exists():
            self.stderr.write(f'❌ Organisation "{code}" existe déjà!')
            return

        org = Organisation.objects.create(
            code_tenant=code, nom=nom, plan=plan
        )
        self.stdout.write(f'✓ Organisation "{nom}" créée.')

        admin_nom    = options.get('admin_nom')    or input('Nom de famille admin: ').strip()
        admin_prenom = options.get('admin_prenom') or input('Prénom admin: ').strip()
        admin_email  = options.get('admin_email', '') or input('Email admin (optionnel): ').strip()

        pwd = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$') for _ in range(14))

        admin = Utilisateur.objects.create_user(
            organisation=org,
            identifiant=f"admin_{code}",
            password=pwd,
            nom=admin_nom,
            prenom=admin_prenom,
            email=admin_email,
            profil='ADMIN',
        )
        org.admin_principal = admin
        org.save()

        self.stdout.write(self.style.SUCCESS('\n══════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('✅ ORGANISATION CRÉÉE AVEC SUCCÈS'))
        self.stdout.write(self.style.SUCCESS('══════════════════════════════════════'))
        self.stdout.write(f'Organisation : {nom}')
        self.stdout.write(f'Code tenant  : {code}')
        self.stdout.write(f'Plan         : {plan}')
        self.stdout.write(f'\nAdmin:')
        self.stdout.write(f'  Identifiant: admin_{code}')
        self.stdout.write(f'  Mot de passe: {pwd}')
        self.stdout.write(self.style.WARNING('\n⚠️  Notez ces identifiants, ils ne seront plus affichés!'))
