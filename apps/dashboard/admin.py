from django.contrib import admin
from .models import JournalAudit, Delegation


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display  = ('horodatage_utc', 'identifiant_user', 'profil_user', 'type_action', 'issue', 'adresse_ip')
    list_filter   = ('type_action', 'issue', 'profil_user')
    search_fields = ('identifiant_user', 'description', 'objet_libelle')
    ordering      = ('-horodatage_utc',)
    readonly_fields = [f.name for f in JournalAudit._meta.fields]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(Delegation)
class DelegationAdmin(admin.ModelAdmin):
    list_display  = ('accordee_par', 'beneficiaire', 'perimetre', 'date_debut', 'date_fin', 'active')
    list_filter   = ('perimetre', 'active')
    ordering      = ('-date_creation',)
    readonly_fields = ('date_creation',)
