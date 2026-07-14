from django.urls import path
from . import views

urlpatterns = [
    # Module 1 - Bureau d Ordre
    path('courriers/',                         views.liste_courriers,      name='courriers'),
    path('courriers/<int:pk>/modifier/',       views.modifier_courrier,    name='modifier'),
    # Module 2 - Assistant DG
    path('courriers/<int:pk>/valider/',        views.valider_courrier,     name='valider'),
    path('courriers/<int:pk>/rejeter/',        views.rejeter_courrier,     name='rejeter'),
    # Module 3 - DG
    path('destinataires/',                     views.liste_destinataires,  name='destinataires'),
    path('consignes-types/',                   views.liste_consignes_types,name='consignes_types'),
    path('courriers/<int:pk>/imputer/',        views.imputer_courrier,     name='imputer'),
    # Module 4 - Destinataire
    path('courriers/<int:pk>/marquer-lu/',     views.marquer_lu,           name='marquer_lu'),
    path('courriers/<int:pk>/marquer-traite/', views.marquer_traite,       name='marquer_traite'),
    # Module 5 - Archiviste
    path('courriers/<int:pk>/archiver/',       views.archiver_courrier,    name='archiver'),
    # Notifications
    path('notifications/',                     views.mes_notifications,    name='notifications'),
    path('notifications/count/',               views.compter_notifications,name='notif_count'),
]
