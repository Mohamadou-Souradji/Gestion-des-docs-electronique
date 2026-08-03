"""
Modèles utilisateurs — GED ESCEP-Niger SaaS.
Ajout du champ organisation (multi-tenant).
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class PROFIL(models.TextChoices):
    DG         = 'DG',     'Directeur Général'
    ASSISTANT  = 'ASSIST', 'Assistant DG'
    BUREAU     = 'BO',     "Bureau d'Ordre"
    DEST       = 'DEST',   'Destinataire'
    ARCHIVISTE = 'ARC',    'Archiviste'
    ADMIN      = 'ADMIN',  'Administrateur'
    SGA        = 'SGA', 'Secrétaire Général Adjoint'
    SG         = 'SG',  'Secrétaire Général'


MODULES_DISPONIBLES = [
    ('courriers',    'Courriers'),
    ('archives',     'Archives'),
    ('recherche',    'Recherche documentaire'),
    ('statistiques', 'Statistiques'),
    ('audit',        "Journal d'audit"),
    ('delegations',  'Délégations'),
]


class Direction(models.Model):
    #  AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='directions',
        null=True,
    )
    nom         = models.CharField(max_length=200)
    sigle       = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    active      = models.BooleanField(default=True)
    ordre       = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Direction'
        ordering     = ['ordre', 'nom']

    def __str__(self):
        return f"{self.sigle} — {self.nom}" if self.sigle else self.nom


class UtilisateurManager(BaseUserManager):

    def create_user(self, identifiant, password=None, **extra_fields):
        if not identifiant:
            raise ValueError("L'identifiant est obligatoire")
        user = self.model(identifiant=identifiant, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifiant, password=None, **extra_fields):
        from .models import MODULES_DISPONIBLES
        tous_modules = [code for code, _ in MODULES_DISPONIBLES]
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('nom', 'Admin')
        extra_fields.setdefault('prenom', 'Admin')
        extra_fields.setdefault('modules_actifs', tous_modules)
        return self.create_user(identifiant, password, **extra_fields)

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    #  AJOUT MULTI-TENANT
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='utilisateurs',
        null=True,
    )

    identifiant   = models.CharField(max_length=50, unique=True)
    nom           = models.CharField(max_length=100)
    prenom        = models.CharField(max_length=100)
    email         = models.EmailField(blank=True)
    fonction      = models.CharField(max_length=150, blank=True)
    direction     = models.ForeignKey(
        Direction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='utilisateurs'
    )
    profil = models.CharField(max_length=10, choices=PROFIL.choices, blank=True, default='')
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    modules_actifs = models.JSONField(default=list, blank=True)

    date_derniere_mdp    = models.DateTimeField(null=True, blank=True)
    alerte_mdp_envoyee   = models.BooleanField(default=False)

    double_auth_active          = models.BooleanField(default=False)
    double_auth_desactive_admin = models.BooleanField(default=False)
    code_2fa                    = models.CharField(max_length=6, blank=True)
    code_2fa_expiration         = models.DateTimeField(null=True, blank=True)

    tentatives_connexion = models.PositiveIntegerField(default=0)
    verrouille_jusqu     = models.DateTimeField(null=True, blank=True)

    objects = UtilisateurManager()

    USERNAME_FIELD  = 'identifiant'
    # REQUIRED_FIELDS = ['nom', 'prenom', 'profil']
    REQUIRED_FIELDS = []
    class Meta:
        verbose_name        = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.get_profil_display()}"

    @property
    def est_verrouille(self):
        if self.verrouille_jusqu and self.verrouille_jusqu > timezone.now():
            return True
        return False

    @property
    def mdp_expire(self):
        if not self.date_derniere_mdp:
            return False
        org = self.organisation
        if org:
            delta = timezone.now() - self.date_derniere_mdp
            return delta.days >= org.duree_validite_mdp
        return False

    def get_modules(self):
        return list(self.modules_actifs or [])
