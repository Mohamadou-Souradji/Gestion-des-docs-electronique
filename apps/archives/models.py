"""
Module 6 - Archives historiques (versement retroactif).
Gere les documents des periodes CNIPT (1969-2011) et EST (2011-2023).
Ces archives sont separees des courriers courants et n'apparaissent pas
dans les statistiques d'activite courante.
"""

from django.db import models
from django.conf import settings


class FondsArchive(models.TextChoices):
    ESCEP = 'ESCEP', 'ESCEP (2023-present)'
    EST   = 'EST',   'EST (2011-2023)'
    CNIPT = 'CNIPT', 'CNIPT (1969-2011)'
    AUTRE = 'AUTRE', 'Autre fonds'


class TypeDocument(models.TextChoices):
    LETTRE      = 'LETTRE',      'Lettre'
    ARRETE      = 'ARRETE',      'Arrete'
    DECRET      = 'DECRET',      'Decret'
    NOTE        = 'NOTE',        'Note de service'
    CONVENTION  = 'CONVENTION',  'Convention'
    RAPPORT     = 'RAPPORT',     'Rapport'
    CIRCULAIRE  = 'CIRCULAIRE',  'Circulaire'
    AUTRE       = 'AUTRE',       'Autre'


class ArchiveHistorique(models.Model):
    """
    Document verse retroactivement dans le systeme.
    Marque comme archive historique, invisible dans les stats courantes.
    Reference systeme : ARC-XXX-AAAA-VNNNN (generee automatiquement).
    La reference d'origine est conservee integralement.
    """

    # Reference systeme generee automatiquement
    reference_systeme  = models.CharField(max_length=30, unique=True, blank=True)

    # Reference d'origine conservee integralement
    reference_origine  = models.CharField(max_length=200, blank=True)

    fonds         = models.CharField(max_length=10, choices=FondsArchive.choices)
    type_document = models.CharField(max_length=15, choices=TypeDocument.choices, default=TypeDocument.LETTRE)

    intitule      = models.CharField(max_length=500)
    expediteur    = models.CharField(max_length=255, blank=True)
    date_document = models.DateField()
    categorie     = models.CharField(max_length=200, blank=True)
    mots_cles     = models.TextField(blank=True, help_text='Mots-cles separes par des virgules')
    resume        = models.TextField(blank=True)

    # Fichier numerise
    fichier       = models.FileField(upload_to='archives/%Y/%m/')

    # Indexation OCR automatique (texte extrait du document)
    contenu_ocr   = models.TextField(blank=True, help_text='Texte extrait automatiquement par OCR')

    # Versement par lot : reference du lot si applicable
    lot           = models.CharField(max_length=100, blank=True, help_text='Identifiant du lot si versement par lot')

    verse_par     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='archives_versees'
    )
    date_versement = models.DateTimeField(auto_now_add=True)

    # Toujours marque comme archive historique
    est_historique = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Archive historique'
        verbose_name_plural = 'Archives historiques'
        ordering            = ['-date_document']

    def __str__(self):
        return f"{self.reference_systeme} - {self.intitule[:60]}"

    def save(self, *args, **kwargs):
        if not self.reference_systeme:
            annee = self.date_document.year if self.date_document else 2026
            count = ArchiveHistorique.objects.filter(
                date_versement__year=annee
            ).count() + 1
            self.reference_systeme = f"ARC-{self.fonds}-{annee}-V{str(count).zfill(4)}"
        super().save(*args, **kwargs)
