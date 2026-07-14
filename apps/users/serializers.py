"""
Serializer de connexion avec gestion 2FA et sécurité.
"""

import random
import string
from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class ConnexionSerializer(TokenObtainPairSerializer):

    username_field = 'identifiant'

    def validate(self, attrs):
        from .models import Utilisateur, ParametresApplication

        identifiant = attrs.get('identifiant', '')
        password    = attrs.get('password', '')

        try:
            user = Utilisateur.objects.get(identifiant=identifiant)
        except Utilisateur.DoesNotExist:
            raise serializers.ValidationError('Identifiant ou mot de passe incorrect.')

        # Vérifier le verrouillage
        if user.est_verrouille:
            raise serializers.ValidationError('Compte verrouillé. Contactez l\'administrateur.')

        # Vérifier le mot de passe
        if not user.check_password(password):
            params = ParametresApplication.get()
            user.tentatives_connexion += 1
            if user.tentatives_connexion >= params.tentatives_max:
                user.verrouille_jusqu = timezone.now() + timedelta(minutes=30)
            user.save()
            raise serializers.ValidationError('Identifiant ou mot de passe incorrect.')

        if not user.is_active:
            raise serializers.ValidationError('Compte désactivé. Contactez l\'administrateur.')

        # Réinitialiser les tentatives
        user.tentatives_connexion = 0
        user.save()

        params = ParametresApplication.get()

        # Vérifier si la 2FA est requise
        need_2fa = (
            params.double_auth_active
            and user.double_auth_active
            and not user.double_auth_desactive_admin
            and user.email
        )

        if need_2fa:
            # Générer et envoyer le code
            code = ''.join(random.choices(string.digits, k=6))
            user.code_2fa            = code
            user.code_2fa_expiration = timezone.now() + timedelta(minutes=10)
            user.save()

            from django.core.mail import send_mail
            from django.conf import settings as django_settings
            texte = params.texte_email_2fa.replace('{code}', code)
            try:
                send_mail(
                    subject       = f'Code de vérification — {params.nom_application}',
                    message       = texte,
                    from_email    = params.email_expediteur or django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list= [user.email],
                    fail_silently = True,
                )
            except Exception:
                import logging
                logging.exception('Erreur lors de l\'envoi de l\'email 2FA')

            self._2fa_payload = {
                'requires_2fa': True,
                'identifiant':  identifiant,
                'detail':       f'Code de vérification envoyé à {user.email[:3]}***',
                'code_2fa':     code,
                'mode':         'console' if django_settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend' else 'email',
            }
            raise serializers.ValidationError('Code de vérification requis.')

        # Connexion sans 2FA
        data = super().validate(attrs)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nom']     = user.nom
        token['prenom']  = user.prenom
        token['profil']  = user.profil
        token['modules'] = user.get_modules()
        token['direction'] = user.direction.nom if user.direction else ''
        return token
