"""
Modèles courriers — GED ESCEP-Niger SaaS.
Ajout du champ organisation pour l'isolation multi-tenant.
"""
from django.db import models
from django.conf import settings


class StatutCourrier(models.TextChoices):
    BROUILLON   = 'BROUILLON',   'Brouillon'
    EN_VERIF    = 'EN_VERIF',    'En vérification'
    VERIFIE     = 'VERIFIE',     'Vérifié'
    REJETE      = 'REJETE',      'Rejeté'
    EN_ATT_IMP  = 'EN_ATT_IMP',  'En attente imputation'
    IMPUTE      = 'IMPUTE',      'Imputé'
    EN_COURS    = 'EN_COURS',    'En cours de traitement'
    TRAITE      = 'TRAITE',      'Traité'
    ARCHIVE     = 'ARCHIVE',     'Archivé'
    EN_ATTENTE_SGA = 'EN_ATT_SGA', 'En attente SGA'
    EN_ATTENTE_SG  = 'EN_ATT_SG',  'En attente SG'


class TypeCourrier(models.TextChoices):
    ENTRANT = 'ENT', 'Courrier entrant'
    INTERNE = 'INT', 'Courrier interne'


class ModeReception(models.TextChoices):
    DEPOT    = 'DEPOT',    'Dépôt direct'
    POSTAL   = 'POSTAL',   'Courrier postal'
    EMAIL    = 'EMAIL',    'Email imprimé'
    COURSIER = 'COURSIER', 'Coursier'


class Priorite(models.TextChoices):
    URGENT   = 'URGENT',   'Urgent'
    NORMALE = 'NORMALE', 'Normale'
    TRES_URGENT   = 'TRES_URGENT',   'Très urgent'


class Courrier(models.Model):
    #  AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='courriers',
        null=True,
    )

    identifiant_temp = models.CharField(max_length=30, unique=True, blank=True, null=True)
    numero_officiel  = models.CharField(max_length=30, unique=True, null=True, blank=True)

    type_courrier  = models.CharField(max_length=3,  choices=TypeCourrier.choices, default=TypeCourrier.ENTRANT)
    mode_reception = models.CharField(max_length=10, choices=ModeReception.choices, default=ModeReception.DEPOT)
    priorite       = models.CharField(max_length=20, choices=Priorite.choices, default=Priorite.NORMALE)
    statut         = models.CharField(max_length=15, choices=StatutCourrier.choices, default=StatutCourrier.BROUILLON)

    objet          = models.CharField(max_length=500)
    expediteur     = models.CharField(max_length=255)
    reference_exp  = models.CharField(max_length=100, blank=True)
    date_document  = models.DateField()
    date_reception = models.DateField()
    heure_depot = models.TimeField(null=True, blank=True)
    observations   = models.TextField(blank=True)
    fichier_reponse = models.FileField(upload_to='reponses/%Y/%m/', null=True, blank=True)

    fichier_pdf    = models.FileField(upload_to='courriers/%Y/%m/')

    saisi_par   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_saisis')
    date_saisie = models.DateTimeField(auto_now_add=True)

    verifie_par       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_verifies', null=True, blank=True)
    date_verification = models.DateTimeField(null=True, blank=True)
    motif_rejet       = models.TextField(blank=True)
    # Workflow étendu — SGA
    proposition_sga     = models.JSONField(null=True, blank=True)
    valide_sga_par      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                            related_name='courriers_valides_sga', null=True, blank=True)
    date_validation_sga = models.DateTimeField(null=True, blank=True)
    motif_rejet_sga     = models.TextField(blank=True)

    # Workflow étendu — SG
    proposition_sg      = models.JSONField(null=True, blank=True)
    valide_sg_par       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                            related_name='courriers_valides_sg', null=True, blank=True)
    date_validation_sg  = models.DateTimeField(null=True, blank=True)
    observation_dg    = models.TextField(blank=True)

    impute_par      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_imputes', null=True, blank=True)
    date_imputation = models.DateTimeField(null=True, blank=True)
    instructions_dg = models.TextField(blank=True)

    destinataire       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_recus', null=True, blank=True)
    date_traitement    = models.DateTimeField(null=True, blank=True)
    reponse_traitement = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_saisie']

    def __str__(self):
        ref = self.numero_officiel or self.identifiant_temp
        return f"{ref} - {self.objet[:60]}"

    def save(self, *args, **kwargs):
        if not self.identifiant_temp:
            from django.utils import timezone
            annee = timezone.now().year
            count = Courrier.objects.filter(date_saisie__year=annee).count() + 1
            self.identifiant_temp = f"BROUILLON-{annee}-{str(count).zfill(5)}"
        super().save(*args, **kwargs)

    def generer_numero_officiel(self):
        from django.utils import timezone
        annee = timezone.now().year
        # Numérotation par organisation
        count = Courrier.objects.filter(
            organisation=self.organisation,
            date_saisie__year=annee,
            numero_officiel__isnull=False
        ).count() + 1
        if self.organisation:
            prefix = (self.organisation.prefixe_courrier or self.organisation.code_tenant).upper()
        else:
            prefix = 'GED'
        return f"{prefix}-{annee}-{str(count).zfill(5)}"

    @property
    def statut_label(self):
        return dict(StatutCourrier.choices).get(self.statut, self.statut)


class Notification(models.Model):
    #  AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
    )
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message      = models.TextField()
    courrier     = models.ForeignKey(Courrier, on_delete=models.CASCADE, null=True, blank=True)
    lue          = models.BooleanField(default=False)
    date         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']


CONSIGNES_TYPES = [
    ('PROJET_REPONSE', 'Projet de réponse'),
    ('AVIS', 'Pour avis'),
    ('DISPOSITION_PRENDRE', 'Disposition à prendre'),
    ('EXPLOITATION', 'Pour exploitation'),
    ('DIFFUSION', 'Pour diffusion'),
    ('ETUDE_OBSERVATION', 'Pour étude et observation'),
    ('ATTRIBUTION', 'Pour attribution'),
    ('SUIVI', 'Pour suivi'),
    ('ASSISTER', 'Pour y assister'),
    ('SUITE_DONNER', 'Suite à donner'),
    ('INFORMATION', 'Pour information'),
    ('SAISIR_INTERESSE', 'Pour saisir l\'intéressé(s)'),
    ('VERIFICATION', 'Pour vérification'),
    ('NOTER_CLASSER', 'Pour noter et classer'),
    ('ARCHIVER', 'Pour archiver'),
    ('COMPTE_RENDU', 'Faire un compte rendu'),
    ('RAPPORT', 'Faire un rapport'),
    ('NOTE', 'Faire une note'),
    ('RESUME', 'Faire un résumé'),
    ('COMMENTAIRE', 'Faire un commentaire'),
    ('PARLER', 'M\'en parler'),
]

class CourrierCopie(models.Model):
    #  AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='courrier_copies',
        null=True,
    )
    courrier     = models.ForeignKey(Courrier, on_delete=models.CASCADE, related_name='copies')
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='courriers_en_copie')
    date_lecture = models.DateTimeField(null=True, blank=True)
    consignes_types = models.JSONField(default=list, blank=True)
    consigne_libre  = models.TextField(blank=True)
    reponse         = models.TextField(blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    fichier_reponse = models.FileField(upload_to='reponses_copie/%Y/%m/', null=True, blank=True)
    class Meta:
        unique_together = ('courrier', 'destinataire')
