from django.urls import path
from apps.courriers import views

urlpatterns = [
    path('courriers/',                          views.liste_courriers,      name='courriers-list'),
    path('courriers/<int:pk>/modifier/',        views.modifier_courrier,    name='courriers-modifier'),
    path('courriers/<int:pk>/valider/',         views.valider_courrier,     name='courriers-valider'),
    path('courriers/<int:pk>/rejeter/',         views.rejeter_courrier,     name='courriers-rejeter'),
    path('courriers/<int:pk>/imputer/',         views.imputer_courrier,     name='courriers-imputer'),
    path('courriers/<int:pk>/marquer-lu/',      views.marquer_lu,           name='courriers-marquer-lu'),
    path('courriers/<int:pk>/marquer-traite/',  views.marquer_traite,       name='courriers-marquer-traite'),
    path('courriers/<int:pk>/archiver/',        views.archiver_courrier,    name='courriers-archiver'),
    path('destinataires/',                      views.liste_destinataires,  name='destinataires'),
    path('consignes-types/',                    views.liste_consignes_types, name='consignes-types'),
    path('notifications/',                      views.mes_notifications,    name='notifications'),
    path('notifications/count/',                views.compter_notifications, name='notifications-count'),
    path('courriers/<int:pk>/valider-sga/', views.valider_sga, name='courriers-valider-sga'),
    path('courriers/<int:pk>/rejeter-sga/', views.rejeter_sga, name='courriers-rejeter-sga'),
    path('courriers/<int:pk>/valider-sg/',  views.valider_sg,  name='courriers-valider-sg'),
    path('courriers/<int:pk>/traiter-copie/', views.traiter_copie, name='traiter-copie'),
]
