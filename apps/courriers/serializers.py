from rest_framework import serializers
from .models import Courrier, CourrierCopie, Notification, CONSIGNES_TYPES


class CourrierCopieSerializer(serializers.ModelSerializer):
    destinataire_nom = serializers.SerializerMethodField()

    class Meta:
        model  = CourrierCopie
        fields = ['id', 'destinataire', 'destinataire_nom', 'date_lecture']

    def get_destinataire_nom(self, obj):
        if not obj.destinataire:
            return ''
        direction = obj.destinataire.direction.nom if obj.destinataire.direction else ''
        return f"{obj.destinataire.prenom} {obj.destinataire.nom} ({direction})"


class CourrierSerializer(serializers.ModelSerializer):

    saisi_par_nom    = serializers.SerializerMethodField()
    fichier_pdf_url  = serializers.SerializerMethodField()
    statut_label     = serializers.SerializerMethodField()
    destinataire_nom = serializers.SerializerMethodField()
    copies           = CourrierCopieSerializer(many=True, read_only=True)

    class Meta:
        model  = Courrier
        fields = [
            'id', 'identifiant_temp', 'numero_officiel', 'type_courrier',
            'mode_reception', 'priorite', 'statut', 'statut_label',
            'objet', 'expediteur', 'reference_exp', 'date_document',
            'date_reception', 'observations', 'fichier_pdf', 'fichier_pdf_url',
            'saisi_par', 'saisi_par_nom', 'date_saisie',
            'verifie_par', 'date_verification', 'motif_rejet', 'observation_dg',
            'impute_par', 'date_imputation', 'instructions_dg',
            'destinataire', 'destinataire_nom', 'copies',
            'date_traitement', 'reponse_traitement',
        ]
        read_only_fields = [
            'id', 'identifiant_temp', 'numero_officiel', 'statut', 'statut_label',
            'date_saisie', 'saisi_par', 'fichier_pdf_url', 'copies',
        ]

    def get_saisi_par_nom(self, obj):
        if not obj.saisi_par:
            return ''
        return f"{obj.saisi_par.prenom} {obj.saisi_par.nom}"

    def get_destinataire_nom(self, obj):
        if not obj.destinataire:
            return ''
        direction = obj.destinataire.direction.nom if obj.destinataire.direction else ''
        return f"{obj.destinataire.prenom} {obj.destinataire.nom} ({direction})"

    def get_fichier_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.fichier_pdf and request:
            return request.build_absolute_uri(obj.fichier_pdf.url)
        return ''

    def get_statut_label(self, obj):
        return obj.statut_label


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'message', 'lue', 'date', 'courrier']
