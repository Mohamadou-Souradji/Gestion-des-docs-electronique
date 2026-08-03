"""
Vues des courriers — GED ESCEP-Niger SaaS.
Filtrage automatique par organisation (tenant).
"""
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.models import journaliser, TypeAction
from .models import Courrier, CourrierCopie, Notification, StatutCourrier, CONSIGNES_TYPES
from .serializers import CourrierSerializer, NotificationSerializer

from .emails import envoyer_notification

def notifier(utilisateur, message, courrier=None, organisation=None):
    org = organisation or (courrier.organisation if courrier else None)
    
    # Notification en base
    Notification.objects.create(
        organisation=org,
        destinataire=utilisateur,
        message=message,
        courrier=courrier
    )
    
    # Notification par email
    if courrier:
        sujet = f"[GED] {courrier.objet[:60]}"
    else:
        sujet = "[GED] Nouvelle notification"
    
    envoyer_notification(utilisateur, sujet, message, org)

# ---------------------------------------------------------------
# MODULE 1 — Bureau d'Ordre
# ---------------------------------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_courriers(request):
    org = request.tenant

    if request.method == 'GET':
        profil = request.user.profil
        qs = Courrier.objects.filter(organisation=org) if org else Courrier.objects.all()

        if profil == 'BO':
            qs = qs.filter(saisi_par=request.user)
        elif profil == 'ASSIST':
            qs = qs.exclude(statut=StatutCourrier.BROUILLON)
        elif profil == 'SGA':
            from django.db.models import Q
            qs = qs.filter(
                Q(statut=StatutCourrier.EN_ATTENTE_SGA) |
                Q(valide_sga_par=request.user)
            )
            # Filtres historique
            statut_f    = request.query_params.get('statut', '')
            date_debut  = request.query_params.get('date_debut', '')
            date_fin    = request.query_params.get('date_fin', '')
            q           = request.query_params.get('q', '')
            if statut_f:   qs = qs.filter(statut=statut_f)
            if date_debut: qs = qs.filter(date_saisie__date__gte=date_debut)
            if date_fin:   qs = qs.filter(date_saisie__date__lte=date_fin)
            if q:          qs = qs.filter(objet__icontains=q)

        elif profil == 'SG':
            from django.db.models import Q
            qs = qs.filter(
                Q(statut=StatutCourrier.EN_ATTENTE_SG) |
                Q(valide_sg_par=request.user)
            )
            statut_f    = request.query_params.get('statut', '')
            date_debut  = request.query_params.get('date_debut', '')
            date_fin    = request.query_params.get('date_fin', '')
            q           = request.query_params.get('q', '')
            if statut_f:   qs = qs.filter(statut=statut_f)
            if date_debut: qs = qs.filter(date_saisie__date__gte=date_debut)
            if date_fin:   qs = qs.filter(date_saisie__date__lte=date_fin)
            if q:          qs = qs.filter(objet__icontains=q)
        elif profil == 'DG':
            pass
        elif profil == 'DEST':
            from django.db.models import Q
            ids_copie = CourrierCopie.objects.filter(
                destinataire=request.user,
                courrier__organisation=org
            ).values_list('courrier_id', flat=True)
            qs = qs.filter(
                Q(destinataire=request.user) | Q(id__in=ids_copie)
            ).exclude(statut__in=[
                StatutCourrier.BROUILLON, StatutCourrier.EN_VERIF,
                StatutCourrier.EN_ATT_IMP, StatutCourrier.EN_ATTENTE_SGA,
                StatutCourrier.EN_ATTENTE_SG
            ])
        elif profil == 'ARC':
            qs = qs.filter(statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE])
        else:
            qs = Courrier.objects.none()

        return Response(CourrierSerializer(qs, many=True, context={'request': request}).data)

    if request.method == 'POST':
        if request.user.profil != 'BO':
            return Response({'detail': "Réservé au Bureau d'Ordre."}, status=403)

        action = request.data.get('action', 'BROUILLON')
        serializer = CourrierSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        if action == 'SOUMETTRE':
            statut_initial = StatutCourrier.EN_ATTENTE_SGA if (org and org.workflow_type == 'ETENDU') else StatutCourrier.EN_VERIF
        else:
            statut_initial = StatutCourrier.BROUILLON

        courrier = serializer.save(
            saisi_par=request.user,
            statut=statut_initial,
            organisation=org
        )

        if action == 'SOUMETTRE':
            from apps.users.models import Utilisateur
            if org and org.workflow_type == 'ETENDU':
                for u in Utilisateur.objects.filter(profil='SGA', is_active=True, organisation=org):
                    notifier(u, f"Nouveau courrier à valider : {courrier.objet}", courrier, org)
            else:
                for a in Utilisateur.objects.filter(profil='ASSIST', is_active=True, organisation=org):
                    notifier(a, f"Nouveau courrier à vérifier : {courrier.objet}", courrier, org)

        journaliser(request, TypeAction.SOUMISSION, f"Courrier soumis : {courrier.objet}", 'courrier', courrier.identifiant_temp, courrier.objet)
        # Limite par défaut 20, augmentable via paramètre
        limite = request.query_params.get('limite')
        if limite:
            try:
                qs = qs[:int(limite)]
            except ValueError:
                pass
        else:
            qs = qs[:20]

        return Response(CourrierSerializer(qs, many=True, context={'request': request}).data)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_courrier(request, pk):
    if request.user.profil != 'BO':
        return Response({'detail': "Réservé au Bureau d'Ordre."}, status=403)
    try:
        courrier = Courrier.objects.get(
            pk=pk, saisi_par=request.user,
            statut__in=[StatutCourrier.BROUILLON, StatutCourrier.REJETE],
            organisation=request.tenant
        )
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou non modifiable.'}, status=404)

    for champ in ['objet', 'expediteur', 'reference_exp', 'type_courrier', 'mode_reception',
                  'priorite', 'date_document', 'date_reception', 'observations']:
        if champ in request.data:
            setattr(courrier, champ, request.data[champ])

    if 'fichier_pdf' in request.FILES:
        courrier.fichier_pdf = request.FILES['fichier_pdf']

    action = request.data.get('action', '')
    if action == 'SOUMETTRE':
        org = request.tenant
        from apps.users.models import Utilisateur
        if org and org.workflow_type == 'ETENDU':
            courrier.statut = StatutCourrier.EN_ATTENTE_SGA
            courrier.motif_rejet_sga = ''
            for u in Utilisateur.objects.filter(profil='SGA', is_active=True, organisation=org):
                notifier(u, f"Courrier corrigé et resoumis : {courrier.objet}", courrier)
        else:
            courrier.statut = StatutCourrier.EN_VERIF
            courrier.motif_rejet = ''
            for a in Utilisateur.objects.filter(profil='ASSIST', is_active=True, organisation=org):
                notifier(a, f"Courrier corrigé et resoumis : {courrier.objet}", courrier)

    courrier.save()
    return Response(CourrierSerializer(courrier, context={'request': request}).data)
# ---------------------------------------------------------------
# MODULE 2 — Assistant DG
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def valider_courrier(request, pk):
    if request.user.profil != 'ASSIST':
        return Response({'detail': "Réservé à l'Assistant DG."}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_VERIF, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)

    courrier.numero_officiel   = courrier.generer_numero_officiel()
    courrier.statut            = StatutCourrier.EN_ATT_IMP
    courrier.verifie_par       = request.user
    courrier.date_verification = timezone.now()
    courrier.observation_dg    = request.data.get('observation_dg', '')
    courrier.save()

    notifier(courrier.saisi_par, f"Courrier validé : '{courrier.objet}'. N° : {courrier.numero_officiel}", courrier)
    journaliser(request, TypeAction.VALIDATION, f"Courrier validé : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)

    from apps.users.models import Utilisateur
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True, organisation=request.tenant):
        notifier(dg, f"Courrier à imputer : {courrier.objet} ({courrier.numero_officiel})", courrier)

    return Response(CourrierSerializer(courrier, context={'request': request}).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejeter_courrier(request, pk):
    if request.user.profil != 'ASSIST':
        return Response({'detail': "Réservé à l'Assistant DG."}, status=403)

    motif = request.data.get('motif_rejet', '').strip()
    if not motif:
        return Response({'detail': 'Le motif du rejet est obligatoire.'}, status=400)

    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_VERIF, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)

    courrier.statut            = StatutCourrier.REJETE
    courrier.verifie_par       = request.user
    courrier.date_verification = timezone.now()
    courrier.motif_rejet       = motif
    courrier.save()

    notifier(courrier.saisi_par, f"Courrier rejeté : '{courrier.objet}'. Motif : {motif}", courrier)
    journaliser(request, TypeAction.REJET, f"Courrier rejeté : {courrier.objet}", 'courrier', courrier.identifiant_temp, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE 3 — DG : Imputation
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_destinataires(request):
    if request.user.profil not in ['DG', 'SGA', 'SG']:
     return Response({'detail': 'Accès non autorisé.'}, status=403)
    from apps.users.models import Utilisateur
    dests = Utilisateur.objects.filter(
        profil='DEST', is_active=True, organisation=request.tenant
    ).select_related('direction')
    data = [{
        'id': u.id, 'nom': u.nom, 'prenom': u.prenom,
        'entite': u.direction.nom if u.direction else '', 'fonction': u.fonction
    } for u in dests]
    return Response(data)
# apps/courriers/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_consignes_types(request):
    org = request.tenant
    if org and org.consignes_imputation:
        items_valides = [c for c in org.consignes_imputation if c.get('code') and c.get('label')]
        if items_valides:
            return Response(items_valides)
    return Response([{'code': c[0], 'label': c[1]} for c in CONSIGNES_TYPES])

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def imputer_courrier(request, pk):
    if request.user.profil not in ['DG', 'SGA', 'SG']:
         return Response({'detail': 'Accès non autorisé.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_ATT_IMP, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou déjà imputé.'}, status=404)

    destinataire_id = request.data.get('destinataire_id')
    copies_items    = request.data.get('copies_items', [])  # ← [{id, consignes_types, consigne_libre}]
    consignes_types = request.data.get('consignes_types', [])
    consigne_libre  = request.data.get('consigne_libre', '').strip()

    if not destinataire_id:
        return Response({'detail': 'Un destinataire principal est obligatoire.'}, status=400)
    if not consignes_types:
        return Response({'detail': 'Au moins une consigne type doit être cochée.'}, status=400)

    from apps.users.models import Utilisateur
    try:
        destinataire = Utilisateur.objects.get(
            pk=destinataire_id, profil='DEST', is_active=True, organisation=request.tenant
        )
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Destinataire introuvable.'}, status=404)

    instructions = ', '.join(consignes_types)
    if consigne_libre:
        instructions += f'\n\nConsigne spécifique : {consigne_libre}'

    courrier.destinataire    = destinataire
    courrier.impute_par      = request.user
    courrier.date_imputation = timezone.now()
    courrier.instructions_dg = instructions
    courrier.statut          = StatutCourrier.IMPUTE
    courrier.save()

    # Copies avec consignes individuelles
    for item in copies_items:
        try:
            dest_copie = Utilisateur.objects.get(
                pk=item['id'], profil='DEST', is_active=True, organisation=request.tenant
            )
            copie, _ = CourrierCopie.objects.get_or_create(
                courrier=courrier,
                destinataire=dest_copie,
                defaults={'organisation': request.tenant}
            )
            copie.consignes_types = item.get('consignes_types', [])
            copie.consigne_libre  = item.get('consigne_libre', '')
            copie.save()

            instructions_copie = ', '.join(item.get('consignes_types', []))
            if item.get('consigne_libre'):
                instructions_copie += f'\nConsigne spécifique : {item["consigne_libre"]}'

            notifier(
                dest_copie,
                f"Vous êtes en copie du courrier : '{courrier.objet}' ({courrier.numero_officiel}). Instructions : {instructions_copie[:100]}",
                courrier
            )
        except (Utilisateur.DoesNotExist, KeyError):
            pass

    notifier(destinataire, f"Nouveau courrier : '{courrier.objet}' ({courrier.numero_officiel}). Instructions : {instructions[:100]}", courrier)
    journaliser(request, TypeAction.IMPUTATION, f"Courrier imputé à {destinataire.prenom} {destinataire.nom}", 'courrier', courrier.numero_officiel, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)
# ---------------------------------------------------------------
# MODULE 4 — Destinataire
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_lu(request, pk):
    if request.user.profil != 'DEST':
        return Response({'detail': 'Réservé aux destinataires.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, destinataire=request.user, statut=StatutCourrier.IMPUTE)
        courrier.statut = StatutCourrier.EN_COURS
        courrier.save()
        journaliser(request, TypeAction.CONSULTATION, f"Courrier consulté : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)
    except Courrier.DoesNotExist:
        pass
    CourrierCopie.objects.filter(courrier_id=pk, destinataire=request.user, date_lecture__isnull=True).update(date_lecture=timezone.now())
    return Response({'detail': 'Courrier marqué comme lu.'})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_traite(request, pk):
    if request.user.profil != 'DEST':
        return Response({'detail': 'Réservé aux destinataires.'}, status=403)
    try:
        courrier = Courrier.objects.get(
            pk=pk, destinataire=request.user,
            statut__in=[StatutCourrier.IMPUTE, StatutCourrier.EN_COURS]
        )
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou déjà traité.'}, status=404)

    courrier.statut             = StatutCourrier.TRAITE
    courrier.date_traitement    = timezone.now()
    courrier.reponse_traitement = request.data.get('reponse', '').strip()

    if 'fichier_reponse' in request.FILES:
        courrier.fichier_reponse = request.FILES['fichier_reponse']

    courrier.save()

    journaliser(request, TypeAction.TRAITEMENT, f"Courrier traité : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)

    from apps.users.models import Utilisateur
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True, organisation=request.tenant):
        notifier(dg, f"Courrier traité par {request.user.prenom} {request.user.nom} : '{courrier.objet}'", courrier)
    for arc in Utilisateur.objects.filter(profil='ARC', is_active=True, organisation=request.tenant):
        notifier(arc, f"Courrier à archiver : '{courrier.objet}' ({courrier.numero_officiel})", courrier)

    return Response(CourrierSerializer(courrier, context={'request': request}).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_lu_copie(request, pk):
    if request.user.profil != 'DEST':
        return Response({'detail': 'Réservé aux destinataires.'}, status=403)
    try:
        copie = CourrierCopie.objects.get(courrier_id=pk, destinataire=request.user)
        copie.date_lecture = timezone.now()
        copie.save()
    except CourrierCopie.DoesNotExist:
        pass
    return Response({'detail': 'Lu.'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def traiter_copie(request, pk):
    if request.user.profil != 'DEST':
        return Response({'detail': 'Réservé aux destinataires.'}, status=403)
    try:
        copie = CourrierCopie.objects.get(courrier_id=pk, destinataire=request.user)
    except CourrierCopie.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)

    copie.reponse        = request.data.get('reponse', '').strip()
    copie.date_traitement = timezone.now()
    if 'fichier_reponse' in request.FILES:
        copie.fichier_reponse = request.FILES['fichier_reponse']
    copie.save()

    from apps.users.models import Utilisateur
    org = request.tenant
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True, organisation=org):
        notifier(dg, f"Compte-rendu en copie de {request.user.prenom} {request.user.nom} : '{copie.courrier.objet}'", copie.courrier)

    journaliser(request, TypeAction.TRAITEMENT, f"Compte-rendu copie : {copie.courrier.objet}", 'courrier', copie.courrier.numero_officiel, copie.courrier.objet)
    return Response({'detail': 'Compte-rendu enregistré.'})

# ---------------------------------------------------------------
# MODULE 5 — Archiviste
# ---------------------------------------------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def archiver_courrier(request, pk):
    if request.user.profil != 'ARC':
        return Response({'detail': "Réservé à l'Archiviste."}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.TRAITE, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable ou non traité.'}, status=404)

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
    non_lues = notifs.filter(lue=False).count()
    notifs.filter(lue=False).update(lue=True)
    return Response({'non_lues': non_lues, 'notifications': NotificationSerializer(notifs, many=True).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compter_notifications(request):
    count = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return Response({'non_lues': count})

# ---------------------------------------------------------------
# MODULE SGA
# ---------------------------------------------------------------
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def valider_sga(request, pk):
    if request.user.profil != 'SGA':
        return Response({'detail': 'Réservé au SGA.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_ATTENTE_SGA, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)
    
    destinataire_id = request.data.get('destinataire_id')
    consignes_types = request.data.get('consignes_types', [])
    copies_items    = request.data.get('copies_items', [])

    if not destinataire_id:
        return Response({'detail': 'Un destinataire principal est obligatoire.'}, status=400)
    if not consignes_types:
        return Response({'detail': 'Au moins une consigne type doit être cochée.'}, status=400)

    courrier.numero_officiel     = courrier.generer_numero_officiel()
    courrier.verifie_par         = request.user
    courrier.date_verification   = timezone.now()
    courrier.proposition_sga     = {
        'destinataire_id': destinataire_id,
        'copies_items':    copies_items,
        'consignes_types': consignes_types,
        'consigne_libre':  request.data.get('consigne_libre', ''),
    }
    courrier.valide_sga_par      = request.user
    courrier.date_validation_sga = timezone.now()
    courrier.statut              = StatutCourrier.EN_ATTENTE_SG
    courrier.save()

    notifier(courrier.saisi_par, f"Courrier validé par le SGA : '{courrier.objet}'. N° : {courrier.numero_officiel}", courrier)
    journaliser(request, TypeAction.VALIDATION, f"Courrier validé SGA : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)

    from apps.users.models import Utilisateur
    for sg in Utilisateur.objects.filter(profil='SG', is_active=True, organisation=request.tenant):
        notifier(sg, f"Courrier à valider : {courrier.objet} ({courrier.numero_officiel})", courrier)

    return Response(CourrierSerializer(courrier, context={'request': request}).data)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rejeter_sga(request, pk):
    if request.user.profil != 'SGA':
        return Response({'detail': 'Réservé au SGA.'}, status=403)

    motif = request.data.get('motif_rejet', '').strip()
    if not motif:
        return Response({'detail': 'Le motif du rejet est obligatoire.'}, status=400)

    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_ATTENTE_SGA, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)

    courrier.statut              = StatutCourrier.BROUILLON
    courrier.valide_sga_par      = request.user
    courrier.date_validation_sga = timezone.now()
    courrier.motif_rejet_sga     = motif
    courrier.save()

    notifier(courrier.saisi_par, f"Courrier retourné par le SGA : '{courrier.objet}'. Motif : {motif}", courrier)
    journaliser(request, TypeAction.REJET, f"Courrier rejeté SGA : {courrier.objet}", 'courrier', courrier.identifiant_temp, courrier.objet)
    return Response(CourrierSerializer(courrier, context={'request': request}).data)


# ---------------------------------------------------------------
# MODULE SG
# ---------------------------------------------------------------
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def valider_sg(request, pk):
    if request.user.profil != 'SG':
        return Response({'detail': 'Réservé au SG.'}, status=403)
    try:
        courrier = Courrier.objects.get(pk=pk, statut=StatutCourrier.EN_ATTENTE_SG, organisation=request.tenant)
    except Courrier.DoesNotExist:
        return Response({'detail': 'Courrier introuvable.'}, status=404)

    destinataire_id = request.data.get('destinataire_id')
    consignes_types = request.data.get('consignes_types', [])
    copies_items    = request.data.get('copies_items', [])

    if destinataire_id and consignes_types:
        courrier.proposition_sg = {
            'destinataire_id': destinataire_id,
            'copies_items':    copies_items,
            'consignes_types': consignes_types,
            'consigne_libre':  request.data.get('consigne_libre', ''),
        }

    courrier.valide_sg_par      = request.user
    courrier.date_validation_sg = timezone.now()
    courrier.statut             = StatutCourrier.EN_ATT_IMP
    courrier.save()

    notifier(courrier.saisi_par, f"Courrier validé par le SG : '{courrier.objet}'", courrier)
    journaliser(request, TypeAction.VALIDATION, f"Courrier validé SG : {courrier.objet}", 'courrier', courrier.numero_officiel, courrier.objet)

    from apps.users.models import Utilisateur
    for dg in Utilisateur.objects.filter(profil='DG', is_active=True, organisation=request.tenant):
        notifier(dg, f"Courrier à imputer : {courrier.objet} ({courrier.numero_officiel})", courrier)

    return Response(CourrierSerializer(courrier, context={'request': request}).data)