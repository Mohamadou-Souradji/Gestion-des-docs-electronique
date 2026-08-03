# apps/dashboard/views.py — CORRIGÉ
# Fix: journal_audit retournait une liste directe,
# le frontend attend { entrees: [], types_action: [] }

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import JournalAudit, TypeAction


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_audit(request):
    if request.user.profil not in ['ADMIN', 'DG']:
        return Response({'detail': 'Accès refusé.'}, status=403)

    org = request.tenant
    qs  = JournalAudit.objects.filter(organisation=org).order_by('-horodatage_utc')

    # Filtres optionnels
    identifiant  = request.query_params.get('identifiant', '')
    type_action  = request.query_params.get('type_action', '')
    issue        = request.query_params.get('issue', '')
    date_debut   = request.query_params.get('date_debut', '')
    date_fin     = request.query_params.get('date_fin', '')
    q            = request.query_params.get('q', '')

    if identifiant:
        qs = qs.filter(identifiant_user__icontains=identifiant)
    if type_action:
        qs = qs.filter(type_action=type_action)
    if issue:
        qs = qs.filter(issue=issue)
    if date_debut:
        qs = qs.filter(horodatage_utc__date__gte=date_debut)
    if date_fin:
        qs = qs.filter(horodatage_utc__date__lte=date_fin)
    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(description__icontains=q) |
            Q(identifiant_user__icontains=q) |
            Q(objet_id__icontains=q)
        )

    qs = qs[:500]

    entrees = [{
        'id':              e.id,
        'identifiant':     e.identifiant_user,
        'profil':          e.profil_user,
        'type_action':     e.type_action,
        'description':     e.description,
        'objet_type':      e.objet_type,
        'objet_id':        e.objet_id,
        'adresse_ip':      str(e.adresse_ip) if e.adresse_ip else '',
        'issue':           e.issue,
        'horodatage':      e.horodatage_utc.strftime('%d/%m/%Y %H:%M:%S'),
    } for e in qs]

    # Types d'action disponibles pour le filtre
    try:
        types_action = [{'code': t[0], 'label': t[1]} for t in TypeAction.choices]
    except Exception:
        types_action = []

    return Response({
        'entrees':      entrees,       # Ce que le frontend attend
        'types_action': types_action,
        'total':        len(entrees),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recherche(request):
    from apps.courriers.models import Courrier
    from apps.archives.models import ArchiveHistorique
    from apps.courriers.serializers import CourrierSerializer
    from apps.archives.serializers import ArchiveHistoriqueSerializer
    from django.db.models import Q

    org           = request.tenant
    q             = request.query_params.get('q', '').strip()
    type_c        = request.query_params.get('type', '')
    statut        = request.query_params.get('statut', '')
    priorite      = request.query_params.get('priorite', '')
    date_debut    = request.query_params.get('date_debut', '')
    date_fin      = request.query_params.get('date_fin', '')
    avec_arc      = request.query_params.get('avec_archives') == 'true'
    type_document = request.query_params.get('type_document', '')  # ← AJOUTER

    qs_c = Courrier.objects.filter(organisation=org)
    if q:
        qs_c = qs_c.filter(
            Q(objet__icontains=q) | Q(expediteur__icontains=q) |
            Q(numero_officiel__icontains=q) | Q(reference_exp__icontains=q)
        )
    if type_c:   qs_c = qs_c.filter(type_courrier=type_c)
    if statut:   qs_c = qs_c.filter(statut=statut)
    if priorite: qs_c = qs_c.filter(priorite=priorite)
    if date_debut: qs_c = qs_c.filter(date_reception__gte=date_debut)
    if date_fin:   qs_c = qs_c.filter(date_reception__lte=date_fin)

    courriers_data = CourrierSerializer(qs_c[:50], many=True, context={'request': request}).data

    archives_data = []
    qs_a_count    = 0
    if avec_arc:
        qs_a = ArchiveHistorique.objects.filter(organisation=org)
        if q:
            qs_a = qs_a.filter(
                Q(intitule__icontains=q) | Q(reference_systeme__icontains=q) |
                Q(mots_cles__icontains=q)
            )
        if type_document: qs_a = qs_a.filter(type_document=type_document)  # ← AJOUTER
        if date_debut:    qs_a = qs_a.filter(date_document__gte=date_debut)
        if date_fin:      qs_a = qs_a.filter(date_document__lte=date_fin)
        qs_a_count    = qs_a.count()
        archives_data = ArchiveHistoriqueSerializer(qs_a[:50], many=True, context={'request': request}).data

    return Response({
        'courriers':       courriers_data,
        'archives':        archives_data,
        'total_courriers': qs_c.count(),
        'total_archives':  qs_a_count,
    })
    
# Remplacer strftime (SQLite) par to_char (PostgreSQL)
from django.db.models.functions import TruncMonth
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistiques(request):
    from apps.courriers.models import Courrier
    org  = request.tenant
    qs   = Courrier.objects.filter(organisation=org)
    now  = timezone.now()

    # Filtres période
    periode    = request.query_params.get('periode', 'mois')
    date_debut = request.query_params.get('date_debut')
    date_fin   = request.query_params.get('date_fin')

    if date_debut: qs = qs.filter(date_saisie__date__gte=date_debut)
    if date_fin:   qs = qs.filter(date_saisie__date__lte=date_fin)

    total      = qs.count()
    total_rejet = qs.filter(statut='REJETE').count()
    taux_rejet = round((total_rejet / total * 100), 1) if total > 0 else 0

    # par_mois avec PostgreSQL
    par_mois = list(
        qs.annotate(mois=TruncMonth('date_saisie'))
          .values('mois').annotate(total=Count('id')).order_by('mois')
    )
    # Convertir les dates en string
    par_mois_clean = [
        {'mois': str(p['mois'])[:7] if p['mois'] else '', 'total': p['total']}
        for p in par_mois
    ]

    return Response({
        'operationnels': {
            'recu_jour':              qs.filter(date_saisie__date=now.date()).count(),
            'recu_semaine':           qs.filter(date_saisie__date__gte=now.date()-timedelta(days=7)).count(),
            'recu_mois':              qs.filter(date_saisie__date__gte=now.date()-timedelta(days=30)).count(),
            'en_attente_imputation':  qs.filter(statut='EN_ATT_IMP').count(),
            'non_consultes_j3':       qs.filter(statut='IMPUTE', date_imputation__lte=now-timedelta(days=3)).count(),
            'en_retard_j7':           qs.filter(date_saisie__lte=now-timedelta(days=7)).exclude(statut__in=['TRAITE','ARCHIVE']).count(),
            'delai_reception_imputation':  None,
            'delai_imputation_traitement': None,
        },
        'strategiques': {
            'total':               total,
            'volume_mois_actuel':  qs.filter(date_saisie__month=now.month, date_saisie__year=now.year).count(),
            'volume_mois_passe':   qs.filter(date_saisie__month=(now.month-1) or 12, date_saisie__year=now.year if now.month > 1 else now.year-1).count(),
            'taux_rejet':          taux_rejet,
            'par_statut':          list(qs.values('statut').annotate(total=Count('id'))),
            'par_mois':            par_mois_clean,
        }
    })

import io
from django.http import HttpResponse

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel(request):
    import openpyxl
    from apps.courriers.models import Courrier

    org = request.tenant
    qs  = Courrier.objects.filter(organisation=org)

    date_debut = request.query_params.get('date_debut')
    date_fin   = request.query_params.get('date_fin')
    if date_debut: qs = qs.filter(date_saisie__date__gte=date_debut)
    if date_fin:   qs = qs.filter(date_saisie__date__lte=date_fin)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Statistiques'

    # En-têtes
    ws.append(['Numéro', 'Objet', 'Expéditeur', 'Statut', 'Date saisie', 'Type'])

    for c in qs:
        ws.append([
            c.numero_officiel or '',
            c.objet or '',
            c.expediteur or '',
            c.statut or '',
            c.date_saisie.strftime('%d/%m/%Y') if c.date_saisie else '',
            c.type_courrier or '',
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="statistiques_ged.xlsx"'}
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from apps.courriers.models import Courrier

    org = request.tenant
    qs  = Courrier.objects.filter(organisation=org)

    date_debut = request.query_params.get('date_debut')
    date_fin   = request.query_params.get('date_fin')
    if date_debut: qs = qs.filter(date_saisie__date__gte=date_debut)
    if date_fin:   qs = qs.filter(date_saisie__date__lte=date_fin)

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elems  = []

    elems.append(Paragraph('Statistiques GED', styles['Title']))
    elems.append(Spacer(1, 12))

    data = [['Numéro', 'Objet', 'Expéditeur', 'Statut', 'Date']]
    for c in qs[:200]:
        data.append([
            c.numero_officiel or '',
            (c.objet or '')[:40],
            (c.expediteur or '')[:30],
            c.statut or '',
            c.date_saisie.strftime('%d/%m/%Y') if c.date_saisie else '',
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1565C0')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTSIZE',   (0,0), (-1,0), 10),
        ('FONTSIZE',   (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f8ff')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elems.append(table)
    doc.build(elems)
    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf',
        headers={'Content-Disposition': 'attachment; filename="statistiques_ged.pdf"'}
    )