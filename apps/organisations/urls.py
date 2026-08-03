from django.urls import path
from apps.organisations import views

urlpatterns = [
    # Super-Admin — Organisations
    path('super/organisations/',                          views.lister_organisations,          name='orgs-list'),
    path('super/organisations/<int:pk>/',                 views.detail_organisation,           name='orgs-detail'),
    path('super/organisations/<int:pk>/admins/',          views.admins_organisation,           name='orgs-admins'),
    path('super/organisations/<int:pk>/admins/ajouter/',  views.ajouter_admin_organisation,    name='orgs-admins-ajouter'),
    path('super/organisations/<int:pk>/admins/<int:admin_pk>/', views.modifier_admin_organisation, name='orgs-admins-modifier'),
    path('super/organisations/<int:pk>/securite/',        views.securite_organisation,         name='orgs-securite'),

    # Paramètres publics (avant connexion — par ?tenant=code ou domaine)
    path('parametres/publics/',                           views.parametres_publics_organisation, name='org-parametres-publics'),

    # Paramètres privés (après connexion)
    path('organisation/parametres/',                      views.mes_parametres_organisation,   name='org-parametres'),
]
