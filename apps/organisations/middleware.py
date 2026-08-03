"""
TenantMiddleware — Injecte le tenant depuis le JWT ou le domaine.
Supporte les URLs par domaine personnalisé (point 8).
"""
import jwt
from django.conf import settings


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant    = None
        request.tenant_id = None

        # 1. Essayer depuis le JWT
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            try:
                token_str = auth_header.split(' ')[1]
                decoded   = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
                tenant_id = decoded.get('tenant_id')
                if tenant_id:
                    from apps.organisations.models import Organisation
                    request.tenant_id = tenant_id
                    request.tenant    = Organisation.objects.get(id=tenant_id, active=True)
            except Exception:
                pass

        # 2. Si pas de JWT, essayer depuis le domaine (point 8)
        if not request.tenant:
            host = request.get_host().split(':')[0]
            try:
                from apps.organisations.models import Organisation
                request.tenant = Organisation.objects.get(
                    domaine_personnalise=host, active=True
                )
                request.tenant_id = request.tenant.id
            except Exception:
                pass

        response = self.get_response(request)
        return response