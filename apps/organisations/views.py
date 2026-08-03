# apps/organisations/views.py
# CORRECTIONS:
# 1. lister_organisations: accepte is_staff aussi (superuser créé via createsuperuser)
# 2. Ajouter champs typographie dans mes_parametres_organisation
# 3. Modifier Organisation model pour supporter typographie

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


def est_super_admin(user):
    """Vérifie si l'utilisateur est super-admin (is_superuser OU is_staff)"""
    return user.is_superuser or user.is_staff

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lister_organisations(request):
    """Super-Admin liste et crée des organisations."""
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.organisations.models import Organisation
    from apps.organisations.serializers import OrganisationSerializer

    if request.method == 'GET':
        orgs = Organisation.objects.all().order_by('-date_creation')
        return Response(OrganisationSerializer(orgs, many=True, context={'request': request}).data)

    # POST — Créer une organisation
    data = request.data

    if not data.get('code_tenant'):
        return Response({'detail': 'Le code tenant est obligatoire.'}, status=400)
    if not data.get('nom'):
        return Response({'detail': 'Le nom est obligatoire.'}, status=400)
    if not data.get('admin_nom'):
        return Response({'detail': "Le nom de l'admin est obligatoire."}, status=400)
    if not data.get('admin_prenom'):
        return Response({'detail': "Le prénom de l'admin est obligatoire."}, status=400)

    code = data.get('code_tenant', '').strip().lower()
    if Organisation.objects.filter(code_tenant=code).exists():
        return Response({'detail': f'Le code tenant "{code}" est déjà utilisé.'}, status=400)

    org = Organisation(
        code_tenant          = code,
        nom                  = data.get('nom', ''),
        slogan               = data.get('slogan', ''),
        texte_pied_page      = data.get('texte_pied_page', f"© {data.get('nom', '')}"),
        couleur_principale   = data.get('couleur_principale', '#1565C0'),
        couleur_accent       = data.get('couleur_accent', '#FDD835'),
        couleur_danger       = data.get('couleur_danger', '#D32F2F'),
        flou_image_fond      = int(data.get('flou_image_fond', 5)),
        plan                 = data.get('plan', 'GRATUIT'),
        max_utilisateurs     = int(data.get('max_utilisateurs', 50)),
        max_stockage_go      = int(data.get('max_stockage_go', 100)),
        timeout_inactivite   = int(data.get('timeout_inactivite', 30)),
        duree_validite_mdp   = int(data.get('duree_validite_mdp', 90)),
        tentatives_max       = int(data.get('tentatives_max', 5)),
        double_auth_active   = data.get('double_auth_active', False),
        email_expediteur     = data.get('email_expediteur', ''),
        domaine_personnalise = data.get('domaine_personnalise') or None,
    )

    if 'logo' in request.FILES:
        org.logo = request.FILES['logo']
    if 'image_fond_login' in request.FILES:
        org.image_fond_login = request.FILES['image_fond_login']

    org.save()

    # Créer l'admin de l'organisation
    from apps.users.models import Utilisateur
    import secrets, string

    pwd         = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$') for _ in range(14))
    identifiant = data.get('admin_identifiant', '').strip() or f"admin_{org.code_tenant}"

    if Utilisateur.objects.filter(identifiant=identifiant).exists():
        identifiant = f"admin_{org.code_tenant}_{org.id}"

    admin = Utilisateur.objects.create_user(
        organisation = org,
        identifiant  = identifiant,
        password     = pwd,
        nom          = data.get('admin_nom', ''),
        prenom       = data.get('admin_prenom', ''),
        profil       = 'ADMIN',
        email        = data.get('admin_email', ''),
        fonction     = 'Administrateur',
    )
    org.admin_principal = admin
    org.save()

    # Envoyer les identifiants par email
    if admin.email:
        import threading
        from django.core.mail import send_mail
        from django.conf import settings

        _pwd    = pwd
        _admin  = admin
        _org    = org

        def _envoyer_identifiants():
            corps = f"""Bonjour {_admin.prenom} {_admin.nom},

Votre espace GED a été créé. Voici vos identifiants de connexion :

Organisation : {_org.nom}
Code tenant  : {_org.code_tenant}
Identifiant  : {_admin.identifiant}
Mot de passe : {_pwd}

Connectez-vous ici : http://localhost:5173/{_org.code_tenant}/login

IMPORTANT : Changez votre mot de passe dès votre première connexion.

---
Message automatique — ne pas répondre.
GED SaaS"""
            try:
                send_mail(
                    subject        = f"[GED] Vos identifiants — {_org.nom}",
                    message        = corps,
                    from_email     = settings.DEFAULT_FROM_EMAIL,
                    recipient_list = [_admin.email],
                    fail_silently  = False,
                )
                print(f"EMAIL ENVOYE A : {_admin.email}")
            except Exception as e:
                print(f"ERREUR EMAIL : {e}")

        threading.Thread(target=_envoyer_identifiants, daemon=False).start()

    from apps.organisations.serializers import OrganisationSerializer
    return Response({
        'organisation':      OrganisationSerializer(org, context={'request': request}).data,
        'admin_identifiant': admin.identifiant,
        'admin_password':    pwd,
        'message':           'Organisation créée avec succès.'
    }, status=201)
    
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def detail_organisation(request, pk):
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.organisations.models import Organisation
    from apps.organisations.serializers import OrganisationSerializer

    try:
        org = Organisation.objects.get(pk=pk)
    except Organisation.DoesNotExist:
        return Response({'detail': 'Organisation introuvable.'}, status=404)

    if request.method == 'GET':
        return Response(OrganisationSerializer(org, context={'request': request}).data)

    if request.method == 'PATCH':
        data = request.data

        champs_texte = [
            'nom', 'slogan', 'texte_pied_page',
            'couleur_principale', 'couleur_accent', 'couleur_danger',
            'plan', 'email_expediteur', 'texte_email_2fa', 'workflow_type', 'prefixe_courrier',
        ]
        for c in champs_texte:
            if c in data:
                setattr(org, c, data[c])

        champs_int = [
            'timeout_inactivite', 'duree_validite_mdp', 'tentatives_max',
            'flou_image_fond', 'max_utilisateurs', 'max_stockage_go',
        ]
        for c in champs_int:
            if c in data:
                setattr(org, c, int(data[c]))

        if 'double_auth_active' in data:
            org.double_auth_active = data['double_auth_active'] in [True, 'true', '1']
        if 'active' in data:
            org.active = data['active'] in [True, 'true', '1']
        if 'domaine_personnalise' in data:
            org.domaine_personnalise = data['domaine_personnalise'] or None

        if 'logo' in request.FILES:
            org.logo = request.FILES['logo']
        if 'image_fond_login' in request.FILES:
            org.image_fond_login = request.FILES['image_fond_login']
        if data.get('supprimer_logo') in [True, 'true', '1']:
            if org.logo: org.logo.delete(save=False)
            org.logo = None
        if data.get('supprimer_fond') in [True, 'true', '1']:
            if org.image_fond_login: org.image_fond_login.delete(save=False)
            org.image_fond_login = None

        org.save()
        return Response(OrganisationSerializer(org, context={'request': request}).data)

    if request.method == 'DELETE':
        try:
            if org.logo:
                org.logo.delete(save=False)
            if org.image_fond_login:
                org.image_fond_login.delete(save=False)
            if org.favicon:
                org.favicon.delete(save=False)
            nom = org.nom
            org.delete()
            return Response({'detail': f'Organisation "{nom}" supprimée définitivement.'})
        except Exception as e:
            return Response({'detail': f'Erreur lors de la suppression : {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admins_organisation(request, pk):
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.users.models import Utilisateur
    admins = Utilisateur.objects.filter(organisation_id=pk, profil='ADMIN').order_by('nom')
    return Response([{
        'id': a.id, 'identifiant': a.identifiant,
        'nom': a.nom, 'prenom': a.prenom,
        'email': a.email, 'is_active': a.is_active,
    } for a in admins])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajouter_admin_organisation(request, pk):
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.organisations.models import Organisation
    from apps.users.models import Utilisateur
    import secrets, string

    try:
        org = Organisation.objects.get(pk=pk)
    except Organisation.DoesNotExist:
        return Response({'detail': 'Organisation introuvable.'}, status=404)

    data = request.data
    if not data.get('nom') or not data.get('prenom'):
        return Response({'detail': 'Nom et prénom obligatoires.'}, status=400)

    pwd = data.get('password') or ''.join(
        secrets.choice(string.ascii_letters + string.digits + '!@#$') for _ in range(14)
    )
    nb = Utilisateur.objects.filter(organisation=org, profil='ADMIN').count() + 1
    identifiant = data.get('identifiant', f"admin_{org.code_tenant}_{nb}")

    if Utilisateur.objects.filter(identifiant=identifiant).exists():
        return Response({'detail': 'Cet identifiant existe déjà.'}, status=400)

    admin = Utilisateur.objects.create_user(
        organisation=org, identifiant=identifiant, password=pwd,
        nom=data['nom'], prenom=data['prenom'],
        profil='ADMIN', email=data.get('email', ''),
    )
    return Response({
        'id': admin.id, 'identifiant': admin.identifiant,
        'admin_password': pwd, 'message': 'Admin créé.'
    }, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_admin_organisation(request, pk, admin_pk):
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.users.models import Utilisateur
    try:
        admin = Utilisateur.objects.get(pk=admin_pk, organisation_id=pk, profil='ADMIN')
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Admin introuvable.'}, status=404)

    data = request.data
    for c in ['nom', 'prenom', 'email']:
        if c in data: setattr(admin, c, data[c])
    if 'password' in data and data['password']:
        admin.set_password(data['password'])
    if 'is_active' in data:
        admin.is_active = data['is_active'] in [True, 'true', '1']
    admin.save()
    return Response({'detail': 'Admin mis à jour.'})


# apps/organisations/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def parametres_publics_organisation(request):
    from apps.organisations.models import Organisation

    code = request.query_params.get('tenant', '').strip()
    org  = None

    if code:
        try:
            org = Organisation.objects.get(code_tenant=code, active=True)
        except Organisation.DoesNotExist:
            pass

    if not org:
        host = request.get_host().split(':')[0]
        try:
            org = Organisation.objects.get(domaine_personnalise=host, active=True)
        except Organisation.DoesNotExist:
            pass

    if not org:
        return Response({
            'nom_application': 'GED',
            'slogan': 'Gestion Electronique des Documents',
            'texte_pied_page': '© GED SaaS',
            'couleur_principale': '#1565C0',
            'couleur_accent': '#FDD835',
            'couleur_danger': '#D32F2F',
            'logo_url': None,
            'favicon_url': None,
            'image_fond_url': None,
            'flou_image_fond': 5,
            'timeout_inactivite': 30,
            'double_auth_active': False,
            'code_tenant': code or '',
            'police': "'Segoe UI', sans-serif",
            'taille_texte_base': '14px',
            'couleur_texte': '#222222',
            'couleur_texte_secondaire': '#666666',
            'graisse_titres': '700',
            'rayon_bord': '6px',
        })

    logo_url = request.build_absolute_uri(org.logo.url) if org.logo else None
    favicon_url = request.build_absolute_uri(org.favicon.url) if org.favicon else None
    fond_url = request.build_absolute_uri(org.image_fond_login.url) if org.image_fond_login else None

    return Response({
        'nom_application': org.nom,
        'slogan': org.slogan,
        'texte_pied_page': org.texte_pied_page,
        'couleur_principale': org.couleur_principale,
        'couleur_accent': org.couleur_accent,
        'couleur_danger': org.couleur_danger,
        'logo_url': logo_url,
        'favicon_url': favicon_url,
        'image_fond_url': fond_url,
        'flou_image_fond': org.flou_image_fond,
        'timeout_inactivite': org.timeout_inactivite,
        'double_auth_active': org.double_auth_active,
        'code_tenant': org.code_tenant,
        'police': getattr(org, 'police', "'Segoe UI', sans-serif"),
        'taille_texte_base': getattr(org, 'taille_texte_base', '14px'),
        'couleur_texte': getattr(org, 'couleur_texte', '#222222'),
        'couleur_texte_secondaire': getattr(org, 'couleur_texte_secondaire', '#666666'),
        'graisse_titres': getattr(org, 'graisse_titres', '700'),
        'rayon_bord': getattr(org, 'rayon_bord', '6px'),
    })
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mes_parametres_organisation(request):
    if not request.tenant:
        return Response({'detail': 'Organisation non trouvée.'}, status=400)

    org = request.tenant

    if request.method == 'GET':
        logo_url = request.build_absolute_uri(org.logo.url) if org.logo else None
        fond_url = request.build_absolute_uri(org.image_fond_login.url) if org.image_fond_login else None
        return Response({
            'nom_application':    org.nom,
            'slogan':             org.slogan,
            'texte_pied_page':    org.texte_pied_page,
            'couleur_principale': org.couleur_principale,
            'couleur_accent':     org.couleur_accent,
            'couleur_danger':     org.couleur_danger,
            'logo_url':           logo_url,
            'image_fond_url':     fond_url,
            'flou_image_fond':    org.flou_image_fond,
            'timeout_inactivite': org.timeout_inactivite,
            'duree_validite_mdp': org.duree_validite_mdp,
            'tentatives_max':     org.tentatives_max,
            'double_auth_active': org.double_auth_active,
            'email_expediteur':   org.email_expediteur,
            'texte_email_2fa':    org.texte_email_2fa,
            'code_tenant':        org.code_tenant,
            'plan':               org.plan,
            'max_utilisateurs':   org.max_utilisateurs,
            'nb_utilisateurs':    org.utilisateurs.filter(is_active=True).count(),
            # Typographie
            'police':                   getattr(org, 'police', "'Segoe UI', sans-serif"),
            'taille_texte_base':        getattr(org, 'taille_texte_base', '14px'),
            'couleur_texte':            getattr(org, 'couleur_texte', '#222222'),
            'couleur_texte_secondaire': getattr(org, 'couleur_texte_secondaire', '#666666'),
            'graisse_titres':           getattr(org, 'graisse_titres', '700'),
            'rayon_bord':               getattr(org, 'rayon_bord', '6px'),
        })

    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    data = request.data

    champs_texte = [
        'nom', 'slogan', 'texte_pied_page',
        'couleur_principale', 'couleur_accent', 'couleur_danger',
        'email_expediteur', 'texte_email_2fa',
        # Typographie
        'police', 'taille_texte_base', 'couleur_texte',
        'couleur_texte_secondaire', 'graisse_titres', 'rayon_bord',
    ]
    for c in champs_texte:
        if c in data:
            setattr(org, c, data[c])

    champs_int = ['timeout_inactivite', 'duree_validite_mdp', 'tentatives_max', 'flou_image_fond']
    for c in champs_int:
        if c in data:
            setattr(org, c, int(data[c]))

    if 'double_auth_active' in data:
        org.double_auth_active = data['double_auth_active'] in [True, 'true', '1']

    if 'logo' in request.FILES:
        org.logo = request.FILES['logo']
    if 'image_fond_login' in request.FILES:
        org.image_fond_login = request.FILES['image_fond_login']
    if data.get('supprimer_logo') in [True, 'true', '1']:
        if org.logo: org.logo.delete(save=False)
        org.logo = None
    if data.get('supprimer_fond') in [True, 'true', '1']:
        if org.image_fond_login: org.image_fond_login.delete(save=False)
        org.image_fond_login = None

    if 'consignes_imputation' in request.data:
        import json
        val = request.data['consignes_imputation']
        try:
            org.consignes_imputation = json.loads(val) if isinstance(val, str) else val
        except (json.JSONDecodeError, TypeError):
            org.consignes_imputation = []
    org.save()
    return Response({'detail': 'Paramètres enregistrés.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def securite_organisation(request, pk):
    if not est_super_admin(request.user):
        return Response({'detail': 'Réservé au Super-Admin.'}, status=403)

    from apps.organisations.models import Organisation
    try:
        org = Organisation.objects.get(pk=pk)
    except Organisation.DoesNotExist:
        return Response({'detail': 'Organisation introuvable.'}, status=404)

    if request.method == 'GET':
        return Response({
            'timeout_inactivite': org.timeout_inactivite,
            'duree_validite_mdp': org.duree_validite_mdp,
            'tentatives_max':     org.tentatives_max,
            'double_auth_active': org.double_auth_active,
            'email_expediteur':   org.email_expediteur,
            'texte_email_2fa':    org.texte_email_2fa,
        })

    data = request.data
    for c in ['timeout_inactivite', 'duree_validite_mdp', 'tentatives_max']:
        if c in data: setattr(org, c, int(data[c]))
    if 'double_auth_active' in data:
        org.double_auth_active = data['double_auth_active'] in [True, 'true', '1']
    for c in ['email_expediteur', 'texte_email_2fa']:
        if c in data: setattr(org, c, data[c])
    org.save()
    return Response({'detail': 'Paramètres de sécurité mis à jour.'})
