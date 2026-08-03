"""
Serializers de connexion, vérification 2FA — GED ESCEP-Niger SaaS.
"""
import random
import string
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Direction, Utilisateur


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Direction
        fields = '__all__'


class ConnexionSerializer(TokenObtainPairSerializer):
    username_field = 'identifiant'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.organisation:
            token['tenant_id']   = user.organisation.id
            token['tenant_code'] = user.organisation.code_tenant
        token['nom']          = user.nom
        token['prenom']       = user.prenom
        token['profil']       = user.profil
        token['modules']      = user.get_modules()
        token['direction']    = user.direction.nom if user.direction else ''
        token['is_superuser'] = user.is_superuser
        return token

    def validate(self, attrs):
        identifiant = attrs.get('identifiant', '')
        password    = attrs.get('password', '')

        try:
            user = Utilisateur.objects.select_related(
                'organisation', 'direction'
            ).get(identifiant=identifiant)
        except Utilisateur.DoesNotExist:
            raise serializers.ValidationError('Identifiant ou mot de passe incorrect.')

        if user.est_verrouille:
            raise serializers.ValidationError("Compte verrouillé. Contactez l'administrateur.")

        if not user.check_password(password):
            org = user.organisation
            tentatives_max = org.tentatives_max if org else 5
            user.tentatives_connexion += 1
            if user.tentatives_connexion >= tentatives_max:
                user.verrouille_jusqu = timezone.now() + timedelta(minutes=30)
            user.save()
            raise serializers.ValidationError('Identifiant ou mot de passe incorrect.')

        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé. Contactez l'administrateur.")

        if user.is_superuser:
            user.tentatives_connexion = 0
            user.save()
            data = super().validate(attrs)
            data['mdp_expire'] = False
            return data

        # Vérifier organisation active
        if user.organisation and not user.organisation.active:
            raise serializers.ValidationError("Organisation désactivée.")

        user.tentatives_connexion = 0
        user.save()

        org = user.organisation

        # Vérifier 2FA
        need_2fa = (
            org and org.double_auth_active
            and user.double_auth_active
            and not user.double_auth_desactive_admin
            and user.email
        )

        if need_2fa:
            code = ''.join(random.choices(string.digits, k=6))
            user.code_2fa            = code
            user.code_2fa_expiration = timezone.now() + timedelta(minutes=10)
            user.save()

            from django.conf import settings as django_settings
            from django.core.mail import send_mail

            texte = org.texte_email_2fa.replace('{code}', code)
            try:
                send_mail(
                    subject        = f"Code de vérification — {org.nom}",
                    message        = texte,
                    from_email     = org.email_expediteur or django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list = [user.email],
                    fail_silently  = True,
                )
            except Exception:
                import logging
                logging.exception('Erreur envoi email 2FA')

            self._2fa_payload = {
                'requires_2fa': True,
                'identifiant':  identifiant,
                'detail':       f"Code envoyé à {user.email[:3]}***",
                'code_2fa':     code,
            }
            raise serializers.ValidationError('Code de vérification requis.')

        data = super().validate(attrs)
        data['mdp_expire'] = user.mdp_expire
        return data


class Verification2FASerializer(serializers.Serializer):
    identifiant = serializers.CharField(required=True)
    code        = serializers.CharField(max_length=6, required=True)

    def validate(self, attrs):
        identifiant = attrs.get('identifiant')
        code        = attrs.get('code')

        try:
            user = Utilisateur.objects.get(identifiant=identifiant)
        except Utilisateur.DoesNotExist:
            raise serializers.ValidationError('Utilisateur introuvable.')

        if not user.code_2fa or user.code_2fa != code:
            raise serializers.ValidationError('Code incorrect.')

        if user.code_2fa_expiration and timezone.now() > user.code_2fa_expiration:
            raise serializers.ValidationError('Code expiré.')

        user.code_2fa            = ''
        user.code_2fa_expiration = None
        user.save()

        refresh = ConnexionSerializer.get_token(user)
        return {
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'mdp_expire': user.mdp_expire,
        }