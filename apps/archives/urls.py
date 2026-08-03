from django.urls import path
from apps.archives import views

urlpatterns = [
    path('archives/fonds/',        views.liste_fonds,    name='fonds-list'),
    path('archives/fonds/<int:pk>/', views.detail_fonds, name='fonds-detail'),
    path('archives/',              views.liste_archives,  name='archives-list'),
    path('archives/<int:pk>/',     views.detail_archive,  name='archives-detail'),
]
