"""
Modele principal des courriers - GED ESCEP-Niger.

Statuts du circuit :
  BROUILLON -> EN_VERIF -> VERIFIE (EN_ATT_IMP) -> IMPUTE -> EN_COURS -> TRAITE -> ARCHIVE
                       -> REJETE (retour possible au BO)

Regles CCFT :
- Numero officiel genere automatiquement a la validation uniquement
- Imputation reservee au DG seul
- Cloisonnement strict par destinataire
"""

from django.db import models
from django.conf import settings


class StatutCourrier(models.TextChoices):
    BROUILLON   = 'BROUILLON',   'Brouillon'
    EN_VERIF    = 'EN_VERIF',    'En verification'
    VERIFIE     = 'VERIFIE',     'Verifie'
    REJETE      = 'REJETE',      'Rejete'
    EN_ATT_IMP  = 'EN_ATT_IMP',  'En attente imputation'
    IMPUTE      = 'IMPUTE',      'Impute'
    EN_COURS    = 'EN_COURS',    'En cours de traitement'
    TRAITE      = 'TRAITE',      'Traite'
    ARCHIVE     = 'ARCHIVE',     'Archive'


class TypeCourrier(models.TextChoices):
    ENTRANT = 'ENT', 'Courrier entrant'
    INTERNE = 'INT', 'Courrier interne'


class ModeReception(models.TextChoices):
    DEPOT    = 'DEPOT',    'Depot direct'
    POSTAL   = 'POSTAL',   'Courrier postal'
    EMAIL    = 'EMAIL',    'Email imprime'
    COURSIER = 'COURSIER', 'Coursier'


class Priorite(models.TextChoices):
    HAUTE   = 'HAUTE',   'Haute'
    NORMALE = 'NORMALE', 'Normale'
    BASSE   = 'BASSE',   'Basse'


class Courrier(models.Model):

    # Identifiant temporaire attribue a la saisie (jamais le numero officiel)
    identifiant_temp = models.CharField(max_length=30, unique=True, blank=True, null=True)

    # Numero officiel - genere automatiquement a la validation par l'Assistant DG
    numero_officiel  = models.CharField(max_length=30, unique=True, null=True, blank=True)

    type_courrier  = models.CharField(max_length=3,  choices=TypeCourrier.choices, default=TypeCourrier.ENTRANT)
    mode_reception = models.CharField(max_length=10, choices=ModeReception.choices, default=ModeReception.DEPOT)
    priorite       = models.CharField(max_length=10, choices=Priorite.choices, default=Priorite.NORMALE)
    statut         = models.CharField(max_length=15, choices=StatutCourrier.choices, default=StatutCourrier.BROUILLON)

    objet          = models.CharField(max_length=500)
    expediteur     = models.CharField(max_length=255)
    reference_exp  = models.CharField(max_length=100, blank=True)
    date_document  = models.DateField()
    date_reception = models.DateField()
    observations   = models.TextField(blank=True)

    fichier_pdf    = models.FileField(upload_to='courriers/%Y/%m/')

    # Bureau d'Ordre
    saisi_par   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_saisis')
    date_saisie = models.DateTimeField(auto_now_add=True)

    # Assistant DG
    verifie_par       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_verifies', null=True, blank=True)
    date_verification = models.DateTimeField(null=True, blank=True)
    motif_rejet       = models.TextField(blank=True)
    observation_dg    = models.TextField(blank=True)

    # DG
    impute_par      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_imputes', null=True, blank=True)
    date_imputation = models.DateTimeField(null=True, blank=True)
    instructions_dg = models.TextField(blank=True)

    # Destinataire
    destinataire       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_recus', null=True, blank=True)
    date_traitement    = models.DateTimeField(null=True, blank=True)
    reponse_traitement = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Courrier'
        verbose_name_plural = 'Courriers'
        ordering            = ['-date_saisie']

    def __str__(self):
        ref = self.numero_officiel or self.identifiant_temp
        return f"{ref} - {self.objet[:60]}"

    def save(self, *args, **kwargs):
        # Generer l'identifiant temporaire automatiquement a la creation
        if not self.identifiant_temp:
            from django.utils import timezone
            annee = timezone.now().year
            count = Courrier.objects.filter(date_saisie__year=annee).count() + 1
            self.identifiant_temp = f"BROUILLON-{annee}-{str(count).zfill(5)}"
        super().save(*args, **kwargs)

    def generer_numero_officiel(self):
        """Genere le numero officiel. Appele uniquement par l'Assistant DG a la validation."""
        from django.utils import timezone
        annee = timezone.now().year
        count = Courrier.objects.filter(
            date_saisie__year=annee,
            numero_officiel__isnull=False
        ).count() + 1
        return f"ESCEP-{annee}-{str(count).zfill(5)}"

    @property
    def statut_label(self):
        return dict(StatutCourrier.choices).get(self.statut, self.statut)


class Notification(models.Model):
    """
    Notifications push entre utilisateurs.
    Ex: BO soumet -> Assistant recoit. Assistant valide/rejette -> BO recoit.
    """
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message      = models.TextField()
    courrier     = models.ForeignKey(Courrier, on_delete=models.CASCADE, null=True, blank=True)
    lue          = models.BooleanField(default=False)
    date         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Notif pour {self.destinataire} - {self.message[:50]}"


# Consignes types predefinies (CCFT Annexe C) - Module 3
CONSIGNES_TYPES = [
    ('TRAITER',    'A traiter'),
    ('REPONDRE',   'A repondre'),
    ('ETUDE',      'Pour etude et avis'),
    ('INFO',       'Pour information'),
    ('SUITE',      'Pour suite a donner'),
    ('ARCHIVER',   'A archiver apres traitement'),
]


class CourrierCopie(models.Model):
    """
    Destinataires en copie d un courrier.
    Un courrier peut avoir plusieurs destinataires en copie (facultatif).
    """
    courrier     = models.ForeignKey(Courrier, on_delete=models.CASCADE, related_name='copies')
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_en_copie')
    date_lecture = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('courrier', 'destinataire')

    def __str__(self):
        return f"Copie de {self.courrier} a {self.destinataire}"
