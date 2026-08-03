from django.contrib import admin
from .models import Courrier


@admin.register(Courrier)
class CourrierAdmin(admin.ModelAdmin):
    list_display  = ('numero_officiel', 'objet', 'expediteur', 'statut', 'date_saisie')
    list_filter   = ('statut', 'type_courrier')
    search_fields = ('numero_officiel', 'objet', 'expediteur')
    ordering      = ('-date_saisie',)
    readonly_fields = ('numero_officiel', 'date_saisie')


