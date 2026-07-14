"""
Vues du module 6 - Versement retroactif d archives historiques.
Acteur : Archiviste uniquement.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ArchiveHistorique
from apps.dashboard.models import journaliser, TypeAction
from .serializers import ArchiveSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_archives(request):
    """
    GET  : liste toutes les archives historiques.
    POST : verse un document (unitaire).
    Accessible a tous les profils en lecture, versement reserve a l Archiviste.
    """
    if request.method == 'GET':
        # Recherche eventuelle
        q       = request.GET.get('q', '').strip()
        fonds   = request.GET.get('fonds', '')
        type_doc = request.GET.get('type', '')
        date_debut = request.GET.get('date_debut', '')
        date_fin   = request.GET.get('date_fin', '')

        qs = ArchiveHistorique.objects.all()

        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(intitule__icontains=q) |
                Q(expediteur__icontains=q) |
                Q(reference_systeme__icontains=q) |
                Q(reference_origine__icontains=q) |
                Q(mots_cles__icontains=q) |
                Q(resume__icontains=q) |
                Q(contenu_ocr__icontains=q)
            )
        if fonds:
            qs = qs.filter(fonds=fonds)
        if type_doc:
            qs = qs.filter(type_document=type_doc)
        if date_debut:
            qs = qs.filter(date_document__gte=date_debut)
        if date_fin:
            qs = qs.filter(date_document__lte=date_fin)

        return Response(ArchiveSerializer(qs, many=True, context={'request': request}).data)

    if request.method == 'POST':
        if request.user.profil != 'ARC':
            return Response({'detail': 'Reserve a l Archiviste.'}, status=403)

        serializer = ArchiveSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        archive = serializer.save(verse_par=request.user)
        journaliser(request, TypeAction.VERSEMENT, f"Archive versée : {archive.intitule}", "archive", archive.reference_systeme, archive.intitule)
        return Response(ArchiveSerializer(archive, context={'request': request}).data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def versement_par_lot(request):
    """
    Versement par lot : plusieurs documents d un meme fonds en une operation.
    Chaque fichier est traite independamment avec un identifiant de lot commun.
    """
    if request.user.profil != 'ARC':
        return Response({'detail': 'Reserve a l Archiviste.'}, status=403)

    fonds      = request.data.get('fonds')
    lot_id     = request.data.get('lot_id', '')
    fichiers   = request.FILES.getlist('fichiers')
    metadonnees = request.data.getlist('metadonnees')  # JSON par fichier

    if not fonds or not fichiers:
        return Response({'detail': 'Fonds et fichiers obligatoires.'}, status=400)

    import json
    archives_crees = []

    for i, fichier in enumerate(fichiers):
        try:
            meta = json.loads(metadonnees[i]) if i < len(metadonnees) else {}
        except Exception:
            meta = {}

        archive = ArchiveHistorique(
            fonds             = fonds,
            intitule          = meta.get('intitule', fichier.name),
            reference_origine = meta.get('reference_origine', ''),
            type_document     = meta.get('type_document', 'AUTRE'),
            date_document     = meta.get('date_document', '2000-01-01'),
            expediteur        = meta.get('expediteur', ''),
            categorie         = meta.get('categorie', ''),
            mots_cles         = meta.get('mots_cles', ''),
            resume            = meta.get('resume', ''),
            fichier           = fichier,
            lot               = lot_id,
            verse_par         = request.user,
        )
        archive.save()
        archives_crees.append(archive.reference_systeme)

    return Response({'archives_crees': archives_crees, 'total': len(archives_crees)}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fonds_disponibles(request):
    """Retourne les fonds d archives disponibles et les types de documents."""
    from .models import FondsArchive, TypeDocument
    return Response({
        'fonds':  [{'code': c[0], 'label': c[1]} for c in FondsArchive.choices],
        'types':  [{'code': c[0], 'label': c[1]} for c in TypeDocument.choices],
    })
