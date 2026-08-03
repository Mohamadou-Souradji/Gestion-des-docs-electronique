from rest_framework import serializers
from .models import Courrier, CourrierCopie, Notification


class CourrierCopieSerializer(serializers.ModelSerializer):
    destinataire_nom    = serializers.SerializerMethodField()
    destinataire_entite = serializers.SerializerMethodField()
    fichier_reponse_url = serializers.SerializerMethodField()   # ← ajouter

    class Meta:
        model  = CourrierCopie
        fields = ['id', 'destinataire', 'destinataire_nom', 'destinataire_entite',
                  'date_lecture', 'consignes_types', 'consigne_libre',
                  'reponse', 'date_traitement', 'fichier_reponse_url']

    def get_destinataire_nom(self, obj):
        if not obj.destinataire:
            return ''
        return f"{obj.destinataire.prenom} {obj.destinataire.nom}"

    def get_destinataire_entite(self, obj):
        if not obj.destinataire:
            return ''
        return obj.destinataire.direction.nom if obj.destinataire.direction else ''

    def get_fichier_reponse_url(self, obj):          # ← ajouter
        request = self.context.get('request')
        if obj.fichier_reponse and request:
            return request.build_absolute_uri(obj.fichier_reponse.url)
        return ''
        
class CourrierSerializer(serializers.ModelSerializer):
    saisi_par_nom        = serializers.SerializerMethodField()
    fichier_pdf_url      = serializers.SerializerMethodField()
    fichier_reponse_url  = serializers.SerializerMethodField()
    statut_label         = serializers.SerializerMethodField()
    destinataire_nom     = serializers.SerializerMethodField()
    destinataire_entite  = serializers.SerializerMethodField()
    copies               = CourrierCopieSerializer(many=True, read_only=True)
    mon_role             = serializers.SerializerMethodField()
    mes_consignes_copie = serializers.SerializerMethodField()

    class Meta:
        model  = Courrier
        fields = [
            'id', 'identifiant_temp', 'numero_officiel', 'type_courrier',
            'mode_reception', 'priorite', 'statut', 'statut_label',
            'objet', 'expediteur', 'reference_exp', 'date_document',
            'date_reception', 'heure_depot', 'observations',
            'fichier_pdf', 'fichier_pdf_url',
            'saisi_par', 'saisi_par_nom', 'date_saisie',
            'verifie_par', 'date_verification', 'motif_rejet', 'observation_dg',
            'impute_par', 'date_imputation', 'instructions_dg',
            'destinataire', 'destinataire_nom', 'destinataire_entite', 'copies',
            'mon_role',
            'date_traitement', 'reponse_traitement',
            'fichier_reponse', 'fichier_reponse_url',
            'proposition_sga', 'valide_sga_par', 'date_validation_sga', 'motif_rejet_sga',
            'proposition_sg', 'valide_sg_par', 'date_validation_sg','mes_consignes_copie',
        ]
        read_only_fields = [
            'id', 'identifiant_temp', 'numero_officiel', 'statut', 'statut_label',
            'date_saisie', 'saisi_par', 'fichier_pdf_url', 'fichier_reponse_url',
            'copies', 'mon_role',
            'proposition_sga', 'valide_sga_par', 'date_validation_sga',
            'proposition_sg', 'valide_sg_par', 'date_validation_sg',
        ]

    def get_saisi_par_nom(self, obj):
        if not obj.saisi_par:
            return ''
        return f"{obj.saisi_par.prenom} {obj.saisi_par.nom}"

    def get_destinataire_nom(self, obj):
        if not obj.destinataire:
            return ''
        return f"{obj.destinataire.prenom} {obj.destinataire.nom}"

    def get_destinataire_entite(self, obj):
        if not obj.destinataire:
            return ''
        return obj.destinataire.direction.nom if obj.destinataire.direction else ''

    def get_fichier_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.fichier_pdf and request:
            return request.build_absolute_uri(obj.fichier_pdf.url)
        return ''

    def get_fichier_reponse_url(self, obj):
        request = self.context.get('request')
        if obj.fichier_reponse and request:
            return request.build_absolute_uri(obj.fichier_reponse.url)
        return ''

    def get_statut_label(self, obj):
        return obj.statut_label

    def get_mon_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        if obj.copies.filter(destinataire=request.user).exists():
            return 'COPIE'
        if obj.destinataire and obj.destinataire.id == request.user.id:
            return 'PRINCIPAL'
        return None

    def get_mes_consignes_copie(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        copie = obj.copies.filter(destinataire=request.user).first()
        if not copie:
            return None
        return {
            'consignes_types': copie.consignes_types or [],
            'consigne_libre':  copie.consigne_libre  or '',
        }    

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'message', 'lue', 'date', 'courrier']