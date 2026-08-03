from rest_framework import serializers
from .models import FondsArchive, ArchiveHistorique


class FondsArchiveSerializer(serializers.ModelSerializer):
    nb_documents = serializers.SerializerMethodField()

    class Meta:
        model  = FondsArchive
        fields = ['id', 'code', 'intitule', 'description', 'date_creation', 'nb_documents']
        read_only_fields = ['id', 'date_creation', 'nb_documents']

    def get_nb_documents(self, obj):
        return obj.documents.count()


class ArchiveHistoriqueSerializer(serializers.ModelSerializer):
    verse_par_nom  = serializers.SerializerMethodField()
    fichier_pdf_url = serializers.SerializerMethodField()
    fonds_nom      = serializers.SerializerMethodField()

    class Meta:
        model  = ArchiveHistorique
        fields = [
            'id', 'reference_systeme', 'intitule', 'description',
            'date_document', 'date_versement',
            'fonds', 'fonds_nom',
            'verse_par', 'verse_par_nom',
            'fichier_pdf', 'fichier_pdf_url',
            'mots_cles',
        ]
        read_only_fields = ['id', 'reference_systeme', 'date_versement', 'verse_par']

    def get_verse_par_nom(self, obj):
        if not obj.verse_par:
            return ''
        return f"{obj.verse_par.prenom} {obj.verse_par.nom}"

    def get_fichier_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.fichier_pdf and request:
            return request.build_absolute_uri(obj.fichier_pdf.url)
        return ''

    def get_fonds_nom(self, obj):
        if not obj.fonds:
            return ''
        return f"{obj.fonds.code} - {obj.fonds.intitule}"
