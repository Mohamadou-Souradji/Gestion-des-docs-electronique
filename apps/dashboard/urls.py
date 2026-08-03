from django.urls import path
from apps.dashboard import views

urlpatterns = [
    path('audit/',        views.journal_audit, name='audit'),
    path('recherche/',    views.recherche,      name='recherche'),
    path('statistiques/', views.statistiques,   name='statistiques'),
    path('export/excel/', views.export_excel, name='export-excel'),
    path('export/pdf/',   views.export_pdf,   name='export-pdf'),
]
