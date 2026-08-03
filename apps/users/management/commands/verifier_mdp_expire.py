from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import threading

class Command(BaseCommand):
    help = 'Vérifie les mots de passe expirés et envoie les alertes email'

    def handle(self, *args, **kwargs):
        from apps.users.models import Utilisateur
        from django.core.mail import send_mail
        from django.conf import settings

        maintenant = timezone.now()
        users = Utilisateur.objects.filter(
            is_active=True,
            email__isnull=False,
            date_derniere_mdp__isnull=False,
        ).select_related('organisation')

        for user in users:
            if not user.email or not user.organisation:
                continue

            duree = user.organisation.duree_validite_mdp or 90
            date_expiration = user.date_derniere_mdp + timedelta(days=duree)
            jours_restants  = (date_expiration - maintenant).days

            # Alerte 7 jours avant
            if jours_restants == 7 and not getattr(user, 'alerte_mdp_envoyee', False):
                self._envoyer_alerte(user, jours_restants, expire=False)
                user.alerte_mdp_envoyee = True
                user.save(update_fields=['alerte_mdp_envoyee'])

            # Expiré — envoyer email
            elif jours_restants <= 0:
                self._envoyer_alerte(user, 0, expire=True)

    def _envoyer_alerte(self, user, jours, expire):
        from django.core.mail import send_mail
        from django.conf import settings

        org  = user.organisation
        lien = f"http://localhost:5173/{org.code_tenant}/login"

        if expire:
            sujet = f"[GED] Votre mot de passe a expiré — {org.nom}"
            corps = f"""Bonjour {user.prenom} {user.nom},

Votre mot de passe a expiré. Vous devez le renouveler pour continuer à accéder à l'application.

Connectez-vous ici et changez votre mot de passe : {lien}

Il vous sera demandé votre ancien mot de passe ainsi que le nouveau.

---
Message automatique — ne pas répondre.
{org.nom}"""
        else:
            sujet = f"[GED] Votre mot de passe expire dans {jours} jours — {org.nom}"
            corps = f"""Bonjour {user.prenom} {user.nom},

Votre mot de passe expire dans {jours} jours.

Pensez à le renouveler avant l'expiration en vous connectant ici : {lien}

---
Message automatique — ne pas répondre.
{org.nom}"""

        expediteur = (org.email_expediteur if org else '') or settings.DEFAULT_FROM_EMAIL

        def _send():
            try:
                send_mail(
                    subject        = sujet,
                    message        = corps,
                    from_email     = expediteur,
                    recipient_list = [user.email],
                    fail_silently  = True,
                )
            except Exception:
                pass
        threading.Thread(target=_send, daemon=True).start()