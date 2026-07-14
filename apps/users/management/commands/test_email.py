from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Envoie un e-mail de test pour vérifier la configuration SMTP'

    def add_arguments(self, parser):
        parser.add_argument('--to', default='mahamadousouradji708@gmail.com')

    def handle(self, *args, **options):
        to = options['to']
        subject = 'Test email GED ESCEP'
        message = 'Ceci est un test d\'envoi email depuis Django.'
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f'Email envoyé avec succès à {to}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur d\'envoi: {e}'))
