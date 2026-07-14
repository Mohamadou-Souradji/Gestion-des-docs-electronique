from django.urls import path
from . import views

urlpatterns = [
    # Module 8 - Statistiques DG
    path('dashboard/statistiques/', views.statistiques_dg,    name='statistiques'),
    # Module 9 - Journal d audit
    path('audit/',                  views.journal_audit,       name='audit'),
    # Module 10 - Delegations
    path('delegations/',            views.liste_delegations,   name='delegations'),
    path('delegations/<int:pk>/revoquer/', views.revoquer_delegation, name='revoquer'),
    # Module 7 - Recherche
    path('recherche/',              views.recherche_globale,   name='recherche'),
    path('dashboard/export/pdf/',     views.export_pdf,       name='export_pdf'),
path('dashboard/export/excel/',   views.export_excel,     name='export_excel'),
]
