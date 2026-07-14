"""
Modèles utilisateurs et paramètres de l'application GED ESCEP-Niger.
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


# Modules disponibles dans le système
MODULES_DISPONIBLES = [
    ('courriers',    'Courriers'),
    ('archives',     'Archives'),
    ('recherche',    'Recherche documentaire'),
    ('statistiques', 'Statistiques'),
    ('audit',        'Journal d\'audit'),
    ('delegations',  'Délégations'),
]


class Direction(models.Model):
    """
    Directions et départements de l'établissement.
    Paramétrées par l'Administrateur.
    """
    nom        = models.CharField(max_length=200, unique=True)
    sigle      = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    active     = models.BooleanField(default=True)
    ordre      = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Direction'
        ordering     = ['ordre', 'nom']

    def __str__(self):
        return f"{self.sigle} — {self.nom}" if self.sigle else self.nom


class ParametresApplication(models.Model):
    """
    Paramètres généraux de l'application.
    Un seul enregistrement (singleton).
    Modifiable par l'Administrateur uniquement.
    """
    # Identité
    nom_application  = models.CharField(max_length=100, default='GED ESCEP-Niger')
    slogan           = models.CharField(max_length=200, default='Gestion Électronique des Documents')
    texte_pied_page  = models.CharField(max_length=300, default='© ESCEP-Niger — Système de Gestion Électronique des Documents')

    # Apparence
    couleur_principale = models.CharField(max_length=7, default='#1565C0')
    couleur_accent     = models.CharField(max_length=7, default='#FDD835')
    couleur_danger     = models.CharField(max_length=7, default='#D32F2F')

    # Logo et image de fond
    logo             = models.ImageField(upload_to='parametres/', null=True, blank=True)
    image_fond_login = models.ImageField(upload_to='parametres/', null=True, blank=True)

    # Sécurité
    timeout_inactivite   = models.PositiveIntegerField(default=30, help_text='Minutes avant déconnexion automatique')
    duree_validite_mdp   = models.PositiveIntegerField(default=90, help_text='Jours avant expiration du mot de passe')
    tentatives_max       = models.PositiveIntegerField(default=5, help_text='Tentatives avant verrouillage')
    double_auth_active   = models.BooleanField(default=False, help_text='Activer la double authentification globalement')

    # Email pour la double authentification
    email_expediteur     = models.EmailField(blank=True, help_text='Email qui envoie les codes 2FA')
    texte_email_2fa      = models.TextField(
        default='Votre code de vérification GED ESCEP-Niger est : {code}\nCe code expire dans 10 minutes.',
        help_text='Texte de l\'email 2FA. Utiliser {code} pour le code.'
    )

    class Meta:
        verbose_name = 'Paramètres de l\'application'

    def __str__(self):
        return self.nom_application

    @classmethod
    def get(cls):
        """Retourne ou crée le singleton des paramètres."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class UtilisateurManager(BaseUserManager):

    def create_user(self, identifiant, password=None, **extra_fields):
        if not identifiant:
            raise ValueError("L'identifiant est obligatoire")
        user = self.model(identifiant=identifiant, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifiant, password=None, **extra_fields):
        extra_fields.setdefault('profil', PROFIL.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(identifiant, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur avec gestion des modules, sécurité renforcée et 2FA.
    """
    identifiant   = models.CharField(max_length=50, unique=True)
    nom           = models.CharField(max_length=100)
    prenom        = models.CharField(max_length=100)
    email         = models.EmailField(blank=True)
    fonction      = models.CharField(max_length=150, blank=True)
    direction     = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    profil        = models.CharField(max_length=10, choices=PROFIL.choices)
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    # Modules accessibles à cet utilisateur (JSON list)
    modules_actifs = models.JSONField(default=list, blank=True,
        help_text='Liste des modules accessibles ex: ["courriers","archives"]')

    # Sécurité mot de passe
    date_derniere_mdp    = models.DateTimeField(null=True, blank=True)
    alerte_mdp_envoyee   = models.BooleanField(default=False)

    # Double authentification
    double_auth_active   = models.BooleanField(default=False)
    double_auth_desactive_admin = models.BooleanField(default=False,
        help_text='Admin a désactivé la 2FA pour cet utilisateur')
    code_2fa             = models.CharField(max_length=6, blank=True)
    code_2fa_expiration  = models.DateTimeField(null=True, blank=True)

    # Verrouillage
    tentatives_connexion = models.PositiveIntegerField(default=0)
    verrouille_jusqu    = models.DateTimeField(null=True, blank=True)

    objects = UtilisateurManager()

    USERNAME_FIELD  = 'identifiant'
    REQUIRED_FIELDS = ['nom', 'prenom', 'profil']

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
        params = ParametresApplication.get()
        delta = timezone.now() - self.date_derniere_mdp
        return delta.days >= params.duree_validite_mdp

    def get_modules(self):
        """Retourne les modules accessibles selon le profil et les modules activés."""
        # Modules par défaut selon le profil
        modules_profil = {
            'DG':    ['courriers', 'statistiques', 'audit', 'delegations', 'recherche'],
            'ASSIST':['courriers'],
            'BO':    ['courriers'],
            'DEST':  ['courriers'],
            'ARC':   ['courriers', 'archives', 'recherche'],
            'ADMIN': ['parametres', 'comptes', 'supervision'],
        }
        base = modules_profil.get(self.profil, [])
        # Ajouter les modules supplémentaires accordés par l'admin
        extra = self.modules_actifs or []
        return list(set(base + extra))
