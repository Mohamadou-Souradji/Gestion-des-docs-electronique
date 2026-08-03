from rest_framework import serializers
from apps.organisations.models import Organisation


class OrganisationSerializer(serializers.ModelSerializer):
    utilisateurs_count = serializers.SerializerMethodField()
    logo_url           = serializers.SerializerMethodField()
    image_fond_url     = serializers.SerializerMethodField()
    admin_nom          = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = [
            'id', 'code_tenant', 'nom', 'slogan', 'texte_pied_page',
            'logo', 'logo_url', 'image_fond_login', 'image_fond_url', 'favicon',
            'couleur_principale', 'couleur_accent', 'couleur_danger', 'flou_image_fond',
            'domaine_personnalise', 'active', 'date_creation',
            'admin_principal', 'admin_nom',
            'max_utilisateurs', 'max_stockage_go',
            'plan', 'date_fin_abonnement',
            'timeout_inactivite', 'duree_validite_mdp', 'tentatives_max',
            'double_auth_active', 'email_expediteur',
            'utilisateurs_count',
             'workflow_type','prefixe_courrier',
        ]
        read_only_fields = ['id', 'date_creation', 'utilisateurs_count', 'logo_url', 'image_fond_url', 'admin_nom']

    def get_utilisateurs_count(self, obj):
        return obj.utilisateurs.filter(is_active=True).count()

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None

    def get_image_fond_url(self, obj):
        request = self.context.get('request')
        if obj.image_fond_login and request:
            return request.build_absolute_uri(obj.image_fond_login.url)
        return None

    def get_admin_nom(self, obj):
        if obj.admin_principal:
            return f"{obj.admin_principal.prenom} {obj.admin_principal.nom}"
        return ''
