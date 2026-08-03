from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users import views

urlpatterns = [
    path('connexion/',                      views.ConnexionView.as_view(),  name='connexion'),
    path('token/refresh/',                  TokenRefreshView.as_view(),     name='token-refresh'),
    path('2fa/verifier/',                   views.verifier_2fa,             name='2fa-verifier'),
    path('2fa/renvoyer/',                   views.renvoyer_code_2fa,        name='2fa-renvoyer'),
    path('moi/',                            views.mon_profil,               name='mon-profil'),
    path('changer-mdp/',                    views.changer_mot_de_passe,     name='changer-mdp'),
    path('parametres/publics/',             views.get_parametres_publics,   name='parametres-publics'),
    path('parametres/',                     views.parametres_application,   name='parametres'),
    path('directions/',                     views.liste_directions,         name='directions-list'),
    path('directions/<int:pk>/',            views.modifier_direction,       name='directions-detail'),
    path('utilisateurs/',                   views.liste_utilisateurs,       name='utilisateurs-list'),
    path('utilisateurs/creer/',             views.creer_utilisateur,        name='utilisateurs-creer'),
    path('utilisateurs/<int:pk>/modifier/', views.modifier_utilisateur,     name='utilisateurs-modifier'),
    path('utilisateurs/<int:pk>/basculer/', views.basculer_compte,          name='utilisateurs-basculer'),
    path('utilisateurs/<int:pk>/deverrouiller/', views.deverrouiller_compte, name='utilisateurs-deverrouiller'),
    path('supervision/',                    views.supervision,              name='supervision'),
    path('verifier-identifiant/',           views.verifier_identifiant,     name='verifier-identifiant'),

]
