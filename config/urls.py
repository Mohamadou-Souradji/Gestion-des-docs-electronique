"""
URLs principales du projet GED ESCEP-Niger.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users : authentification, paramètres, directions, comptes
    path('api/', include('apps.users.urls')),

    # Courriers : modules 1 à 5
    path('api/', include('apps.courriers.urls')),

    # Archives : module 6
    path('api/', include('apps.archives.urls')),

    # Dashboard : modules 7, 8, 9, 10
    path('api/', include('apps.dashboard.urls')),

    # Renouvellement token JWT
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
