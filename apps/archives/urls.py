from django.urls import path
from . import views

urlpatterns = [
    path('archives/',              views.liste_archives,    name='archives'),
    path('archives/lot/',          views.versement_par_lot, name='versement_lot'),
    path('archives/fonds/',        views.fonds_disponibles, name='fonds'),
]
