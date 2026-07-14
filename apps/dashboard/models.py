"""
Modeles pour les modules 9 et 10 de la GED ESCEP-Niger.
Module 9 : Journal d audit immutable - toutes les actions du systeme
Module 10 : Delegations ponctuelles du DG
"""

from django.db import models
from django.conf import settings


# ---------------------------------------------------------------
# MODULE 9 - Journal d audit
# ---------------------------------------------------------------

class TypeAction(models.TextChoices):
    # Courriers
    SAISIE        = 'SAISIE',        'Saisie de courrier'
    SOUMISSION    = 'SOUMISSION',     'Soumission a verification'
    MODIFICATION  = 'MODIFICATION',  'Modification de courrier'
    VALIDATION    = 'VALIDATION',    'Validation de courrier'
    REJET         = 'REJET',         'Rejet de courrier'
    IMPUTATION    = 'IMPUTATION',    'Imputation de courrier'
    CONSULTATION  = 'CONSULTATION',  'Consultation de courrier'
    TELECHARGEMENT= 'TELECHARGEMENT','Telechargement de document'
    TRAITEMENT    = 'TRAITEMENT',    'Traitement de courrier'
    ARCHIVAGE     = 'ARCHIVAGE',     'Archivage de courrier'
    # Comptes
    CREATION_COMPTE   = 'CREATION_COMPTE',   'Creation de compte'
    MODIFICATION_COMPTE = 'MODIF_COMPTE',    'Modification de compte'
    DESACTIVATION_COMPTE = 'DESACT_COMPTE',  'Desactivation de compte'
    # Delegations
    DELEGATION_ACCORDEE = 'DELEG_ACCORD',   'Delegation accordee'
    DELEGATION_REVOQUEE = 'DELEG_REVOQUE',  'Delegation revoquee'
    DELEGATION_UTILISEE = 'DELEG_UTIL',     'Delegation utilisee'
    # Acces
    CONNEXION     = 'CONNEXION',     'Connexion'
    ACCES_REFUSE  = 'ACCES_REFUSE',  'Acces refuse'
    # Archives
    VERSEMENT     = 'VERSEMENT',     'Versement d archive'


class Issue(models.TextChoices):
    SUCCES = 'SUCCES', 'Succes'
    REFUS  = 'REFUS',  'Refus'
    ERREUR = 'ERREUR', 'Erreur'


class JournalAudit(models.Model):
    """
    Journal d audit immutable.
    Aucune entree ne peut etre modifiee ou supprimee.
    Reserve en lecture au DG uniquement.
    """

    # Horodatage UTC et local
    horodatage_utc   = models.DateTimeField(auto_now_add=True)

    # Utilisateur
    utilisateur      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='actions_audit'
    )
    identifiant_user = models.CharField(max_length=50, blank=True)  # conserve si compte supprime
    profil_user      = models.CharField(max_length=10, blank=True)

    # Action
    type_action      = models.CharField(max_length=20, choices=TypeAction.choices)
    description      = models.TextField()

    # Objet de l action
    objet_type       = models.CharField(max_length=50, blank=True)  # 'courrier', 'archive', 'compte'
    objet_id         = models.CharField(max_length=100, blank=True) # numero ou identifiant
    objet_libelle    = models.CharField(max_length=500, blank=True) # objet lisible

    # Origine
    adresse_ip       = models.GenericIPAddressField(null=True, blank=True)
    terminal         = models.CharField(max_length=255, blank=True) # user-agent

    # Resultat
    issue            = models.CharField(max_length=10, choices=Issue.choices, default=Issue.SUCCES)

    class Meta:
        verbose_name        = 'Journal d audit'
        verbose_name_plural = 'Journal d audit'
        ordering            = ['-horodatage_utc']
        # Empecher toute modification
        default_permissions = ('view',)

    def __str__(self):
        return f"{self.horodatage_utc} | {self.identifiant_user} | {self.type_action}"

    def save(self, *args, **kwargs):
        # Conserver l identifiant meme si le compte est supprime
        if self.utilisateur and not self.identifiant_user:
            self.identifiant_user = self.utilisateur.identifiant
            self.profil_user      = self.utilisateur.profil
        # Empecher la modification d une entree existante
        if self.pk:
            raise PermissionError("Le journal d audit est immutable.")
        super().save(*args, **kwargs)


def journaliser(request, type_action, description, objet_type='', objet_id='', objet_libelle='', issue=Issue.SUCCES):
    """
    Fonction utilitaire pour creer une entree dans le journal.
    A appeler depuis toutes les vues apres chaque action significative.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    terminal = request.META.get('HTTP_USER_AGENT', '')[:255]

    JournalAudit.objects.create(
        utilisateur    = request.user if request.user.is_authenticated else None,
        identifiant_user = request.user.identifiant if request.user.is_authenticated else 'anonyme',
        profil_user    = request.user.profil if request.user.is_authenticated else '',
        type_action    = type_action,
        description    = description,
        objet_type     = objet_type,
        objet_id       = str(objet_id),
        objet_libelle  = objet_libelle[:500],
        adresse_ip     = ip or None,
        terminal       = terminal,
        issue          = issue,
    )


# ---------------------------------------------------------------
# MODULE 10 - Delegations ponctuelles
# ---------------------------------------------------------------

class PerimetreDelegation(models.TextChoices):
    COURRIER  = 'COURRIER',  'Un courrier specifique'
    PERIODE   = 'PERIODE',   'Une periode donnee'
    FONDS     = 'FONDS',     'Un fonds d archive'
    DOSSIER   = 'DOSSIER',   'Un dossier thematique'


class Delegation(models.Model):
    """
    Delegation ponctuelle accordee par le DG a un agent.
    Droits accordes uniquement en lecture, jamais en modification.
    Expiration automatique a la date prevue.
    """

    accordee_par  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='delegations_accordees'
    )
    beneficiaire  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='delegations_recues'
    )

    perimetre     = models.CharField(max_length=15, choices=PerimetreDelegation.choices)
    motif         = models.TextField()

    # Perimetre detail selon le type
    courrier_vise      = models.ForeignKey(
        'courriers.Courrier', on_delete=models.CASCADE,
        null=True, blank=True, related_name='delegations'
    )
    periode_debut      = models.DateField(null=True, blank=True)
    periode_fin_perim  = models.DateField(null=True, blank=True)
    fonds_vise         = models.CharField(max_length=10, blank=True)  # ESCEP, EST, CNIPT
    dossier_thematique = models.CharField(max_length=255, blank=True)

    # Duree de la delegation
    date_debut    = models.DateField()
    date_fin      = models.DateField()

    # Etat
    active        = models.BooleanField(default=True)
    date_revocation = models.DateTimeField(null=True, blank=True)
    motif_revocation = models.TextField(blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Delegation'
        verbose_name_plural = 'Delegations'
        ordering            = ['-date_creation']

    def __str__(self):
        return f"Delegation de {self.accordee_par} a {self.beneficiaire} ({self.perimetre})"

    @property
    def est_active(self):
        """Verifie si la delegation est active et non expiree."""
        from django.utils import timezone
        aujourd_hui = timezone.now().date()
        return self.active and self.date_debut <= aujourd_hui <= self.date_fin
