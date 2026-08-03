import logging
import threading
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def envoyer_notification(destinataire, sujet, message, organisation=None):
    if not destinataire.email:
        return
    # Lancer dans un thread séparé — Django répond immédiatement sans bloquer la requête
    thread = threading.Thread(
        target=_envoyer_email,
        args=(destinataire, sujet, message, organisation),
        daemon=True,
    )
    thread.start()


def _envoyer_email(destinataire, sujet, message, organisation):
    # Le vrai envoi ici — s'exécute en arrière-plan
    expediteur = settings.DEFAULT_FROM_EMAIL
    if organisation and organisation.email_expediteur:
        expediteur = organisation.email_expediteur

    corps = f"""Bonjour {destinataire.prenom} {destinataire.nom},

{message}

Accédez à l'application : http://localhost:5173/

---
Message automatique — ne pas répondre.
{organisation.nom if organisation else 'GED SaaS'}"""

    try:
        send_mail(
            subject=sujet,
            message=corps,
            from_email=expediteur,
            recipient_list=[destinataire.email],
            fail_silently=False,  # Passe à False pour voir les erreurs d'envoi SMTP dans les logs si besoin
        )
    except Exception as e:
        logger.exception(f"Erreur envoi email : {e}")