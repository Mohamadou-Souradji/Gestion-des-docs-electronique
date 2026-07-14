from django.urls import path
from .views import ConnexionView
from . import views

urlpatterns = [
    # Authentification
    path('connexion/',          ConnexionView.as_view(),     name='connexion'),
    path('2fa/verifier/',       views.verifier_2fa,          name='verifier_2fa'),
    path('2fa/renvoyer/',       views.renvoyer_code_2fa,     name='renvoyer_2fa'),
    path('mot-de-passe/',       views.changer_mot_de_passe,  name='changer_mdp'),

    # Paramètres publics (avant connexion)
    path('parametres/publics/', views.get_parametres_publics, name='parametres_publics'),

    # Paramètres application (admin)
    path('parametres/',         views.parametres_application, name='parametres'),

    # Directions
    path('directions/',              views.liste_directions,   name='directions'),
    path('directions/<int:pk>/',     views.modifier_direction, name='modifier_direction'),

    # Utilisateurs
    path('utilisateurs/',                     views.liste_utilisateurs,  name='utilisateurs'),
    path('utilisateurs/creer/',               views.creer_utilisateur,   name='creer_utilisateur'),
    path('utilisateurs/<int:pk>/modifier/',   views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:pk>/basculer/',   views.basculer_compte,     name='basculer_compte'),
    path('utilisateurs/<int:pk>/deverrouiller/', views.deverrouiller_compte, name='deverrouiller'),

    # Supervision
    path('moi/', views.mon_profil, name='mon_profil'),
    path('supervision/',        views.supervision,           name='supervision'),
]
