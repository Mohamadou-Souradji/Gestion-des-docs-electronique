# apps/dashboard/admin.py
from django.contrib import admin
from .models import JournalAudit


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display  = ['horodatage_utc', 'identifiant_user', 'profil_user', 'type_action', 'issue', 'organisation']
    list_filter   = ['type_action', 'issue', 'profil_user', 'organisation']
    search_fields = ['identifiant_user', 'description', 'objet_id']
    readonly_fields = [
        'organisation', 'utilisateur', 'identifiant_user', 'profil_user',
        'type_action', 'description', 'objet_type', 'objet_id', 'objet_label',
        'adresse_ip', 'terminal', 'issue', 'horodatage_utc'
    ]
    ordering = ['-horodatage_utc']

    def has_add_permission(self, request):
        return False  # Journal en lecture seule

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # ← au lieu de return False