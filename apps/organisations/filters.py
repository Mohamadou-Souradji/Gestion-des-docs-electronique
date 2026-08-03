from rest_framework import filters

class TenantFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not hasattr(request, 'tenant') or not request.tenant:
            return queryset.none()
        
        model_fields = [f.name for f in queryset.model._meta.get_fields()]
        if 'organisation' in model_fields:
            return queryset.filter(organisation=request.tenant)
        
        return queryset
