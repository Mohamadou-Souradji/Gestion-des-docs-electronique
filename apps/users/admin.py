from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Direction, ParametresApplication


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    list_display  = ('identifiant', 'nom', 'prenom', 'profil', 'direction', 'is_active')
    list_filter   = ('profil', 'is_active')
    search_fields = ('identifiant', 'nom', 'prenom')
    ordering      = ('nom',)

    fieldsets = (
        ('Connexion',    {'fields': ('identifiant', 'password')}),
        ('Informations', {'fields': ('nom', 'prenom', 'email', 'fonction', 'direction')}),
        ('Profil',       {'fields': ('profil', 'modules_actifs')}),
        ('Sécurité',     {'fields': ('double_auth_active', 'double_auth_desactive_admin', 'tentatives_connexion', 'verrouille_jusqu')}),
        ('Accès',        {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('identifiant', 'nom', 'prenom', 'profil', 'direction', 'password1', 'password2'),
        }),
    )


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display  = ('sigle', 'nom', 'active', 'ordre')
    list_filter   = ('active',)
    search_fields = ('nom', 'sigle')
    ordering      = ('ordre', 'nom')


@admin.register(ParametresApplication)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ('nom_application', 'double_auth_active', 'timeout_inactivite')
