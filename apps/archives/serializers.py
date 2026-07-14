from rest_framework import serializers
from .models import ArchiveHistorique


class ArchiveSerializer(serializers.ModelSerializer):
    verse_par_nom = serializers.SerializerMethodField()
    fichier_url   = serializers.SerializerMethodField()

    class Meta:
        model  = ArchiveHistorique
        fields = [
            'id', 'reference_systeme', 'reference_origine', 'fonds',
            'type_document', 'intitule', 'expediteur', 'date_document',
            'categorie', 'mots_cles', 'resume', 'fichier', 'fichier_url',
            'contenu_ocr', 'lot', 'verse_par', 'verse_par_nom', 'date_versement',
        ]
        read_only_fields = ['id', 'reference_systeme', 'verse_par', 'verse_par_nom', 'date_versement', 'fichier_url']

    def get_verse_par_nom(self, obj):
        return f"{obj.verse_par.prenom} {obj.verse_par.nom}" if obj.verse_par else ''

    def get_fichier_url(self, obj):
        request = self.context.get('request')
        if obj.fichier and request:
            return request.build_absolute_uri(obj.fichier.url)
        return ''
