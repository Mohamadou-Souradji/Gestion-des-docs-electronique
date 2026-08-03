# apps/archives/admin.py
from django.contrib import admin
from .models import FondsArchive, ArchiveHistorique


@admin.register(FondsArchive)
class FondsArchiveAdmin(admin.ModelAdmin):
    list_display  = ['code', 'intitule', 'organisation', 'date_creation']
    list_filter   = ['organisation']
    search_fields = ['code', 'intitule']


@admin.register(ArchiveHistorique)
class ArchiveAdmin(admin.ModelAdmin):
    list_display  = ['reference_systeme', 'intitule', 'fonds', 'date_document', 'date_versement', 'organisation']
    list_filter   = ['organisation', 'fonds']
    search_fields = ['reference_systeme', 'intitule', 'mots_cles']
    readonly_fields = ['reference_systeme', 'date_versement', 'verse_par']