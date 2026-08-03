from django.contrib import admin
from apps.organisations.models import Organisation

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'code_tenant', 'plan', 'active', 'date_creation']
    list_filter   = ['plan', 'active']
    search_fields = ['nom', 'code_tenant']
    readonly_fields = ['date_creation']

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def delete_queryset(self, request, queryset):
        for org in queryset:
            org.delete()