"""
Vues des modules 8, 9 et 10 - GED ESCEP-Niger.
Module 8 : Statistiques DG
Module 9 : Journal d audit
Module 10 : Delegations ponctuelles
"""

from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta

from .models import JournalAudit, Delegation, TypeAction, Issue, journaliser, PerimetreDelegation


# ---------------------------------------------------------------
# MODULE 8 - Statistiques DG
# ---------------------------------------------------------------


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistiques_dg(request):
    if request.user.profil != 'DG':
        journaliser(request, TypeAction.ACCES_REFUSE, 'Tentative acces statistiques DG', issue=Issue.REFUS)
        return Response({'detail': 'Reserve au Directeur General.'}, status=403)

    from apps.courriers.models import Courrier, StatutCourrier

    # Lire les filtres
    periode    = request.GET.get('periode', 'mois')
    date_debut = request.GET.get('date_debut', '')
    date_fin   = request.GET.get('date_fin', '')

    maintenant  = timezone.now()
    aujourd_hui = maintenant.date()

    # Plage de dates selon filtre
    if date_debut and date_fin:
        from datetime import date as date_type
        debut = date_type.fromisoformat(date_debut)
        fin   = date_type.fromisoformat(date_fin)
    elif periode == 'jour':
        debut = aujourd_hui
        fin   = aujourd_hui
    elif periode == 'semaine':
        debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin   = aujourd_hui
    elif periode == 'trimestre':
        mois_debut = ((aujourd_hui.month - 1) // 3) * 3 + 1
        debut = aujourd_hui.replace(month=mois_debut, day=1)
        fin   = aujourd_hui
    elif periode == 'annee':
        debut = aujourd_hui.replace(month=1, day=1)
        fin   = aujourd_hui
    else:  # mois par defaut
        debut = aujourd_hui.replace(day=1)
        fin   = aujourd_hui

    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    debut_mois    = aujourd_hui.replace(day=1)
    an_passe      = debut_mois.replace(year=debut_mois.year - 1)

    # Indicateurs operationnels — toujours sur les periodes fixes
    recu_jour    = Courrier.objects.filter(date_reception=aujourd_hui).count()
    recu_semaine = Courrier.objects.filter(date_reception__gte=debut_semaine).count()
    recu_mois    = Courrier.objects.filter(date_reception__gte=debut_mois).count()

    en_attente = Courrier.objects.filter(statut=StatutCourrier.EN_ATT_IMP).count()

    seuil_j3 = maintenant - timedelta(days=3)
    non_consultes_j3 = Courrier.objects.filter(
        statut=StatutCourrier.IMPUTE, date_imputation__lt=seuil_j3
    ).count()

    seuil_j7 = maintenant - timedelta(days=7)
    en_retard_j7 = Courrier.objects.filter(
        statut__in=[StatutCourrier.IMPUTE, StatutCourrier.EN_COURS],
        date_imputation__lt=seuil_j7
    ).count()

    courriers_imputes = Courrier.objects.filter(date_imputation__isnull=False)
    delai_rec_imp = None
    if courriers_imputes.exists():
        total = sum(
            (c.date_imputation.date() - c.date_reception).days
            for c in courriers_imputes if c.date_imputation and c.date_reception
        )
        delai_rec_imp = round(total / courriers_imputes.count(), 1)

    courriers_traites = Courrier.objects.filter(
        date_traitement__isnull=False, date_imputation__isnull=False
    )
    delai_imp_trt = None
    if courriers_traites.exists():
        total = sum(
            (c.date_traitement.date() - c.date_imputation.date()).days
            for c in courriers_traites if c.date_traitement and c.date_imputation
        )
        delai_imp_trt = round(total / courriers_traites.count(), 1)

    # Indicateurs strategiques — filtrés par la plage choisie
    qs_periode = Courrier.objects.filter(date_reception__gte=debut, date_reception__lte=fin)

    volume_mois     = qs_periode.count()
    volume_an_passe = Courrier.objects.filter(
        date_reception__gte=an_passe, date_reception__lt=debut_mois
    ).count()

    par_type = list(
        qs_periode.values('type_courrier')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    par_statut = list(
        Courrier.objects.values('statut')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    total_verifies = Courrier.objects.filter(
        statut__in=[StatutCourrier.REJETE, StatutCourrier.EN_ATT_IMP,
                    StatutCourrier.IMPUTE, StatutCourrier.EN_COURS,
                    StatutCourrier.TRAITE, StatutCourrier.ARCHIVE]
    ).count()
    total_rejetes = Courrier.objects.filter(statut=StatutCourrier.REJETE).count()
    taux_rejet = round(total_rejetes / total_verifies * 100, 1) if total_verifies > 0 else 0

    performance = list(
        qs_periode.filter(
            destinataire__isnull=False,
            statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE]
        )
        .values('destinataire__nom', 'destinataire__prenom', 'destinataire__direction__nom')
        .annotate(total_traites=Count('id'))
        .order_by('-total_traites')[:10]
    )

    return Response({
        'periode': {
            'type':  periode,
            'debut': str(debut),
            'fin':   str(fin),
        },
        'operationnels': {
            'recu_jour':                   recu_jour,
            'recu_semaine':                recu_semaine,
            'recu_mois':                   recu_mois,
            'en_attente_imputation':       en_attente,
            'non_consultes_j3':            non_consultes_j3,
            'en_retard_j7':                en_retard_j7,
            'delai_reception_imputation':  delai_rec_imp,
            'delai_imputation_traitement': delai_imp_trt,
        },
        'strategiques': {
            'volume_mois_actuel': volume_mois,
            'volume_mois_passe':  volume_an_passe,
            'par_type':           par_type,
            'par_statut':         par_statut,
            'taux_rejet':         taux_rejet,
            'performance_dest':   performance,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel(request):
    """Export des statistiques en Excel."""
    if request.user.profil != 'DG':
        return Response({'detail': 'Reserve au Directeur General.'}, status=403)

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        return Response({'detail': 'Installez openpyxl : pip install openpyxl'}, status=500)

    import io
    from django.http import HttpResponse
    from apps.courriers.models import Courrier, StatutCourrier

    maintenant  = timezone.now()
    aujourd_hui = maintenant.date()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    debut_mois    = aujourd_hui.replace(day=1)
    seuil_j3 = maintenant - timedelta(days=3)
    seuil_j7 = maintenant - timedelta(days=7)

    wb  = openpyxl.Workbook()
    en  = Font(bold=True, color='FFFFFF')
    fd  = PatternFill('solid', fgColor='1565C0')

    # Feuille 1 - Indicateurs operationnels
    ws1 = wb.active
    ws1.title = 'Indicateurs operationnels'
    ws1.append(['Indicateur', 'Valeur'])
    for c in ws1[1]: c.font = en; c.fill = fd
    ws1.append(['Recus aujourd hui',     Courrier.objects.filter(date_reception=aujourd_hui).count()])
    ws1.append(['Recus cette semaine',   Courrier.objects.filter(date_reception__gte=debut_semaine).count()])
    ws1.append(['Recus ce mois',         Courrier.objects.filter(date_reception__gte=debut_mois).count()])
    ws1.append(['En attente imputation', Courrier.objects.filter(statut=StatutCourrier.EN_ATT_IMP).count()])
    ws1.append(['Non consultes J+3',     Courrier.objects.filter(statut=StatutCourrier.IMPUTE, date_imputation__lt=seuil_j3).count()])
    ws1.append(['En retard J+7',         Courrier.objects.filter(statut__in=[StatutCourrier.IMPUTE, StatutCourrier.EN_COURS], date_imputation__lt=seuil_j7).count()])
    ws1.column_dimensions['A'].width = 35
    ws1.column_dimensions['B'].width = 15

    # Feuille 2 - Repartition par statut
    ws2 = wb.create_sheet('Repartition par statut')
    ws2.append(['Statut', 'Nombre'])
    for c in ws2[1]: c.font = en; c.fill = fd
    for s in Courrier.objects.values('statut').annotate(total=Count('id')).order_by('-total'):
        ws2.append([s['statut'], s['total']])
    ws2.column_dimensions['A'].width = 20
    ws2.column_dimensions['B'].width = 15

    # Feuille 3 - Performance destinataires
    ws3 = wb.create_sheet('Performance destinataires')
    ws3.append(['Nom', 'Prenom', 'Entite', 'Courriers traites'])
    for c in ws3[1]: c.font = en; c.fill = fd
    for d in Courrier.objects.filter(
        destinataire__isnull=False,
        statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE]
    ).values('destinataire__nom', 'destinataire__prenom', 'destinataire__direction__nom').annotate(total=Count('id')).order_by('-total'):
        ws3.append([d['destinataire__nom'], d['destinataire__prenom'], d['destinataire__direction__nom'], d['total']])
    for col in ['A', 'B', 'C', 'D']:
        ws3.column_dimensions[col].width = 22

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="statistiques_ged_{aujourd_hui}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf(request):
    """Export des statistiques en PDF."""
    if request.user.profil != 'DG':
        return Response({'detail': 'Reserve au Directeur General.'}, status=403)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return Response({'detail': 'Installez reportlab : pip install reportlab'}, status=500)

    import io
    from django.http import HttpResponse
    from apps.courriers.models import Courrier, StatutCourrier

    maintenant  = timezone.now()
    aujourd_hui = maintenant.date()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    debut_mois    = aujourd_hui.replace(day=1)
    seuil_j3 = maintenant - timedelta(days=3)
    seuil_j7 = maintenant - timedelta(days=7)

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story  = []

    bleu = colors.HexColor('#1565C0')
    gris = colors.HexColor('#f5f8ff')

    story.append(Paragraph('GED ESCEP-Niger — Tableau de bord statistiques', styles['Title']))
    story.append(Paragraph(f"Genere le {aujourd_hui.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))

    def faire_tableau(data):
        t = Table(data, colWidths=[350, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0), bleu),
            ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
            ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, gris]),
            ('GRID',           (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN',          (1, 0), (1, -1), 'CENTER'),
        ]))
        return t

    story.append(Paragraph('Indicateurs operationnels', styles['Heading2']))
    story.append(faire_tableau([
        ['Indicateur', 'Valeur'],
        ['Recus aujourd hui',     Courrier.objects.filter(date_reception=aujourd_hui).count()],
        ['Recus cette semaine',   Courrier.objects.filter(date_reception__gte=debut_semaine).count()],
        ['Recus ce mois',         Courrier.objects.filter(date_reception__gte=debut_mois).count()],
        ['En attente imputation', Courrier.objects.filter(statut=StatutCourrier.EN_ATT_IMP).count()],
        ['Non consultes J+3',     Courrier.objects.filter(statut=StatutCourrier.IMPUTE, date_imputation__lt=seuil_j3).count()],
        ['En retard J+7',         Courrier.objects.filter(statut__in=[StatutCourrier.IMPUTE, StatutCourrier.EN_COURS], date_imputation__lt=seuil_j7).count()],
    ]))

    story.append(Spacer(1, 20))
    story.append(Paragraph('Repartition par statut', styles['Heading2']))
    data_st = [['Statut', 'Nombre']]
    for s in Courrier.objects.values('statut').annotate(total=Count('id')).order_by('-total'):
        data_st.append([s['statut'], s['total']])
    story.append(faire_tableau(data_st))

    story.append(Spacer(1, 20))
    story.append(Paragraph('Performance par destinataire', styles['Heading2']))
    data_perf = [['Nom', 'Entite', 'Traites']]
    for d in Courrier.objects.filter(
        destinataire__isnull=False,
        statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE]
    ).values('destinataire__nom', 'destinataire__prenom', 'destinataire__direction__nom').annotate(total=Count('id')).order_by('-total')[:10]:
        data_perf.append([f"{d['destinataire__prenom']} {d['destinataire__nom']}", d['destinataire__direction__nom'], d['total']])
    story.append(faire_tableau(data_perf))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="statistiques_ged_{aujourd_hui}.pdf"'
    return response
# ---------------------------------------------------------------
# MODULE 9 - Journal d audit
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_audit(request):
    """
    Consultation du journal d audit.
    Reserve au DG uniquement.
    Filtres : type action, utilisateur, date debut/fin, issue, objet.
    """
    if request.user.profil not in ['DG', 'ADMIN']:
        journaliser(request, TypeAction.ACCES_REFUSE, 'Tentative accès journal audit', issue=Issue.REFUS)
        return Response({'detail': 'Réservé au Directeur Général.'}, status=403)

    qs = JournalAudit.objects.all()

    # Filtres
    type_action = request.GET.get('type_action', '')
    identifiant = request.GET.get('identifiant', '')
    date_debut  = request.GET.get('date_debut', '')
    date_fin    = request.GET.get('date_fin', '')
    issue       = request.GET.get('issue', '')
    q           = request.GET.get('q', '')

    if type_action: qs = qs.filter(type_action=type_action)
    if identifiant: qs = qs.filter(identifiant_user__icontains=identifiant)
    if date_debut:  qs = qs.filter(horodatage_utc__date__gte=date_debut)
    if date_fin:    qs = qs.filter(horodatage_utc__date__lte=date_fin)
    if issue:       qs = qs.filter(issue=issue)
    if q:           qs = qs.filter(Q(description__icontains=q) | Q(objet_libelle__icontains=q))

    # Limiter a 500 entrees par requete
    qs = qs[:500]

    data = [{
        'id':              e.id,
        'horodatage':      e.horodatage_utc.strftime('%d/%m/%Y %H:%M:%S'),
        'identifiant':     e.identifiant_user,
        'profil':          e.profil_user,
        'type_action':     e.type_action,
        'description':     e.description,
        'objet_type':      e.objet_type,
        'objet_id':        e.objet_id,
        'objet_libelle':   e.objet_libelle,
        'adresse_ip':      str(e.adresse_ip) if e.adresse_ip else '',
        'issue':           e.issue,
    } for e in qs]

    return Response({
        'total': len(data),
        'types_action': [{'code': c[0], 'label': c[1]} for c in TypeAction.choices],
        'entrees': data,
    })


# ---------------------------------------------------------------
# MODULE 10 - Delegations ponctuelles
# ---------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_delegations(request):
    """
    GET  : liste des delegations (DG voit tout, autres voient les leurs).
    POST : creer une delegation (DG uniquement).
    """
    if request.method == 'GET':
        if request.user.profil == 'DG':
            delegations = Delegation.objects.all().select_related('beneficiaire', 'accordee_par')
        else:
            delegations = Delegation.objects.filter(beneficiaire=request.user, active=True)

        aujourd_hui = timezone.now().date()
        data = [{
            'id':              d.id,
            'beneficiaire_nom': f"{d.beneficiaire.prenom} {d.beneficiaire.nom}",
            'beneficiaire_profil': d.beneficiaire.profil,
            'perimetre':       d.perimetre,
            'motif':           d.motif,
            'date_debut':      str(d.date_debut),
            'date_fin':        str(d.date_fin),
            'active':          d.active,
            'est_active':      d.est_active,
            'expiree':         d.date_fin < aujourd_hui,
            'courrier_vise':   d.courrier_vise.numero_officiel if d.courrier_vise else None,
            'fonds_vise':      d.fonds_vise,
            'dossier_thematique': d.dossier_thematique,
            'periode_debut':   str(d.periode_debut) if d.periode_debut else None,
            'periode_fin_perim': str(d.periode_fin_perim) if d.periode_fin_perim else None,
            'date_creation':   d.date_creation.strftime('%d/%m/%Y %H:%M'),
        } for d in delegations]
        return Response(data)

    if request.method == 'POST':
        if request.user.profil != 'DG':
            return Response({'detail': 'Reserve au Directeur General.'}, status=403)

        beneficiaire_id = request.data.get('beneficiaire_id')
        perimetre       = request.data.get('perimetre')
        motif           = request.data.get('motif', '').strip()
        date_debut      = request.data.get('date_debut')
        date_fin        = request.data.get('date_fin')

        if not all([beneficiaire_id, perimetre, motif, date_debut, date_fin]):
            return Response({'detail': 'Tous les champs obligatoires doivent etre remplis.'}, status=400)

        if date_debut > date_fin:
            return Response({'detail': 'La date de fin doit etre apres la date de debut.'}, status=400)

        from apps.users.models import Utilisateur
        try:
            beneficiaire = Utilisateur.objects.get(pk=beneficiaire_id, is_active=True)
        except Utilisateur.DoesNotExist:
            return Response({'detail': 'Beneficiaire introuvable.'}, status=404)

        delegation = Delegation(
            accordee_par  = request.user,
            beneficiaire  = beneficiaire,
            perimetre     = perimetre,
            motif         = motif,
            date_debut    = date_debut,
            date_fin      = date_fin,
        )

        # Perimetre detail
        if perimetre == PerimetreDelegation.COURRIER:
            courrier_id = request.data.get('courrier_id')
            if courrier_id:
                from apps.courriers.models import Courrier
                try:
                    delegation.courrier_vise = Courrier.objects.get(pk=courrier_id)
                except Courrier.DoesNotExist:
                    pass
        elif perimetre == PerimetreDelegation.PERIODE:
            delegation.periode_debut     = request.data.get('periode_debut', date_debut)
            delegation.periode_fin_perim = request.data.get('periode_fin_perim', date_fin)
        elif perimetre == PerimetreDelegation.FONDS:
            delegation.fonds_vise = request.data.get('fonds_vise', '')
        elif perimetre == PerimetreDelegation.DOSSIER:
            delegation.dossier_thematique = request.data.get('dossier_thematique', '')

        delegation.save()

        # Journaliser
        journaliser(
            request, TypeAction.DELEGATION_ACCORDEE,
            f"Delegation accordee a {beneficiaire.prenom} {beneficiaire.nom} ({beneficiaire.profil}). Motif : {motif}",
            objet_type='delegation', objet_id=str(delegation.id),
            objet_libelle=f"Delegation {perimetre} jusqu au {date_fin}"
        )

        # Notifier le beneficiaire
        from apps.courriers.models import Notification
        Notification.objects.create(
            destinataire=beneficiaire,
            message=f"Le DG vous a accorde une delegation de lecture ({perimetre}) du {date_debut} au {date_fin}. Motif : {motif}"
        )

        return Response({'detail': 'Delegation creee.', 'id': delegation.id}, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def revoquer_delegation(request, pk):
    """Le DG peut revoquer une delegation a tout moment."""
    if request.user.profil != 'DG':
        return Response({'detail': 'Reserve au Directeur General.'}, status=403)

    try:
        delegation = Delegation.objects.get(pk=pk, active=True)
    except Delegation.DoesNotExist:
        return Response({'detail': 'Delegation introuvable ou deja revoquee.'}, status=404)

    motif_revocation = request.data.get('motif', '').strip()

    delegation.active            = False
    delegation.date_revocation   = timezone.now()
    delegation.motif_revocation  = motif_revocation
    delegation.save()

    journaliser(
        request, TypeAction.DELEGATION_REVOQUEE,
        f"Delegation #{pk} revoquee. Beneficiaire : {delegation.beneficiaire.identifiant}. Motif : {motif_revocation}",
        objet_type='delegation', objet_id=str(pk)
    )

    return Response({'detail': 'Delegation revoquee.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recherche_globale(request):
    """Module 7 - Recherche documentaire filtree par droits."""
    from apps.courriers.models import Courrier, StatutCourrier, CourrierCopie
    from apps.archives.models import ArchiveHistorique

    profil = request.user.profil
    q            = request.GET.get('q', '').strip()
    type_c       = request.GET.get('type', '')
    statut       = request.GET.get('statut', '')
    priorite     = request.GET.get('priorite', '')
    date_debut   = request.GET.get('date_debut', '')
    date_fin     = request.GET.get('date_fin', '')
    avec_archives = request.GET.get('avec_archives', 'false') == 'true'

    if profil == 'BO':
        qs = Courrier.objects.filter(saisi_par=request.user)
    elif profil == 'ASSIST':
        qs = Courrier.objects.exclude(statut=StatutCourrier.BROUILLON)
    elif profil == 'DG':
        qs = Courrier.objects.all()
    elif profil == 'DEST':
        ids_copie = CourrierCopie.objects.filter(destinataire=request.user).values_list('courrier_id', flat=True)
        qs = Courrier.objects.filter(Q(destinataire=request.user) | Q(id__in=ids_copie))
    elif profil == 'ARC':
        qs = Courrier.objects.filter(statut__in=[StatutCourrier.TRAITE, StatutCourrier.ARCHIVE])
    else:
        qs = Courrier.objects.none()

    if q:       qs = qs.filter(Q(objet__icontains=q) | Q(expediteur__icontains=q) | Q(numero_officiel__icontains=q) | Q(reference_exp__icontains=q))
    if type_c:  qs = qs.filter(type_courrier=type_c)
    if statut:  qs = qs.filter(statut=statut)
    if priorite: qs = qs.filter(priorite=priorite)
    if date_debut: qs = qs.filter(date_reception__gte=date_debut)
    if date_fin:   qs = qs.filter(date_reception__lte=date_fin)

    from apps.courriers.serializers import CourrierSerializer
    courriers_data = CourrierSerializer(qs[:50], many=True, context={'request': request}).data

    archives_data = []
    if avec_archives and profil in ['DG', 'ARC']:
        qs_arc = ArchiveHistorique.objects.all()
        if q:          qs_arc = qs_arc.filter(Q(intitule__icontains=q) | Q(expediteur__icontains=q) | Q(reference_systeme__icontains=q) | Q(reference_origine__icontains=q) | Q(mots_cles__icontains=q) | Q(resume__icontains=q))
        if date_debut: qs_arc = qs_arc.filter(date_document__gte=date_debut)
        if date_fin:   qs_arc = qs_arc.filter(date_document__lte=date_fin)
        from apps.archives.serializers import ArchiveSerializer
        archives_data = ArchiveSerializer(qs_arc[:50], many=True, context={'request': request}).data

    return Response({'courriers': courriers_data, 'archives': archives_data, 'total_courriers': len(courriers_data), 'total_archives': len(archives_data)})
