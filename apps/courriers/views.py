"""
Vues de l API courriers - GED ESCEP-Niger.
Modules 1, 2, 3, 4 et 5.
"""

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.models import journaliser, TypeAction, Issue
from .models import Courrier, CourrierCopie, Notification, StatutCourrier, CONSIGNES_TYPES
from .serializers import CourrierSerializer, NotificationSerializer


def notifier(utilisateur, message, courrier=None):
    """Cree une notification pour un utilisateur."""
    Notification.objects.create(destinataire=utilisateur, message=message, courrier=courrier)


# ---------------------------------------------------------------
# MODULE 1 - Bureau d Ordre
# ---------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_courriers(request):
    if request.method == 'GET':
        profil = request.user.profil
        if profil == 'BO':
            qs = Courrier.objects.filter(saisi_par=request.user)
        elif profil == 'ASSIST':
            qs = Courrier.objects.exclude(statut=StatutCourrier.BROUILLON)
        elif profil == 'DG':
            qs = Courrier.objects.all()
        elif profil == 'DEST':
            # Cloisonnement : destinataire principal ou en copie uniquement
            from django.db.models import Q
            ids_copie = CourrierCopie.objects.filter(destinataire=request.user).values_list('courrier_id', flat=True)
            qs = Courrier.objects.filter(
                Q(destinataire=request.user) | Q(id__in=ids_copie)
            ).exclude(statut__in=[StatutCourrier.BROUILLON, StatutCourrier.EN_VERIF, StatutCourrier.EN_ATT_IMP])
        elif profil == 'ARC':
            qs = Courrier.objects.filter(statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE])
        else:
            qs = Courrier.objects.none()
        return Response(CourrierSerializer(qs, many=True, context={'request': request}).data)

    if request.method == 'POST':
        if request.user.profil != 'BO':
            return Response({'detail': 'Reserve au Bureau d Ordre.'}, status=403)
        action = request.data.get('action', 'BROUILLON')
        serializer = CourrierSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        statut_initial = StatutCourrier.EN_VERIF if action == 'SOUMETTRE' else StatutCourrier.BROUILLON
        courrier = serializer.save(saisi_par=request.user, statut=statut_initial)
        if action == 'SOUMETTRE':
            from apps.users.models import Utilisateur
            for a in Utilisateur.objects.filter(profil='ASSIST', is_active=True):
                notifier(a, f"Nouveau courrier a verifier : {courrier.objet} (de {courrier.expediteur})", courrier)
        journaliser(request, TypeAction.SOUMISSION, f"Courrier soumis a verification : {courrier.objet}", 'courrier', courrier.identifiant_temp, courrier.objet)
        return Response(CourrierSerializer(courrier, context={'request': request}).data, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_courrier(request, pk):
    if request.user.profil != 'BO':
        return Response({'detail': 'Reserve au Bureau d Ordre.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, saisi_par=request.user, statut__in=[StatutCourrier.BROUILLON, StatutCourrier.REJETE])
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou non modifiable.'}, status=404)
    for champ in ['objet', 'expediteur', 'reference_exp', 'type_courrier', 'mode_reception', 'priorite', 'date_document', 'date_reception', 'observations']:
        if champ in request.data:
            setattr(courrier, champ, request.data[champ])
    if 'fichier_pdf' in request.FILES:
        courrier.fichier_pdf = request.FILES['fichier_pdf']
    # Resoumettre apres correction
    action = request.data.get('action', '')
    if action == 'SOUMETTRE':
        courrier.statut = StatutCourrier.EN_VERIF
        courrier.motif_rejet = ''
        from apps.users.models import Utilisateur
        for a in Utilisateur.objects.filter(profil='ASSIST', is_active=True):
            notifier(a, f"Courrier corrige et resoumis : {courrier.objet}", courrier)
    courrier.save()
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE 2 - Assistant DG
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def valider_courrier(request, pk):
    if request.user.profil != 'ASSIST':
        return Response({'detail': 'Reserve a l Assistant DG.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_VERIF)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)
    courrier.numero_officiel   = courrier.generer_numero_officiel()
    courrier.statut            = StatutCourrier.EN_ATT_IMP
    courrier.verifie_par       = request.user
    courrier.date_verification = timezone.now()
    courrier.observation_dg    = request.data.get('observation_dg', '')
    courrier.save()
    notifier(courrier.saisi_par, f"Courrier valide : '{courrier.objet}'. Numero : {courrier.numero_officiel}", courrier)
    journaliser(request, TypeAction.VALIDATION, f"Courrier valide : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)
    from apps.users.models import Utilisateur
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True):
        notifier(dg, f"Courrier en attente d imputation : {courrier.objet} ({courrier.numero_officiel})", courrier)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejeter_courrier(request, pk):
    if request.user.profil != 'ASSIST':
        return Response({'detail': 'Reserve a l Assistant DG.'}, status=403)
    motif = request.data.get('motif_rejet', '').strip()
    if not motif:
        return Response({'detail': 'Le motif du rejet est obligatoire.'}, status=400)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_VERIF)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)
    courrier.statut            = StatutCourrier.REJETE
    courrier.verifie_par       = request.user
    courrier.date_verification = timezone.now()
    courrier.motif_rejet       = motif
    courrier.save()
    notifier(courrier.saisi_par, f"Courrier rejete : '{courrier.objet}'. Motif : {motif}", courrier)
    journaliser(request, TypeAction.REJET, f"Courrier rejete : {courrier.objet}. Motif : {motif}", 'courrier', courrier.identifiant_temp, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE 3 - DG : Imputation
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_destinataires(request):
    """Retourne la liste des utilisateurs pouvant recevoir des courriers (profil DEST)."""
    if request.user.profil != 'DG':
        return Response({'detail': 'Reserve au DG.'}, status=403)
    from apps.users.models import Utilisateur
    dests = Utilisateur.objects.filter(profil='DEST', is_active=True).select_related('direction')
    data = [{'id': u.id, 'nom': u.nom, 'prenom': u.prenom, 'entite': u.direction.nom if u.direction else '', 'fonction': u.fonction} for u in dests]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_consignes_types(request):
    """Retourne les consignes types predefinies (CCFT Annexe C)."""
    return Response([{'code': c[0], 'label': c[1]} for c in CONSIGNES_TYPES])


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def imputer_courrier(request, pk):
    """
    Module 3 - Imputation par le DG.
    - Destinataire principal unique obligatoire
    - Destinataires en copie facultatifs
    - Au moins une consigne type obligatoire
    - Consigne libre facultative
    """
    if request.user.profil != 'DG':
        return Response({'detail': 'Reserve au Directeur General.'}, status=403)

    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_ATT_IMP)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou deja impute.'}, status=404)

    destinataire_id = request.data.get('destinataire_id')
    copies_ids      = request.data.get('copies_ids', [])
    consignes_types = request.data.get('consignes_types', [])
    consigne_libre  = request.data.get('consigne_libre', '').strip()

    if not destinataire_id:
        return Response({'detail': 'Un destinataire principal est obligatoire.'}, status=400)
    if not consignes_types:
        return Response({'detail': 'Au moins une consigne type doit etre cochee.'}, status=400)

    from apps.users.models import Utilisateur
    try:
        destinataire = Utilisateur.objects.get(pk=destinataire_id, profil='DEST', is_active=True)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Destinataire introuvable.'}, status=404)

    # Construire les instructions : consignes types + consigne libre
    instructions = ', '.join(consignes_types)
    if consigne_libre:
        instructions += f'\n\nConsigne specifique : {consigne_libre}'

    courrier.destinataire   = destinataire
    courrier.impute_par     = request.user
    courrier.date_imputation = timezone.now()
    courrier.instructions_dg = instructions
    courrier.statut          = StatutCourrier.IMPUTE
    courrier.save()

    # Ajouter les destinataires en copie
    for cid in copies_ids:
        try:
            dest_copie = Utilisateur.objects.get(pk=cid, profil='DEST', is_active=True)
            CourrierCopie.objects.get_or_create(courrier=courrier, destinataire=dest_copie)
        except Utilisateur.DoesNotExist:
            pass

    # Notifier le destinataire principal
    notifier(destinataire, f"Nouveau courrier impute : '{courrier.objet}' ({courrier.numero_officiel}). Instructions : {instructions[:100]}", courrier)

    # Notifier les destinataires en copie
    for copie in courrier.copies.all():
        notifier(copie.destinataire, f"Vous etes en copie du courrier : '{courrier.objet}' ({courrier.numero_officiel})", courrier)

    journaliser(request, TypeAction.IMPUTATION, f"Courrier impute a {destinataire.prenom} {destinataire.nom}", 'courrier', courrier.numero_officiel, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE 4 - Destinataire : Consultation et traitement
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_lu(request, pk):
    """Enregistre la premiere consultation du courrier."""
    if request.user.profil != 'DEST':
        return Response({'detail': 'Reserve aux destinataires.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, destinataire=request.user, statut=StatutCourrier.IMPUTE)
        courrier.statut = StatutCourrier.EN_COURS
        courrier.save()
        journaliser(request, TypeAction.CONSULTATION, f"Courrier consulté : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)
    except Courrier.DoesNotExist:
        pass
    # Enregistrer la lecture en copie si applicable
    CourrierCopie.objects.filter(courrier_id=pk, destinataire=request.user, date_lecture__isnull=True).update(date_lecture=timezone.now())
    return Response({'detail': 'Courrier marque comme lu.'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_traite(request, pk):
    """
    Le destinataire principal marque le courrier comme traite.
    Seul le destinataire principal peut marquer comme traite (pas les copies).
    """
    if request.user.profil != 'DEST':
        return Response({'detail': 'Reserve aux destinataires.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, destinataire=request.user, statut__in=[StatutCourrier.IMPUTE, StatutCourrier.EN_COURS])
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou deja traite.'}, status=404)
    courrier.statut          = StatutCourrier.TRAITE
    courrier.date_traitement = timezone.now()
    courrier.reponse_traitement = request.data.get('reponse', '').strip()
    courrier.save()
    journaliser(request, TypeAction.TRAITEMENT, f"Courrier traité : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)
    # Notifier le DG
    from apps.users.models import Utilisateur
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True):
        notifier(dg, f"Courrier traite par {request.user.prenom} {request.user.nom} : '{courrier.objet}' ({courrier.numero_officiel})", courrier)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE 5 - Archiviste
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def archiver_courrier(request, pk):
    """L archiviste classe un courrier traite en archive definitive."""
    if request.user.profil != 'ARC':
        return Response({'detail': 'Reserve a l Archiviste.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.TRAITE)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou non traite.'}, status=404)
    courrier.statut = StatutCourrier.ARCHIVE
    courrier.save()
    journaliser(request, TypeAction.ARCHIVAGE, f"Courrier archivé : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_notifications(request):
    notifs = Notification.objects.filter(destinataire=request.user)
    # Compter les non lues avant de les marquer
    non_lues = notifs.filter(lue=False).count()
    notifs.filter(lue=False).update(lue=True)
    data = NotificationSerializer(notifs, many=True).data
    return Response({'non_lues': non_lues, 'notifications': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compter_notifications(request):
    """Compte les notifications non lues sans les marquer comme lues. Utilise pour le badge."""
    count = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return Response({'non_lues': count})
