"""
Permissions personnalisees pour les courriers.
Chaque profil a des droits precis definis par le CCFT.
"""

from rest_framework.permissions import BasePermission


class EstBureauOrdre(BasePermission):
    """Seul le Bureau d'Ordre peut creer des courriers."""
    def has_permission(self, request, view):
        return request.user.profil == 'BO'


class EstAssistantDG(BasePermission):
    """Seul l'Assistant DG peut valider ou rejeter les courriers."""
    def has_permission(self, request, view):
        return request.user.profil == 'ASSIST'


class EstDG(BasePermission):
    """Seul le DG peut imputer les courriers."""
    def has_permission(self, request, view):
        return request.user.profil == 'DG'


class EstDestinataire(BasePermission):
    """Un destinataire peut voir et traiter ses courriers."""
    def has_permission(self, request, view):
        return request.user.profil == 'DEST'
