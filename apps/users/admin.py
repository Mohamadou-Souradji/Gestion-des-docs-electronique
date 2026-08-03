# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Direction


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'sigle', 'organisation', 'active', 'ordre']
    list_filter   = ['active', 'organisation']
    search_fields = ['nom', 'sigle']


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display  = ['identifiant', 'nom', 'prenom', 'profil', 'organisation', 'is_active']
    list_filter   = ['profil', 'is_active', 'organisation']
    search_fields = ['identifiant', 'nom', 'prenom', 'email']
    ordering      = ['nom']

    fieldsets = (
        ('Identité', {'fields': ('identifiant', 'password', 'nom', 'prenom', 'email', 'fonction')}),
        ('Organisation', {'fields': ('organisation', 'direction', 'profil')}),
        ('Modules', {'fields': ('modules_actifs',)}),
        ('Sécurité', {'fields': (
            'double_auth_active', 'double_auth_desactive_admin',
            'tentatives_connexion', 'verrouille_jusqu',
            'date_derniere_mdp',
        )}),
        ('Droits', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('identifiant', 'organisation', 'profil', 'nom', 'prenom', 'password1', 'password2'),
        }),
    )