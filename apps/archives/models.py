from django.db import models
from django.conf import settings

class FondsArchive(models.Model):
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='fonds_archives',
        null=True,
    )
    code        = models.CharField(max_length=20)
    intitule    = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.intitule}"


class ArchiveHistorique(models.Model):
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='archives',
        null=True,
    )
    fonds              = models.ForeignKey(FondsArchive, on_delete=models.PROTECT, related_name='documents',null=True)
    reference_systeme  = models.CharField(max_length=50, unique=True, blank=True)
    intitule           = models.CharField(max_length=255)
    description        = models.TextField(blank=True)
    date_document      = models.DateField(null=True, blank=True)
    date_versement     = models.DateTimeField(auto_now_add=True)
    verse_par          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fichier_pdf        = models.FileField(upload_to='archives/%Y/%m/', null=True, blank=True)
    mots_cles          = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-date_versement']

    def __str__(self):
        return f"{self.reference_systeme} - {self.intitule}"

    def save(self, *args, **kwargs):
        if not self.reference_systeme:
            from django.utils import timezone
            annee = timezone.now().year
            prefix = self.organisation.code_tenant.upper() if self.organisation else 'ARC'
            count = ArchiveHistorique.objects.filter(
                organisation=self.organisation,
                date_versement__year=annee
            ).count() + 1
            self.reference_systeme = f"{prefix}-ARC-{annee}-{str(count).zfill(5)}"
        super().save(*args, **kwargs)
