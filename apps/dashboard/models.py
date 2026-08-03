"""
Dashboard — Journal d'audit multi-tenant.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class TypeAction(models.TextChoices):
    CONNEXION    = 'CONNEXION',    'Connexion'
    SOUMISSION   = 'SOUMISSION',   'Soumission'
    VALIDATION   = 'VALIDATION',   'Validation'
    REJET        = 'REJET',        'Rejet'
    IMPUTATION   = 'IMPUTATION',   'Imputation'
    CONSULTATION = 'CONSULTATION', 'Consultation'
    TRAITEMENT   = 'TRAITEMENT',   'Traitement'
    ARCHIVAGE    = 'ARCHIVAGE',    'Archivage'
    MODIF_COMPTE = 'MODIF_COMPTE', 'Modification compte'
    CREATION_COMPTE = 'CREATION_COMPTE', 'Création compte'
    DESACT_COMPTE   = 'DESACT_COMPTE',   'Désactivation compte'


class Issue(models.TextChoices):
    SUCCES = 'SUCCES', 'Succès'
    ECHEC  = 'ECHEC',  'Échec'
    REFUS  = 'REFUS',  'Refus'


class JournalAudit(models.Model):
    # AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='journal_audit',
        null=True,
    )
    utilisateur      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    identifiant_user = models.CharField(max_length=50, blank=True)
    profil_user      = models.CharField(max_length=10, blank=True)
    type_action      = models.CharField(max_length=20, choices=TypeAction.choices)
    description      = models.TextField()
    objet_type       = models.CharField(max_length=50, blank=True)
    objet_id         = models.CharField(max_length=100, blank=True)
    objet_label      = models.CharField(max_length=255, blank=True)
    adresse_ip       = models.GenericIPAddressField(null=True, blank=True)
    terminal         = models.CharField(max_length=255, blank=True)
    issue            = models.CharField(max_length=10, choices=Issue.choices, default=Issue.SUCCES)
    horodatage_utc   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-horodatage_utc']

    def __str__(self):
        return f"[{self.type_action}] {self.description[:60]}"


def journaliser(request, type_action, description, objet_type='', objet_id='', objet_label='', issue='SUCCES'):
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        JournalAudit.objects.create(
            organisation     = getattr(request, 'tenant', None),
            utilisateur      = request.user if request.user.is_authenticated else None,
            identifiant_user = request.user.identifiant if request.user.is_authenticated else 'anonyme',
            profil_user      = request.user.profil if request.user.is_authenticated else '',
            type_action      = type_action,
            description      = description,
            objet_type       = objet_type,
            objet_id         = str(objet_id),
            objet_label      = objet_label,
            adresse_ip       = ip or None,
            terminal         = request.META.get('HTTP_USER_AGENT', '')[:255],
            issue            = issue,
        )
    except Exception:
        pass
