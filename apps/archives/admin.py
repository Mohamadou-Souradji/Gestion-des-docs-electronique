from django.contrib import admin
from .models import ArchiveHistorique

@admin.register(ArchiveHistorique)
class ArchiveAdmin(admin.ModelAdmin):
    list_display  = ('reference_systeme', 'intitule', 'fonds', 'type_document', 'date_document', 'verse_par')
    list_filter   = ('fonds', 'type_document')
    search_fields = ('reference_systeme', 'reference_origine', 'intitule', 'expediteur', 'mots_cles')
    ordering      = ('-date_versement',)
    readonly_fields = ('reference_systeme', 'date_versement')
