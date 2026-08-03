from django.db import models
from django.conf import settings

class Organisation(models.Model):
    """Chaque client SaaS est une organisation indépendante"""
    
    code_tenant = models.CharField(
        max_length=50, unique=True,
        help_text="Slug unique (escep, ministere, universite, etc.)"
    )
    nom = models.CharField(max_length=200)
    slogan = models.CharField(max_length=200, blank=True)
    texte_pied_page = models.CharField(max_length=300, blank=True)
    
    logo = models.ImageField(upload_to='organisations/%Y/%m/', null=True, blank=True)
    image_fond_login = models.ImageField(upload_to='organisations/%Y/%m/', null=True, blank=True)
    favicon = models.ImageField(upload_to='organisations/%Y/%m/', null=True, blank=True)
    
    couleur_principale = models.CharField(max_length=7, default='#1565C0')
    couleur_accent = models.CharField(max_length=7, default='#FDD835')
    couleur_danger = models.CharField(max_length=7, default='#D32F2F')
    flou_image_fond = models.PositiveIntegerField(default=5)
    # Dans apps/organisations/models.py
    consignes_imputation = models.JSONField(
        default=list,
        blank=True,
    )
    # Typographie (NOUVEAUX CHAMPS)
    police = models.CharField(
        max_length=200,
        default="'Segoe UI', sans-serif",
        help_text='Police CSS (ex: Roboto, Arial, Montserrat)'
    )
    taille_texte_base = models.CharField(
        max_length=10,
        default='14px',
        help_text='Taille de base (ex: 13px, 14px, 15px)'
    )
    couleur_texte = models.CharField(
        max_length=7,
        default='#222222',
        help_text='Couleur texte principal'
    )
    couleur_texte_secondaire = models.CharField(
        max_length=7,
        default='#666666',
        help_text='Couleur texte secondaire/sous-titres'
    )
    graisse_titres = models.CharField(
        max_length=10,
        default='700',
        help_text='Graisse des titres (500, 600, 700, 800)'
    )
    rayon_bord = models.CharField(
        max_length=10,
        default='6px',
        help_text='Rayon des coins (0px, 4px, 6px, 10px)'
    )

    
    domaine_personnalise = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    admin_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='organisations_administrees'
    )
    
    max_utilisateurs = models.PositiveIntegerField(default=50)
    max_stockage_go = models.PositiveIntegerField(default=100)
    
    plan = models.CharField(
        max_length=20,
        choices=[('GRATUIT', 'Gratuit'), ('PRO', 'Pro'), ('ENTERPRISE', 'Entreprise')],
        default='GRATUIT'
    )
    WORKFLOW_CHOICES = [
        ('CLASSIQUE', 'Classique (ASSIST → DG)'),
        ('ETENDU',    'Étendu (SGA → SG → DG)'),
    ]
    workflow_type = models.CharField(
        max_length=10,
        choices=WORKFLOW_CHOICES,
        default='CLASSIQUE',
    )
    date_fin_abonnement = models.DateField(null=True, blank=True)
    
    timeout_inactivite = models.PositiveIntegerField(default=30)
    duree_validite_mdp = models.PositiveIntegerField(default=90)
    tentatives_max = models.PositiveIntegerField(default=5)
    double_auth_active = models.BooleanField(default=False)
    email_expediteur = models.EmailField(blank=True)
    
    prefixe_courrier = models.CharField(
        max_length=10, blank=True,
        help_text="Préfixe des numéros de courrier (ex: OT, MIN-FIN). Laissez vide pour utiliser le code tenant."
    )
    texte_email_2fa = models.TextField(
        default='Votre code de vérification est : {code}\nCe code expire dans 10 minutes.'
    )
    
    class Meta:
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code_tenant})"
