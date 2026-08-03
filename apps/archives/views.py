# apps/archives/views.py — CORRIGÉ
# Fix: liste_fonds retourne maintenant le format attendu par VersementArchive
# { fonds: [{code, label, id}], types: [{code, label}] }

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FondsArchive, ArchiveHistorique
from .serializers import FondsArchiveSerializer, ArchiveHistoriqueSerializer


TYPES_DOCUMENTS = [
    ('LETTRE',        'Lettre'),
    ('RAPPORT',       'Rapport'),
    ('DECISION',      'Décision'),
    ('CIRCULAIRE',    'Circulaire'),
    ('PROCES_VERBAL', 'Procès-verbal'),
    ('CONTRAT',       'Contrat'),
    ('CONVENTION',    'Convention'),
    ('ARRETE',        'Arrêté'),
    ('DECRET',        'Décret'),
    ('NOTE',          'Note de service'),
    ('FACTURE',       'Facture'),
    ('BON_COMMANDE',  'Bon de commande'),
    ('AUTRE',         'Autre'),
]


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_fonds(request):
    """
    GET : Retourne les fonds de l'organisation au format compatible VersementArchive.
    POST : Crée un nouveau fonds.
    """
    org = request.tenant
    qs  = FondsArchive.objects.filter(organisation=org) if org else FondsArchive.objects.none()

    if request.method == 'GET':
        # Format compatible avec VersementArchive et FondsArchives
        # Retourne les deux formats: liste complète + format {code, label}
        fonds_liste = [{
            'id':          f.id,
            'code':        f.code,
            'label':       f.intitule,          # ← VersementArchive attend 'label'
            'intitule':    f.intitule,
            'description': f.description,
            'nb_documents': f.documents.count(),
        } for f in qs]

        return Response({
            'fonds':  fonds_liste,                                              # ← Pour VersementArchive/FondsArchives
            'types':  [{'code': t[0], 'label': t[1]} for t in TYPES_DOCUMENTS], # ← Pour VersementArchive
            'liste':  FondsArchiveSerializer(qs, many=True).data,               # ← Pour GestionFonds admin
        })

    # POST — Créer un nouveau fonds
    if request.user.profil not in ['ADMIN', 'ARC']:
        return Response({'detail': "Réservé à l'Archiviste ou l'Administrateur."}, status=403)

    code = request.data.get('code', '').strip().upper()
    if not code:
        return Response({'detail': 'Le code est obligatoire.'}, status=400)
    if not request.data.get('intitule', '').strip():
        return Response({'detail': "L'intitulé est obligatoire."}, status=400)

    if FondsArchive.objects.filter(organisation=org, code=code).exists():
        return Response({'detail': f'Un fonds avec le code "{code}" existe déjà.'}, status=400)

    fonds = FondsArchive.objects.create(
        organisation = org,
        code         = code,
        intitule     = request.data.get('intitule', '').strip(),
        description  = request.data.get('description', '').strip(),
    )
    return Response(FondsArchiveSerializer(fonds).data, status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def detail_fonds(request, pk):
    org = request.tenant
    try:
        fonds = FondsArchive.objects.get(pk=pk, organisation=org)
    except FondsArchive.DoesNotExist:
        return Response({'detail': 'Fonds introuvable.'}, status=404)

    if request.method == 'GET':
        return Response(FondsArchiveSerializer(fonds).data)

    if request.user.profil not in ['ADMIN', 'ARC']:
        return Response({'detail': "Réservé à l'Archiviste ou l'Administrateur."}, status=403)

    if request.method == 'PATCH':
        for c in ['intitule', 'description']:
            if c in request.data:
                setattr(fonds, c, request.data[c])
        fonds.save()
        return Response(FondsArchiveSerializer(fonds).data)

    if request.method == 'DELETE':
        if fonds.documents.exists():
            return Response({'detail': 'Impossible de supprimer un fonds contenant des archives.'}, status=400)
        fonds.delete()
        return Response({'detail': 'Fonds supprimé.'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_archives(request):
    org = request.tenant
    qs  = ArchiveHistorique.objects.filter(organisation=org) if org else ArchiveHistorique.objects.none()

    if request.method == 'GET':
        fonds_id = request.query_params.get('fonds')
        if fonds_id:
            if fonds_id.isdigit():
                qs = qs.filter(fonds_id=fonds_id)
            else:
                qs = qs.filter(fonds__code=fonds_id)

        q = request.query_params.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(intitule__icontains=q) |
                Q(reference_systeme__icontains=q) |
                Q(mots_cles__icontains=q) |
                Q(description__icontains=q)
            )

        type_doc   = request.query_params.get('type', '')
        date_debut = request.query_params.get('date_debut', '')
        date_fin   = request.query_params.get('date_fin', '')

        if type_doc:   qs = qs.filter(type_document=type_doc)
        if date_debut: qs = qs.filter(date_document__gte=date_debut)
        if date_fin:   qs = qs.filter(date_document__lte=date_fin)

        return Response(ArchiveHistoriqueSerializer(qs, many=True, context={'request': request}).data)

    if request.user.profil not in ['ADMIN', 'ARC']:
        return Response({'detail': "Réservé à l'Archiviste."}, status=403)

    # Résoudre le fonds par code ou ID
    fonds_code = request.data.get('fonds', '')
    fonds_obj  = None
    if fonds_code:
        try:
            if str(fonds_code).isdigit():
                fonds_obj = FondsArchive.objects.get(pk=fonds_code, organisation=org)
            else:
                fonds_obj = FondsArchive.objects.get(code=fonds_code, organisation=org)
        except FondsArchive.DoesNotExist:
            return Response({'detail': f'Fonds "{fonds_code}" introuvable pour cette organisation.'}, status=404)

    serializer = ArchiveHistoriqueSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    archive = serializer.save(organisation=org, verse_par=request.user, fonds=fonds_obj)
    return Response(ArchiveHistoriqueSerializer(archive, context={'request': request}).data, status=201)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def detail_archive(request, pk):
    org = request.tenant
    try:
        archive = ArchiveHistorique.objects.get(pk=pk, organisation=org)
    except ArchiveHistorique.DoesNotExist:
        return Response({'detail': 'Archive introuvable.'}, status=404)

    if request.method == 'GET':
        return Response(ArchiveHistoriqueSerializer(archive, context={'request': request}).data)

    if request.user.profil not in ['ADMIN', 'ARC']:
        return Response({'detail': "Réservé à l'Archiviste."}, status=403)

    if request.method == 'PATCH':
        serializer = ArchiveHistoriqueSerializer(archive, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        archive.delete()
        return Response({'detail': 'Archive supprimée.'})
